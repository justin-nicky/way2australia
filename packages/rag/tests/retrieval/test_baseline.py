"""Baseline runner and CLI tests on a fake index with tmp_path output.

Nothing here writes under experiments/results/ or the repository.
"""

import copy
import json
import re
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from conftest import LEGACY_SUITE, REPO_ROOT, live_suite_rows, manifest_document_count
from qdrant_client import QdrantClient
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.embedding import EmbedderInfo, FakeEmbedder
from way2australia_rag.retrieval import baseline_cli
from way2australia_rag.retrieval.access import build_access_filter
from way2australia_rag.retrieval.baseline import (
    BaselineResult,
    default_output_path,
    git_state,
    run_baseline,
    write_result,
)
from way2australia_rag.retrieval.errors import RetrievalConfigurationError
from way2australia_rag.retrieval.goldens import GoldenCase, SuiteRef
from way2australia_rag.retrieval.index import DenseIndex
from way2australia_rag.retrieval.retriever import DenseRetriever

from .test_cli import Factory
from .test_retriever import BASE, EMBEDDER, VERSION, build_client, guest, make_point

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

SUITE = SuiteRef(
    evaluation_suite_id="s", version=3, golden_dataset_path="evaluation/x.jsonl"
)
QUERY_TEXT = "text number 3 SECRET-QUERY"
CHUNK_TEXT = "chunk body SECRET-CHUNK"


class DeviceStub:
    """Reports no device until its first embed call, like an unloaded BGE-M3."""

    def __init__(self) -> None:
        self._inner = FakeEmbedder()
        self.info = self._inner.info
        self._loaded = False

    info: EmbedderInfo

    @property
    def device(self) -> str | None:
        return "mps" if self._loaded else None

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return self._inner.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        self._loaded = True
        return self._inner.embed_query(text)


def case(
    i: int, relevant: str, language: str = "en", cat: str = "business"
) -> GoldenCase:
    return GoldenCase(
        case_id=f"g{i}",
        case_version=1,
        query=f"text number {i}" if i != 3 else QUERY_TEXT,
        query_language=language,
        category=cat,
        relevant_document_ids=[relevant],
        answerable=True,
        status="active",
        # a hostile case-level access context must never widen access
        access_context={"role": "admin", "tenant_id": "other"},
    )


def setup(tmp_path: Path, embedder: DeviceStub | FakeEmbedder | None = None):  # noqa: ANN202
    points = [make_point(f"doc_{i}", CHUNK_TEXT + str(i)) for i in range(8)]
    client = build_client(points)
    emb = embedder or EMBEDDER
    index = DenseIndex.open(client, BASE, VERSION, emb.info)
    return index, emb, DenseRetriever(index, emb)


def run(index, emb, retriever, *, allow_fake=True, cases=None):  # noqa: ANN001, ANN201
    return run_baseline(
        retriever=retriever,
        index=index,
        embedder=emb,
        access=guest(),
        cases=cases
        or [case(1, "doc_1"), case(2, "doc_2", "mixed", "official"), case(3, "doc_9")],
        excluded_case_count=2,
        suite=SUITE,
        release_id="seed-v1",
        top_k=5,
        allow_fake=allow_fake,
        repo_root=REPO_ROOT,
    )


def test_fake_index_refused_without_allow_fake(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    with pytest.raises(RetrievalConfigurationError, match="--allow-fake"):
        run(index, emb, retriever, allow_fake=False)


def test_required_fields_and_notes(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    doc = run(index, emb, retriever).document
    for key in (
        "schema_version", "kind", "created_at", "git_commit", "git_dirty",
        "evaluation_suite_id", "evaluation_suite_version",
        "declared_knowledge_release_id", "release_snapshot_verified", "collection",
        "index_version", "index_settings", "retrieval_strategy", "top_k", "device",
        "embedder_is_fake", "case_count", "excluded_case_count", "document_count",
        "random_hit_rate_at_k", "random_hit_rate_formula", "metrics", "latency_ms",
        "cases", "notes",
    ):  # fmt: skip
        assert key in doc, key
    assert doc["declared_knowledge_release_id"] == "seed-v1"
    assert doc["release_snapshot_verified"] is False
    assert doc["retrieval_strategy"] == "dense" and doc["embedder_is_fake"] is True
    assert (
        doc["document_count"] == 8 and doc["random_hit_rate_formula"] == "min(1, 5/8)"
    )
    assert doc["random_hit_rate_at_k"] == pytest.approx(0.625)
    assert doc["index_settings"]["embedder_is_fake"] is True
    assert doc["case_count"] == 3 and doc["excluded_case_count"] == 2
    overall = doc["metrics"]["overall"]
    assert overall["n"] == 3
    assert set(doc["metrics"]["by_query_language"]) == {"en", "mixed"}
    assert set(doc["metrics"]["by_category"]) == {"business", "official"}
    notes = " ".join(doc["notes"])
    assert "optimistic" in notes and "min(1, 5/8)" in notes
    assert "not verified against the declared release" in notes
    assert "warm-up" in notes
    assert "not a quality measurement" in doc["notes"]
    miss = next(c for c in doc["cases"] if c["case_id"] == "g3")
    assert miss["hit"] is False and miss["reciprocal_rank"] == 0.0


def test_warmup_excluded_from_measured_cases(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)

    class Counting(DenseRetriever):
        calls = 0

        def retrieve(self, *a, **k):  # noqa: ANN002, ANN003, ANN202
            Counting.calls += 1
            return super().retrieve(*a, **k)

    counting = Counting(index, emb)
    doc = run(index, emb, counting).document
    assert Counting.calls == 4  # 1 warm-up + 3 measured
    assert doc["latency_ms"]["measured_cases"] == 3 == len(doc["cases"])
    assert doc["latency_ms"]["warmup_ms"] >= 0
    assert {"p50", "p95"} <= set(doc["latency_ms"])


def test_device_recorded_after_warmup(tmp_path: Path) -> None:
    stub = DeviceStub()
    index, emb, retriever = setup(tmp_path, stub)
    assert stub.device is None
    doc = run(index, emb, retriever).document
    assert doc["device"] == "mps"


def test_case_access_context_never_widens_access(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    seen = []
    original = index.search

    def spy(vector, query_filter, limit):  # noqa: ANN001, ANN202
        seen.append(query_filter)
        return original(vector, query_filter, limit)

    index.search = spy  # type: ignore[method-assign]
    run(index, emb, retriever)
    expected = build_access_filter(guest())
    assert seen and all(f == expected for f in seen)


def test_no_query_chunk_text_or_absolute_path(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    result = run(index, emb, retriever)
    out = tmp_path / "r.json"
    write_result(out, result)
    text = out.read_text()
    assert "SECRET-QUERY" not in text and "SECRET-CHUNK" not in text
    assert str(REPO_ROOT) not in text and str(tmp_path) not in text
    assert not re.search(r'"/[A-Za-z]', text)
    assert json.loads(text)["kind"] == "retrieval_baseline"


def test_existing_output_is_never_overwritten(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    result = run(index, emb, retriever)
    out = tmp_path / "r.json"
    out.write_text("keep")
    with pytest.raises(RetrievalConfigurationError, match="already exists"):
        write_result(out, result)
    assert out.read_text() == "keep"


def test_failed_write_removes_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index, emb, retriever = setup(tmp_path)
    result = run(index, emb, retriever)
    out = tmp_path / "r.json"
    real_open = Path.open

    class Failing:
        def __init__(self, handle):  # noqa: ANN001, ANN204
            self._h = handle

        def __enter__(self):  # noqa: ANN204
            return self

        def __exit__(self, *a):  # noqa: ANN002, ANN204
            self._h.close()

        def write(self, text: str) -> None:
            self._h.write(text[:5])  # a partial file now exists
            raise OSError("disk full")

    def fake_open(self, *a, **k):  # noqa: ANN001, ANN002, ANN003, ANN202
        handle = real_open(self, *a, **k)
        return Failing(handle) if self == out else handle

    monkeypatch.setattr(Path, "open", fake_open)
    with pytest.raises(RetrievalConfigurationError, match="could not write"):
        write_result(out, result)
    assert not out.exists()


def test_formula_shows_the_cap_when_k_reaches_document_count(tmp_path: Path) -> None:
    points = [make_point(f"doc_{i}", CHUNK_TEXT + str(i)) for i in range(3)]
    index = DenseIndex.open(build_client(points), BASE, VERSION, EMBEDDER.info)
    doc = run_baseline(
        retriever=DenseRetriever(index, EMBEDDER),
        index=index,
        embedder=EMBEDDER,
        access=guest(),
        cases=[case(1, "doc_1")],
        excluded_case_count=0,
        suite=SUITE,
        release_id="seed-v1",
        top_k=5,
        allow_fake=True,
        repo_root=REPO_ROOT,
    ).document
    assert doc["document_count"] == 3
    assert doc["random_hit_rate_formula"] == "min(1, 5/3)"
    assert doc["random_hit_rate_at_k"] == 1.0


def test_default_output_path_naming_is_utc() -> None:
    plus_ten = timezone(timedelta(hours=10))
    now = datetime(2026, 10, 21, 9, 5, 7, tzinfo=plus_ten)  # 2026-10-20 23:05:07Z
    root = Path("/repo-root")
    assert default_output_path(root, "idx-v1", now) == (
        root
        / "experiments"
        / "results"
        / "retrieval-baseline-idx-v1-20261020T230507Z.json"
    )
    utc_now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    assert default_output_path(root, "v2", utc_now).name == (
        "retrieval-baseline-v2-20260102T030405Z.json"
    )


# --- CLI (in-memory Qdrant, fake embedder, tmp_path output) ---


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


@pytest.fixture
def seeded() -> Factory:
    client = QdrantClient(":memory:")
    argv = ["--repo-root", str(REPO_ROOT), "--embedder", "fake"]
    assert ingestion_cli.main(argv, client_factory=Factory(client)) == 0
    return Factory(client)


def cli_run(factory: Factory, *extra: str) -> int:
    return baseline_cli.main(
        ["--repo-root", str(REPO_ROOT), "--embedder", "fake", *extra],
        client_factory=factory,
    )


def test_cli_without_allow_fake_exits_2_and_writes_nothing(
    seeded: Factory, tmp_path: Path
) -> None:
    out = tmp_path / "b.json"
    assert cli_run(seeded, "--output", str(out)) == 2
    assert not out.exists()


def test_cli_with_allow_fake_writes_result_and_prints_summary(
    seeded: Factory, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "b.json"
    assert cli_run(seeded, "--allow-fake", "--output", str(out)) == 0
    doc = json.loads(out.read_text())
    documents = manifest_document_count()
    assert doc["document_count"] == documents
    assert doc["case_count"] == len(
        live_suite_rows(
            "golden_answerable",
            active_only=True,
            suite=LEGACY_SUITE,
        )
    )
    assert doc["random_hit_rate_formula"] == f"min(1, 5/{documents})"
    assert "not a quality measurement" in doc["notes"]
    shown = capsys.readouterr().out
    assert "HitRate@5" in shown and "random" in shown and "b.json" in shown
    assert str(tmp_path) not in shown
    assert cli_run(seeded, "--allow-fake", "--output", str(out)) == 2  # exists
    assert json.loads(out.read_text()) == doc


def test_cli_release_mismatch_and_bad_args_exit_2(
    seeded: Factory, tmp_path: Path
) -> None:
    out = tmp_path / "x.json"
    assert (
        cli_run(seeded, "--allow-fake", "--release", "nope", "--output", str(out)) == 2
    )
    assert cli_run(seeded, "--allow-fake", "--top-k", "0", "--output", str(out)) == 2
    assert not out.exists()
    assert seeded.calls == 0


def test_cli_parser_has_no_role_scope_or_tenant_option() -> None:
    options = {o for a in baseline_cli._parser()._actions for o in a.option_strings}
    assert not {"--role", "--scope", "--tenant", "--tenant-id"} & options


def test_summary_strips_control_characters(tmp_path: Path) -> None:
    index, emb, retriever = setup(tmp_path)
    doc = copy.deepcopy(run(index, emb, retriever).document)
    bad = "x\n9 forged \x1b[31mred\x1b[0m"
    doc["collection"] = bad
    doc["device"] = bad
    doc["index_settings"]["embedder_model_id"] = bad
    doc["notes"].append(bad)
    summary = baseline_cli.format_summary(
        BaselineResult(document=doc), tmp_path / f"{bad}.json", REPO_ROOT
    )
    assert "\x1b" not in summary
    assert not re.search(r"[\x00-\x09\x0b-\x1f\x7f]", summary)
    expected_lines = 7 + len(doc["notes"])
    assert len(summary.splitlines()) == expected_lines


def _git(repo: Path, *args: str) -> None:
    import subprocess

    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def test_git_state_ignores_only_untracked_result_files(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "experiments" / "results").mkdir(parents=True)
    (repo / "tracked.txt").write_text("a", encoding="utf-8")
    (repo / "experiments" / "results" / "old.json").write_text("{}", encoding="utf-8")
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "init")

    commit, dirty = git_state(repo)
    assert commit and dirty is False  # an untracked result file only

    (repo / "experiments" / "results" / "sub").mkdir()
    (repo / "experiments" / "results" / "sub" / "new.json").write_text(
        "{}", encoding="utf-8"
    )
    assert git_state(repo)[1] is False  # also in a new untracked folder

    (repo / "other.txt").write_text("x", encoding="utf-8")
    assert git_state(repo)[1] is True  # any other untracked file
    (repo / "other.txt").unlink()
    assert git_state(repo)[1] is False

    (repo / "tracked.txt").write_text("changed", encoding="utf-8")
    assert git_state(repo)[1] is True  # a tracked change
    _git(repo, "checkout", "--", "tracked.txt")

    _git(repo, "add", "-f", "experiments/results/old.json")
    assert git_state(repo)[1] is True  # a staged (tracked) result file
