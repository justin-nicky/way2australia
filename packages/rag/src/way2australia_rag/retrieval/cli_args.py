"""Retrieval arguments shared by `make retrieve` and `make ask` (Spec 012 T4).

Extracted unchanged from `retrieval/cli.py`: the argument definitions and the
resolution of the effective strategy, rerank setting and `lote`. Authorization
stays server configuration only: there is no role, scope or tenant argument.
`open_retrieval` is still called by each CLI (so tests can wrap it per CLI).
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from way2australia_rag.ingestion.cli import ClientFactory
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    RuntimeSettings,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.retrieval.applicability import ResolvedLote, resolve_lote
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.retriever import (
    DEFAULT_TOP_K,
    MAX_TOP_K,
    MIN_TOP_K,
)
from way2australia_rag.retrieval.strategy import RetrievalConfig, load_retrieval_config

DEFAULT_RETRIEVAL_CONFIG = "config/retrieval.yaml"


def add_retrieval_arguments(
    parser: argparse.ArgumentParser, *, top_k_default: int | None = DEFAULT_TOP_K
) -> None:
    """Query and the shared retrieval options (`top_k_default` None = unset)."""
    parser.add_argument("query")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help=f"ingestion config (default: <repo-root>/{DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument("--top-k", type=int, default=top_k_default)
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--rerank",
        dest="rerank",
        action="store_const",
        const=True,
        default=None,
        help="rerank hybrid results (default: rerank.enabled in the config)",
    )
    group.add_argument("--no-rerank", dest="rerank", action="store_const", const=False)
    parser.add_argument(
        "--reranker",
        choices=("bge", "fake"),
        default=None,
        help="reranker (default: rerank.provider from the retrieval config)",
    )
    parser.add_argument(
        "--lote",
        default=None,
        help="CCL language code (active product_support code, not en)",
    )


def check_top_k(top_k: int) -> None:
    if not MIN_TOP_K <= top_k <= MAX_TOP_K:
        raise RetrievalConfigurationError(
            f"top_k must be an integer from {MIN_TOP_K} to {MAX_TOP_K}."
        )


@dataclass(frozen=True)
class ResolvedRetrievalArgs:
    """Everything `open_retrieval` needs, resolved from the arguments."""

    repo_root: Path
    lote: ResolvedLote | None
    config: IngestionConfig
    settings: RuntimeSettings
    provider: str
    retrieval_config: RetrievalConfig
    strategy: Strategy
    rerank: bool
    reranker_provider: str | None

    def open_kwargs(
        self, client_factory: ClientFactory | None, top_k: int | None = None
    ) -> dict[str, Any]:
        return {
            "settings": self.settings,
            "ingestion_config": self.config,
            "retrieval_config": self.retrieval_config,
            "provider": self.provider,
            "repo_root": self.repo_root,
            "client_factory": client_factory,
            "rerank": self.rerank,
            "reranker_provider": self.reranker_provider,
            "top_k": top_k,
        }


def resolve_retrieval_args(args: argparse.Namespace) -> ResolvedRetrievalArgs:
    """Validate and resolve; the order of checks is the one `make retrieve` had."""
    repo_root = args.repo_root.resolve()
    config_path: Path = args.config or repo_root / DEFAULT_CONFIG_PATH
    if not args.query.strip():
        raise RetrievalConfigurationError("the query must not be empty.")
    check_top_k(args.top_k)
    lote = resolve_lote(args.lote, active_lote_codes(repo_root))
    config = load_ingestion_config(config_path)
    settings = load_runtime_settings(RetrievalConfigurationError)
    provider = args.embedder or config.embedder.provider
    retrieval_config = load_retrieval_config(
        args.retrieval_config or repo_root / DEFAULT_RETRIEVAL_CONFIG
    )
    strategy = Strategy(args.strategy or retrieval_config.default_strategy)
    rerank = retrieval_config.rerank.enabled if args.rerank is None else args.rerank
    return ResolvedRetrievalArgs(
        repo_root=repo_root,
        lote=lote,
        config=config,
        settings=settings,
        provider=provider,
        retrieval_config=retrieval_config,
        strategy=strategy,
        rerank=rerank,
        reranker_provider=args.reranker,
    )
