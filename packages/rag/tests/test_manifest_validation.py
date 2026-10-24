import json
from pathlib import Path
from typing import Any

import pytest
from conftest import manifest_document_count
from way2australia_rag.repositories import (
    DuplicateDocumentError,
    ManifestValidationError,
    load_manifest,
    validate_manifest,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_body_sha256, sha256_hex
from way2australia_rag.repositories.manifest import load_schema

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = REPO_ROOT / "knowledge/schemas/document_metadata.schema.json"
SEED_MANIFEST = REPO_ROOT / "knowledge/manifest/document_manifest.jsonl"


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
    }
    base.update(overrides)
    return base


def write_doc(root: Path, meta: dict[str, Any], rel: str = "knowledge/a.md") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    front = "\n".join(f"{k}: {json.dumps(v)}" for k, v in meta.items())
    path.write_text(f"---\n{front}\n---\n\nBody text.\n", encoding="utf-8")


def write_manifest(root: Path, records: list[dict[str, Any]]) -> Path:
    path = root / "manifest.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return path


def record(root: Path | None = None, **overrides: Any) -> dict[str, Any]:
    """Manifest record; hashes are real when the file already exists under `root`."""
    sha, body_sha = "0" * 64, "1" * 64
    if root is not None and (root / "knowledge/a.md").is_file():
        raw = (root / "knowledge/a.md").read_bytes()
        sha = sha256_hex(raw)
        body_sha = compute_body_sha256(split_frontmatter(raw.decode("utf-8"))[1])
    rec = metadata(path="knowledge/a.md", sha256=sha, body_sha256=body_sha)
    rec.update(overrides)
    return rec


def run(root: Path, records: list[dict[str, Any]]) -> list[str]:
    manifest = write_manifest(root, records)
    return [str(p) for p in validate_manifest(manifest, root, SCHEMA)]


def test_seed_manifest_loads_and_validates() -> None:
    entries = load_manifest(SEED_MANIFEST, load_schema(SCHEMA))
    assert len(entries) == manifest_document_count()
    assert validate_manifest(SEED_MANIFEST, REPO_ROOT, SCHEMA) == []


def test_valid_manifest_loads(tmp_path: Path) -> None:
    write_doc(tmp_path, metadata())
    assert run(tmp_path, [record(tmp_path)]) == []


def test_duplicate_document_id_rejected(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, [record(), record(document_version=2)])
    with pytest.raises(DuplicateDocumentError) as exc:
        load_manifest(manifest, load_schema(SCHEMA))
    assert exc.value.document_id == "doc_a"
    assert exc.value.version is None


def test_duplicate_document_version_rejected(tmp_path: Path) -> None:
    manifest = write_manifest(tmp_path, [record(), record()])
    with pytest.raises(DuplicateDocumentError) as exc:
        load_manifest(manifest, load_schema(SCHEMA))
    assert (exc.value.document_id, exc.value.version) == ("doc_a", 1)


def test_missing_referenced_file_detected(tmp_path: Path) -> None:
    problems = run(tmp_path, [record()])
    assert len(problems) == 1
    assert problems[0].startswith("doc_a: path: referenced file does not exist")
    assert str(tmp_path) not in problems[0]


def test_manifest_frontmatter_mismatch_reported(tmp_path: Path) -> None:
    write_doc(tmp_path, metadata(access_scope="staff"))
    problems = run(tmp_path, [record(tmp_path)])
    assert problems == [
        "doc_a: access_scope: manifest has 'public' but frontmatter has 'staff'"
    ]


def test_frontmatter_schema_violation_names_document_and_field(tmp_path: Path) -> None:
    meta = metadata(document_version="one")
    write_doc(tmp_path, meta)
    problems = run(tmp_path, [record()])
    assert len(problems) == 1
    assert problems[0].startswith("doc_a: document_version:")


def test_frontmatter_missing_required_field(tmp_path: Path) -> None:
    meta = metadata()
    del meta["tenant_id"]
    write_doc(tmp_path, meta)
    assert "doc_a: tenant_id: required field is missing" in run(tmp_path, [record()])


def test_manifest_record_schema_violation_is_actionable(tmp_path: Path) -> None:
    rec = record()
    del rec["introduced_in_release"]
    manifest = write_manifest(tmp_path, [rec])
    with pytest.raises(ManifestValidationError, match="doc_a: introduced_in_release"):
        load_manifest(manifest, load_schema(SCHEMA))


def test_manifest_missing_bookkeeping_and_unsafe_path(tmp_path: Path) -> None:
    rec = record(path="../outside.md")
    del rec["sha256"]
    manifest = write_manifest(tmp_path, [rec])
    with pytest.raises(ManifestValidationError) as exc:
        load_manifest(manifest, load_schema(SCHEMA))
    assert "doc_a: sha256: required field is missing" in str(exc.value)
    assert "doc_a: path: must be a relative path" in str(exc.value)


def test_malformed_json_line_reports_line_number(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("{not json}\n", encoding="utf-8")
    with pytest.raises(ManifestValidationError, match="line 1"):
        load_manifest(manifest, load_schema(SCHEMA))


def test_missing_manifest_file(tmp_path: Path) -> None:
    with pytest.raises(ManifestValidationError, match="cannot read manifest"):
        load_manifest(tmp_path / "nope.jsonl", load_schema(SCHEMA))


def test_frontmatter_parsing_keeps_dates_as_strings() -> None:
    meta, body = split_frontmatter('---\nd: 2026-10-09\nx: "a"\n---\nhello\n')
    assert meta == {"d": "2026-10-09", "x": "a"}
    assert body == "hello\n"


@pytest.mark.parametrize("text", ["no frontmatter", "---\na: 1\n", "---\n- a\n---\n"])
def test_frontmatter_errors(text: str) -> None:
    with pytest.raises(ValueError):
        split_frontmatter(text)


def test_nested_required_violation_keeps_parent_path() -> None:
    from jsonschema import Draft202012Validator
    from way2australia_rag.repositories.manifest import schema_problems

    schema = {
        "type": "object",
        "properties": {
            "outer": {"type": "object", "required": ["inner"]},
        },
    }
    problems = schema_problems(Draft202012Validator(schema), {"outer": {}}, "doc_a")
    assert [str(p) for p in problems] == [
        "doc_a: outer.inner: required field is missing"
    ]
