"""BM25 retriever over the lexical index (Spec 007 R6).

Authorization is part of the SQL `WHERE` clause (`build_sql_access_clause`) and
every returned payload is re-checked by `check_hit` (fail closed). The raw query
never reaches SQLite: it is tokenized with `lexical-v1`, every token is quoted
and the quoted tokens, joined with `OR`, are the only `MATCH` argument. The
query is never embedded.
"""

import json
from time import perf_counter

from way2australia_rag.lexical.store import LexicalIndex
from way2australia_rag.lexical.tokenizer import query_terms
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_sql_access_clause,
    check_hit,
)
from way2australia_rag.retrieval.base import DEFAULT_TOP_K, Strategy, validate_request
from way2australia_rag.retrieval.identity import IndexIdentity
from way2australia_rag.retrieval.models import (
    LexicalIdentity,
    RetrievalResult,
    RetrievedChunk,
)


def match_expression(terms: list[str]) -> str:
    """Quoted terms joined by `OR`; embedded quotes are doubled."""
    return " OR ".join('"' + term.replace('"', '""') + '"' for term in terms)


class BM25Retriever:
    strategy = Strategy.BM25

    def __init__(self, identity: IndexIdentity, lexical: LexicalIndex) -> None:
        """`identity` supplies only the dense identity recorded in results (the
        caller checked the lexical file against it); nothing is queried."""
        self._identity = identity
        self._lexical = lexical

    def retrieve(
        self,
        query_text: str,
        access: ResolvedAccess,
        top_k: int = DEFAULT_TOP_K,
    ) -> RetrievalResult:
        validate_request(query_text, top_k)
        started = perf_counter()
        terms = query_terms(query_text)
        hits: list[RetrievedChunk] = []
        if terms.terms:
            where, params = build_sql_access_clause(access)
            rows = self._lexical.search(
                match_expression(terms.terms), where, params, top_k
            )
            for rank, row in enumerate(rows, start=1):
                try:
                    raw = json.loads(row.payload_json)
                except ValueError:
                    raw = None
                payload = check_hit(raw if isinstance(raw, dict) else {}, access)
                hits.append(
                    RetrievedChunk(
                        rank=rank,
                        point_id=row.point_id,
                        score=-row.score + 0.0,
                        document_id=payload.document_id,
                        document_version=payload.document_version,
                        section_id=payload.section_id,
                        chunk_position=payload.chunk_position,
                        title=payload.title,
                        chunk_text=payload.chunk_text,
                        knowledge_domain=payload.knowledge_domain,
                        source_authority=payload.source_authority,
                        source_type=payload.source_type,
                        source_url=payload.source_url,
                        content_language=payload.content_language,
                        lote_languages=list(payload.lote_languages),
                    )
                )
        latency_ms = (perf_counter() - started) * 1000.0
        identity = self._identity
        lexical = self._lexical.settings
        return RetrievalResult(
            hits=hits,
            collection=identity.collection,
            index_version=identity.index_version,
            embedder_model_id=identity.embedder_model_id,
            embedder_revision=identity.embedder_revision,
            embedder_is_fake=identity.embedder_is_fake,
            device=None,
            top_k=top_k,
            latency_ms=latency_ms,
            strategy=Strategy.BM25.value,
            score_kind="bm25",
            lexical=LexicalIdentity(
                label=self._lexical.label,
                tokenizer_name=lexical.tokenizer_name,
                tokenizer_version=lexical.tokenizer_version,
                source_chunk_digest=lexical.source_chunk_digest,
                chunk_count=lexical.chunk_count,
            ),
            query_terms_truncated=terms.truncated,
            requested_strategy=Strategy.BM25.value,
        )
