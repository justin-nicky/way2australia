"""Two-phase startup and shutdown (Spec 013 R2, R8, R16).

Phase 1 runs synchronously inside the lifespan: configuration and cross-file
checks, prompt, generator construction, active `lote` codes and the standalone
lexical file (identity, chunker, tokenizer, freshness). Any failure stops the
process with a path- and key-free message. Phase 2 runs on a background thread
(`open_serving_stack`: models, Qdrant, warm-up) so uvicorn can answer `/ready`
with `starting` while models load. Shutdown closes the holder.

Ownership of the generator: once it is handed to `open_serving_stack` through
`ServingInputs.generator`, the holder closes it (at shutdown and when the open
fails). The lifespan closes it only when phase 1 fails after it was built.
"""

import logging
import os
import signal
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from threading import Lock, Thread
from typing import Any

from fastapi import FastAPI
from way2australia_rag.generation.base import Generator
from way2australia_rag.generation.build import build_generator
from way2australia_rag.generation.config import (
    DEFAULT_GENERATION_CONFIG,
    load_generation_config,
)
from way2australia_rag.generation.errors import GeneratorConfigurationError
from way2australia_rag.generation.prompts import (
    PromptConfigurationError,
    PromptRegistry,
)
from way2australia_rag.ingestion.chunker_build import chunker_identity_for_run
from way2australia_rag.ingestion.config import (
    DEFAULT_CONFIG_PATH,
    IngestionConfig,
    RuntimeSettings,
    load_ingestion_config,
    load_runtime_settings,
)
from way2australia_rag.ingestion.errors import IngestionError
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.base import Strategy
from way2australia_rag.retrieval.errors import (
    RetrievalConfigurationError,
    RetrievalError,
)
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.opening import open_standalone_lexical
from way2australia_rag.retrieval.strategy import RetrievalConfig, load_retrieval_config
from way2australia_rag.retrieval.text import safe_text
from way2australia_rag.serving.config import (
    ServingConfigurationError,
    load_serving_config,
)
from way2australia_rag.serving.readiness import Readiness
from way2australia_rag.serving.stack import (
    ServingInputs,
    StackHolder,
    open_serving_stack,
)

from way2australia_api.config import Settings
from way2australia_api.slots import SlotPool

logger = logging.getLogger(__name__)

RETRIEVAL_CONFIG = "config/retrieval.yaml"
FAKE_WARNING = (
    "WARNING fake mode (W2A_API_FAKE): the embedder, reranker and generator are "
    "deterministic test doubles; answers are not model answers."
)

StackFactory = Callable[[ServingInputs, Readiness], StackHolder]

# Families whose messages are path- and secret-free by contract (as `make ask`).
_SAFE_ERRORS = (
    RetrievalError,
    IngestionError,
    GeneratorConfigurationError,
    PromptConfigurationError,
    ServingConfigurationError,
)


class StartupError(RuntimeError):
    """Phase 1 failed. The message carries no path, URL or key."""


def exit_process() -> None:
    """Default `on_fatal`: ask uvicorn to shut down (graceful SIGTERM)."""
    os.kill(os.getpid(), signal.SIGTERM)


@dataclass(frozen=True)
class PhaseOne:
    inputs: ServingInputs
    lote_codes: tuple[str, ...]


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _safe_message(error: Exception) -> str:
    if isinstance(error, _SAFE_ERRORS):
        return f"startup failed: {type(error).__name__}: {safe_text(error)}"
    return f"startup failed: {type(error).__name__}"


def _close_generator(generator: Generator) -> None:
    try:
        generator.close()
    except Exception as error:  # noqa: BLE001
        logger.warning("generator close failed: %s", type(error).__name__)


def run_phase_one(settings: Settings) -> PhaseOne:
    """Everything that can fail fast. A failure after the generator was built
    closes it here, exactly once; on success the generator is in
    `ServingInputs.generator` and the holder owns it."""
    generator: Generator | None = None
    try:
        repo_root = settings.repo_root.resolve()
        fake = settings.api_fake
        retrieval = load_retrieval_config(repo_root / RETRIEVAL_CONFIG)
        ingestion = load_ingestion_config(repo_root / DEFAULT_CONFIG_PATH)
        generation = load_generation_config(
            repo_root / DEFAULT_GENERATION_CONFIG, repo_root
        )
        if not fake:
            _refuse_fake_providers(ingestion, retrieval, generation)
        generator_provider = "fake" if fake else None
        serving = load_serving_config(
            _resolve(repo_root, settings.serving_config),
            generation_config=generation,
            retrieval_config=retrieval,
            generator_provider=generator_provider,
        )
        prompt = PromptRegistry(repo_root).get(
            generation.prompt.id, generation.prompt.version
        )
        runtime = load_runtime_settings(RetrievalConfigurationError)
        provider = "fake" if fake else ingestion.embedder.provider
        generator = build_generator(generation, generator_provider)
        lote_codes = tuple(active_lote_codes(repo_root))
        if Strategy(retrieval.default_strategy) is not Strategy.DENSE:
            _check_lexical(repo_root, ingestion, retrieval, runtime, provider)
        inputs = ServingInputs(
            settings=runtime,
            ingestion_config=ingestion,
            retrieval_config=retrieval,
            generation_config=generation,
            serving_config=serving,
            repo_root=repo_root,
            provider=provider,
            reranker_provider="fake" if fake else None,
            generator_provider=generator_provider,
            generator=generator,
            prompt_version=prompt,
        )
        return PhaseOne(inputs, lote_codes)
    except Exception as error:  # noqa: BLE001 - mapped to a safe message
        if generator is not None:
            _close_generator(generator)
        raise StartupError(_safe_message(error)) from None


def _refuse_fake_providers(
    ingestion: IngestionConfig,
    retrieval: RetrievalConfig,
    generation: Any,
) -> None:
    """Fake providers only run under `W2A_API_FAKE`, so `X-W2A-Fake` and the
    readiness `fake` flag always tell the truth (R16)."""
    chosen = [
        name
        for name, value in (
            ("embedder", ingestion.embedder.provider),
            (
                "reranker",
                retrieval.rerank.provider if retrieval.rerank.enabled else None,
            ),
            ("generator", generation.default_generator),
        )
        if value == "fake"
    ]
    if chosen:
        raise RetrievalConfigurationError(
            "configuration selects a fake "
            + ", ".join(chosen)
            + "; fake providers need W2A_API_FAKE"
        )


def _check_lexical(
    repo_root: Path,
    ingestion: IngestionConfig,
    retrieval: RetrievalConfig,
    runtime: RuntimeSettings,
    provider: str,
) -> None:
    """Identity, chunker, tokenizer and freshness of the standalone lexical file.
    The handle is closed: phase 2 opens its own."""
    expected = IndexIdentity.expected(ingestion, runtime, provider)
    chunker = chunker_identity_for_run(ingestion, provider)
    repository = LocalDocumentRepository(LocalRepositoryConfig(repo_root=repo_root))
    lexical = open_standalone_lexical(runtime, repo_root, expected, chunker, repository)
    try:
        lexical.check_tokenizer(retrieval.lexical.tokenizer)
    finally:
        lexical.close()


class _Loader:
    """Phase 2: one background thread; shutdown-aware."""

    def __init__(
        self,
        inputs: ServingInputs,
        readiness: Readiness,
        stack_factory: StackFactory,
        on_fatal: Callable[[], None],
    ) -> None:
        self._inputs = inputs
        self._readiness = readiness
        self._factory = stack_factory
        self._on_fatal = on_fatal
        self._lock = Lock()
        self._closing = False
        self.holder: StackHolder | None = None
        self.thread = Thread(target=self._run, name="serving-loader", daemon=True)

    def start(self) -> None:
        self.thread.start()

    def _run(self) -> None:
        try:
            holder = self._factory(self._inputs, self._readiness)
        except BaseException as error:  # noqa: BLE001 - everything is closed by the factory
            logger.error("serving stack failed to open: %s", type(error).__name__)
            self._readiness.set_failed()
            try:
                self._on_fatal()
            except Exception as fatal:  # noqa: BLE001
                logger.error("shutdown callback failed: %s", type(fatal).__name__)
            return
        with self._lock:
            if self._closing:
                late = holder
            else:
                late = None
                self.holder = holder
                self._readiness.set_ready()
        if late is not None:
            late.close()

    def close(self) -> None:
        """Shutdown: after this no new request is accepted (uvicorn has stopped
        serving), so the holder can close with no lease outstanding."""
        with self._lock:
            self._closing = True
            holder, self.holder = self.holder, None
        if holder is not None:
            holder.close()


def make_lifespan(
    settings: Settings,
    *,
    stack_factory: StackFactory | None = None,
    on_fatal: Callable[[], None] | None = None,
):
    factory = stack_factory or open_serving_stack
    fatal = on_fatal or exit_process

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        readiness: Readiness = app.state.readiness
        phase_one = run_phase_one(settings)
        app.state.serving_config = phase_one.inputs.serving_config
        app.state.lote_codes = phase_one.lote_codes
        app.state.runtime_settings = phase_one.inputs.settings
        app.state.top_k = phase_one.inputs.generation_config.retrieval.top_k
        pool = SlotPool(phase_one.inputs.serving_config.concurrency.max_in_flight)
        app.state.slots = pool
        readiness.set_abandoned_provider(lambda: pool.abandoned_in_flight)
        if settings.api_fake:
            logger.warning(FAKE_WARNING)
        loader = _Loader(phase_one.inputs, readiness, factory, fatal)
        app.state.loader = loader
        loader.start()
        try:
            yield
        finally:
            loader.close()

    return lifespan
