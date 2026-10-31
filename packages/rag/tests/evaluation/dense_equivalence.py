"""Deterministic dense evaluation run for the Spec 007 T6 equivalence test.

The fixture `fixtures/dense_eval_2_0.json` was captured with the runner as it
was BEFORE the T6 changes (result format 2.0). The same setup is replayed by
`test_strategy_eval.py` against the 2.1 runner.
"""

import itertools
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any
from unittest.mock import patch

from conftest import REPO_ROOT
from retrieval.test_retriever import guest
from way2australia_rag.evaluation.retrieval_eval import run_retrieval_evaluation
from way2australia_rag.retrieval.access import build_access_filter
from way2australia_rag.retrieval.identity import IndexIdentity

from .test_retrieval_eval import (
    AUTH,
    build,
    golden,
    suite_of,
    unanswerable,
)

FIXTURE_NAME = "dense_eval_2_0.json"
FIXED_NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)


def equivalence_suite():  # noqa: ANN201
    return suite_of(
        [
            golden(1, ["doc_1"]),
            golden(2, ["doc_2", "doc_3"], lang="mixed"),
            golden(3, ["doc_9"]),
            golden(5, ["doc_5"], lang="x1"),
            golden(4, ["doc_4"], status="deprecated"),
        ],
        unanswerable=[unanswerable(1), unanswerable(2)],
    )


@contextmanager
def deterministic_clock() -> Iterator[None]:
    ticks = itertools.count()

    def fake_perf_counter() -> float:
        return next(ticks) * 0.001

    with (
        patch(
            "way2australia_rag.evaluation.retrieval_eval.perf_counter",
            fake_perf_counter,
        ),
        patch("way2australia_rag.retrieval.retriever.perf_counter", fake_perf_counter),
        patch(
            "way2australia_rag.evaluation.retrieval_eval.git_state",
            lambda _root: ("0" * 40, False),
        ),
    ):
        yield


def run_equivalence(**extra: Any) -> dict[str, Any]:
    index, emb, retriever = build()
    with deterministic_clock():
        return run_retrieval_evaluation(
            retriever=retriever,
            identity=IndexIdentity.from_dense(index),
            document_count=index.document_count(build_access_filter(guest())),
            index_settings=index.settings,
            embedder=emb,
            access=guest(),
            suite=equivalence_suite(),
            release_id="seed-v1",
            top_k=5,
            authorities=AUTH,
            registry_languages=["en", "x1"],
            repo_root=REPO_ROOT,
            clock=lambda: FIXED_NOW,
            **extra,
        )
