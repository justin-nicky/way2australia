"""FakeReranker determinism and hooks (Spec 011 R1)."""

import math

import pytest
from way2australia_rag.rerank.base import Reranker
from way2australia_rag.rerank.errors import RerankerUnavailableError
from way2australia_rag.rerank.fake import FakeReranker

TEXTS = ["alpha beta", "gamma", "delta epsilon zeta"]


def test_scores_are_deterministic_and_per_text_in_order() -> None:
    first = FakeReranker().score("q", TEXTS)
    second = FakeReranker().score("q", TEXTS)
    assert first.scores == second.scores
    assert len(first.scores) == len(TEXTS)
    assert all(math.isfinite(s) for s in first.scores)
    assert FakeReranker().score("other", TEXTS).scores != first.scores


def test_score_depends_on_the_text_only_through_its_content() -> None:
    reranker = FakeReranker()
    single = reranker.score("q", ["gamma"]).scores[0]
    assert reranker.score("q", TEXTS).scores[1] == single


def test_it_satisfies_the_protocol_and_reports_identity() -> None:
    reranker: Reranker = FakeReranker(max_length=64)
    assert reranker.info.is_fake is True
    assert reranker.info.max_length == 64
    assert reranker.device is None
    reranker.load()
    reranker.load()
    assert reranker.device == "fake"


def test_prefer_scores_chosen_texts_highest() -> None:
    reranker = FakeReranker(prefer=lambda text: text == "gamma")
    scores = reranker.score("q", TEXTS).scores
    assert scores.index(max(scores)) == 1


def test_fail_on_load() -> None:
    with pytest.raises(RerankerUnavailableError):
        FakeReranker(fail_on_load=True).load()


def test_fail_on_call_fails_only_that_call() -> None:
    reranker = FakeReranker(fail_on_call=2)
    reranker.score("q", TEXTS)
    with pytest.raises(RerankerUnavailableError):
        reranker.score("q", TEXTS)
    assert len(reranker.score("q", TEXTS).scores) == len(TEXTS)


def test_malformed_count_and_nan() -> None:
    assert len(FakeReranker(malformed="count").score("q", TEXTS).scores) == 2
    assert math.isnan(FakeReranker(malformed="nan").score("q", TEXTS).scores[0])


def test_truncation_counts_whitespace_tokens_against_max_length() -> None:
    reranker = FakeReranker(max_length=3)
    assert reranker.score("one", TEXTS).truncated_pairs == 1  # 1 + 3 > 3
    assert reranker.score("one two", TEXTS).truncated_pairs == 2  # 2+2, 2+3
