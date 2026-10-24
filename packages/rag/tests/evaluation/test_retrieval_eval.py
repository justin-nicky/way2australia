"""Retrieval evaluation runner tests (Spec 006 R4, R5, R7).

Injected index, retriever and embedder on in-memory Qdrant. No model, no Docker,
nothing written outside tmp_path.
"""

import json
import re
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from retrieval.test_retriever import guest, make_payload
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.models import (
    GoldenCase,
    LoadedSuite,
    SuiteManifest,
    UnanswerableCase,
)
from way2australia_rag.evaluation.results import write_document
from way2australia_rag.evaluation.retrieval_eval import run_retrieval_evaluation
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.settings import build_index_settings
from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
from way2australia_rag.retrieval.access import build_access_filter
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BASE, VERSION = "way2australia", "idx-v1"
SECRET_QUERY = "SECRET-QUERY text number 3"
SECRET_CHUNK = "SECRET-CHUNK body"
AUTH = {f"doc_{i}": ("naati" if i % 2 else "owner_approved") for i in range(8)}


class RealStub(FakeEmbedder):
    """Same vectors as the fake embedder, but reports itself as a real model."""

    def __init__(self) -> None:
        super().__init__()
        self.info = self.info.model_copy(update={"is_fake": False})


def build(embedder: FakeEmbedder | None = None, count: int = 8):  # noqa: ANN201
    emb = embedder or RealStub()
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VERSION)
    store.ensure_collection(build_index_settings(VERSION, emb.info, HeadingChunker()))
    for i in range(count):
        text = f"{SECRET_CHUNK} {i}"
        payload = make_payload(f"doc_{i}", text)
        store.replace_document(
            f"doc_{i}",
            [
                IndexPoint(
                    point_id=point_id(f"doc_{i}", "main", 0),
                    vector=emb.embed_documents([text])[0],
                    payload=payload,
                )
            ],
        )
    index = DenseIndex.open(client, BASE, VERSION, emb.info)
    return index, emb, DenseRetriever(index, emb)


def golden(i: int, relevant: list[str], lang: str = "en", **extra: Any) -> GoldenCase:
    fields: dict[str, Any] = {
        "case_id": f"g{i:03d}",
        "case_version": 1,
        "status": "active",
        "query": SECRET_QUERY if i == 3 else f"golden query {i}",
        "answerable": True,
        "relevant_document_ids": relevant,
        "query_language": lang,
        "category": "business",
    }
    fields.update(extra)
    return GoldenCase(**fields)


def suite_of(goldens: list[GoldenCase], status: str = "active", **kw: Any):  # noqa: ANN202
    return LoadedSuite(
        manifest=SuiteManifest(
            evaluation_suite_id="s", version=2, datasets=[], status=status
        ),
        goldens=goldens,
        **kw,
    )


def run(index, emb, retriever, suite, **over):  # noqa: ANN001, ANN003, ANN201
    args: dict[str, Any] = {
        "retriever": retriever,
        "index": index,
        "embedder": emb,
        "access": guest(),
        "suite": suite,
        "release_id": "seed-v1",
        "top_k": 5,
        "authorities": AUTH,
        "registry_languages": ["en", "x1"],
        "repo_root": REPO_ROOT,
    }
    args.update(over)
    return run_retrieval_evaluation(**args)


def basic_suite() -> LoadedSuite:
    return suite_of(
        [
            golden(1, ["doc_1"]),
            golden(2, ["doc_2", "doc_3"], lang="mixed"),
            golden(3, ["doc_9"]),
            golden(4, ["doc_4"], status="deprecated"),
        ]
    )


def test_field_set_is_a_superset_of_the_1_0_keys() -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    one_zero = (
        "schema_version created_at git_commit git_dirty evaluation_suite_id "
        "evaluation_suite_version declared_knowledge_release_id "
        "release_snapshot_verified collection index_version index_settings "
        "retrieval_strategy top_k device embedder_is_fake case_count "
        "excluded_case_count document_count random_hit_rate_at_k "
        "random_hit_rate_formula metrics latency_ms cases notes kind"
    ).split()
    for key in one_zero:
        assert key in doc, key
    for key in (
        "evaluation_suite",
        "absent_query_languages",
        "section_level",
        "small_sample_threshold",
    ):
        assert key in doc, key
    assert doc["schema_version"] == "2.0" and doc["kind"] == "retrieval_evaluation"
    assert doc["case_count"] == 3 and doc["excluded_case_count"] == 1
    assert doc["evaluation_suite"]["excluded_by_status"]["golden_answerable"] == {
        "deprecated": 1
    }
    assert doc["evaluation_suite"]["cases_by_type"]["golden_answerable"] == 4
    assert doc["metrics"]["overall"]["small_sample"] is True
    assert doc["absent_query_languages"] == ["x1"]
    assert doc["section_level"]["measurable_cases"] == 0
    assert doc["latency_ms"]["measured_cases"] == 3
    case = doc["cases"][0]
    assert {"source_authority", "top1_score", "latency_ms"} <= set(case)
    assert doc["embedder_is_fake"] is False


def test_source_authority_slices_are_disjoint() -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    sliced = doc["metrics"]["by_source_authority"]
    assert sum(v["n"] for v in sliced.values()) == 3
    assert "naati+owner_approved" in sliced  # g002: doc_2 + doc_3


def test_no_query_chunk_text_or_absolute_path(tmp_path: Path) -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    out = tmp_path / "r.json"
    write_document(out, doc)
    text = out.read_text()
    assert "SECRET-QUERY" not in text and "SECRET-CHUNK" not in text
    assert "golden query" not in text
    assert str(REPO_ROOT) not in text and str(tmp_path) not in text
    assert not re.search(r'"/[A-Za-z]', text)
    assert json.loads(text)["kind"] == "retrieval_evaluation"


def test_fake_embedder_refused() -> None:
    index, _, retriever = build()
    with pytest.raises(EvaluationConfigurationError, match="fake"):
        run(index, FakeEmbedder(), retriever, basic_suite())


def test_fake_index_refused() -> None:
    fake = FakeEmbedder()
    index, _, retriever = build(fake)
    assert index.settings.embedder_is_fake is True
    with pytest.raises(EvaluationConfigurationError, match="fake embedder"):
        run(index, RealStub(), retriever, basic_suite())


@pytest.mark.parametrize("status", ["draft", "deprecated", "replaced", ""])
def test_non_active_suite_refused(status: str) -> None:
    index, emb, retriever = build()
    suite = suite_of([golden(1, ["doc_1"])], status=status)
    with pytest.raises(EvaluationConfigurationError, match="only an active suite"):
        run(index, emb, retriever, suite)


def test_active_golden_without_relevant_documents_is_refused() -> None:
    index, emb, retriever = build()
    suite = suite_of([golden(1, [])])
    with pytest.raises(EvaluationConfigurationError, match="validate-evaluation"):
        run(index, emb, retriever, suite)


def test_no_active_golden_cases_refused() -> None:
    index, emb, retriever = build()
    suite = suite_of([golden(1, ["doc_1"], status="suggested")])
    with pytest.raises(EvaluationConfigurationError, match="no active golden"):
        run(index, emb, retriever, suite)


def test_default_collection_is_accepted_and_recorded() -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    assert doc["collection"] == "way2australia-idx-v1"
    assert doc["index_version"] == "idx-v1"


def test_existing_output_is_never_overwritten(tmp_path: Path) -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    out = tmp_path / "r.json"
    out.write_text("keep")
    with pytest.raises(RetrievalConfigurationError, match="already exists"):
        write_document(out, doc)
    assert out.read_text() == "keep"


def test_failed_write_removes_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index, emb, retriever = build()
    doc = run(index, emb, retriever, basic_suite())
    out = tmp_path / "r.json"
    real_open = Path.open

    class Failing:
        def __init__(self, handle):  # noqa: ANN001, ANN204
            self._h = handle

        def __enter__(self):  # noqa: ANN204
            return self

        def __exit__(self, *a):  # noqa: ANN002, ANN204
            self._h.close()

        def write(self, text: str) -> None:
            self._h.write(text[:5])
            raise OSError("disk full")

    def fake_open(self, *a, **k):  # noqa: ANN001, ANN002, ANN003, ANN202
        handle = real_open(self, *a, **k)
        return Failing(handle) if self == out else handle

    monkeypatch.setattr(Path, "open", fake_open)
    with pytest.raises(RetrievalConfigurationError, match="could not write"):
        write_document(out, doc)
    assert not out.exists()


def test_g004_note_only_while_both_cases_are_active() -> None:
    index, emb, retriever = build()

    def unanswerable(status: str) -> UnanswerableCase:
        return UnanswerableCase(
            case_id="u001", case_version=1, status=status, query="q",
            answerable=False, expected_behavior="refuse",
        )  # fmt: skip

    both = suite_of(
        [golden(4, ["doc_1"], case_id="g004")], unanswerable=[unanswerable("active")]
    )
    notes = " ".join(run(index, emb, retriever, both)["notes"])
    assert "g004 overlaps unanswerable u001" in notes
    resolved = suite_of(
        [golden(4, ["doc_1"], case_id="g004")],
        unanswerable=[unanswerable("deprecated")],
    )
    assert "g004" not in " ".join(run(index, emb, retriever, resolved)["notes"])
    required = " ".join(run(index, emb, retriever, both)["notes"])
    assert "optimistic" in required and "1/1" in required
    assert "single chunk" in required and "several relevant" in required


def test_case_access_context_never_widens_access() -> None:
    """A case's own access_context is ignored: every search uses the one
    server-resolved guest filter."""
    index, emb, retriever = build()
    seen: list[Any] = []
    original = index.search

    def spy(vector, query_filter, limit):  # noqa: ANN001, ANN202
        seen.append(query_filter)
        return original(vector, query_filter, limit)

    index.search = spy  # type: ignore[method-assign]
    hostile = [
        {"role": "admin", "tenant_id": "other"},
        {"role": "staff", "tenant_id": "way2australia", "access_scope": "staff"},
        None,
    ]
    suite = suite_of(
        [golden(i, [f"doc_{i}"], access_context=ctx) for i, ctx in enumerate(hostile)]
    )
    run(index, emb, retriever, suite)
    expected = build_access_filter(guest())
    assert len(seen) == len(hostile) + 1  # + the warm-up query
    assert all(f == expected for f in seen)
