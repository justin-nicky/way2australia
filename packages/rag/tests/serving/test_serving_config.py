"""`config/serving.yaml` loader and the cross-file budget check (Spec 013 R5-R10)."""

from pathlib import Path

import pytest
from conftest import REPO_ROOT
from generation.support import generation_config
from way2australia_rag.retrieval.strategy import load_retrieval_config
from way2australia_rag.serving.config import (
    ServingConfigurationError,
    load_serving_config,
)

COMMITTED = REPO_ROOT / "config/serving.yaml"


def _load(path: Path, provider: str | None = None):  # type: ignore[no-untyped-def]
    return load_serving_config(
        path,
        generation_config=generation_config(),
        retrieval_config=load_retrieval_config(REPO_ROOT / "config/retrieval.yaml"),
        generator_provider=provider,
    )


def _write(tmp_path: Path, **changes: str) -> Path:
    text = COMMITTED.read_text(encoding="utf-8")
    for old, new in changes.items():
        assert old in text
        text = text.replace(old, new)
    path = tmp_path / "serving.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_committed_file_loads() -> None:
    config = _load(COMMITTED)
    assert config.concurrency.max_in_flight == 4
    assert config.budget.request_s == 40


def test_unknown_key_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "s.yaml"
    path.write_text(COMMITTED.read_text() + "extra: 1\n", encoding="utf-8")
    with pytest.raises(ServingConfigurationError, match="extra"):
        _load(path)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("max_query_chars: 1000", "max_query_chars: 0"),
        ("max_body_bytes: 16384", "max_body_bytes: 10"),
        ("max_in_flight: 4", "max_in_flight: 65"),
        ("failure_threshold: 3", "failure_threshold: 21"),
        ("cooldown_s: 30", "cooldown_s: 0"),
        ("max_in_flight: 4", "max_in_flight: true"),
    ],
)
def test_out_of_range_values_are_refused(tmp_path: Path, old: str, new: str) -> None:
    with pytest.raises(ServingConfigurationError, match="check"):
        _load(_write(tmp_path, **{old: new}))


def test_budget_below_deadline_plus_timeout_plus_minimum_is_refused(
    tmp_path: Path,
) -> None:
    # 30 + 3 + 2 = 35 > 34
    path = _write(tmp_path, **{"request_s: 40": "request_s: 34"})
    with pytest.raises(ServingConfigurationError, match="budget.request_s") as raised:
        _load(path)
    assert str(tmp_path) not in str(raised.value)


def test_budget_at_the_minimum_is_accepted_and_fake_needs_no_deadline(
    tmp_path: Path,
) -> None:
    assert _load(_write(tmp_path, **{"request_s: 40": "request_s: 35"}))
    assert _load(_write(tmp_path, **{"request_s: 40": "request_s: 6"}), "fake")


def test_unreadable_and_non_mapping_files(tmp_path: Path) -> None:
    with pytest.raises(ServingConfigurationError, match="cannot read"):
        _load(tmp_path / "missing.yaml")
    bad = tmp_path / "list.yaml"
    bad.write_text("- 1\n", encoding="utf-8")
    with pytest.raises(ServingConfigurationError, match="mapping"):
        _load(bad)
