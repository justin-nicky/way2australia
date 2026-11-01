"""Command-line entry point (Spec 004 R11, R12).

Run as ``python -m way2australia_rag.ingestion.cli`` (via ``make ingest``).

Exit codes: 0 success; 1 one or more document failures; 2 refusal or
configuration error (any ``IngestionError``, an unreachable Qdrant, bad config).
Output carries labels, counts and ``document_id``s only: no absolute paths, no
document text, no API key.
"""

import argparse
import asyncio
import logging
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from qdrant_client import QdrantClient

from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    RuntimeSettings,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import Embedder, FakeEmbedder
from way2australia_rag.ingestion.errors import (
    IngestionConfigurationError,
    IngestionError,
)
from way2australia_rag.ingestion.service import IngestionService, RunReport
from way2australia_rag.ingestion.store import QdrantIndexStore
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)

EXIT_OK = 0
EXIT_DOCUMENT_FAILURES = 1
EXIT_REFUSED = 2

ClientFactory = Callable[[RuntimeSettings], QdrantClient]


def default_client_factory(settings: RuntimeSettings) -> QdrantClient:
    key = settings.qdrant_api_key
    return QdrantClient(
        location=settings.qdrant_url,
        api_key=key.get_secret_value() if key is not None else None,
    )


def build_embedder(config: IngestionConfig, provider: str) -> Embedder:
    """Build exactly one embedder for the run."""
    embedder = config.embedder
    if provider == "fake":
        return FakeEmbedder(embedder.fake_vector_size)
    # Imported here so a path that builds no embedder (`bm25`) never loads the
    # module (Spec 008 R5).
    from way2australia_rag.ingestion.bge_m3 import BGE_M3_MODEL_ID, BgeM3Embedder

    if embedder.model_id != BGE_M3_MODEL_ID or not embedder.normalize:
        raise IngestionConfigurationError(
            f"the bge_m3 embedder supports only {BGE_M3_MODEL_ID} with "
            "normalize: true; check embedder.model_id and embedder.normalize."
        )
    return BgeM3Embedder(embedder.revision, embedder.batch_size)


def build_chunker(config: IngestionConfig) -> HeadingChunker:
    chunker = HeadingChunker(config.chunker.max_chunk_chars)
    if (config.chunker.name, config.chunker.version) != (
        chunker.name,
        chunker.version,
    ):
        raise IngestionConfigurationError(
            f"unsupported chunker '{config.chunker.name}' version "
            f"'{config.chunker.version}'; check chunker.name and chunker.version."
        )
    return chunker


def format_summary(report: RunReport, embedder_revision: str) -> str:
    lines = [
        f"index: {report.collection} (index_version {report.index_version}; "
        f"embedder {report.embedder_model_id} @ {embedder_revision}, "
        f"fake={str(report.embedder_is_fake).lower()})",
        f"added: {len(report.added)}  updated: {len(report.updated)}  "
        f"unchanged: {len(report.unchanged)}  deleted: {len(report.deleted)}",
    ]
    for label, ids in (
        ("added", report.added),
        ("updated", report.updated),
        ("unchanged", report.unchanged),
        ("deleted", report.deleted),
    ):
        if ids:
            lines.append(f"  {label}: {', '.join(ids)}")
    lines.extend(f"ERROR {f.document_id}: {f.reason}" for f in report.failures)
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m way2australia_rag.ingestion.cli",
        description="Index approved public knowledge into Qdrant.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"ingestion config (default: <repo-root>/{DEFAULT_CONFIG_PATH})",
    )
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
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(IngestionConfigurationError)
        provider = args.embedder or config.embedder.provider
        embedder = build_embedder(config, provider)  # the run's only embedder
        chunker = build_chunker(config)
        repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=repo_root))
        store = QdrantIndexStore(
            client_factory(settings), settings.collection_base, config.index_version
        )
        service = IngestionService(
            repository,
            GUEST_PUBLIC_POLICY,
            chunker,
            embedder,
            store,
            config.embedder.batch_size,
        )
        report = asyncio.run(service.run())
    except (IngestionError, DocumentRepositoryError) as error:
        # Both families are path-free by contract (document_id and field names).
        print(f"ERROR {type(error).__name__}: {error}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, bad repository
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    print(format_summary(report, embedder.info.revision))
    return EXIT_DOCUMENT_FAILURES if report.failures else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
