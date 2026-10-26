"""`make index-lexical` CLI tests (Spec 007 R4). No Qdrant client, no model."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import qdrant_client
from conftest import REPO_ROOT
from way2australia_rag.ingestion import bge_m3
from way2australia_rag.ingestion.bge_m3 import BgeM3Embedder
from way2australia_rag.ingestion.config import RuntimeSettings, load_ingestion_config
from way2australia_rag.lexical.build import default_lexical_dir
from way2australia_rag.lexical.cli import (
    LexicalTargetRefusedError,
    check_target_allowed,
    embedder_identity,
    main,
)
from way2australia_rag.lexical.store import LexicalIndex


@pytest.fixture(autouse=True)
def _no_qdrant(monkeypatch: pytest.MonkeyPatch) -> None:
    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("a Qdrant client must not be constructed")

    monkeypatch.setattr(qdrant_client.QdrantClient, "__init__", forbidden)


@pytest.fixture
def lexical_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    directory = tmp_path / "lexdir"
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "w2a-t007-abcd1234")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(directory))
    return directory


def run(args: list[str]) -> int:
    return main(["--repo-root", str(REPO_ROOT), *args])


def test_success_summary_and_digest_stability(
    lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--embedder", "fake"]) == 0
    first = capsys.readouterr()
    pattern = (
        r"^lexical index: w2a-t007-abcd1234-idx-v1\.sqlite "
        r"\(collection w2a-t007-abcd1234-idx-v1, index_version idx-v1; "
        r"lexical-v1; chunks \d+; digest [0-9a-f]{12}\)$"
    )
    assert re.match(pattern, first.out.strip()), first.out
    assert str(tmp_root := lexical_dir.parent) not in first.out + first.err
    assert str(REPO_ROOT) not in first.out + first.err
    assert tmp_root.exists()
    assert (lexical_dir / "w2a-t007-abcd1234-idx-v1.sqlite").is_file()

    assert run(["--embedder", "fake"]) == 0
    second = capsys.readouterr()
    assert second.out == first.out  # same digest, same line


def test_file_holds_the_identity_and_no_chunk_text_is_printed(
    lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--embedder", "fake"]) == 0
    out = capsys.readouterr()
    path = lexical_dir / "w2a-t007-abcd1234-idx-v1.sqlite"
    index = LexicalIndex.open(path, "w2a-t007-abcd1234-idx-v1", "idx-v1")
    assert index.settings.dense_identity.embedder_model_id == "fake-hash-embedder"
    rows = index.search('"naati"', "c.tenant_id = ?", ("way2australia",), 1)
    index.close()
    assert rows
    assert "naati" not in (out.out + out.err).lower().replace("w2a-t007", "")


def test_output_option_and_relative_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("W2A_LEXICAL_INDEX_DIR", raising=False)
    target = tmp_path / "custom.sqlite"
    assert run(["--embedder", "fake", "--output", str(target)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("lexical index: custom.sqlite (")  # outside repo: name only
    assert target.is_file()


def test_bad_config_exits_2(
    lexical_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("schema_version: '9'\n", encoding="utf-8")
    assert run(["--config", str(bad)]) == 2
    captured = capsys.readouterr()
    assert captured.err.startswith("ERROR IngestionConfigurationError")
    assert captured.out == ""
    assert str(tmp_path) not in captured.err
    assert not lexical_dir.exists()


def test_missing_config_exits_2(
    lexical_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--config", str(tmp_path / "missing.yaml")]) == 2
    assert "ERROR" in capsys.readouterr().err


def test_runtime_setting_defaults_and_blank(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("W2A_LEXICAL_INDEX_DIR", raising=False)
    assert RuntimeSettings(_env_file=None).lexical_index_dir is None  # type: ignore[call-arg]
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", "  ")
    assert RuntimeSettings(_env_file=None).lexical_index_dir is None  # type: ignore[call-arg]
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", "/somewhere")
    settings = RuntimeSettings(_env_file=None)  # type: ignore[call-arg]
    assert settings.lexical_index_dir == Path("/somewhere")
    assert default_lexical_dir(Path("/r")) == Path("/r/.local/lexical")


def test_lexical_location_is_git_ignored() -> None:
    lines = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "/.local/lexical/" in lines


def test_default_embedder_identity_equals_the_bge_m3_adapter_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # The constructor only checks that the optional extra is installed; it never
    # loads the model (lazy), so the extra is not needed for this test.
    monkeypatch.setattr(bge_m3, "_group_installed", lambda: True)
    config = load_ingestion_config(REPO_ROOT / "config" / "ingestion.yaml")
    info = BgeM3Embedder(config.embedder.revision).info  # lazy: no model load
    assert embedder_identity(config, "bge_m3") == (info.model_id, info.revision)


@pytest.mark.parametrize("name", ["knowledge", "evaluation", "config"])
def test_output_under_protected_directory_is_refused(
    name: str, lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = REPO_ROOT / name / "never-written.sqlite"
    assert run(["--embedder", "fake", "--output", str(target)]) == 2
    assert "ERROR LexicalTargetRefusedError" in capsys.readouterr().err
    assert not target.exists()


def test_relative_output_into_protected_directory_is_refused(
    lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--embedder", "fake", "--output", "knowledge/x.sqlite"]) == 2
    assert "LexicalTargetRefusedError" in capsys.readouterr().err
    assert not (REPO_ROOT / "knowledge" / "x.sqlite").exists()


def test_env_dir_into_tracked_directory_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "w2a-t007-abcd1234")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", str(REPO_ROOT / "packages"))
    assert run(["--embedder", "fake"]) == 2
    assert "LexicalTargetRefusedError" in capsys.readouterr().err


def test_repo_root_itself_is_refused(
    lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(["--embedder", "fake", "--output", str(REPO_ROOT / "x.sqlite")]) == 2
    assert not (REPO_ROOT / "x.sqlite").exists()


def test_tracked_directory_in_a_temp_git_repo_is_refused(
    tmp_path: Path, lexical_dir: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "data").mkdir(parents=True)
    (repo / "data" / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    with pytest.raises(LexicalTargetRefusedError):
        check_target_allowed(repo / "data" / "i.sqlite", repo)
    (repo / "fresh").mkdir()  # no tracked files here
    check_target_allowed(repo / "fresh" / "i.sqlite", repo)


def test_default_location_is_allowed() -> None:
    check_target_allowed(default_lexical_dir(REPO_ROOT) / "x.sqlite", REPO_ROOT)


def _git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "gitrepo"
    for name in ("knowledge", "docs"):
        (repo / name).mkdir(parents=True)
        (repo / name / "a.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    return repo


def test_new_subfolder_in_protected_or_tracked_tree_is_refused(
    tmp_path: Path,
) -> None:
    repo = _git_repo(tmp_path)
    for rel in ("knowledge/new/sub/i.sqlite", "docs/new/i.sqlite", "new/i.sqlite"):
        with pytest.raises(LexicalTargetRefusedError):
            check_target_allowed(repo / rel, repo)
        assert not (repo / rel).parent.exists()


def test_differently_cased_protected_name_is_refused(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    cased = repo / "KNOWLEDGE"
    if not cased.exists():
        pytest.skip("case-sensitive filesystem: the spelling is a different folder")
    with pytest.raises(LexicalTargetRefusedError):
        check_target_allowed(cased / "newdir" / "i.sqlite", repo)


def test_cased_name_cannot_write_into_the_real_repository(
    lexical_dir: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    if not (REPO_ROOT / "Knowledge").exists():
        pytest.skip("case-sensitive filesystem")
    target = REPO_ROOT / "Knowledge" / "t3-never" / "x.sqlite"
    assert run(["--embedder", "fake", "--output", str(target)]) == 2
    assert not (REPO_ROOT / "knowledge" / "t3-never").exists()


def test_ignored_and_outside_targets_are_allowed(tmp_path: Path) -> None:
    repo = _git_repo(tmp_path)
    (repo / ".gitignore").write_text(".local/\n", encoding="utf-8")
    check_target_allowed(repo / ".local" / "lexical" / "i.sqlite", repo)
    check_target_allowed(tmp_path / "elsewhere" / "i.sqlite", repo)


def test_relative_output_resolves_against_repo_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("W2A_LEXICAL_INDEX_DIR", raising=False)
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "w2a-t007-abcd1234")
    out_dir = REPO_ROOT / ".local" / "lexical" / "t3-rel-output"
    try:
        code = main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "--embedder",
                "fake",
                "--output",
                ".local/lexical/t3-rel-output/r.sqlite",
            ]
        )
        assert code == 0, capsys.readouterr().err
        assert (out_dir / "r.sqlite").is_file()
        assert ".local/lexical/t3-rel-output/r.sqlite" in capsys.readouterr().out
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)


def test_relative_env_dir_resolves_against_repo_root(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("QDRANT_COLLECTION_BASE", "w2a-t007-abcd1234")
    monkeypatch.setenv("W2A_LEXICAL_INDEX_DIR", ".local/lexical/t3-rel-env")
    out_dir = REPO_ROOT / ".local" / "lexical" / "t3-rel-env"
    try:
        assert run(["--embedder", "fake"]) == 0, capsys.readouterr().err
        assert (out_dir / "w2a-t007-abcd1234-idx-v1.sqlite").is_file()
    finally:
        shutil.rmtree(out_dir, ignore_errors=True)
