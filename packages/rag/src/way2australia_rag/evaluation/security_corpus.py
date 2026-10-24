"""Isolated repository over the security fixtures (Spec 006 R8).

Moved from `tests/conftest.py`. The fixture root is an explicit parameter: no
fixture path is built into library code (the CLI owns the default). The result
is a throwaway repository root in `work_dir` holding only the fixtures, with a
generated manifest, so they load through `LocalDocumentRepository` and the JSON
Schema exactly like real documents. Security fixtures are never part of the
production corpus.
"""

import json
import shutil
from pathlib import Path

from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.repositories import (
    LocalDocumentRepository,
    LocalRepositoryConfig,
)
from way2australia_rag.repositories.frontmatter import split_frontmatter
from way2australia_rag.repositories.hashing import compute_body_sha256, sha256_hex

SCHEMA = "knowledge/schemas/document_metadata.schema.json"
ISOLATED_ROOT = "security_corpus"
SECURITY_FIXTURE_FILES = ("poisoned_public_document.md", "staff_only_canary.md")


def _fixture_files(fixture_root: Path) -> list[Path]:
    """The two expected fixtures; refuse anything else visible before any copy."""
    try:
        present = {p.name for p in fixture_root.iterdir() if not p.name.startswith(".")}
    except OSError as error:
        raise EvaluationConfigurationError(
            "the security fixture folder cannot be read."
        ) from error
    for name in SECURITY_FIXTURE_FILES:
        if name not in present:
            raise EvaluationConfigurationError(f"security fixture '{name}' is missing.")
    for name in sorted(present - set(SECURITY_FIXTURE_FILES)):
        raise EvaluationConfigurationError(
            f"unexpected entry '{name}' in the security fixture folder."
        )
    return [fixture_root / name for name in SECURITY_FIXTURE_FILES]


def build_security_repository(
    fixture_root: Path, work_dir: Path, *, schema_source: Path
) -> LocalDocumentRepository:
    """Copy the two named fixtures under `fixture_root` into `work_dir` with a manifest.

    Only `SECURITY_FIXTURE_FILES` are copied. Hidden (dot-prefixed) entries are
    ignored; any other visible entry, or a missing listed file, is refused before
    anything is copied. `schema_source` is the document metadata JSON Schema.
    """
    fixtures = _fixture_files(fixture_root)
    (work_dir / SCHEMA).parent.mkdir(parents=True)
    shutil.copy(schema_source, work_dir / SCHEMA)
    (work_dir / ISOLATED_ROOT).mkdir()
    records = []
    for fixture in fixtures:
        raw = fixture.read_bytes()
        (work_dir / ISOLATED_ROOT / fixture.name).write_bytes(raw)
        metadata, body = split_frontmatter(raw.decode("utf-8"))
        records.append(
            {
                **metadata,
                "path": f"{ISOLATED_ROOT}/{fixture.name}",
                "sha256": sha256_hex(raw),
                "body_sha256": compute_body_sha256(body),
            }
        )
    manifest = work_dir / "knowledge/manifest/document_manifest.jsonl"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8"
    )
    return LocalDocumentRepository(
        LocalRepositoryConfig(repo_root=work_dir, approved_roots=(ISOLATED_ROOT,))
    )
