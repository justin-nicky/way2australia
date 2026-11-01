"""Developer retrieval CLI (Spec 005 R5, R6; Spec 007 R8).

Run as ``python -m way2australia_rag.retrieval.cli`` (via ``make retrieve``).

Authorization is server configuration only: there is no flag for role, scope or
tenant. Exit codes: 0 success (including zero hits); 2 refusal or configuration
error. Output carries labels, ``document_id``/``section_id``, scores and titles
only: no absolute paths, API key or chunk text.
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

from way2australia_rag.ingestion.cli import ClientFactory
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import (
    RetrievalConfigurationError,
    RetrievalError,
)
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
)
from way2australia_rag.retrieval.strategy import load_retrieval_config
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2
DEFAULT_RETRIEVAL_CONFIG = "config/retrieval.yaml"
MAX_TERMS_NOTE = "note: the query was cut to its first 64 distinct terms for BM25."


def _strategy_line(result: RetrievalResult) -> str:
    line = f"strategy: {safe_text(result.strategy)}"
    if result.fallback_reason is not None:
        line += (
            f" (requested: {safe_text(result.requested_strategy or 'unknown')}; "
            f"fallback: {safe_text(result.fallback_reason)})"
        )
    return line


def format_result(result: RetrievalResult) -> str:
    lines = [
        f"index: {safe_text(result.collection)} "
        f"(index_version {safe_text(result.index_version)}; "
        f"embedder {safe_text(result.embedder_model_id)} @ "
        f"{safe_text(result.embedder_revision)}, "
        f"fake={str(result.embedder_is_fake).lower()}, "
        f"device={safe_text(result.device or 'unknown')})",
        f"hits: {len(result.hits)} (strategy={safe_text(result.strategy)}, "
        f"top_k {result.top_k}, {result.latency_ms:.1f} ms)",
    ]
    if result.fallback_reason is not None:
        lines.insert(0, _strategy_line(result))
    for hit in result.hits:
        line = (
            f"{hit.rank}  {safe_text(hit.document_id)}  {safe_text(hit.section_id)}  "
            f"{hit.score:.4f}  {safe_text(hit.title)}"
        )
        if hit.leg_ranks is not None:
            legs = "  ".join(
                f"{leg}={'-' if hit.leg_ranks.get(leg) is None else hit.leg_ranks[leg]}"
                for leg in ("dense", "bm25")
            )
            line += f"  {legs}"
        lines.append(line)
    if result.query_terms_truncated:
        lines.append(MAX_TERMS_NOTE)
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m way2australia_rag.retrieval.cli",
        description="Dense retrieval over the guest/public index.",
    )
    parser.add_argument("query")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"ingestion config (default: <repo-root>/{DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument(
        "--embedder",
        choices=("bge_m3", "fake"),
        default=None,
        help="embedder (default: embedder.provider from the config)",
    )
    parser.add_argument(
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=None,
        help="retrieval strategy (default: default_strategy in config/retrieval.yaml)",
    )
    parser.add_argument(
        "--retrieval-config",
        type=Path,
        default=None,
        help=f"retrieval config (default: <repo-root>/{DEFAULT_RETRIEVAL_CONFIG})",
    )
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory | None = None,
) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    opened = None
    try:
        if not args.query.strip():
            raise RetrievalConfigurationError("the query must not be empty.")
        if not MIN_TOP_K <= args.top_k <= MAX_TOP_K:
            raise RetrievalConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(RetrievalConfigurationError)
        provider = args.embedder or config.embedder.provider
        retrieval_config = load_retrieval_config(
            args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
        )
        strategy = Strategy(args.strategy or retrieval_config.default_strategy)
        opened = open_retrieval(
            strategy,
            settings=settings,
            ingestion_config=config,
            retrieval_config=retrieval_config,
            provider=provider,
            repo_root=repo_root,
            client_factory=client_factory,
        )
        access = resolve_access(guest_access(settings))
        result = opened.retriever.retrieve(args.query, access, args.top_k)
    except (RetrievalError, IngestionError) as error:
        # Both families are path- and secret-free by contract.
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, bad config
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    finally:
        if opened is not None:
            opened.close()
    if result.fallback_reason is not None:
        print(
            f"WARNING retrieval fell back to {safe_text(result.strategy)}: "
            f"{safe_text(result.fallback_reason)}",
            file=sys.stderr,
        )
    print(format_result(result))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
