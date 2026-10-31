"""Evaluation command line (Spec 006).

Run as ``python -m way2australia_rag.evaluation.cli <subcommand>``.

- ``validate`` (``make validate-evaluation``): exit 0 when valid, 1 on validation
  problems, 2 on configuration errors or an unexpected exception (class name only).
- ``security`` (``make eval-security``): the authorization hard gate on a
  throwaway in-memory index. Exit 0 pass, 1 violation (ids only, never text),
  2 harness or configuration error.
- ``compare`` (``make eval-compare``): exit 0 pass (warnings allowed), 1 quality
  gate failure, 2 refusal (unlike runs, a fake run, an unreadable file).
- ``retrieval`` (``make eval-retrieval``): exit 0 on success, 2 on refusal or
  error. Nothing is written on error. There is no flag for embedder, role, scope
  or tenant, and no ``--allow-fake``.
"""

import argparse
import asyncio
import logging
import sys
import tempfile
import uuid
import warnings
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from qdrant_client import QdrantClient

from way2australia_rag.evaluation.compare import compare
from way2australia_rag.evaluation.errors import (
    EvaluationConfigurationError,
    EvaluationError,
)
from way2australia_rag.evaluation.results import (
    check_output_free,
    default_output_path,
    read_result,
    write_document,
)
from way2australia_rag.evaluation.retrieval_eval import (
    require_active_suite,
    require_real_embedder,
    require_real_index,
    run_retrieval_evaluation,
)
from way2australia_rag.evaluation.security_corpus import SCHEMA as SECURITY_SCHEMA
from way2australia_rag.evaluation.security_corpus import build_security_repository
from way2australia_rag.evaluation.security_eval import (
    run_security_evaluation,
    security_document,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    SECURITY_COLLECTION_PREFIX,
    build_security_index,
    delete_security_index,
)
from way2australia_rag.evaluation.slices import active_registry_languages
from way2australia_rag.evaluation.suite import declared_release_id, load_suite
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.cli import ClientFactory, build_embedder
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import Embedder, FakeEmbedder
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
)
from way2australia_rag.retrieval.strategy import (
    build_retriever,
    load_retrieval_config,
    needs_lexical,
    open_bound_lexical,
)
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_ERROR = 2
DEFAULT_SUITE = "evaluation/suites/public-eval-v2.json"
DEFAULT_RELEASE = "seed-v1"
DEFAULT_RETRIEVAL_CONFIG = "config/retrieval.yaml"

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


def _unanswerable_line(report: dict[str, Any]) -> str:
    def fmt(dist: dict[str, Any]) -> str:
        return "/".join(
            "n/a" if dist[key] is None else f"{dist[key]:.4f}"
            for key in ("min", "p50", "p95", "max")
        )

    return (
        f"unanswerable ({report['status']}, informational, no pass/fail): "
        f"n={report['n']}, top-1 score min/p50/p95/max "
        f"{fmt(report['top1_score'])} vs golden {fmt(report['golden_top1_score'])}"
    )


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
        f"strategy: {document['retrieval_strategy']} "
        f"(scores: {document['score_kind']})",
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
        _unanswerable_line(document["unanswerable"]),
        f"result: {shown}",
        *[f"note: {note}" for note in document["notes"]],
    ]
    return "\n".join(safe_text(line) for line in lines)


def _retrieval(
    args: argparse.Namespace,
    client_factory: ClientFactory | None,
    embedder_factory: EmbedderFactory,
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root: Path = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    lexical = None
    try:
        # 1. top-k, config, runtime settings
        if not MIN_TOP_K <= args.top_k <= MAX_TOP_K:
            raise EvaluationConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(EvaluationConfigurationError)
        retrieval_config = load_retrieval_config(
            args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
        )
        strategy = Strategy(args.strategy or retrieval_config.default_strategy)
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
        timeouts = retrieval_config.qdrant
        client = (
            client_factory(settings)
            if client_factory is not None
            else retrieval_client_factory(settings, timeouts)
        )
        index = DenseIndex.open(
            client,
            settings.collection_base,
            config.index_version,
            embedder.info,
            query_timeout_s=timeouts.query_timeout_s,
        )
        require_real_index(index)
        # 6b. the lexical file, opened read-only and bound to the dense index
        if needs_lexical(strategy):
            lexical = open_bound_lexical(settings, repo_root, index)
        retriever = build_retriever(
            strategy, index, embedder, lexical, retrieval_config
        )
        # 7. the one server-resolved access
        access = resolve_access(guest_access(settings))
        log.info(
            "suite %s loaded; strategy %s; index %s (index_version %s) bound",
            safe_text(suite.manifest.evaluation_suite_id),
            strategy.value,
            safe_text(index.collection),
            safe_text(index.index_version),
        )
        document = run_retrieval_evaluation(
            retriever=retriever,
            index=index,
            embedder=embedder,
            access=access,
            suite=suite,
            release_id=release_id,
            top_k=args.top_k,
            authorities=authorities,
            registry_languages=languages,
            repo_root=repo_root,
            fusion=retrieval_config.fusion if strategy == Strategy.HYBRID else None,
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
    finally:
        if lexical is not None:
            lexical.close()
    print(f"collection: {safe_text(index.collection)}")
    print(format_summary(document, output, repo_root))
    return EXIT_OK


DEFAULT_FIXTURE_ROOT = "tests/fixtures/security"


def default_security_output_path(repo_root: Path, now: datetime) -> Path:
    stamp = now.astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return repo_root / "experiments/results/tmp" / f"security-evaluation-{stamp}.json"


def _security(args: argparse.Namespace) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # In-memory Qdrant warns that payload indexes have no effect; expected here.
    warnings.filterwarnings("ignore", message="Payload indexes have no effect")
    repo_root: Path = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    fixture_root: Path = args.fixture_root or repo_root / DEFAULT_FIXTURE_ROOT
    client: QdrantClient | None = None
    index = None
    try:
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(EvaluationConfigurationError)
        retrieval_config = load_retrieval_config(
            args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
        )
        suite = load_suite(repo_root, args.suite)
        require_active_suite(suite)
        now = datetime.now(UTC)
        output: Path = args.output or default_security_output_path(repo_root, now)
        check_output_free(output)
        queries, deferred = select_security_queries(suite)
        access = resolve_access(guest_access(settings))
        started = perf_counter()
        client = QdrantClient(location=":memory:")
        base = f"{SECURITY_COLLECTION_PREFIX}{uuid.uuid4().hex[:8]}"
        with tempfile.TemporaryDirectory(prefix="w2a-sectest-") as work:
            security_repository = build_security_repository(
                fixture_root,
                Path(work),
                schema_source=repo_root / SECURITY_SCHEMA,
            )
            index = build_security_index(
                client,
                base,
                [q.text for q in queries],
                FakeEmbedder(FAKE_VECTOR_SIZE),
                HeadingChunker(config.chunker.max_chunk_chars),
                seed_repository=LocalDocumentRepository(
                    LocalRepositoryConfig(repo_root)
                ),
                security_repository=security_repository,
                tenant_id=settings.tenant_id,
                lexical_dir=Path(work) / "lexical",
            )
            log.info(
                "security index %s built; %d queries, %d deferred case(s)",
                safe_text(index.collection),
                len(queries),
                len(deferred),
            )
            try:
                report = run_security_evaluation(
                    index, access, queries, deferred, retrieval_config
                )
            finally:
                # close the lexical file before its temporary directory goes
                index.lexical.close()
        duration_ms = (perf_counter() - started) * 1000.0
        document = security_document(
            index=index,
            report=report,
            suite=suite,
            access=access,
            duration_ms=duration_ms,
            created_at=now.isoformat(),
            repo_root=repo_root,
        )
        write_document(output, document)
    except (
        EvaluationError,
        RetrievalError,
        IngestionError,
        DocumentRepositoryError,
    ) as e:
        print(f"ERROR {type(e).__name__}: {safe_text(e)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001 - class name only
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    finally:
        if index is not None:
            delete_security_index(index)
        if client is not None:
            client.close()
    try:
        shown = output.resolve().relative_to(repo_root)
    except ValueError:
        shown = Path(output.name)
    print(format_security_summary(document, shown))
    return EXIT_OK if report.passed else EXIT_PROBLEMS


def format_security_summary(document: dict[str, Any], shown: Path) -> str:
    lines = [
        f"suite: {document['evaluation_suite_id']} "
        f"v{document['evaluation_suite_version']}",
        f"throwaway index: {document['index']['collection']} (removed after the run)",
        f"strategies: {', '.join(document['strategies'])}",
        f"queries: {document['query_count']} "
        f"({document['security_cases_run']} security cases, "
        f"{document['golden_queries_run']} golden); "
        f"deferred security cases: {len(document['deferred'])}",
    ]
    for item in document["deferred"]:
        lines.append(
            f"deferred {item['case_id']} ({item['attack_type']}): {item['owner']}"
        )
    for item in document["excluded_fixtures"]:
        lines.append(f"excluded fixture {item['document_id']}")
    for v in document["violations"]:
        lines.append(
            f"VIOLATION case {v['case_id']} document {v['document_id'] or '-'} "
            f"variant {v['variant']}"
        )
    verdict = "PASS" if document["passed"] else "FAIL"
    lines.append(
        f"eval-security: {verdict} in {document['duration_ms']:.0f} ms; result: {shown}"
    )
    return "\n".join(safe_text(line) for line in lines)


def _compare(args: argparse.Namespace) -> int:
    try:
        base = read_result(args.base, "BASE")
        candidate = read_result(args.candidate, "CANDIDATE")
        comparison = compare(base, candidate)
    except EvaluationError as error:
        print(safe_text(error), file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001 - class name only
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    print("\n".join(comparison.lines))
    return EXIT_OK if comparison.passed else EXIT_PROBLEMS


def main(
    argv: Sequence[str] | None = None,
    *,
    client_factory: ClientFactory | None = None,
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
        "retrieval",
        help="run the active golden cases through the chosen retrieval strategy",
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
        "--strategy",
        choices=[strategy.value for strategy in Strategy],
        default=None,
        help="retrieval strategy (default: default_strategy in config/retrieval.yaml)",
    )
    retrieval.add_argument(
        "--retrieval-config",
        type=Path,
        default=None,
        help=f"retrieval config (default: <repo-root>/{DEFAULT_RETRIEVAL_CONFIG})",
    )
    retrieval.add_argument(
        "--output",
        type=Path,
        default=None,
        help="result file (default: experiments/results/retrieval-evaluation-*.json)",
    )
    security = commands.add_parser(
        "security",
        help="authorization hard gate on a throwaway in-memory index",
    )
    security.add_argument("--repo-root", type=Path, default=Path.cwd())
    security.add_argument("--config", type=Path, default=None)
    security.add_argument("--suite", default=DEFAULT_SUITE)
    security.add_argument("--retrieval-config", type=Path, default=None)
    security.add_argument(
        "--fixture-root",
        type=Path,
        default=None,
        help=f"fixture directory (default: <repo-root>/{DEFAULT_FIXTURE_ROOT})",
    )
    security.add_argument(
        "--output",
        type=Path,
        default=None,
        help="result file (default: experiments/results/tmp/security-*.json)",
    )
    compare_cmd = commands.add_parser(
        "compare", help="compare two result files and apply the quality gate"
    )
    compare_cmd.add_argument("--base", type=Path, required=True)
    compare_cmd.add_argument("--candidate", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "compare":
        return _compare(args)
    if args.command == "validate":
        return _validate(args.repo_root.resolve())
    if args.command == "security":
        return _security(args)
    return _retrieval(args, client_factory, embedder_factory)


if __name__ == "__main__":
    sys.exit(main())
