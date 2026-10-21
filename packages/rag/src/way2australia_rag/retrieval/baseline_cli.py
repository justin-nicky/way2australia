"""Retrieval baseline CLI (Spec 005 R8).

Run as ``python -m way2australia_rag.retrieval.baseline_cli`` (via
``make retrieval-baseline``). Same startup order and exit codes as the retrieve
CLI: 0 success, 2 refusal or configuration error. On any error nothing is
written. There is no flag for role, scope or tenant.
"""

import argparse
import logging
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
from way2australia_rag.retrieval.baseline import (
    BaselineResult,
    check_output_free,
    default_output_path,
    run_baseline,
    write_result,
)
from way2australia_rag.retrieval.errors import (
    RetrievalConfigurationError,
    RetrievalError,
)
from way2australia_rag.retrieval.goldens import (
    declared_release_id,
    load_golden_cases,
    load_suite,
)
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
    DenseRetriever,
)
from way2australia_rag.retrieval.text import safe_text

EXIT_OK = 0
EXIT_REFUSED = 2
DEFAULT_SUITE = "evaluation/suites/public-eval-v1.json"
DEFAULT_RELEASE = "seed-v1"

log = logging.getLogger(__name__)


def format_summary(result: BaselineResult, output: Path, repo_root: Path) -> str:
    doc: dict[str, Any] = result.document
    k = doc["top_k"]
    overall = doc["metrics"]["overall"]
    latency = doc["latency_ms"]
    try:
        shown = output.resolve().relative_to(repo_root.resolve())
    except ValueError:
        shown = Path(output.name)
    lines = [
        f"index: {doc['collection']} (index_version {doc['index_version']}; "
        f"embedder {doc['index_settings']['embedder_model_id']} @ "
        f"{doc['index_settings']['embedder_revision']}, "
        f"fake={str(doc['embedder_is_fake']).lower()}, "
        f"device={doc['device'] or 'unknown'})",
        f"cases: {doc['case_count']} (excluded {doc['excluded_case_count']}), "
        f"documents: {doc['document_count']}",
        f"HitRate@{k}: {overall[f'hit_rate_at_{k}']:.4f} "
        f"(random {doc['random_hit_rate_at_k']:.4f} = "
        f"{doc['random_hit_rate_formula']})",
        f"Recall@{k}: {overall[f'recall_at_{k}']:.4f}",
        f"MRR: {overall['mrr']:.4f}",
        f"latency p50 {latency['p50']:.1f} ms, p95 {latency['p95']:.1f} ms "
        f"(warm-up {latency['warmup_ms']:.1f} ms excluded)",
        f"result: {shown}",
        *[f"note: {note}" for note in doc["notes"]],
    ]
    return "\n".join(safe_text(line) for line in lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m way2australia_rag.retrieval.baseline_cli",
        description="Run the golden cases through dense retrieval and record a result.",
    )
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
    parser.add_argument("--suite", default=DEFAULT_SUITE)
    parser.add_argument("--release", default=DEFAULT_RELEASE)
    parser.add_argument("--allow-fake", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="result file (default: experiments/results/retrieval-baseline-*.json)",
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
        if not MIN_TOP_K <= args.top_k <= MAX_TOP_K:
            raise RetrievalConfigurationError(
                f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
            )
        config = load_ingestion_config(config_path)
        settings = load_runtime_settings(RetrievalConfigurationError)
        suite = load_suite(repo_root, args.suite)
        release_id = declared_release_id(repo_root, args.release)
        cases, excluded = load_golden_cases(repo_root, suite)
        now = datetime.now(UTC)
        output: Path = args.output or default_output_path(
            repo_root, config.index_version, now
        )
        check_output_free(output)
        provider = args.embedder or config.embedder.provider
        embedder = build_embedder(config, provider)  # missing extra exits here
        client = client_factory(settings)
        index = DenseIndex.open(
            client, settings.collection_base, config.index_version, embedder.info
        )
        access = resolve_access(guest_access(settings))
        result = run_baseline(
            retriever=DenseRetriever(index, embedder),
            index=index,
            embedder=embedder,
            access=access,
            cases=cases,
            excluded_case_count=excluded,
            suite=suite,
            release_id=release_id,
            top_k=args.top_k,
            allow_fake=args.allow_fake,
            repo_root=repo_root,
            clock=lambda: now,
        )
        log.info(
            "baseline: collection %s, index_version %s, %d cases, N=%d",
            safe_text(index.collection),
            safe_text(index.index_version),
            result.document["case_count"],
            result.document["document_count"],
        )
        write_result(output, result)
    except (RetrievalError, IngestionError) as error:
        # Both families are path- and secret-free by contract.
        print(f"ERROR {type(error).__name__}: {safe_text(error)}", file=sys.stderr)
        return EXIT_REFUSED
    except Exception as error:  # noqa: BLE001 - unreachable Qdrant, bad config
        # Class name only: client messages can carry URLs or credentials.
        print(f"ERROR {type(error).__name__}", file=sys.stderr)
        return EXIT_REFUSED
    print(format_summary(result, output, repo_root))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
