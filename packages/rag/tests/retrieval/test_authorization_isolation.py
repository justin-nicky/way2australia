"""Authorization isolation on an isolated in-memory collection (Spec 005 R2, R3).

Synthetic points that must never be returned are each the nearest vector to the
query (their chunk text equals the query under the fake embedder).
"""

from typing import Any

import pytest
from qdrant_client import models
from way2australia_rag.retrieval.errors import RetrievalAuthorizationError
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

from .test_retriever import (
    BASE,
    EMBEDDER,
    VERSION,
    build_client,
    guest,
    make_point,
)

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

QUERY = "the nearest text of all"
FORBIDDEN: dict[str, dict[str, Any]] = {
    "staff_scope": {"access_scope": "staff"},
    "other_tenant": {"tenant_id": "other-tenant"},
    "owned": {"owner_user_id": "user-1"},
}


@pytest.fixture
def client_with_forbidden():  # type: ignore[no-untyped-def]
    points = [make_point(f"public_{i}", f"public text {i}") for i in range(3)]
    points += [
        make_point(f"forbidden_{name}", QUERY, **over)
        for name, over in FORBIDDEN.items()
    ]
    return build_client(points)


def test_forbidden_points_are_never_returned(client_with_forbidden) -> None:  # type: ignore[no-untyped-def]
    index = DenseIndex.open(client_with_forbidden, BASE, VERSION, EMBEDDER.info)
    result = DenseRetriever(index, EMBEDDER).retrieve(QUERY, guest(), top_k=50)
    ids = {h.document_id for h in result.hits}
    assert ids == {"public_0", "public_1", "public_2"}
    # Sanity: without a filter the forbidden points really are the nearest.
    raw = client_with_forbidden.query_points(
        index.collection, query=EMBEDDER.embed_query(QUERY), using="dense", limit=3
    ).points
    assert {p.payload["document_id"] for p in raw if p.payload} == {
        f"forbidden_{name}" for name in FORBIDDEN
    }


class FilterDroppingIndex(DenseIndex):
    """A store that ignores the authorization filter it is given."""

    def search(
        self, vector: list[float], query_filter: models.Filter, limit: int
    ) -> list[models.ScoredPoint]:
        return super().search(vector, models.Filter(), limit)


def test_store_dropping_the_filter_fails_closed(client_with_forbidden) -> None:  # type: ignore[no-untyped-def]
    real = DenseIndex.open(client_with_forbidden, BASE, VERSION, EMBEDDER.info)
    bad = FilterDroppingIndex(client_with_forbidden, real.collection, real.settings)
    with pytest.raises(RetrievalAuthorizationError) as raised:
        DenseRetriever(bad, EMBEDDER).retrieve(QUERY, guest(), top_k=50)
    assert QUERY not in str(raised.value)
