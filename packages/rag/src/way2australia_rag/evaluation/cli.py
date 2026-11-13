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
from collections import Counter
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
    EvaluationHarnessError,
)
from way2australia_rag.evaluation.generation_eval import (
    apply_pricing_overrides,
    check_thresholds,
    default_generation_output_path,
    estimate_cost,
    format_generation_summary,
    print_cost_estimate,
    require_confirmation,
    require_real_generator_pricing,
    run_generation_evaluation,
    select_cases,
)
from way2australia_rag.evaluation.results import (
    check_output_free,
    default_output_path,
    read_result,
    write_document,
)
from way2australia_rag.evaluation.retrieval_eval import (
    ingestion_config_report,
    require_active_suite,
    require_real_embedder,
    require_real_reranker,
    run_retrieval_evaluation,
)
from way2australia_rag.evaluation.security_corpus import SCHEMA as SECURITY_SCHEMA
from way2australia_rag.evaluation.security_corpus import build_security_repository
from way2australia_rag.evaluation.security_eval import (
    run_generation_security_checks,
    run_security_evaluation,
    security_document,
    security_gate_chunkers,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    SECURITY_COLLECTION_PREFIX,
    build_security_index,
    delete_security_index,
    require_non_applicable_lote_inactive,
)
from way2australia_rag.evaluation.slices import active_registry_languages
from way2australia_rag.evaluation.suite import declared_release_id, load_suite
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.generation.build import build_generator
from way2australia_rag.generation.config import (
    DEFAULT_GENERATION_CONFIG,
    load_generation_config,
)
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.prompts import (
    PromptConfigurationError,
    PromptRegistry,
)
from way2australia_rag.generation.service import AnswerService, retrieval_identity
from way2australia_rag.ingestion.cli import ClientFactory, build_embedder
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.embedding import Embedder, FakeEmbedder
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepositoryError,
    LocalDocumentRepository,
    LocalRepositoryConfig,
    list_eligible_documents,
)
from way2australia_rag.rerank.base import Reranker
from way2australia_rag.rerank.build import build_reranker
from way2australia_rag.retrieval.access import guest_access, resolve_access
from way2australia_rag.retrieval.applicability import resolve_lote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalError
from way2australia_rag.retrieval.opening import open_retrieval
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
)
from way2australia_rag.retrieval.strategy import RerankConfig, load_retrieval_config
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_PROBLEMS = 1
EXIT_ERROR = 2
DEFAULT_SUITE = "evaluation/suites/public-eval-v4.json"
DEFAULT_RELEASE = "seed-v1"
DEFAULT_RETRIEVAL_CONFIG = "config/retrieval.yaml"

log = logging.getLogger(__name__)

EmbedderFactory = Callable[[IngestionConfig, str], Embedder]
RerankerFactory = Callable[[RerankConfig, str | None], Reranker]


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
    def fmt(dist: dict[str, Any] | None) -> str:
        if dist is None:
            return "n/a (mixed score kinds)"
        return "/".join(
            "n/a" if dist[key] is None else f"{dist[key]:.4f}"
            for key in ("min", "p50", "p95", "max")
        )

    return (
        f"unanswerable ({report['status']}, informational, no pass/fail): "
        f"n={report['n']}, top-1 score min/p50/p95/max "
        f"{fmt(report['top1_score'])} vs golden {fmt(report['golden_top1_score'])}"
    )


def _rerank_lines(document: dict[str, Any]) -> list[str]:
    identity = document["rerank"]
    if not document["rerank_requested"]:
        return ["rerank: off"]
    if identity is None:
        return ["rerank: requested but not loaded (served without the reranker)"]
    latency = document["latency_ms"]
    lines = [
        f"rerank: {identity['model_id']}@{str(identity['revision'])[:7]} "
        f"depth {identity['depth']} max_length {identity['max_length']} "
        f"(fake={str(identity['is_fake']).lower()}, "
        f"device={identity['device'] or 'unknown'})"
    ]
    if latency.get("warmup_rerank_load_ms") is not None:
        lines.append(
            f"rerank load {latency['warmup_rerank_load_ms']:.1f} ms "
            "(in warm-up, excluded from p50/p95)"
        )
    leg = (latency.get("legs") or {}).get("rerank")
    if leg:
        lines.append(f"rerank leg p50 {leg['p50']:.1f} ms, p95 {leg['p95']:.1f} ms")
    skips = document["rerank_skip_counts"]
    if skips:
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(skips.items()))
        lines.append(f"rerank skipped (measured queries): {counts}")
    truncation = document["rerank_truncation"]
    if truncation["pairs"]:
        lines.append(
            f"rerank truncated pairs: {truncation['pairs']} in "
            f"{truncation['cases']} query(ies)"
        )
    return lines


def format_summary(document: dict[str, Any], output: Path, repo_root: Path) -> str:
    k = document["top_k"]
    overall = document["metrics"]["overall"]
    latency = document["latency_ms"]
    try:
        shown = output.resolve().relative_to(repo_root.resolve())
    except ValueError:
        shown = Path(output.name)
    settings = document["index_settings"]
    embedder = (
        f"{settings['embedder_model_id']} @ {settings['embedder_revision']}"
        if settings
        else "n/a (Qdrant not contacted)"
    )
    requested = document["requested_strategy"]
    served_counts = Counter(row["served_strategy"] for row in document["cases"])
    fallbacks = document["fallback_counts"]
    if document["served_strategies"] == [requested] and not fallbacks:
        strategy_line = (
            f"strategy: {document['retrieval_strategy']} "
            f"(scores: {document['score_kind']})"
        )
    else:
        served = ", ".join(f"{k}: {v}" for k, v in sorted(served_counts.items()))
        strategy_line = (
            f"strategy: requested {requested}, served {served} "
            f"(scores: {document['score_kind'] or 'mixed'})"
        )
    lines = [
        strategy_line,
        f"index: {document['collection']} (index_version {document['index_version']}; "
        f"embedder {embedder}, "
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
    for name in (
        "by_query_language",
        "by_script_mix",
        "by_category",
        "by_source_authority",
    ):
        for key, value in document["metrics"][name].items():
            flag = " (small sample)" if value["small_sample"] else ""
            lines.append(
                f"{name[3:]} {key}: n={value['n']}{flag} "
                f"HitRate@{k} {value[f'hit_rate_at_{k}']:.4f} MRR {value['mrr']:.4f}"
            )
    absent = document["absent_query_languages"]
    if absent:
        lines.append(f"absent query languages (no golden case): {', '.join(absent)}")
    lines.append(
        "section-level measurable cases: "
        f"{document['section_level']['measurable_cases']}"
    )
    if fallbacks:
        counts = ", ".join(f"{k}: {v}" for k, v in sorted(fallbacks.items()))
        lines.append(f"fallbacks (measured cases): {counts}")
    if latency["p50"] is not None:
        lines.append(
            f"latency p50 {latency['p50']:.1f} ms, p95 {latency['p95']:.1f} ms "
            f"(warm-up {latency['warmup_ms']:.1f} ms excluded)"
        )
    for path, value in latency["by_served_path"].items():
        if "+fallback:" in path or len(latency["by_served_path"]) > 1:
            note = " (includes failed dense attempt)" if "+fallback:" in path else ""
            lines.append(
                f"latency {path}: p50 {value['p50']:.1f} ms, p95 "
                f"{value['p95']:.1f} ms, n={value['n']}{note}"
            )
    lines.extend(_rerank_lines(document))
    lines += [
        _unanswerable_line(document["unanswerable"]),
        f"result: {shown}",
        *[f"note: {note}" for note in document["notes"]],
    ]
    return "\n".join(safe_text(line) for line in lines)


def _retrieval(
    args: argparse.Namespace,
    client_factory: ClientFactory | None,
    embedder_factory: EmbedderFactory,
    reranker_factory: RerankerFactory = build_reranker,
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # request lines carry URLs
    repo_root: Path = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    opened = None
    try:
        # 1. top-k, config, runtime settings
        if not MIN_TOP_K <= args.top_k <= MAX_TOP_K:
            raise EvaluationConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        lote = resolve_lote(args.lote, active_lote_codes(repo_root))
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(EvaluationConfigurationError)
        retrieval_config = load_retrieval_config(
            args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
        )
        strategy = Strategy(args.strategy or retrieval_config.default_strategy)
        rerank = retrieval_config.rerank.enabled if args.rerank is None else args.rerank
        if rerank and retrieval_config.rerank.provider == "fake":
            # Before any Qdrant contact: a quality run never uses a fake reranker.
            raise EvaluationConfigurationError(
                "rerank.provider is 'fake'; eval-retrieval measures quality and "
                "never runs on a fake reranker."
            )
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

        # 5. open the stack. A fake embedder is refused as soon as it is built,
        # before any Qdrant contact; `bm25` builds none (its fake provider is
        # refused by `run_retrieval_evaluation` through the identity).
        def real_embedder_factory(cfg: IngestionConfig, provider: str) -> Embedder:
            built = embedder_factory(cfg, provider)
            require_real_embedder(built)
            return built

        def real_reranker_factory(cfg: RerankConfig, name: str | None) -> Reranker:
            built = reranker_factory(cfg, name)
            require_real_reranker(built)
            return built

        # Depth this run will ask of the retriever when the dense path is up.
        # `args.top_k` is the metric cutoff, not that depth (design: eval-retrieval
        # passes its effective depth). After an open-time fallback the recorded
        # depth is corrected below.
        open_depth = (
            retrieval_config.rerank.depth
            if rerank
            else retrieval_config.fusion.candidate_depth
        )
        opened = open_retrieval(
            strategy,
            settings=settings,
            ingestion_config=config,
            retrieval_config=retrieval_config,
            provider=config.embedder.provider,
            repo_root=repo_root,
            client_factory=client_factory,
            embedder_factory=real_embedder_factory,
            rerank=rerank,
            reranker_factory=real_reranker_factory,
            top_k=open_depth,
        )
        identity = opened.identity
        # 6. the one server-resolved access
        access = resolve_access(guest_access(settings))
        log.info(
            "suite %s loaded; strategy %s; index %s (index_version %s) bound",
            safe_text(suite.manifest.evaluation_suite_id),
            strategy.value,
            safe_text(identity.collection),
            safe_text(identity.index_version),
        )
        document = run_retrieval_evaluation(
            retriever=opened.retriever,
            identity=identity,
            document_count=opened.document_count(access, lote),
            embedder=opened.embedder,
            index_settings=opened.index_settings,
            lexical=opened.lexical,
            access=access,
            suite=suite,
            release_id=release_id,
            top_k=args.top_k,
            # The stage returns at most `rerank.depth` chunks, but only when a
            # reranker was loaded on a dense-capable path. After an open-time
            # fallback the served path is plain BM25 at candidate depth
            # (Spec 011 F1).
            retrieval_depth=(
                retrieval_config.rerank.depth
                if rerank and opened.reranker is not None
                else retrieval_config.fusion.candidate_depth
            ),
            chunks_per_document=opened.chunks_per_document(),
            ingestion_config=ingestion_config_report(config_path, repo_root),
            authorities=authorities,
            registry_languages=languages,
            repo_root=repo_root,
            fusion=retrieval_config.fusion if strategy == Strategy.HYBRID else None,
            qdrant_timeouts=(
                None if strategy == Strategy.BM25 else retrieval_config.qdrant
            ),
            lote=lote,
            rerank_requested=rerank,
            reranker=opened.reranker,
            rerank_depth=retrieval_config.rerank.depth if rerank else None,
            rerank_load_ms=opened.rerank_load_ms,
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
        if opened is not None:
            opened.close()
    print(f"collection: {safe_text(identity.collection)}")
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
    fixture_root: Path = args.fixture_root or repo_root / DEFAULT_FIXTURE_ROOT
    client: QdrantClient | None = None
    completed_runs: list[tuple[Any, Any]] = []
    generation_checks = None
    try:
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
        lote_codes = active_lote_codes(repo_root)
        require_non_applicable_lote_inactive(lote_codes)
        if len(lote_codes) != 1:
            raise EvaluationConfigurationError(
                "the security gate requires exactly one active lote code."
            )
        active_lote = resolve_lote(lote_codes[0], lote_codes)
        assert active_lote is not None
        started = perf_counter()
        client = QdrantClient(location=":memory:")
        seed_repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root))
        with tempfile.TemporaryDirectory(prefix="w2a-sectest-") as work:
            work_path = Path(work)
            security_repository = build_security_repository(
                fixture_root,
                work_path,
                schema_source=repo_root / SECURITY_SCHEMA,
            )
            for chunker in security_gate_chunkers():
                base = f"{SECURITY_COLLECTION_PREFIX}{uuid.uuid4().hex[:8]}"
                index = build_security_index(
                    client,
                    base,
                    [q.text for q in queries],
                    FakeEmbedder(FAKE_VECTOR_SIZE),
                    chunker,
                    seed_repository=seed_repository,
                    security_repository=security_repository,
                    tenant_id=settings.tenant_id,
                    lexical_dir=work_path / "lexical",
                    active_lote_code=active_lote.code,
                )
                log.info(
                    "security index %s built (%s v%s); %d queries, %d deferred case(s)",
                    safe_text(index.collection),
                    chunker.name,
                    chunker.version,
                    len(queries),
                    len(deferred),
                )
                try:
                    report = run_security_evaluation(
                        index,
                        access,
                        queries,
                        deferred,
                        retrieval_config,
                        active_lote=active_lote,
                    )
                    completed_runs.append((index, report))
                    if generation_checks is None and report.passed:
                        generation_checks = run_generation_security_checks(
                            index,
                            access,
                            queries,
                            retrieval_config,
                            repo_root,
                            fixture_root,
                        )
                finally:
                    index.lexical.close()
                    delete_security_index(index)
        duration_ms = (perf_counter() - started) * 1000.0
        document = security_document(
            runs=completed_runs,
            suite=suite,
            access=access,
            duration_ms=duration_ms,
            created_at=now.isoformat(),
            repo_root=repo_root,
            lote_modes=[None, active_lote.code],
            generation_checks=generation_checks,
        )
        write_document(output, document)
    except (
        EvaluationError,
        RetrievalError,
        IngestionError,
        DocumentRepositoryError,
        EvaluationHarnessError,
    ) as e:
        print(f"ERROR {type(e).__name__}: {safe_text(e)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001 - class name only
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    finally:
        if client is not None:
            client.close()
    try:
        shown = output.resolve().relative_to(repo_root)
    except ValueError:
        shown = Path(output.name)
    print(format_security_summary(document, shown))
    return EXIT_OK if document["passed"] else EXIT_PROBLEMS


def format_security_summary(document: dict[str, Any], shown: Path) -> str:
    lote_modes = document.get("lote_modes")
    lote_line = ""
    if isinstance(lote_modes, list):
        shown_modes = ["none" if mode is None else str(mode) for mode in lote_modes]
        lote_line = f"lote modes: {', '.join(shown_modes)}"
    lines = [
        f"suite: {document['evaluation_suite_id']} "
        f"v{document['evaluation_suite_version']}",
        f"chunker runs: {len(document['runs'])}; "
        f"deferred security cases: {len(document['deferred'])}",
    ]
    if lote_line:
        lines.append(lote_line)
    for run in document["runs"]:
        chunker = run["chunker"]
        lines.append(
            f"chunker {chunker['name']} v{chunker['version']}: "
            f"{'PASS' if run['passed'] else 'FAIL'} "
            f"({run['query_count']} queries, "
            f"{run['security_cases_run']} security, "
            f"{run['golden_queries_run']} golden)"
        )
        lines.append(f"  paths: {', '.join(run['paths'])}")
        lines.append(f"  strategies: {', '.join(run['strategies'])}")
        for path, detail in (run.get("path_details") or {}).items():
            reranker = detail["reranker"]
            skip = detail["skip"]
            lines.append(
                f"  {path}: fake reranker {reranker['model_id']} "
                f"(depth {detail['depth']}); "
                + (
                    "no skip"
                    if skip is None
                    else f"skip {skip['reason']} at {skip['stage']}"
                )
            )
        for key, label in (
            ("authorization_violations", "AUTH"),
            ("applicability_violations", "APPLIC"),
        ):
            rows = run.get(key)
            if not isinstance(rows, list):
                rows = run["violations"] if key == "authorization_violations" else []
            for v in rows:
                lote = v.get("lote", "none")
                lines.append(
                    f"  {label} VIOLATION path {v['path']} lote {lote} "
                    f"case {v['case_id']} document {v['document_id'] or '-'} "
                    f"variant {v['variant']}"
                )
    for item in document["deferred"]:
        lines.append(
            f"deferred {item['case_id']} ({item['attack_type']}): {item['owner']}"
        )
    for item in document["excluded_fixtures"]:
        lines.append(f"excluded fixture {item['document_id']}")
    verdict = "PASS" if document["passed"] else "FAIL"
    lines.append(
        f"eval-security: {verdict} in {document['duration_ms']:.0f} ms; result: {shown}"
    )
    return "\n".join(safe_text(line) for line in lines)


def _generation(
    args: argparse.Namespace,
    client_factory: ClientFactory | None,
    embedder_factory: EmbedderFactory,
    reranker_factory: RerankerFactory = build_reranker,
) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stderr)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    repo_root: Path = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    gen_path: Path = args.generation_config or repo_root / DEFAULT_GENERATION_CONFIG
    generator = None
    opened = None
    problems: list[str] = []
    try:
        top_k = args.top_k
        lote = resolve_lote(args.lote, active_lote_codes(repo_root))
        suite = load_suite(repo_root, args.suite)
        require_active_suite(suite)
        release_id = declared_release_id(repo_root, args.release)
        config = load_generation_config(gen_path, repo_root)
        if args.generator is None and config.default_generator is None:
            raise GeneratorConfigurationError(
                "no generator is configured; pass --generator fake, "
                "--generator bedrock or --generator anthropic."
            )
        config, pricing_applied = apply_pricing_overrides(
            config,
            input_per_mtok=args.price_input,
            output_per_mtok=args.price_output,
            source="cli",
        )
        generator = build_generator(config, args.generator, args.model_id)
        if generator.info.is_fake and not args.allow_fake:
            raise EvaluationConfigurationError(
                "the fake generator needs --allow-fake; results go to "
                "experiments/results/tmp/ only."
            )
        use_all = bool(args.all) or (generator.info.is_fake and args.limit is None)
        if not generator.info.is_fake and not args.all and args.limit is None:
            raise EvaluationConfigurationError(
                "a real generator run needs exactly one of --limit N or --all."
            )
        selected = select_cases(suite, limit=args.limit, all_cases=use_all)
        ingestion = load_ingestion_config(config_path)
        settings = load_runtime_settings(EvaluationConfigurationError)
        retrieval_config = load_retrieval_config(
            args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
        )
        strategy = Strategy(args.strategy or retrieval_config.default_strategy)
        rerank = retrieval_config.rerank.enabled if args.rerank is None else args.rerank
        provider = args.embedder or ingestion.embedder.provider
        reranker_provider = args.reranker or retrieval_config.rerank.provider
        if top_k is None:
            top_k = config.retrieval.top_k
        if not MIN_TOP_K <= top_k <= MAX_TOP_K:
            raise EvaluationConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        prompt = PromptRegistry(repo_root).get(config.prompt.id, config.prompt.version)
        now = datetime.now(UTC)
        tmp = generator.info.is_fake
        output: Path = args.output or default_generation_output_path(
            repo_root, ingestion.index_version, now, tmp=tmp
        )
        check_output_free(output)
        opened = open_retrieval(
            strategy,
            settings=settings,
            ingestion_config=ingestion,
            retrieval_config=retrieval_config,
            provider=provider,
            repo_root=repo_root,
            client_factory=client_factory,
            embedder_factory=embedder_factory,
            rerank=rerank,
            reranker_factory=reranker_factory,
            reranker_provider=reranker_provider,
            top_k=top_k,
        )
        access = resolve_access(guest_access(settings))
        builder = ContextBuilder(config.context)
        estimated_cost_usd: float | None = None
        if not generator.info.is_fake:
            require_real_generator_pricing(generator, config.pricing)
            estimate = estimate_cost(
                selected=selected,
                retriever=opened.retriever,
                builder=builder,
                prompt=prompt,
                access=access,
                config=config,
                top_k=top_k,
                lote=lote,
            )
            estimated_cost_usd = estimate.estimated_cost_usd
            print_cost_estimate(estimate, config.pricing)
            if getattr(generator, "calls", 0) != 0:
                raise EvaluationHarnessError(
                    "cost guard: generator was called before confirmation."
                )
            require_confirmation(yes=bool(args.yes))
        service = AnswerService(opened.retriever, builder, prompt, generator, config)
        warm_query = (
            selected.goldens[0].query
            if selected.goldens
            else selected.unanswerables[0].query
        )
        warm = opened.retriever.retrieve(warm_query, access, top_k, lote=lote)
        retrieval_id = retrieval_identity(warm)
        document = run_generation_evaluation(
            retriever=opened.retriever,
            generator=generator,
            service=service,
            suite=suite,
            selected=selected,
            access=access,
            release_id=release_id,
            top_k=top_k,
            lote=lote,
            config=config,
            prompt=prompt,
            generator_info=generator.info,
            pricing_applied=pricing_applied,
            retrieval_identity=retrieval_id,
            ingestion_config=ingestion_config_report(config_path, repo_root),
            repo_root=repo_root,
            min_answer_rate=args.min_answer_rate,
            min_refusal_rate=args.min_refusal_rate,
            estimated_cost_usd=estimated_cost_usd,
            clock=lambda: now,
        )
        problems = check_thresholds(
            document["metrics"],
            min_answer_rate=args.min_answer_rate,
            min_refusal_rate=args.min_refusal_rate,
        )
        write_document(output, document)
    except (
        EvaluationError,
        RetrievalError,
        IngestionError,
        GeneratorConfigurationError,
        PromptConfigurationError,
    ) as error:
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as error:  # noqa: BLE001
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_ERROR
    finally:
        if generator is not None:
            generator.close()
        if opened is not None:
            opened.close()
    try:
        shown = output.resolve().relative_to(repo_root)
    except ValueError:
        shown = Path(output.name)
    print(format_generation_summary(document, shown))
    if problems:
        for problem in problems:
            print(f"GATE {problem}", file=sys.stderr)
        return EXIT_PROBLEMS
    return EXIT_OK


def _compare(args: argparse.Namespace) -> int:
    try:
        base = read_result(args.base, "BASE")
        candidate = read_result(args.candidate, "CANDIDATE")
        comparison = compare(
            base,
            candidate,
            cross_index=args.cross_index,
            cross_tokenizer=args.cross_tokenizer,
            cross_rerank=args.cross_rerank,
        )
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
    reranker_factory: RerankerFactory = build_reranker,
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
    retrieval.add_argument(
        "--lote",
        default=None,
        help="CCL language code (active product_support code, not en)",
    )
    group = retrieval.add_mutually_exclusive_group()
    group.add_argument(
        "--rerank",
        dest="rerank",
        action="store_const",
        const=True,
        default=None,
        help="rerank hybrid results (default: rerank.enabled in the config)",
    )
    group.add_argument("--no-rerank", dest="rerank", action="store_const", const=False)
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
    generation = commands.add_parser(
        "generation",
        help="run goldens and unanswerable cases through the answer path",
    )
    generation.add_argument("--repo-root", type=Path, default=Path.cwd())
    generation.add_argument("--config", type=Path, default=None)
    generation.add_argument("--generation-config", type=Path, default=None)
    generation.add_argument("--suite", default=DEFAULT_SUITE)
    generation.add_argument("--release", default=DEFAULT_RELEASE)
    generation.add_argument(
        "--strategy", choices=[s.value for s in Strategy], default=None
    )
    generation.add_argument("--retrieval-config", type=Path, default=None)
    generation.add_argument("--embedder", choices=("bge_m3", "fake"), default=None)
    generation.add_argument("--top-k", type=int, default=None)
    generation.add_argument("--lote", default=None)
    group = generation.add_mutually_exclusive_group()
    group.add_argument(
        "--rerank",
        dest="rerank",
        action="store_const",
        const=True,
        default=None,
    )
    group.add_argument("--no-rerank", dest="rerank", action="store_const", const=False)
    generation.add_argument("--reranker", choices=("bge", "fake"), default=None)
    generation.add_argument(
        "--generator", choices=("fake", "bedrock", "anthropic"), default=None
    )
    generation.add_argument("--model-id", default=None)
    generation.add_argument(
        "--price-input", type=float, default=None, dest="price_input"
    )
    generation.add_argument(
        "--price-output", type=float, default=None, dest="price_output"
    )
    generation.add_argument("--allow-fake", action="store_true")
    generation.add_argument("--yes", action="store_true")
    limit_group = generation.add_mutually_exclusive_group()
    limit_group.add_argument("--limit", type=int, default=None)
    limit_group.add_argument("--all", action="store_true")
    generation.add_argument("--min-answer-rate", type=float, default=None)
    generation.add_argument("--min-refusal-rate", type=float, default=None)
    generation.add_argument("--output", type=Path, default=None)
    compare_cmd = commands.add_parser(
        "compare", help="compare two result files and apply the quality gate"
    )
    compare_cmd.add_argument("--base", type=Path, required=True)
    compare_cmd.add_argument("--candidate", type=Path, required=True)
    compare_cmd.add_argument(
        "--cross-index",
        action="store_true",
        help=(
            "allow collection, index_version and chunker differences (result 2.3 only)"
        ),
    )
    compare_cmd.add_argument(
        "--cross-tokenizer",
        action="store_true",
        help=(
            "allow lexical tokenizer name and version to differ when digest and "
            "chunk_count match"
        ),
    )
    compare_cmd.add_argument(
        "--cross-rerank",
        action="store_true",
        help="allow rerank identity (enabled, model, revision, depth, max_length) "
        "to differ",
    )
    args = parser.parse_args(argv)
    if args.command == "compare":
        return _compare(args)
    if args.command == "validate":
        return _validate(args.repo_root.resolve())
    if args.command == "security":
        return _security(args)
    if args.command == "generation":
        return _generation(args, client_factory, embedder_factory, reranker_factory)
    return _retrieval(args, client_factory, embedder_factory, reranker_factory)


if __name__ == "__main__":
    sys.exit(main())
