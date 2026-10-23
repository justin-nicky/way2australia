"""Characterization of legacy `make retrieval-baseline` (Spec 006 R12).

Runs the legacy CLI (`baseline_cli.main`) against a frozen miniature repository
(`fixtures/legacy_baseline_repo/`: 13 seed documents, manifest, a small fixed
golden suite) with the fake embedder, in-memory Qdrant, a fixed clock, a patched
git state and deterministic timers. The written JSON and the printed summary are
compared byte-for-byte with committed snapshots generated from the unmodified
Spec 005 code.

Nothing here reads live `knowledge/`, `evaluation/` or `config/`, so the test
fails only when legacy code behavior changes, never when approved data changes.
The fixture copy must never be refreshed (see its README).
"""

import builtins
import io
import itertools
import shutil
from collections.abc import Callable, Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from qdrant_client import QdrantClient
from way2australia_rag.ingestion import cli as ingestion_cli
from way2australia_rag.ingestion.config import RuntimeSettings
from way2australia_rag.retrieval import baseline, baseline_cli, retriever

pytestmark = pytest.mark.filterwarnings(
    "ignore:Payload indexes have no effect:UserWarning"
)

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE_ROOT = FIXTURES / "legacy_baseline_repo"
SNAPSHOT = FIXTURES / "legacy_baseline_snapshot.json"
SUMMARY = FIXTURES / "legacy_baseline_summary.txt"
FIXED_NOW = datetime(2026, 10, 23, 12, 0, 0, tzinfo=UTC)
LIVE_DIRS = tuple(
    (REPO_ROOT / name).resolve() for name in ("knowledge", "evaluation", "config")
)
DATA_SUFFIXES = {".md", ".json", ".jsonl", ".yaml", ".yml", ".csv"}


class _Factory:
    def __init__(self, client: QdrantClient) -> None:
        self.client = client

    def __call__(self, settings: RuntimeSettings) -> QdrantClient:
        return self.client


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz: Any = None) -> "_FixedDatetime":  # type: ignore[override]
        return cls.fromtimestamp(FIXED_NOW.timestamp(), tz)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    for name in (
        "QDRANT_URL",
        "QDRANT_API_KEY",
        "QDRANT_COLLECTION_BASE",
        "W2A_TENANT_ID",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)  # no stray .env


def run_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    root: Path,
    out_dir: Path,
    capsys: pytest.CaptureFixture[str],
) -> tuple[str, str]:
    """(result JSON text as written, printed summary) for a legacy run over `root`."""
    ticks = itertools.count()
    monkeypatch.setattr(baseline, "perf_counter", lambda: next(ticks) * 0.001)
    monkeypatch.setattr(retriever, "perf_counter", lambda: next(ticks) * 0.001)
    monkeypatch.setattr(baseline, "git_state", lambda _root: ("0" * 40, False))
    monkeypatch.setattr(baseline_cli, "datetime", _FixedDatetime)

    client = QdrantClient(":memory:")
    factory = _Factory(client)
    config = str(root / "config/ingestion.yaml")
    ingest = ["--repo-root", str(root), "--config", config, "--embedder", "fake"]
    assert ingestion_cli.main(ingest, client_factory=factory) == 0
    capsys.readouterr()

    output = out_dir / "legacy-result.json"
    argv = [
        "--repo-root",
        str(root),
        "--config",
        config,
        "--suite",
        "evaluation/suites/legacy-fixture-suite.json",
        "--embedder",
        "fake",
        "--allow-fake",
        "--output",
        str(output),
    ]
    assert baseline_cli.main(argv, client_factory=factory) == 0
    summary = capsys.readouterr().out.rstrip("\n")
    return output.read_text(encoding="utf-8"), summary


def test_legacy_result_json_matches_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    text, _summary = run_snapshot(monkeypatch, FIXTURE_ROOT, tmp_path, capsys)
    assert text == SNAPSHOT.read_text(encoding="utf-8")


def test_legacy_summary_matches_snapshot(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _text, summary = run_snapshot(monkeypatch, FIXTURE_ROOT, tmp_path, capsys)
    assert summary == SUMMARY.read_text(encoding="utf-8").rstrip("\n")


def _record_opens(monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    seen: list[Path] = []

    def note(target: object) -> None:
        if isinstance(target, (str, bytes, Path)) or hasattr(target, "__fspath__"):
            try:
                seen.append(
                    Path(
                        str(target)
                        if not isinstance(target, bytes)
                        else target.decode()
                    ).resolve()
                )
            except (OSError, ValueError):
                pass

    real_open = builtins.open
    real_io_open = io.open
    real_path_open = Path.open
    real_read_text = Path.read_text
    real_read_bytes = Path.read_bytes

    def wrap_func(real: Callable[..., Any]) -> Callable[..., Any]:
        def inner(file: Any, *args: Any, **kwargs: Any) -> Any:
            note(file)
            return real(file, *args, **kwargs)

        return inner

    def wrap_method(real: Callable[..., Any]) -> Callable[..., Any]:
        def inner(self: Path, *args: Any, **kwargs: Any) -> Any:
            note(self)
            return real(self, *args, **kwargs)

        return inner

    monkeypatch.setattr(builtins, "open", wrap_func(real_open))
    monkeypatch.setattr(io, "open", wrap_func(real_io_open))
    monkeypatch.setattr(Path, "open", wrap_method(real_path_open))
    monkeypatch.setattr(Path, "read_text", wrap_method(real_read_text))
    monkeypatch.setattr(Path, "read_bytes", wrap_method(real_read_bytes))
    return seen


def _repo_data_paths(paths: list[Path]) -> Iterator[Path]:
    for path in paths:
        if (
            path.suffix in DATA_SUFFIXES
            and path.is_relative_to(REPO_ROOT)
            and ".venv" not in path.parts
        ):
            yield path


def test_snapshot_run_never_opens_live_data(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seen = _record_opens(monkeypatch)
    text, _summary = run_snapshot(monkeypatch, FIXTURE_ROOT, tmp_path, capsys)
    monkeypatch.undo()  # restore open() before assertions touch files
    assert text == SNAPSHOT.read_text(encoding="utf-8")
    assert seen, "the recorder saw no file opens"
    fixture = FIXTURE_ROOT.resolve()
    for path in seen:
        for live in LIVE_DIRS:
            assert not path.is_relative_to(live), "live data was opened"
    repo_data = list(_repo_data_paths(seen))
    assert repo_data
    for path in repo_data:
        assert path.is_relative_to(fixture), "a data file outside the fixture was read"
    # The documents, manifest, schema, release and suite all came from the copy.
    names = {p.name for p in repo_data}
    assert {
        "document_manifest.jsonl",
        "golden_fixture.jsonl",
        "ingestion.yaml",
    } <= names


def test_snapshot_is_independent_of_location(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    copy_root = tmp_path / "elsewhere" / "legacy_baseline_repo"
    shutil.copytree(FIXTURE_ROOT, copy_root)
    out = tmp_path / "out"
    out.mkdir()
    text, summary = run_snapshot(monkeypatch, copy_root, out, capsys)
    assert text == SNAPSHOT.read_text(encoding="utf-8")
    assert summary == SUMMARY.read_text(encoding="utf-8").rstrip("\n")
