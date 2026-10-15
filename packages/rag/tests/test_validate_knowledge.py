import json
import shutil
from pathlib import Path
from typing import Any

import pytest
from way2australia_rag.repositories import LocalRepositoryConfig
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_body_sha256, sha256_hex
from way2australia_rag.repositories.validate import main, validate_knowledge

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "knowledge/schemas/document_metadata.schema.json"
MANIFEST_REL = "knowledge/manifest/document_manifest.jsonl"
DOC_REL = "knowledge/public/business/a.md"


def metadata(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema_version": "1.0",
        "document_id": "doc_a",
        "document_version": 1,
        "tenant_id": "way2australia",
        "title": "Doc A",
        "access_scope": "public",
        "source_authority": "owner_approved",
        "approval_status": "approved",
        "lifecycle_status": "active",
        "introduced_in_release": "seed-v1",
        "retrieval_enabled": True,
        "synthetic": False,
        "language_scope": "global",
        "lote_languages": ["*"],
        "content_language": "en",
        "knowledge_domain": "business_overview",
        "source_type": "owner_approved_knowledge_base",
    }
    base.update(overrides)
    return base


def write_doc(root: Path, meta: dict[str, Any], rel: str = DOC_REL) -> dict[str, Any]:
    """Write a document and return its manifest record with real hashes."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    front = "\n".join(f"{k}: {json.dumps(v)}" for k, v in meta.items())
    path.write_text(f"---\n{front}\n---\n\nBody text.\n", encoding="utf-8")
    raw = path.read_bytes()
    body = split_frontmatter(raw.decode("utf-8"))[1]
    record = dict(meta)
    record.update(
        path=rel, sha256=sha256_hex(raw), body_sha256=compute_body_sha256(body)
    )
    return record


def build_repo(root: Path, records: list[dict[str, Any]]) -> Path:
    schema = root / SCHEMA_REL
    schema.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(REPO_ROOT / SCHEMA_REL, schema)
    manifest = root / MANIFEST_REL
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )
    return root


def problems_for(root: Path) -> list[str]:
    return [str(p) for p in validate_knowledge(LocalRepositoryConfig(repo_root=root))]


def run_cli(root: Path, capsys: pytest.CaptureFixture[str]) -> tuple[int, str]:
    code = main(["--repo-root", str(root)])
    return code, capsys.readouterr().out


def test_seed_corpus_is_valid(capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run_cli(REPO_ROOT, capsys)
    assert code == 0
    assert "0 problems" in out


def test_valid_temporary_repository_exits_zero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata())])
    assert run_cli(tmp_path, capsys) == (0, "validate-knowledge: OK, 0 problems\n")


def test_duplicate_id_exits_one_with_document_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rec = write_doc(tmp_path, metadata())
    build_repo(tmp_path, [rec, {**rec, "document_version": 2}])
    code, out = run_cli(tmp_path, capsys)
    assert code == 1
    assert "ERROR doc_a: document_id:" in out
    assert "FAILED with 1 problem(s)" in out


def test_missing_file_exits_one_with_document_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rec = write_doc(tmp_path, metadata())
    (tmp_path / DOC_REL).unlink()
    build_repo(tmp_path, [rec])
    code, out = run_cli(tmp_path, capsys)
    assert code == 1
    assert "doc_a: path: referenced file does not exist" in out
    assert str(tmp_path) not in out


def test_schema_violation_exits_one_with_document_id_and_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    meta = metadata(access_scope="everyone")
    rec = write_doc(tmp_path, meta)
    build_repo(tmp_path, [rec])
    code, out = run_cli(tmp_path, capsys)
    assert code == 1
    assert "doc_a: access_scope:" in out


def test_hash_mismatch_exits_one_with_document_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rec = write_doc(tmp_path, metadata())
    with (tmp_path / DOC_REL).open("a", encoding="utf-8") as handle:
        handle.write("Edited after hashing.\n")
    build_repo(tmp_path, [rec])
    code, out = run_cli(tmp_path, capsys)
    assert code == 1
    assert "doc_a: sha256: manifest hash does not match" in out
    assert "doc_a: body_sha256: manifest hash does not match" in out


def test_every_problem_is_listed_with_count(tmp_path: Path) -> None:
    good = write_doc(tmp_path, metadata())
    bad = write_doc(
        tmp_path, metadata(document_id="doc_b"), "knowledge/public/business/b.md"
    )
    (tmp_path / "knowledge/public/business/b.md").unlink()
    build_repo(tmp_path, [good, bad])
    (tmp_path / "knowledge/public/business/c.md").write_text("x", encoding="utf-8")
    problems = problems_for(tmp_path)
    assert len(problems) == 2


def test_synthetic_retrievable_document_fails(tmp_path: Path) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata(synthetic=True))])
    assert "doc_a: synthetic: synthetic document is retrievable" in problems_for(
        tmp_path
    )


def test_unapproved_retrievable_document_fails(tmp_path: Path) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata(approval_status="draft"))])
    assert any(p.startswith("doc_a: approval_status:") for p in problems_for(tmp_path))


def test_non_public_document_in_public_corpus_fails(tmp_path: Path) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata(access_scope="staff"))])
    assert any(p.startswith("doc_a: access_scope:") for p in problems_for(tmp_path))


def test_disabled_synthetic_document_is_not_retrievable(tmp_path: Path) -> None:
    meta = metadata(synthetic=True, retrieval_enabled=False)
    build_repo(tmp_path, [write_doc(tmp_path, meta)])
    assert problems_for(tmp_path) == []


def test_entry_outside_approved_roots_is_reported(tmp_path: Path) -> None:
    rec = write_doc(tmp_path, metadata(), "tests/fixtures/security/a.md")
    build_repo(tmp_path, [rec])
    problems = problems_for(tmp_path)
    assert len(problems) == 1
    assert problems[0].startswith(
        "doc_a: path: tests/fixtures/security/a.md is outside"
    )


def test_unlisted_file_under_approved_root_is_reported(tmp_path: Path) -> None:
    build_repo(tmp_path, [write_doc(tmp_path, metadata())])
    stray = tmp_path / "knowledge/public/official/stray.md"
    stray.parent.mkdir(parents=True)
    stray.write_text("no frontmatter", encoding="utf-8")
    problems = problems_for(tmp_path)
    assert len(problems) == 1
    assert problems[0].startswith("knowledge/public/official/stray.md: path:")


def test_non_iso_effective_date_is_rejected(tmp_path: Path) -> None:
    meta = metadata(effective_from="2026-01-01T00:00:00")
    build_repo(tmp_path, [write_doc(tmp_path, meta)])
    assert "doc_a: effective_from: must be a YYYY-MM-DD date" in problems_for(tmp_path)


def test_impossible_effective_date_is_rejected(tmp_path: Path) -> None:
    meta = metadata(effective_to="2026-02-31")
    build_repo(tmp_path, [write_doc(tmp_path, meta)])
    assert "doc_a: effective_to: must be a YYYY-MM-DD date" in problems_for(tmp_path)


def test_all_model_errors_are_listed(tmp_path: Path) -> None:
    meta = metadata(lote_languages=[], language_scope="nonsense")
    build_repo(tmp_path, [write_doc(tmp_path, meta)])
    problems = problems_for(tmp_path)
    assert len([p for p in problems if p.startswith("doc_a:")]) == len(problems) >= 1


def test_missing_schema_file_is_reported(tmp_path: Path) -> None:
    problems = problems_for(tmp_path)
    assert len(problems) == 1
    assert "cannot load metadata schema" in problems[0]
    assert str(tmp_path) not in problems[0]
