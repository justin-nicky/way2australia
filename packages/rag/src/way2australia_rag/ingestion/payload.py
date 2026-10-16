"""Point payload: the exact fields stored with every indexed chunk (Spec 004 R8).

Every non-identity field is covered by `content_hash` (metadata fields in
`CONTENT_HASH_METADATA_FIELDS`, `chunk_text` via the body); identity fields are
compared directly. `persona_scope` and `last_reviewed_at` are left out on
purpose, as are eligibility-only fields (the eligibility policy owns those).
Authorization and language fields stay separate.
"""

from pydantic import BaseModel, ConfigDict
from way2australia_core.documents import KnowledgeDocument

from way2australia_rag.ingestion.chunking import Chunk

IDENTITY_FIELDS: tuple[str, ...] = (
    "document_id",
    "document_version",
    "section_id",
    "chunk_position",
)


class PointPayload(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    tenant_id: str
    access_scope: str
    owner_user_id: str | None
    language_scope: str
    lote_languages: list[str]
    content_language: str
    title: str
    knowledge_domain: str
    source_authority: str
    source_type: str
    source_url: str | None
    chunk_text: str
    content_hash: str
    document_id: str
    document_version: int
    section_id: str
    chunk_position: int


def build_payload(document: KnowledgeDocument, chunk: Chunk) -> PointPayload:
    return PointPayload(
        tenant_id=document.tenant_id,
        access_scope=str(document.access_scope),
        owner_user_id=document.owner_user_id,
        language_scope=str(document.language_scope),
        lote_languages=list(document.lote_languages),
        content_language=document.content_language,
        title=document.title,
        knowledge_domain=document.knowledge_domain,
        source_authority=str(document.source_authority),
        source_type=document.source_type,
        source_url=document.source_url,
        chunk_text=chunk.text,
        content_hash=document.content_hash,
        document_id=document.document_id,
        document_version=document.document_version,
        section_id=chunk.section_id,
        chunk_position=chunk.position,
    )
