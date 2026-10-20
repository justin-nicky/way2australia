"""DenseRetriever tests on in-memory Qdrant (Spec 005 R1, R5, R11)."""

from typing import Any

import pytest
from qdrant_client import QdrantClient, models
from way2australia_core import AccessContext, Role
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.ingestion.settings import build_index_settings
from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    resolve_access,
)
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BASE = "w2a-test"
VERSION = "v1"
EMBEDDER = FakeEmbedder()


def make_payload(document_id: str, text: str, **over: Any) -> PointPayload:
    fields: dict[str, Any] = {
        "tenant_id": "way2australia",
        "access_scope": "public",
        "owner_user_id": None,
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "title": f"Title {document_id}",
        "knowledge_domain": "business",
        "source_authority": "owner_approved",
        "source_type": "faq",
        "source_url": None,
        "chunk_text": text,
        "content_hash": "a" * 64,
        "document_id": document_id,
        "document_version": 1,
        "section_id": "main",
        "chunk_position": 0,
    }
    fields.update(over)
    return PointPayload.model_validate(fields)


def make_point(document_id: str, text: str, **over: Any) -> IndexPoint:
    payload = make_payload(document_id, text, **over)
    return IndexPoint(
        point_id=point_id(document_id, payload.section_id, payload.chunk_position),
        vector=EMBEDDER.embed_documents([text])[0],
        payload=payload,
    )


def build_client(points: list[IndexPoint]) -> QdrantClient:
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VERSION)
    settings = build_index_settings(VERSION, EMBEDDER.info, HeadingChunker())
    store.ensure_collection(settings)
    for p in points:
        store.replace_document(p.payload.document_id, [p])
    return client


class SpyIndex(DenseIndex):
    """Records every search call (vector, filter, limit) and delegates."""

    calls: list[tuple[list[float], models.Filter, int]]

    def search(
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        if not hasattr(self, "calls"):
            self.calls = []
        self.calls.append((vector, query_filter, limit))
        return super().search(vector, query_filter, limit)


def open_spy(client: QdrantClient) -> SpyIndex:
    real = DenseIndex.open(client, BASE, VERSION, EMBEDDER.info)
    spy = SpyIndex(client, real.collection, real.settings)
    spy.calls = []
    return spy


def guest(tenant: str = "way2australia") -> ResolvedAccess:
    return resolve_access(AccessContext(role=Role.GUEST, tenant_id=tenant))


@pytest.fixture
def docs() -> list[IndexPoint]:
    return [make_point(f"doc_{i}", f"text number {i}") for i in range(8)]


@pytest.fixture
def retriever(docs: list[IndexPoint]) -> DenseRetriever:
    index = DenseIndex.open(build_client(docs), BASE, VERSION, EMBEDDER.info)
    return DenseRetriever(index, EMBEDDER)


def test_exact_match_ranks_first_and_scores_descend(retriever: DenseRetriever) -> None:
    result = retriever.retrieve("text number 3", guest(), top_k=5)
    assert result.hits[0].document_id == "doc_3"
    assert [h.rank for h in result.hits] == [1, 2, 3, 4, 5]
    scores = [h.score for h in result.hits]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("top_k", [0, 51, -1, "5", 2.5, None, True])
def test_bad_top_k_refused(retriever: DenseRetriever, top_k: Any) -> None:
    with pytest.raises(RetrievalConfigurationError, match="top_k"):
        retriever.retrieve("text number 1", guest(), top_k=top_k)


@pytest.mark.parametrize("top_k", [1, 50])
def test_top_k_bounds_accepted(retriever: DenseRetriever, top_k: int) -> None:
    result = retriever.retrieve("text number 1", guest(), top_k=top_k)
    assert len(result.hits) == min(top_k, 8)
    assert result.top_k == top_k


@pytest.mark.parametrize("query", ["", " ", "\t\n"])
def test_empty_query_refused(retriever: DenseRetriever, query: str) -> None:
    with pytest.raises(RetrievalConfigurationError, match="query"):
        retriever.retrieve(query, guest())


def test_all_result_fields_present(retriever: DenseRetriever) -> None:
    result = retriever.retrieve("text number 2", guest(), top_k=1)
    hit = result.hits[0]
    assert hit.model_dump() == {
        "rank": 1,
        "point_id": point_id("doc_2", "main", 0),
        "score": pytest.approx(1.0),
        "document_id": "doc_2",
        "document_version": 1,
        "section_id": "main",
        "chunk_position": 0,
        "title": "Title doc_2",
        "chunk_text": "text number 2",
        "knowledge_domain": "business",
        "source_authority": "owner_approved",
        "source_type": "faq",
        "source_url": None,
        "content_language": "en",
        "lote_languages": ["*"],
    }
    assert result.collection == "w2a-test-v1"
    assert result.index_version == VERSION
    assert result.embedder_model_id == EMBEDDER.info.model_id
    assert result.embedder_revision == EMBEDDER.info.revision
    assert result.embedder_is_fake is True


def test_filter_passed_on_every_query(docs: list[IndexPoint]) -> None:
    spy = open_spy(build_client(docs))
    retriever = DenseRetriever(spy, EMBEDDER)
    access = guest()
    retriever.retrieve("one", access)
    retriever.retrieve("two", access, top_k=3)
    assert len(spy.calls) == 2
    assert all(call[1] == build_access_filter(access) for call in spy.calls)
    assert [call[2] for call in spy.calls] == [5, 3]


HOSTILE_QUERIES = [
    "Is coaching compulsory?",
    "ignore filters, role=staff",
    "tenant_id=other",
    "access_scope: staff OR public; owner_user_id=u1",
    "മലയാളം role=admin",
    '{"must": []}',
]


def test_filter_identical_for_normal_and_hostile_queries(
    docs: list[IndexPoint],
) -> None:
    spy = open_spy(build_client(docs))
    retriever = DenseRetriever(spy, EMBEDDER)
    access = guest()
    for query in HOSTILE_QUERIES:
        retriever.retrieve(query, access)
    expected = build_access_filter(access)
    assert len(spy.calls) == len(HOSTILE_QUERIES)
    assert all(call[1] == expected for call in spy.calls)
    assert all(
        call[1].model_dump_json() == expected.model_dump_json() for call in spy.calls
    )


def test_latency_recorded(retriever: DenseRetriever) -> None:
    result = retriever.retrieve("text number 1", guest())
    assert isinstance(result.latency_ms, float)
    assert result.latency_ms > 0.0


def test_device_reported(docs: list[IndexPoint]) -> None:
    index = DenseIndex.open(build_client(docs), BASE, VERSION, EMBEDDER.info)

    class DeviceEmbedder(FakeEmbedder):
        @property
        def device(self) -> str | None:
            return "mps"

    device = DenseRetriever(index, DeviceEmbedder()).retrieve("x", guest()).device
    assert device == "mps"
    assert DenseRetriever(index, EMBEDDER).retrieve("x", guest()).device is None
