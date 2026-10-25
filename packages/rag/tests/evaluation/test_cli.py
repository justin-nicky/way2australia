"""`eval-retrieval` CLI tests (Spec 006 R4, R7). Writes go to tmp_path only."""

import json
import shutil
from pathlib import Path

import pytest
from conftest import REPO_ROOT, live_suite_rows
from qdrant_client import QdrantClient, models
from retrieval.test_cli import Factory
from retrieval.test_retriever import make_payload
from way2australia_rag.evaluation import cli
from way2australia_rag.ingestion.chunking import HeadingChunker
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.ingestion.embedding import FakeEmbedder
from way2australia_rag.ingestion.errors import OptionalDependencyError
from way2australia_rag.ingestion.identity import point_id
from way2australia_rag.ingestion.settings import build_index_settings
from way2australia_rag.ingestion.store import IndexPoint, QdrantIndexStore
from way2australia_rag.retrieval.access import (
    build_access_filter,
    guest_access,
    resolve_access,
)
from way2australia_rag.retrieval.index import DenseIndex

from .test_retrieval_eval import RealStub

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)
BASE, VERSION = "way2australia", "idx-v1"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in (
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION_BASE",
        "W2A_TENANT_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)


def index_factory(embedder: FakeEmbedder, tenant: str = "way2australia") -> Factory:
    client = QdrantClient(":memory:")
    store = QdrantIndexStore(client, BASE, VERSION)
    settings = build_index_settings(VERSION, embedder.info, HeadingChunker())
    store.ensure_collection(settings)
    for doc_id in cli._authority_map(REPO_ROOT):
        text = f"chunk {doc_id}"
        store.replace_document(
            doc_id,
            [
                IndexPoint(
                    point_id=point_id(doc_id, "main", 0),
                    vector=embedder.embed_documents([text])[0],
                    payload=make_payload(doc_id, text, tenant_id=tenant),
                )
            ],
        )
    return Factory(client)


def real_factory(config, provider):  # noqa: ANN001, ANN201
    return RealStub()


def run(factory: Factory, *extra: str, root: Path = REPO_ROOT, embedder=real_factory):  # noqa: ANN001, ANN201
    return cli.main(
        ["retrieval", "--repo-root", str(root), *extra],
        client_factory=factory,
        embedder_factory=embedder,
    )


def test_success_writes_result_prints_collection_and_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    factory = index_factory(RealStub())
    out = tmp_path / "e.json"
    assert run(factory, "--output", str(out)) == 0
    doc = json.loads(out.read_text())
    goldens = len(live_suite_rows("golden_answerable", active_only=True))
    unanswerable = len(live_suite_rows("unanswerable_refusal", active_only=True))
    assert doc["kind"] == "retrieval_evaluation" and doc["case_count"] == goldens
    assert doc["collection"] == "way2australia-idx-v1"
    assert (
        doc["evaluation_suite"]["cases_by_type"]["unanswerable_refusal"] == unanswerable
    )
    block = doc["unanswerable"]
    assert (
        block["status"] == "not_evaluable_before_generation"
        and block["n"] == unanswerable
    )
    shown = capsys.readouterr().out
    assert "unanswerable (not_evaluable_before_generation, informational" in shown
    assert "collection: way2australia-idx-v1" in shown
    assert "HitRate@5" in shown and "e.json" in shown


def test_existing_output_exits_2_before_qdrant(tmp_path: Path) -> None:
    factory = index_factory(RealStub())
    out = tmp_path / "e.json"
    out.write_text("keep")
    assert run(factory, "--output", str(out)) == 2
    assert out.read_text() == "keep"


def test_bad_top_k_exits_2(tmp_path: Path) -> None:
    factory = index_factory(RealStub())
    out = tmp_path / "e.json"
    assert run(factory, "--top-k", "0", "--output", str(out)) == 2
    assert not out.exists() and factory.calls == 0


def test_missing_extra_exits_2_before_qdrant(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def missing(config, provider):  # noqa: ANN001, ANN202
        raise OptionalDependencyError("install the bge-m3 extra")

    factory = index_factory(RealStub())
    out = tmp_path / "e.json"
    assert run(factory, "--output", str(out), embedder=missing) == 2
    assert factory.calls == 0 and not out.exists()
    assert "bge-m3" in capsys.readouterr().err


def test_fake_embedder_exits_2_before_qdrant(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    factory = index_factory(FakeEmbedder())
    out = tmp_path / "e.json"
    code = run(factory, "--output", str(out), embedder=lambda c, p: FakeEmbedder())
    assert code == 2 and factory.calls == 0 and not out.exists()
    assert "ERROR EvaluationConfigurationError" in capsys.readouterr().err


def test_recorded_fake_index_exits_2_and_writes_nothing(tmp_path: Path) -> None:
    factory = index_factory(FakeEmbedder())  # index records embedder_is_fake
    out = tmp_path / "e.json"
    assert run(factory, "--output", str(out)) == 2  # binding mismatch (D036)
    assert factory.calls == 1 and not out.exists()


def test_non_active_suite_exits_2_before_qdrant(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    for name in ("evaluation", "knowledge", "config"):
        shutil.copytree(REPO_ROOT / name, root / name)
    suite = root / "evaluation/suites/public-eval-v2.json"
    raw = json.loads(suite.read_text())
    raw["status"] = "draft"
    suite.write_text(json.dumps(raw))
    factory = index_factory(RealStub())
    out = tmp_path / "e.json"
    assert run(factory, "--output", str(out), root=root) == 2
    assert factory.calls == 0 and not out.exists()


def test_unexpected_exception_prints_class_name_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    def boom(settings):  # noqa: ANN001, ANN202
        raise ConnectionError("http://user:secret@host/")

    out = tmp_path / "e.json"
    code = cli.main(
        ["retrieval", "--repo-root", str(REPO_ROOT), "--output", str(out)],
        client_factory=boom,
        embedder_factory=real_factory,
    )
    err = capsys.readouterr().err
    assert code == 2 and "ConnectionError" in err and "secret" not in err
    assert not out.exists()


def test_filter_carries_the_server_tenant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("W2A_TENANT_ID", "tenant-eval-x")
    seen: list[models.Filter] = []
    real_search = DenseIndex.search

    def spy(self, vector, query_filter, limit):  # noqa: ANN001, ANN202
        seen.append(query_filter)
        return real_search(self, vector, query_filter, limit)

    monkeypatch.setattr(DenseIndex, "search", spy)
    factory = index_factory(RealStub(), "tenant-eval-x")
    out = tmp_path / "e.json"
    assert run(factory, "--output", str(out)) == 0
    expected = build_access_filter(
        resolve_access(guest_access(RuntimeSettings(tenant_id="tenant-eval-x")))
    )
    assert seen
    assert all(f == expected for f in seen)
    assert all("tenant-eval-x" in repr(f) for f in seen)
    assert all("way2australia" not in repr(f) for f in seen)


def test_cli_has_no_embedder_or_allow_fake_flag() -> None:
    with pytest.raises(SystemExit):
        cli.main(["retrieval", "--embedder", "fake"])
    with pytest.raises(SystemExit):
        cli.main(["retrieval", "--allow-fake"])
