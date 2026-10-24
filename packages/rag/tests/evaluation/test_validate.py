"""validate-evaluation tests (Spec 006 R2, R3, R14). Temp copies only."""

import asyncio
import json
import re
import shutil
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation import cli
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.suite import load_suite
from way2australia_rag.evaluation.validate import validate_evaluation
from way2australia_rag.repositories import (
    DocumentQuery,
    LocalDocumentRepository,
    LocalRepositoryConfig,
)

SUITE = "evaluation/suites/public-eval-v1.json"
GOLDEN = "evaluation/datasets/golden_public.jsonl"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    for name in ("evaluation", "knowledge"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def edit_suite(root: Path, change) -> None:  # noqa: ANN001
    path = root / SUITE
    raw = json.loads(path.read_text())
    change(raw)
    path.write_text(json.dumps(raw))


def edit_rows(root: Path, rel: str, change) -> None:  # noqa: ANN001
    path = root / rel
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    change(rows)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def run(root: Path, capsys) -> tuple[int, str]:  # noqa: ANN001
    code = cli.main(["validate", "--repo-root", str(root)])
    out = capsys.readouterr()
    return code, out.out + out.err


def test_current_repository_validates(capsys) -> None:  # noqa: ANN001
    code, out = run(REPO_ROOT, capsys)
    assert code == 0
    assert "OK, 0 problems" in out


def test_unknown_case_status(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[0].update(status="retired"))
    code, out = run(root, capsys)
    assert code == 1
    assert f"{GOLDEN}:1 g001 status" in out
    assert "retired" not in out


def test_case_missing_suite_id(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[2].pop("evaluation_suite_id"))
    code, out = run(root, capsys)
    assert code == 1
    assert f"{GOLDEN}:3 g003 evaluation_suite_id" in out


def test_manifest_missing_suite_id(root: Path, capsys) -> None:  # noqa: ANN001
    edit_suite(root, lambda r: r.pop("evaluation_suite_id"))
    code, out = run(root, capsys)
    assert code == 1
    assert f"{SUITE} evaluation_suite_id" in out


@pytest.mark.parametrize(
    ("label", "change", "field"),
    [
        ("missing status", lambda r: r.pop("status"), "status"),
        ("empty status", lambda r: r.update(status=""), "status"),
        (
            "missing release",
            lambda r: r.pop("introduced_in_release"),
            "introduced_in_release",
        ),
        ("missing case_count", lambda r: r.pop("case_count"), "case_count"),
        ("non-integer case_count", lambda r: r.update(case_count="85"), "case_count"),
    ],
)
def test_manifest_field_failures(root, capsys, label, change, field) -> None:  # noqa: ANN001
    edit_suite(root, change)
    code, out = run(root, capsys)
    assert code == 1, label
    assert f"{SUITE} {field}" in out


def test_active_golden_without_relevant_documents(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[0].update(relevant_document_ids=[]))
    code, out = run(root, capsys)
    assert code == 1
    assert f"{GOLDEN}:1 g001 relevant_document_ids" in out


def test_case_with_empty_suite_id(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[0].update(evaluation_suite_id=""))
    code, out = run(root, capsys)
    assert code == 1
    assert f"{GOLDEN}:1 g001 evaluation_suite_id" in out


def test_duplicate_case_id(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[1].update(case_id="g001"))
    code, out = run(root, capsys)
    assert code == 1
    assert "case_id: duplicate" in out


def test_suite_id_mismatch(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[0].update(evaluation_suite_id="other"))
    code, out = run(root, capsys)
    assert code == 1
    assert "does not match the suite manifest" in out


def test_case_count_mismatch(root: Path, capsys) -> None:  # noqa: ANN001
    declared = json.loads((root / SUITE).read_text())["case_count"]
    edit_suite(root, lambda r: r.update(case_count=declared - 1))
    code, out = run(root, capsys)
    assert code == 1
    assert f"declares {declared - 1} cases but the datasets hold {declared}" in out


def test_duplicate_dataset_path(root: Path, capsys) -> None:  # noqa: ANN001
    edit_suite(root, lambda r: r["datasets"].append(dict(r["datasets"][0])))
    code, out = run(root, capsys)
    assert code == 1
    assert "dataset path listed twice" in out


def test_unknown_document(root: Path, capsys) -> None:  # noqa: ANN001
    edit_rows(root, GOLDEN, lambda r: r[0].update(relevant_document_ids=["nope"]))
    code, out = run(root, capsys)
    assert code == 1
    assert "unknown document 'nope'" in out


def test_ineligible_document() -> None:
    config = LocalRepositoryConfig(repo_root=REPO_ROOT)
    real = LocalDocumentRepository(config)
    docs = asyncio.run(real.list_documents(DocumentQuery()))
    target = "business_001_overview_scope"

    class Stub:
        async def list_documents(self, query: Any = None) -> list[Any]:
            out = []
            for d in docs:
                if d.document_id == target:
                    d = d.model_copy(update={"retrieval_enabled": False})
                out.append(d)
            return [d for d in out if query is None or query.matches(d)]

    problems = validate_evaluation(REPO_ROOT, repository=Stub())  # type: ignore[arg-type]
    texts = [str(p) for p in problems]
    assert any(f"document '{target}' not eligible for guest/public" in t for t in texts)
    assert not any("unknown document" in t for t in texts)


def test_malformed_line_has_no_case_text(root: Path, capsys) -> None:  # noqa: ANN001
    path = root / GOLDEN
    path.write_text(path.read_text() + '{"query": "SECRET text\n')
    code, out = run(root, capsys)
    assert code == 1
    assert "line is not valid JSON" in out
    assert "SECRET" not in out
    assert str(root) not in out


def test_missing_schema_exits_2(root: Path, capsys) -> None:  # noqa: ANN001
    (root / "evaluation/schemas/evaluation_suite.schema.json").unlink()
    code, out = run(root, capsys)
    assert code == 2
    assert "EvaluationConfigurationError" in out


def test_invalid_corpus_exits_2(root: Path, capsys) -> None:  # noqa: ANN001
    (root / "knowledge/manifest/document_manifest.jsonl").write_text("not json\n")
    code, out = run(root, capsys)
    assert code == 2
    assert "make validate-knowledge" in out


# ---- candidates (R14) ----

CANDIDATE = {
    "candidate_id": "c1",
    "status": "suggested",
    "proposal_type": "new_case",
    "target_suite_id": "public-eval-v1",
    "proposed_by": "spec-006",
    "drafted_by": "agent",
    "requires_review": ["owner_review"],
    "needs_fluent_speaker_review": False,
    "rationale": "r",
    "proposed_case": {
        "case_id": "c1",
        "case_version": 1,
        "status": "suggested",
        "introduced_in_release": "seed-v1",
        "evaluation_suite_id": "public-eval-v1",
        "query": "q",
        "answerable": True,
        "relevant_document_ids": ["business_001_overview_scope"],
        "query_language": "en",
        "category": "business",
    },
}


def write_candidates(root: Path, *rows: dict[str, Any]) -> None:
    directory = root / "evaluation/candidates"
    directory.mkdir(exist_ok=True)
    (directory / "t.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_valid_candidate_passes(root: Path, capsys) -> None:  # noqa: ANN001
    write_candidates(root, CANDIDATE)
    assert run(root, capsys)[0] == 0


def test_candidate_not_suggested(root: Path, capsys) -> None:  # noqa: ANN001
    write_candidates(root, {**CANDIDATE, "status": "active"})
    code, out = run(root, capsys)
    assert code == 1
    assert "evaluation/candidates/t.jsonl:1 c1 status" in out


def test_candidate_unknown_and_ineligible_documents(root: Path, capsys) -> None:  # noqa: ANN001
    case = {**CANDIDATE["proposed_case"], "relevant_document_ids": ["nope"]}
    write_candidates(root, {**CANDIDATE, "proposed_case": case})
    code, out = run(root, capsys)
    assert code == 1
    assert "unknown document 'nope'" in out


def test_candidate_ineligible_document_is_not_unknown(root: Path) -> None:
    target = "business_001_overview_scope"
    write_candidates(root, CANDIDATE)
    real = LocalDocumentRepository(LocalRepositoryConfig(repo_root=root))
    docs = asyncio.run(real.list_documents(DocumentQuery()))

    class Stub:
        async def list_documents(self, query: Any = None) -> list[Any]:
            out = [
                d.model_copy(update={"retrieval_enabled": False})
                if d.document_id == target
                else d
                for d in docs
            ]
            return [d for d in out if query is None or query.matches(d)]

    problems = validate_evaluation(root, repository=Stub())  # type: ignore[arg-type]
    texts = [str(p) for p in problems if "candidates" in p.file]
    assert any(f"document '{target}' not eligible" in t for t in texts)
    assert not any("unknown document" in t for t in texts)


def test_suite_dataset_path_escaping_repository(root: Path, capsys) -> None:  # noqa: ANN001
    edit_suite(
        root,
        lambda r: r["datasets"].append(
            {"type": "golden_answerable", "path": "../outside.jsonl"}
        ),
    )
    code, out = run(root, capsys)
    assert code == 2
    assert "outside.jsonl" in out
    assert str(root) not in out
    assert str(root.parent) not in out


def test_candidate_referenced_by_suite(root: Path, capsys) -> None:  # noqa: ANN001
    write_candidates(root, CANDIDATE)
    edit_suite(
        root,
        lambda r: r["datasets"].append(
            {"type": "golden_answerable", "path": "evaluation/candidates/t.jsonl"}
        ),
    )
    code, out = run(root, capsys)
    assert code == 1
    assert "suite references a candidates file" in out


def test_non_default_language_needs_review_flags(root: Path, capsys) -> None:  # noqa: ANN001
    case = {**CANDIDATE["proposed_case"], "query_language": "xx"}
    write_candidates(root, {**CANDIDATE, "proposed_case": case})
    code, out = run(root, capsys)
    assert code == 1
    assert "needs_fluent_speaker_review" in out
    write_candidates(
        root,
        {
            **CANDIDATE,
            "proposed_case": case,
            "needs_fluent_speaker_review": True,
            "requires_review": ["fluent_speaker"],
        },
    )
    code, out = run(root, capsys)
    assert code == 1
    assert "requires_review" in out
    good = {
        **CANDIDATE,
        "proposed_case": case,
        "needs_fluent_speaker_review": True,
        "requires_review": ["fluent_speaker", "owner_review"],
    }
    write_candidates(root, good)
    assert run(root, capsys)[0] == 0


def test_case_change_candidate_rules(root: Path, capsys) -> None:  # noqa: ANN001
    row = {k: v for k, v in CANDIDATE.items() if k != "proposed_case"}
    row.update(proposal_type="case_change", target_case_ids=["g001"], options=["a"])
    write_candidates(root, row)
    assert run(root, capsys)[0] == 0
    row["target_case_ids"] = ["zzz"]
    write_candidates(root, row)
    code, out = run(root, capsys)
    assert code == 1
    assert "unknown case 'zzz'" in out
    row["target_case_ids"] = ["g001"]
    del row["options"]
    write_candidates(root, row)
    code, out = run(root, capsys)
    assert code == 1
    assert "options" in out
    assert "unknown case" not in out


def test_real_candidates_file_validates_and_is_not_loaded(capsys) -> None:  # noqa: ANN001
    path = REPO_ROOT / "evaluation/candidates/006-candidates.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    assert rows
    assert all(
        r["status"] == "suggested"
        and r["target_suite_id"] == "public-eval-v1"
        and r["proposed_by"] == "spec-006"
        for r in rows
    )
    assert all("relevant_section_ids" not in r.get("proposed_case", {}) for r in rows)
    code, out = run(REPO_ROOT, capsys)
    assert code == 0, out
    loaded = load_suite(REPO_ROOT, SUITE)
    every = (*loaded.goldens, *loaded.unanswerable, *loaded.security)
    loaded_ids = {c.case_id for c in every}
    for r in rows:
        assert r["candidate_id"] not in loaded_ids
        if "proposed_case" in r:
            assert r["proposed_case"]["case_id"] not in loaded_ids
    manifest = (REPO_ROOT / SUITE).read_text()
    assert "candidates" not in manifest
    declared = json.loads(manifest)["case_count"]
    assert len(every) == declared
    assert all(c.status != "suggested" for c in every)
    change = next(r for r in rows if r["candidate_id"] == "cand006_change_g004_u001")
    assert "owner_review" in change["requires_review"]


def test_no_language_literal_in_evaluation_code() -> None:
    src = REPO_ROOT / "packages/rag/src/way2australia_rag/evaluation"
    pattern = re.compile(r"""["']ml["']|\bml\b""")
    for path in src.glob("*.py"):
        assert not pattern.search(path.read_text()), path.name


def test_validation_is_read_only(root: Path) -> None:
    before = {
        p: p.read_bytes() for p in (root / "evaluation").rglob("*") if p.is_file()
    }
    validate_evaluation(root)
    after = {p: p.read_bytes() for p in (root / "evaluation").rglob("*") if p.is_file()}
    assert before == after


def test_unexpected_exception_prints_class_only(monkeypatch, capsys) -> None:  # noqa: ANN001
    def boom(_: Path) -> None:
        raise RuntimeError("SECRET")

    monkeypatch.setattr(cli, "validate_evaluation", boom)
    code, out = run(REPO_ROOT, capsys)
    assert code == 2
    assert "RuntimeError" in out
    assert "SECRET" not in out


def test_config_error_type() -> None:
    with pytest.raises(EvaluationConfigurationError):
        validate_evaluation(Path("/nonexistent-root-xyz"))
