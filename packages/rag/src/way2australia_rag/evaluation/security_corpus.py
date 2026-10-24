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


def build_security_repository(
    fixture_root: Path, work_dir: Path, *, schema_source: Path
) -> LocalDocumentRepository:
    """Copy the `*.md` fixtures under `fixture_root` into `work_dir` with a manifest.

    `schema_source` is the document metadata JSON Schema to validate against.
    """
    fixtures = sorted(fixture_root.glob("*.md"))
    if not fixtures:
        raise EvaluationConfigurationError("no security fixture documents were found.")
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
