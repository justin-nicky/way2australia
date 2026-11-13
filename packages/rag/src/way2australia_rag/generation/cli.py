"""`make ask`: retrieval, context, answerability, generation and citation check.

Spec 012 R8. Run as ``python -m way2australia_rag.generation.cli``. Retrieval
arguments are shared with `make retrieve` (`retrieval/cli_args.py`); authorization
is server configuration only. Exit codes: 0 for any of the three answer statuses,
2 for a configuration error or refusal. Output carries labels, identifiers and the
answer (through `safe_text`); never chunk text outside the answer, paths or
credentials.
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from way2australia_rag.generation.base import Generator
from way2australia_rag.generation.build import build_generator
from way2australia_rag.generation.config import (
    DEFAULT_GENERATION_CONFIG,
    load_generation_config,
)
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.models import AnswerResponse
from way2australia_rag.generation.prompts import (
    PromptConfigurationError,
    PromptRegistry,
)
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.ingestion.cli import ClientFactory
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.cli_args import (
    add_retrieval_arguments,
    resolve_retrieval_args,
)
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2
FAKE_WARNING = (
    "WARNING fake generator: this output is deterministic test output, "
    "not a model answer."
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m way2australia_rag.generation.cli",
        description="Answer a question from the guest/public index with citations.",
    )
    add_retrieval_arguments(parser, top_k_default=None)
    parser.add_argument(
        "--generator",
        choices=("fake", "bedrock", "anthropic"),
        default=None,
        help="generator (default: default_generator in config/generation.yaml)",
    )
    parser.add_argument(
        "--model-id",
        default=None,
        help=(
            "model ID for bedrock or anthropic (default: bedrock.model_id or "
            "anthropic.model_id in the generation config)"
        ),
    )
    parser.add_argument(
        "--generation-config",
        type=Path,
        default=None,
        help=f"generation config (default: <repo-root>/{DEFAULT_GENERATION_CONFIG})",
    )
    return parser


def _retrieval_line(response: AnswerResponse) -> str:
    retrieval = response.identity.retrieval
    line = f"retrieval: strategy {safe_text(retrieval['strategy'])}"
    if retrieval["fallback_reason"] is not None:
        line += (
            f" (requested: {safe_text(retrieval['requested_strategy'] or 'unknown')}; "
            f"fallback: {safe_text(retrieval['fallback_reason'])})"
        )
    rerank = retrieval["rerank"]
    if rerank is None:
        line += "; rerank: off"
    elif rerank["skipped_reason"] is not None:
        line += f"; rerank: skipped ({safe_text(rerank['skipped_reason'])})"
    else:
        line += (
            f"; rerank: {safe_text(rerank['model_id'])} depth {rerank['depth']}"
            f" (fake={str(rerank['is_fake']).lower()})"
        )
    return line


def _citation_line(source_id: str, title: str, authority: str, url: str | None) -> str:
    return (
        f"[{safe_text(source_id)}] {safe_text(title)} - {safe_text(authority)} - "
        f"{safe_text(url) if url else 'owner-approved'}"
    )


def format_response(response: AnswerResponse, generator: Generator) -> str:
    lines = [f"status: {response.status.value}"]
    if response.reason is not None:
        lines.append(f"reason: {response.reason.value}")
    if response.sub_reason is not None:
        lines.append(f"sub_reason: {safe_text(response.sub_reason)}")
    if response.answer is not None:
        lines.append("answer:")
        lines.extend(f"  {safe_text(line)}" for line in response.answer.splitlines())
    for citation in response.citations:
        lines.append(
            _citation_line(
                citation.source_id,
                citation.title,
                citation.source_authority,
                citation.source_url,
            )
        )
    if response.message is not None:
        lines.append(
            f"message ({safe_text(response.message_language)}): "
            f"{safe_text(response.message)}"
        )
    for source in response.evidence:
        lines.append(
            _citation_line(
                source.source_id,
                source.title,
                source.source_authority,
                source.source_url,
            )
            + f" | {safe_text(source.snippet)}"
        )
    lines.append(_retrieval_line(response))
    info = generator.info
    called = "" if response.identity.generator is not None else "; not called"
    where = info.inference_profile or info.region or "none"
    lines.append(
        f"generator: {info.provider} (model {safe_text(info.model_id)}"
        f", endpoint {safe_text(info.endpoint or 'none')}"
        f", region/profile {safe_text(where)}"
        f", fake={str(info.is_fake).lower()}{called}"
        + (
            f", response model {safe_text(response.identity.response_model)}"
            if response.identity.response_model
            else ""
        )
        + ")"
    )
    prompt = response.identity.prompt
    lines.append(
        f"prompt: {safe_text(prompt.prompt_id)} v{prompt.prompt_version} "
        f"{safe_text(prompt.sha256[:12])}"
    )
    usage = response.usage
    if usage is None:
        lines.append("tokens: n/a")
    else:
        tokens_in = "n/a" if usage.input_tokens is None else usage.input_tokens
        tokens_out = "n/a" if usage.output_tokens is None else usage.output_tokens
        lines.append(
            f"tokens: in {tokens_in} out {tokens_out} attempts {usage.attempts}"
        )
    latency = response.latency_ms
    lines.append(
        "latency: " + " ".join(f"{name} {value:.1f}" for name, value in latency.items())
    )
    return "\n".join(lines)


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory | None = None,
) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root = args.repo_root.resolve()
    generator: Generator | None = None
    opened = None
    try:
        config = load_generation_config(
            args.generation_config or repo_root / DEFAULT_GENERATION_CONFIG,
            repo_root,
        )
        prompt_version = PromptRegistry(repo_root).get(
            config.prompt.id, config.prompt.version
        )
        # Built before retrieval opens: a configuration error never touches Qdrant.
        generator = build_generator(config, args.generator, args.model_id)
        if args.top_k is None:
            args.top_k = config.retrieval.top_k
        resolved = resolve_retrieval_args(args)
        opened = open_retrieval(
            resolved.strategy, **resolved.open_kwargs(client_factory)
        )
        access = resolve_access(guest_access(resolved.settings))
        service = AnswerService(
            opened.retriever,
            ContextBuilder(config.context),
            prompt_version,
            generator,
            config,
        )
        response = service.answer(args.query, access, args.top_k, lote=resolved.lote)
    except (
        RetrievalError,
        IngestionError,
        GeneratorConfigurationError,
        PromptConfigurationError,
    ) as error:
        # These families are path- and secret-free by contract.
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, SDK errors
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    finally:
        if generator is not None:
            generator.close()
        if opened is not None:
            opened.close()
    assert generator is not None  # set when no exception was returned above
    if generator.info.is_fake:
        print(FAKE_WARNING, file=sys.stderr)
    retrieval = response.identity.retrieval
    if retrieval["fallback_reason"] is not None:
        print(
            f"WARNING retrieval fell back to {safe_text(retrieval['strategy'])}: "
            f"{safe_text(retrieval['fallback_reason'])}",
            file=sys.stderr,
        )
    print(f"lote: {safe_text(retrieval['lote'] or 'none')}")
    print(format_response(response, generator))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
