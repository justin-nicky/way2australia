"""R7: generation cannot widen what the guest can see (security corpus, fakes only)."""

import uuid

import pytest
from qdrant_client import QdrantClient
from way2australia_core import AccessContext, Role
from way2australia_rag.evaluation.security_eval import (
    ALL_PATHS,
    _retrievers,
    select_security_queries,
)
from way2australia_rag.evaluation.security_index import (
    FAKE_VECTOR_SIZE,
    build_security_index,
    is_forbidden_document,
)
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.generation.context import ContextBuilder
from way2australia_rag.generation.fake import FakeGenerator, FakeMode
from way2australia_rag.generation.prompts import PromptRegistry
from way2australia_rag.generation.service import AnswerService
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.languages import active_lote_codes
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.retrieval.access import resolve_access
from way2australia_rag.retrieval.strategy import load_retrieval_config

from .support import REPO_ROOT as ROOT
from .support import generation_config

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

TENANT = "way2australia"
QUERY_LIMIT = 6  # retrieval-side security cases first; enough to exercise every path


def test_no_forbidden_text_or_document_id_reaches_any_rendered_prompt(
    security_repository: LocalDocumentRepository, tmp_path
) -> None:
    from way2australia_rag.evaluation.cli import DEFAULT_SUITE
    from way2australia_rag.ingestion.chunking import HeadingChunker

    queries, _ = select_security_queries(load_suite(ROOT, DEFAULT_SUITE))
    texts = [q.text for q in queries[:QUERY_LIMIT]]
    lote_codes = active_lote_codes(ROOT)
    client = QdrantClient(":memory:")
    index = build_security_index(
        client,
        "w2a-sectest-" + uuid.uuid4().hex[:8],
        texts,
        FakeEmbedder(FAKE_VECTOR_SIZE),
        HeadingChunker(2000),
        seed_repository=LocalDocumentRepository(LocalRepositoryConfig(ROOT)),
        security_repository=security_repository,
        tenant_id=TENANT,
        lexical_dir=tmp_path / "lexical",
        active_lote_code=lote_codes[0],
    )
    forbidden_ids: set[str] = set()
    forbidden_texts: set[str] = set()
    points, _ = client.scroll(index.collection, limit=2000, with_payload=True)
    for point in points:
        payload = point.payload or {}
        if is_forbidden_document(str(payload["document_id"])):
            forbidden_ids.add(str(payload["document_id"]))
            forbidden_texts.add(str(payload["chunk_text"]))
    assert forbidden_ids and forbidden_texts  # the corpus really holds forbidden rows

    config = generation_config()
    prompt = PromptRegistry(ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id=TENANT))
    retrieval_config = load_retrieval_config(ROOT / "config/retrieval.yaml")
    rendered = 0
    for path, retriever in _retrievers(index, retrieval_config, ALL_PATHS):
        generator = FakeGenerator(record=True)
        service = AnswerService(
            retriever, ContextBuilder(config.context), prompt, generator, config
        )
        for text in texts:
            response = service.answer(text, access, 5)
            dumped = response.model_dump_json()
            for document_id in forbidden_ids:
                assert document_id not in dumped, path
        for recorded in generator.prompts:
            rendered += 1
            for document_id in forbidden_ids:
                assert document_id not in recorded.user, path
            for chunk in forbidden_texts:
                assert chunk not in recorded.user, path
    assert rendered > 0  # not vacuous: prompts were rendered on the gated paths


def test_model_output_cannot_change_access_or_citation_metadata() -> None:
    from .support import FakeRetriever, hit

    config = generation_config()
    prompt = PromptRegistry(ROOT).get(config.prompt.id, config.prompt.version)
    access = resolve_access(AccessContext(role=Role.GUEST, tenant_id=TENANT))
    retriever = FakeRetriever([hit(1, "Public text.", document_id="doc_public")])
    # A model that names a staff document and a URL, and cites an unissued ID.
    generator = FakeGenerator(FakeMode.UNKNOWN_ID)
    response = AnswerService(
        retriever, ContextBuilder(config.context), prompt, generator, config
    ).answer("q", access)
    assert response.citations == [] and response.answer is None
    assert len(retriever.calls) == 1  # retrieval ran once, before the model
    ok = AnswerService(
        retriever,
        ContextBuilder(config.context),
        prompt,
        FakeGenerator(),
        config,
    ).answer("q", access)
    assert [c.document_id for c in ok.citations] == ["doc_public"]
