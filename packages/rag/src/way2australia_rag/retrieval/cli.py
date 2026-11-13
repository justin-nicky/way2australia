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

from way2australia_rag.ingestion.cli import ClientFactory
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.cli_args import (
    add_retrieval_arguments,
    resolve_retrieval_args,
)
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2
MAX_TERMS_NOTE = "note: the query was cut to its first 64 distinct terms for BM25."


def _strategy_line(result: RetrievalResult) -> str:
    line = f"strategy: {safe_text(result.strategy)}"
    if result.fallback_reason is not None:
        line += (
            f" (requested: {safe_text(result.requested_strategy or 'unknown')}; "
            f"fallback: {safe_text(result.fallback_reason)})"
        )
    return line


def rerank_line(result: RetrievalResult, rerank_requested: bool) -> str | None:
    record = result.rerank
    if record is None:
        return "rerank: off" if not rerank_requested else None
    if record.skipped_reason is not None:
        return (
            f"rerank: skipped ({safe_text(record.skipped_reason)}, "
            f"{safe_text(record.stage or 'unknown')})"
        )
    return (
        f"rerank: {safe_text(record.model_id)}@{safe_text(record.revision[:7])} "
        f"depth {record.depth}"
    )


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
    add_retrieval_arguments(parser)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory | None = None,
) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    opened = None
    try:
        resolved = resolve_retrieval_args(args)
        rerank = resolved.rerank
        opened = open_retrieval(
            resolved.strategy, **resolved.open_kwargs(client_factory)
        )
        access = resolve_access(guest_access(resolved.settings))
        result = opened.retriever.retrieve(
            args.query, access, args.top_k, lote=resolved.lote
        )
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
    print(f"lote: {safe_text(result.lote or 'none')}")
    if result.rerank is not None and result.rerank.skipped_reason is not None:
        print(
            "WARNING reranking skipped: "
            f"{safe_text(result.rerank.skipped_reason)} "
            f"({safe_text(result.rerank.stage or 'unknown')}); "
            "served un-reranked hybrid.",
            file=sys.stderr,
        )
    print(format_result(result))
    line = rerank_line(result, rerank)
    if line is not None:
        print(line)
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
