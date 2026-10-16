"""IngestionService tests: in-memory Qdrant, fake embedder (Spec 004 R1, R10, R13)."""

import asyncio
import warnings
from collections.abc import Iterable, Sequence
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from test_chunking import make_document  # type: ignore[import-not-found]
from way2australia_core.documents import KnowledgeDocument
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.errors import IndexSettingsMismatchError
from way2australia_rag.ingestion.service import IngestionService, RunReport
from way2australia_rag.ingestion.store import (
    SETTINGS_POINT_ID,
    IndexedDocument,
    IndexPoint,
    QdrantIndexStore,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentQuery,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.errors import DocumentNotFoundError

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

BASE = "w2a-svc"
VERSION = "v1"
THREE_SECTIONS = "intro\n\n# One\n\nbody one\n\n# Two\n\nbody two\n"
TWO_SECTIONS = "intro\n\n# One\n\nbody one\n"


class ListRepository:
    """In-memory DocumentRepository over a mutable list of documents."""

    def __init__(self, documents: Iterable[KnowledgeDocument] = ()) -> None:
        self.documents = list(documents)

    def put(self, document: KnowledgeDocument) -> None:
        self.documents = [
            d for d in self.documents if d.document_id != document.document_id
        ] + [document]

    def remove(self, document_id: str) -> None:
        self.documents = [d for d in self.documents if d.document_id != document_id]

    async def get_document(
        self, document_id: str, version: int | None = None
    ) -> KnowledgeDocument:
        for d in self.documents:
            if d.document_id == document_id:
                return d
        raise DocumentNotFoundError(document_id)

    async def list_documents(
        self, query: DocumentQuery | None = None
    ) -> list[KnowledgeDocument]:
        return [d for d in self.documents if query is None or query.matches(d)]


class CountingEmbedder:
    def __init__(self, fail_on: str | None = None) -> None:
        self._inner = FakeEmbedder()
        self.info = self._inner.info
        self.calls = 0
        self.fail_on = fail_on

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls += 1
        if self.fail_on and any(self.fail_on in t for t in texts):
            raise RuntimeError("boom: secret document text")
        return self._inner.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._inner.embed_query(text)


class CountingStore(QdrantIndexStore):
    def __init__(self, client: QdrantClient) -> None:
        super().__init__(client, BASE, VERSION)
        self.replaced: list[str] = []
        self.deleted: list[list[str]] = []

    def replace_document(self, document_id: str, points: Sequence[IndexPoint]) -> None:
        self.replaced.append(document_id)
        super().replace_document(document_id, points)

    def delete_documents(self, document_ids: Iterable[str]) -> None:
        ids = list(document_ids)
        self.deleted.append(ids)
        super().delete_documents(ids)


def doc(
    document_id: str, content: str = "hello", **overrides: Any
) -> KnowledgeDocument:
    overrides.setdefault("content_hash", f"{abs(hash((document_id, content))):064x}")
    return make_document(content, document_id=document_id, **overrides)


class Harness:
    def __init__(self, documents: Iterable[KnowledgeDocument] = ()) -> None:
        self.client = QdrantClient(":memory:")
        self.repository = ListRepository(documents)
        self.embedder = CountingEmbedder()
        self.store = CountingStore(self.client)

    def run(self) -> RunReport:
        service = IngestionService(
            self.repository,
            GUEST_PUBLIC_POLICY,
            HeadingChunker(),
            self.embedder,
            self.store,
            batch_size=2,
        )
        return asyncio.run(service.run())

    def point_ids(self, document_id: str) -> set[str]:
        return set(self.store.read_state()[document_id].point_ids)

    def reset_counts(self) -> None:
        self.embedder.calls = 0
        self.store.replaced.clear()
        self.store.deleted.clear()


def test_first_run_adds_all_second_run_is_idempotent() -> None:
    h = Harness([doc("a"), doc("b")])
    first = h.run()
    assert first.added == ["a", "b"]
    assert (first.updated, first.unchanged, first.deleted, first.failures) == (
        [],
        [],
        [],
        [],
    )
    assert (first.index_version, first.collection) == (VERSION, f"{BASE}-{VERSION}")
    assert first.embedder_model_id == h.embedder.info.model_id
    assert first.embedder_is_fake is True
    h.reset_counts()
    second = h.run()
    assert second.added == second.updated == second.deleted == []
    assert second.unchanged == ["a", "b"]
    assert h.embedder.calls == 0
    assert h.store.replaced == [] and h.store.deleted == []


def test_changed_body_updates() -> None:
    h = Harness([doc("a", "one")])
    h.run()
    h.repository.put(doc("a", "two"))
    assert h.run().updated == ["a"]


def test_changed_metadata_field_updates() -> None:
    h = Harness([doc("a", "same")])
    h.run()
    h.repository.put(doc("a", "same", title="New title", content_hash="b" * 64))
    report = h.run()
    assert report.updated == ["a"]
    records, _ = h.client.scroll(h.store.collection, with_payload=True)
    assert {r.payload["title"] for r in records if r.payload} == {"New title"}


def test_bumped_document_version_updates() -> None:
    h = Harness([doc("a")])
    h.run()
    h.repository.put(doc("a", document_version=2))
    report = h.run()
    assert report.updated == ["a"]
    assert h.store.read_state()["a"].document_version == 2


def test_review_date_change_does_not_update() -> None:
    first = doc("a", last_reviewed_at="2026-01-01")
    h = Harness([first])
    h.run()
    h.repository.put(first.model_copy(update={"last_reviewed_at": None}))
    h.reset_counts()
    report = h.run()
    assert report.unchanged == ["a"] and report.updated == []
    assert h.embedder.calls == 0 and h.store.replaced == []


def test_chunk_shrink_leaves_no_orphan() -> None:
    h = Harness([doc("a", THREE_SECTIONS)])
    h.run()
    assert len(h.point_ids("a")) == 3
    h.repository.put(doc("a", TWO_SECTIONS))
    assert h.run().updated == ["a"]
    assert len(h.point_ids("a")) == 2
    assert h.client.count(h.store.collection, exact=True).count == 2


@pytest.mark.parametrize(
    "change",
    [
        {"lifecycle_status": "deprecated"},
        {"retrieval_enabled": False},
    ],
)
def test_no_longer_eligible_document_is_deleted(change: dict[str, Any]) -> None:
    h = Harness([doc("a"), doc("b")])
    h.run()
    h.repository.put(doc("a", **change))
    report = h.run()
    assert report.deleted == ["a"]
    assert report.unchanged == ["b"]
    assert set(h.store.read_state()) == {"b"}


def test_removed_document_is_deleted() -> None:
    h = Harness([doc("a"), doc("b")])
    h.run()
    h.repository.remove("b")
    assert h.run().deleted == ["b"]
    assert set(h.store.read_state()) == {"a"}


def test_ineligible_documents_never_reach_the_index() -> None:
    h = Harness(
        [
            doc("ok"),
            doc("staff", access_scope="staff"),
            doc("private", access_scope="user_private", owner_user_id="u1"),
            doc("synthetic", synthetic=True),
            doc("draft", approval_status="pending_review"),
            doc("off", retrieval_enabled=False),
            doc("old", lifecycle_status="deprecated"),
        ]
    )
    report = h.run()
    assert report.added == ["ok"]
    assert set(h.store.read_state()) == {"ok"}


def test_security_fixtures_never_reach_the_index(security_repository: Any) -> None:
    h = Harness()
    h.repository = security_repository
    report = h.run()
    assert report.added == [] and report.failures == []
    assert h.store.read_state() == {}


def test_embedding_failure_keeps_old_points_and_continues() -> None:
    h = Harness([doc("a", "old a"), doc("b", "old b")])
    h.run()
    old_a = h.point_ids("a")
    h.repository.put(doc("a", "new BAD"))
    h.repository.put(doc("b", "new b"))
    h.repository.put(doc("c", "new c"))
    h.embedder.fail_on = "BAD"
    h.reset_counts()
    report = h.run()
    assert [f.document_id for f in report.failures] == ["a"]
    assert report.failures[0].reason == "RuntimeError"
    assert "secret" not in repr(report)
    assert report.updated == ["b"] and report.added == ["c"]
    assert "a" not in report.updated
    state = h.store.read_state()
    assert state["a"].point_ids == old_a
    assert state["a"].content_hash == doc("a", "old a").content_hash
    assert "a" not in h.store.replaced
    h.embedder.fail_on = None
    assert h.run().updated == ["a"]


def test_missing_points_with_matching_hash_and_version_are_repaired() -> None:
    h = Harness([doc("a", THREE_SECTIONS)])
    h.run()
    victim = sorted(h.point_ids("a"))[0]
    h.client.delete(h.store.collection, points_selector=[victim])
    assert len(h.point_ids("a")) == 2
    report = h.run()
    assert report.updated == ["a"]
    assert len(h.point_ids("a")) == 3
    assert h.run().unchanged == ["a"]


def test_inconsistent_state_is_classified_as_updated() -> None:
    """T6 F1: read_state reports version 0 and an empty hash for disagreeing points."""
    h = Harness([doc("a", THREE_SECTIONS)])
    h.run()
    victim = sorted(h.point_ids("a"))[0]
    h.client.set_payload(
        h.store.collection, payload={"content_hash": "f" * 64}, points=[victim]
    )
    assert h.store.read_state()["a"] == IndexedDocument(
        document_version=0, content_hash="", point_ids=frozenset(h.point_ids("a"))
    )
    report = h.run()
    assert report.updated == ["a"]
    assert (
        h.store.read_state()["a"].content_hash == doc("a", THREE_SECTIONS).content_hash
    )
    assert h.run().unchanged == ["a"]


def test_settings_mismatch_refuses_before_any_write() -> None:
    h = Harness([doc("a")])
    h.run()
    h.repository.put(doc("a", "changed"))
    h.embedder.info = h.embedder.info.model_copy(update={"model_id": "other"})
    h.reset_counts()
    with pytest.raises(IndexSettingsMismatchError):
        h.run()
    assert h.embedder.calls == 0 and h.store.replaced == []


def test_malformed_settings_payload_becomes_ingestion_error() -> None:
    """T6 F3: a foreign settings payload is not a raw pydantic ValidationError."""
    h = Harness([doc("a")])
    h.run()
    h.client.overwrite_payload(
        h.store.settings_collection,
        payload={"unexpected": "private text"},
        points=[SETTINGS_POINT_ID],
    )
    with pytest.raises(IndexSettingsMismatchError, match="malformed or foreign") as e:
        h.run()
    assert "private text" not in str(e.value)


def test_delete_failure_is_reported_and_run_continues() -> None:
    h = Harness([doc("a"), doc("b")])
    h.run()
    h.repository.remove("a")
    h.repository.put(doc("b", "changed"))

    def broken(document_ids: Iterable[str]) -> None:
        raise RuntimeError("down")

    h.store.delete_documents = broken  # type: ignore[method-assign]
    report = h.run()
    assert report.deleted == []
    assert [(f.document_id, f.reason) for f in report.failures] == [
        ("a", "RuntimeError")
    ]
    assert report.updated == ["b"]


def test_report_has_no_paths_or_text() -> None:
    h = Harness([doc("a", "distinctive body text")])
    dumped = h.run().model_dump_json()
    assert "distinctive" not in dumped
    assert "/" not in dumped.replace(f"{BASE}-{VERSION}", "")


def test_seed_corpus_indexes_13_documents_and_is_idempotent() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        h = Harness()
    h.repository = LocalDocumentRepository(  # type: ignore[assignment]
        LocalRepositoryConfig(repo_root=REPO_ROOT)
    )
    first = h.run()
    assert len(first.added) == 13
    assert first.updated == first.deleted == first.failures == []
    state = h.store.read_state()
    assert len(state) == 13
    assert all(len(s.point_ids) == 1 for s in state.values())
    h.reset_counts()
    second = h.run()
    assert second.added == second.updated == second.deleted == []
    assert len(second.unchanged) == 13
    assert h.embedder.calls == 0 and h.store.replaced == []
