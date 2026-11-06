"""The offline/empty-cache test setup and its smoke opt-outs (Spec 011 T1)."""

import os

import pytest
from conftest import HUB_OPT_OUT_VARIABLES, apply_hub_offline_empty_cache


def _clear_opt_outs(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in HUB_OPT_OUT_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)


def test_offline_setup_applied_when_no_opt_out_is_set(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_opt_outs(monkeypatch)
    assert apply_hub_offline_empty_cache(monkeypatch) is True
    assert os.environ["HF_HUB_OFFLINE"] == "1"


@pytest.mark.parametrize("variable", HUB_OPT_OUT_VARIABLES)
def test_each_opt_out_alone_lifts_the_offline_setup(
    monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    _clear_opt_outs(monkeypatch)
    monkeypatch.setenv(variable, "1")
    assert apply_hub_offline_empty_cache(monkeypatch) is False
    assert "HF_HUB_OFFLINE" not in os.environ
