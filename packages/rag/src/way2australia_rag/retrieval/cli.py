"""Developer retrieval CLI (Spec 005 R5, R6).

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

from way2australia_rag.ingestion.cli import (
    ClientFactory,
    build_embedder,
    default_client_factory,
)
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.errors import (
    RetrievalConfigurationError,
    RetrievalError,
)
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.models import RetrievalResult
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
    DenseRetriever,
)
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2


def format_result(result: RetrievalResult) -> str:
    lines = [
        f"index: {safe_text(result.collection)} "
        f"(index_version {safe_text(result.index_version)}; "
        f"embedder {safe_text(result.embedder_model_id)} @ "
        f"{safe_text(result.embedder_revision)}, "
        f"fake={str(result.embedder_is_fake).lower()}, "
        f"device={safe_text(result.device or 'unknown')})",
        f"hits: {len(result.hits)} (top_k {result.top_k}, {result.latency_ms:.1f} ms)",
    ]
    lines.extend(
        f"{hit.rank}  {safe_text(hit.document_id)}  {safe_text(hit.section_id)}  "
        f"{hit.score:.4f}  {safe_text(hit.title)}"
        for hit in result.hits
    )
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
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory = default_client_factory,
) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
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
        embedder = build_embedder(config, provider)  # missing extra exits here
        client = client_factory(settings)
        index = DenseIndex.open(
            client, settings.collection_base, config.index_version, embedder.info
        )
        access = resolve_access(guest_access(settings))
        result = DenseRetriever(index, embedder).retrieve(
            args.query, access, args.top_k
        )
    except (RetrievalError, IngestionError) as error:
        # Both families are path- and secret-free by contract.
        print(f"ERROR {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, bad config
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    print(format_result(result))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
