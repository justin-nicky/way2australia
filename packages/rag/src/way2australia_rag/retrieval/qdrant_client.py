"""Qdrant client for retrieval with bounded requests (Spec 008 R2).

qdrant-client takes one integer `timeout` and applies it to every httpx phase,
so the connect bound is the client default and `DenseIndex.search` overrides it
per request with the query bound. Ingestion keeps its own factory.
"""

from qdrant_client import QdrantClient

from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.retrieval.strategy import QdrantTimeouts


def retrieval_client_factory(
    settings: RuntimeSettings, timeouts: QdrantTimeouts
) -> QdrantClient:
    """A client whose default request timeout is `connect_timeout_s`.

    The compatibility check is off: it is an extra unbounded call and its
    warnings can carry the server URL.
    """
    key = settings.qdrant_api_key
    return QdrantClient(
        location=settings.qdrant_url,
        api_key=key.get_secret_value() if key is not None else None,
        timeout=timeouts.connect_timeout_s,
        check_compatibility=False,
    )
