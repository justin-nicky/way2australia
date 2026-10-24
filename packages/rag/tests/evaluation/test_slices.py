"""Slice keys, small_sample and absent languages (Spec 006 R5)."""

import json
import re
from pathlib import Path

import pytest
from conftest import REPO_ROOT
from way2australia_rag.evaluation.errors import EvaluationConfigurationError
from way2australia_rag.evaluation.slices import (
    SMALL_SAMPLE_THRESHOLD,
    absent_query_languages,
    active_registry_languages,
    aggregate,
    slice_by,
    source_authority_key,
)

AUTH = {"a": "owner_approved", "b": "naati", "c": "naati"}


def row(lang: str, hit: bool, rr: float, **extra: object) -> dict:
    return {
        "query_language": lang,
        "category": "x",
        "hit": hit,
        "recall": 1.0 if hit else 0.0,
        "reciprocal_rank": rr,
        **extra,
    }


def test_source_authority_key_is_sorted_and_joined() -> None:
    assert source_authority_key(["a"], AUTH) == "owner_approved"
    assert source_authority_key(["b", "c"], AUTH) == "naati"
    assert source_authority_key(["a", "b"], AUTH) == "naati+owner_approved"
    assert source_authority_key(["b", "a"], AUTH) == "naati+owner_approved"
    assert source_authority_key(["zzz"], AUTH) == "unknown"


def test_small_sample_threshold_is_ten() -> None:
    assert SMALL_SAMPLE_THRESHOLD == 10
    nine = aggregate([row("en", True, 1.0)] * 9, 5)
    ten = aggregate([row("en", True, 1.0)] * 10, 5)
    assert nine["small_sample"] is True and nine["n"] == 9
    assert ten["small_sample"] is False


def test_slice_keys_come_from_data_and_carry_n() -> None:
    rows = [row("en", True, 1.0), row("zz", False, 0.0), row("en", False, 0.0)]
    sliced = slice_by(rows, "query_language", 5)
    assert list(sliced) == ["en", "zz"]
    assert sliced["en"]["n"] == 2 and sliced["en"]["hit_rate_at_5"] == 0.5
    assert sliced["zz"]["small_sample"] is True


def test_absent_languages_from_a_temp_registry(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    registry = {
        "product_support": {
            "one": {"internal_code": "x1", "status": "active"},
            "two": {"internal_code": "x2", "status": "planned"},
            "three": {"internal_code": "x3", "status": "active"},
        }
    }
    (tmp_path / "config/language_registry.json").write_text(json.dumps(registry))
    languages = active_registry_languages(tmp_path)
    assert languages == ["en", "x1", "x3"]
    assert absent_query_languages(languages, ["en", "x3"]) == ["x1"]


def test_missing_registry_section_is_a_configuration_error(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config/language_registry.json").write_text("{}")
    with pytest.raises(EvaluationConfigurationError):
        active_registry_languages(tmp_path)


def test_real_registry_lists_en_and_the_active_product_language() -> None:
    languages = active_registry_languages(REPO_ROOT)
    assert "en" in languages and len(languages) >= 2


def test_no_language_literal_in_evaluation_code() -> None:
    source = REPO_ROOT / "packages/rag/src/way2australia_rag/evaluation"
    for path in source.glob("*.py"):
        text = path.read_text()
        assert not re.search(r"\bml\b|malayalam", text, re.IGNORECASE), path.name
