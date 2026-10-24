"""Throwaway security index builder (Spec 006 R8, R9, R13).

This is the only code that writes ineligible content (the staff-only canary and
synthetic forbidden points) into a collection. It can only ever create a fresh
throwaway collection named `w2a-sectest-<8 hex>`: a base that does not match, or
a target collection (or its `-settings`) that already exists, is refused before
any write. The security index records `embedder_is_fake: true`, so
`eval-retrieval` and real `make retrieve` refuse to bind it (D036).
"""

import asyncio
import re
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from qdrant_client import QdrantClient, models
from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.evaluation.errors import (
    EvaluationConfigurationError,
    EvaluationHarnessError,
)
from way2australia_rag.ingestion.chunking import Chunker
from way2australia_rag.ingestion.embedding import DEFAULT_FAKE_VECTOR_SIZE, Embedder
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.payload import PointPayload, build_payload
from way2australia_rag.ingestion.service import IngestionService
from way2australia_rag.ingestion.settings import collection_name
from way2australia_rag.ingestion.store import (
    DENSE_VECTOR_NAME,
    SETTINGS_COLLECTION_SUFFIX,
    IndexPoint,
    QdrantIndexStore,
)
from way2australia_rag.repositories import (
    GUEST_PUBLIC_POLICY,
    DocumentRepository,
)
from way2australia_rag.retrieval.index import DenseIndex

SECURITY_COLLECTION_PREFIX = "w2a-sectest-"
SECURITY_COLLECTION_BASE_RE = re.compile(r"^w2a-sectest-[0-9a-f]{8}$")
SECURITY_INDEX_VERSION = "sec-v1"
FAKE_VECTOR_SIZE = DEFAULT_FAKE_VECTOR_SIZE
FORBIDDEN_VARIANTS = ("staff_scope", "other_tenant", "owned", "missing_owner")
CANARY_DOCUMENT_ID = "fixture_staff_canary"
FORBIDDEN_DOCUMENT_PREFIX = "forbidden_"
FORBIDDEN_SENTINEL = "forbidden fixture"
_BATCH_SIZE = 16


@dataclass(frozen=True)
class SecurityIndex:
    """A built throwaway index plus what the gate needs to run against it."""

    client: QdrantClient
    collection_base: str
    collection: str
    embedder: Embedder
    dense: DenseIndex
    queries: tuple[str, ...]
    seed_document_ids: frozenset[str]
    points_per_variant: dict[str, int]


def is_forbidden_document(document_id: str) -> bool:
    return document_id == CANARY_DOCUMENT_ID or document_id.startswith(
        FORBIDDEN_DOCUMENT_PREFIX
    )


def forbidden_variant(document_id: str) -> str:
    if document_id.startswith(FORBIDDEN_DOCUMENT_PREFIX):
        return document_id[len(FORBIDDEN_DOCUMENT_PREFIX) :]
    return "staff_canary"


def require_security_base(collection_base: str) -> None:
    if not SECURITY_COLLECTION_BASE_RE.fullmatch(collection_base):
        raise EvaluationConfigurationError(
            "the security index collection base must match "
            f"'{SECURITY_COLLECTION_PREFIX}' followed by 8 hex characters."
        )


def _forbidden_payload(
    variant: str, query_index: int, tenant_id: str
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "tenant_id": tenant_id,
        "access_scope": "public",
        "owner_user_id": None,
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "title": f"Forbidden fixture {variant}",
        "knowledge_domain": "security_fixture",
        "source_authority": "synthetic",
        "source_type": "security_fixture",
        "source_url": None,
        "chunk_text": FORBIDDEN_SENTINEL,
        "content_hash": "forbidden-fixture",
        "document_id": f"{FORBIDDEN_DOCUMENT_PREFIX}{variant}",
        "document_version": 1,
        "section_id": "main",
        "chunk_position": query_index,
    }
    if variant == "staff_scope":
        payload["access_scope"] = "staff"
    elif variant == "other_tenant":
        payload["tenant_id"] = f"{tenant_id}-other"
    elif variant == "owned":
        payload["owner_user_id"] = "eval-user"
    elif variant == "missing_owner":
        del payload["owner_user_id"]  # deliberately breaks the PointPayload model
    else:  # pragma: no cover - guarded by FORBIDDEN_VARIANTS
        raise EvaluationHarnessError(f"unknown forbidden variant '{variant}'")
    return payload


def build_security_index(
    client: QdrantClient,
    collection_base: str,
    queries: Sequence[str],
    embedder: Embedder,
    chunker: Chunker,
    *,
    seed_repository: DocumentRepository,
    security_repository: DocumentRepository,
    tenant_id: str,
) -> SecurityIndex:
    """Build a fresh throwaway index: seed corpus, canary and forbidden points.

    Refuses, before any write, a base that does not match the throwaway pattern
    and any target collection that already exists.
    """
    require_security_base(collection_base)
    if not embedder.info.is_fake:
        raise EvaluationConfigurationError(
            "the security index is built with the fake embedder only."
        )
    collection = collection_name(collection_base, SECURITY_INDEX_VERSION)
    for name in (collection, collection + SETTINGS_COLLECTION_SUFFIX):
        if client.collection_exists(name):
            raise EvaluationConfigurationError(
                f"collection '{name}' already exists; the security index builder "
                "only creates a new throwaway collection."
            )

    store = QdrantIndexStore(client, collection_base, SECURITY_INDEX_VERSION)
    # 1. seed corpus through the production ingestion path (creates the collection)
    report = asyncio.run(
        IngestionService(
            seed_repository, GUEST_PUBLIC_POLICY, chunker, embedder, store, _BATCH_SIZE
        ).run()
    )
    if report.failures:
        raise EvaluationHarnessError(
            "seed ingestion failed for: "
            + ", ".join(sorted(f.document_id for f in report.failures))
        )
    seed_ids = frozenset(report.added)

    vectors = [embedder.embed_query(q) for q in queries]

    # 2. staff canary: its own text vector plus one probe point per query
    canary = asyncio.run(security_repository.get_document(CANARY_DOCUMENT_ID))
    canary_points = _canary_points(canary, chunker, embedder, vectors)
    store.replace_document(CANARY_DOCUMENT_ID, canary_points)

    # 3. synthetic forbidden points (raw upsert: one variant breaks the model)
    for variant in FORBIDDEN_VARIANTS:
        client.upsert(
            store.collection,
            points=[
                models.PointStruct(
                    id=point_id(f"{FORBIDDEN_DOCUMENT_PREFIX}{variant}", "main", i),
                    vector={DENSE_VECTOR_NAME: vector},
                    payload=_forbidden_payload(variant, i, tenant_id),
                )
                for i, vector in enumerate(vectors)
            ],
            wait=True,
        )

    dense = DenseIndex.open(
        client, collection_base, SECURITY_INDEX_VERSION, embedder.info
    )
    counts = {variant: len(vectors) for variant in FORBIDDEN_VARIANTS}
    counts["staff_canary"] = len(canary_points)
    return SecurityIndex(
        client=client,
        collection_base=collection_base,
        collection=store.collection,
        embedder=embedder,
        dense=dense,
        queries=tuple(queries),
        seed_document_ids=seed_ids,
        points_per_variant=counts,
    )


def _canary_points(
    canary: KnowledgeDocument,
    chunker: Chunker,
    embedder: Embedder,
    query_vectors: Sequence[list[float]],
) -> list[IndexPoint]:
    chunks = chunker.chunk(canary)
    own_vectors = embedder.embed_documents([c.text for c in chunks])
    points = [
        IndexPoint(
            point_id=point_id(canary.document_id, c.section_id, c.position),
            vector=vector,
            payload=build_payload(canary, c),
        )
        for c, vector in zip(chunks, own_vectors, strict=True)
    ]
    base: PointPayload = points[0].payload
    for i, vector in enumerate(query_vectors):
        points.append(
            IndexPoint(
                point_id=point_id(canary.document_id, "query-probe", i),
                vector=vector,
                payload=base.model_copy(update={"chunk_position": i}),
            )
        )
    return points


def delete_security_index(index: SecurityIndex) -> None:
    """Remove the throwaway collection and its settings record (only ever these)."""
    require_security_base(index.collection_base)
    for name in (index.collection, index.collection + SETTINGS_COLLECTION_SUFFIX):
        if index.client.collection_exists(name):
            index.client.delete_collection(name)
