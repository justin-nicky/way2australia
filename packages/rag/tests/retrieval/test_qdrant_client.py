"""The retrieval client factory (Spec 008 R2)."""

from typing import Any

import pytest
from pydantic import SecretStr
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.retrieval import qdrant_client as module
from way2australia_rag.retrieval.qdrant_client import retrieval_client_factory
from way2australia_rag.retrieval.strategy import QdrantTimeouts


def settings(api_key: str | None) -> RuntimeSettings:
    return RuntimeSettings.model_construct(
        qdrant_url="http://qdrant.test:6333",
        qdrant_api_key=SecretStr(api_key) if api_key else None,
        collection_base="w2a-test",
        tenant_id="way2australia",
    )


@pytest.mark.parametrize("api_key", [None, "k"])
def test_factory_sets_the_connect_timeout_and_disables_the_version_check(
    monkeypatch: pytest.MonkeyPatch, api_key: str | None
) -> None:
    seen: dict[str, Any] = {}

    def recording(**kwargs: Any) -> str:
        seen.update(kwargs)
        return "client"

    monkeypatch.setattr(module, "QdrantClient", recording)
    timeouts = QdrantTimeouts(connect_timeout_s=5, query_timeout_s=9)
    assert retrieval_client_factory(settings(api_key), timeouts) == "client"  # type: ignore[comparison-overlap]
    assert seen == {
        "location": "http://qdrant.test:6333",
        "api_key": api_key,
        "timeout": 5,
        "check_compatibility": False,
    }
