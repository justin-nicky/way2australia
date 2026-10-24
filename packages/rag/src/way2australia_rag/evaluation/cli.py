"""Evaluation command line (Spec 006).

Run as ``python -m way2australia_rag.evaluation.cli <subcommand>``.

- ``validate`` (``make validate-evaluation``): exit 0 when valid, 1 on validation
  problems, 2 on configuration errors or an unexpected exception (class name only).
- ``retrieval`` (``make eval-retrieval``): exit 0 on success, 2 on refusal or
  error. Nothing is written on error. There is no flag for embedder, role, scope
  or tenant, and no ``--allow-fake``.
"""

import argparse
import asyncio
import logging
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from way2australia_rag.evaluation.errors import (
    EvaluationConfigurationError,
    EvaluationError,
)
from way2australia_rag.evaluation.results import (
    check_output_free,
    default_output_path,
    write_document,
)
from way2australia_rag.evaluation.retrieval_eval import (
    require_active_suite,
    require_real_embedder,
    require_real_index,
    run_retrieval_evaluation,
)
from way2australia_rag.evaluation.slices import active_registry_languages
from way2australia_rag.evaluation.suite import declared_release_id, load_suite
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.ingestion.cli import (
    ClientFactory,
    build_embedder,
    default_client_factory,
)
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import Embedder
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
    DenseRetriever,
)
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_ERROR = 2
DEFAULT_SUITE = "evaluation/suites/public-eval-v1.json"
DEFAULT_RELEASE = "seed-v1"

log = logging.getLogger(__name__)

EmbedderFactory = Callable[[IngestionConfig, str], Embedder]


def _validate(repo_root: Path) -> int:
    try:
        problems = validate_evaluation(repo_root)
    except EvaluationError as error:
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # never print messages: they may hold case text
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    for problem in problems:
        print(f"ERROR {problem}")
    if problems:
        print(f"validate-evaluation: FAILED with {len(problems)} problem(s)")
        return EXIT_PROBLEMS
    print("validate-evaluation: OK, 0 problems")
    return EXIT_OK


def _authority_map(repo_root: Path) -> dict[str, str]:
    """document_id -> source_authority over the guest/public eligible documents."""
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root))

    async def collect() -> dict[str, str]:
        documents = await list_eligible_documents(repository, GUEST_PUBLIC_POLICY)
        return {d.document_id: str(d.source_authority) for d in documents}

    try:
        return asyncio.run(collect())
    except DocumentRepositoryError as error:
        raise EvaluationConfigurationError(
            "the knowledge corpus is invalid; run `make validate-knowledge`."
        ) from error


def format_summary(document: dict[str, Any], output: Path, repo_root: Path) -> str:
    k = document["top_k"]
    overall = document["metrics"]["overall"]
    latency = document["latency_ms"]
    try:
        shown = output.resolve().relative_to(repo_root.resolve())
    except ValueError:
        shown = Path(output.name)
    settings = document["index_settings"]
    lines = [
        f"index: {document['collection']} (index_version {document['index_version']}; "
        f"embedder {settings['embedder_model_id']} @ {settings['embedder_revision']}, "
        f"fake={str(document['embedder_is_fake']).lower()}, "
        f"device={document['device'] or 'unknown'})",
        f"suite: {document['evaluation_suite_id']} "
        f"v{document['evaluation_suite_version']}"
        f" ({document['case_count']} golden cases, excluded "
        f"{document['excluded_case_count']}), documents: {document['document_count']}",
        f"HitRate@{k}: {overall[f'hit_rate_at_{k}']:.4f} "
        f"(random {document['random_hit_rate_at_k']:.4f} = "
        f"{document['random_hit_rate_formula']})",
        f"Recall@{k}: {overall[f'recall_at_{k}']:.4f}",
        f"MRR: {overall['mrr']:.4f}",
    ]
    for name in ("by_query_language", "by_category", "by_source_authority"):
        for key, value in document["metrics"][name].items():
            flag = " (small sample)" if value["small_sample"] else ""
            lines.append(
                f"{name[3:]} {key}: n={value['n']}{flag} "
                f"HitRate@{k} {value[f'hit_rate_at_{k}']:.4f} MRR {value['mrr']:.4f}"
            )
    absent = document["absent_query_languages"]
    if absent:
        lines.append(f"absent query languages (no golden case): {', '.join(absent)}")
    lines += [
        "section-level measurable cases: "
        f"{document['section_level']['measurable_cases']}",
        f"latency p50 {latency['p50']:.1f} ms, p95 {latency['p95']:.1f} ms "
        f"(warm-up {latency['warmup_ms']:.1f} ms excluded)",
        f"result: {shown}",
        *[f"note: {note}" for note in document["notes"]],
    ]
    return "\n".join(safe_text(line) for line in lines)


def _retrieval(
    args: argparse.Namespace,
    client_factory: ClientFactory,
    embedder_factory: EmbedderFactory,
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root: Path = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    try:
        # 1. top-k, config, runtime settings
        if not MIN_TOP_K <= args.top_k <= MAX_TOP_K:
            raise EvaluationConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(EvaluationConfigurationError)
        # 2. suite; only an active suite is evaluated
        suite = load_suite(repo_root, args.suite)
        require_active_suite(suite)
        # 3. declared release, repository map, language registry
        release_id = declared_release_id(repo_root, args.release)
        authorities = _authority_map(repo_root)
        languages = active_registry_languages(repo_root)
        # 4. output
        now = datetime.now(UTC)
        output: Path = args.output or default_output_path(
            repo_root, config.index_version, now
        )
        check_output_free(output)
        # 5. embedder; a fake one is refused before any Qdrant contact
        embedder = embedder_factory(config, config.embedder.provider)
        require_real_embedder(embedder)
        # 6. read-only index binding; a recorded fake index is refused
        client = client_factory(settings)
        index = DenseIndex.open(
            client, settings.collection_base, config.index_version, embedder.info
        )
        require_real_index(index)
        # 7. the one server-resolved access
        access = resolve_access(guest_access(settings))
        log.info(
            "suite %s loaded; index %s (index_version %s) bound",
            safe_text(suite.manifest.evaluation_suite_id),
            safe_text(index.collection),
            safe_text(index.index_version),
        )
        document = run_retrieval_evaluation(
            retriever=DenseRetriever(index, embedder),
            index=index,
            embedder=embedder,
            access=access,
            suite=suite,
            release_id=release_id,
            top_k=args.top_k,
            authorities=authorities,
            registry_languages=languages,
            repo_root=repo_root,
            clock=lambda: now,
        )
        write_document(output, document)
    except (EvaluationError, RetrievalError, IngestionError) as error:
        # These families are path- and secret-free by contract.
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, bad config
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    print(f"collection: {safe_text(index.collection)}")
    print(format_summary(document, output, repo_root))
    return EXIT_OK


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory = default_client_factory,
    embedder_factory: EmbedderFactory = build_embedder,
) -> int:
    parser = argparse.ArgumentParser(
        prog="evaluation", description="Way2Australia evaluation tools."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser(
        "validate", help="validate evaluation suites, cases and candidates"
    )
    validate.add_argument(
        "--repo-root", type=Path, default=Path.cwd(), help="repository root"
    )
    retrieval = commands.add_parser(
        "retrieval", help="run the active golden cases through dense retrieval"
    )
    retrieval.add_argument("--repo-root", type=Path, default=Path.cwd())
    retrieval.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"ingestion config (default: <repo-root>/{DEFAULT_CONFIG_PATH})",
    )
    retrieval.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    retrieval.add_argument("--suite", default=DEFAULT_SUITE)
    retrieval.add_argument("--release", default=DEFAULT_RELEASE)
    retrieval.add_argument(
        "--output",
        type=Path,
        default=None,
        help="result file (default: experiments/results/retrieval-evaluation-*.json)",
    )
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args.repo_root.resolve())
    return _retrieval(args, client_factory, embedder_factory)


if __name__ == "__main__":
    sys.exit(main())
