"""classify_reranker_error table (Spec 011 R1, R5)."""

import httpx
import pytest
from huggingface_hub.errors import (
    HfHubHTTPError,
    LocalEntryNotFoundError,
    OfflineModeIsEnabled,
)
from way2australia_rag.rerank.errors import (
    RerankerUnavailableError,
    RerankSkipReason,
    classify_reranker_error,
)
from way2australia_rag.retrieval.availability import (
    MAX_CAUSE_LINKS,
    classify_model_error,
)
from way2australia_rag.retrieval.errors import RetrievalUnavailableError


def caused_by(outer: BaseException, cause: BaseException) -> BaseException:
    outer.__cause__ = cause
    return outer


def reason(error: BaseException) -> RerankSkipReason | None:
    result = classify_reranker_error(error)
    return None if result is None else result.reason


def test_unavailable_is_not_a_retrieval_unavailable_error() -> None:
    assert not issubclass(RerankerUnavailableError, RetrievalUnavailableError)
    assert RerankerUnavailableError(RerankSkipReason.MODEL_TIMEOUT).reason is (
        RerankSkipReason.MODEL_TIMEOUT
    )


def test_reasons_are_the_closed_set() -> None:
    assert {m.value for m in RerankSkipReason} == {
        "model_unavailable",
        "model_timeout",
    }


@pytest.mark.parametrize(
    "error",
    [
        caused_by(OSError("connect"), httpx.ConnectError("refused")),
        caused_by(OSError("down"), ConnectionError("down")),
        httpx.ReadError("raw"),
    ],
    ids=["connect", "connection", "raw"],
)
def test_network_cause_is_model_unavailable(error: BaseException) -> None:
    assert reason(error) is RerankSkipReason.MODEL_UNAVAILABLE


@pytest.mark.parametrize(
    "error",
    [
        caused_by(OSError("slow"), httpx.ReadTimeout("slow")),
        caused_by(OSError("slow"), TimeoutError("slow")),
    ],
    ids=["httpx", "builtin"],
)
def test_timeout_cause_is_model_timeout(error: BaseException) -> None:
    assert reason(error) is RerankSkipReason.MODEL_TIMEOUT


def test_context_is_never_followed() -> None:
    try:
        try:
            raise httpx.ConnectError("refused")
        except httpx.ConnectError:
            raise ValueError("unrelated") from None
    except ValueError as error:
        assert error.__context__ is not None
        assert classify_reranker_error(error) is None


def test_chain_walk_is_bounded() -> None:
    error: BaseException = httpx.ConnectError("deep")
    for _ in range(MAX_CAUSE_LINKS):
        error = caused_by(OSError("link"), error)
    assert classify_reranker_error(error) is None


def hub_5xx() -> BaseException:
    response = httpx.Response(503, request=httpx.Request("GET", "http://hub.invalid"))
    status = httpx.HTTPStatusError("503", request=response.request, response=response)
    return caused_by(HfHubHTTPError("503", response=response), status)


@pytest.mark.parametrize(
    "error",
    [
        caused_by(OSError("hub 5xx"), hub_5xx()),
        OSError("plain"),
        PermissionError("denied"),
        ValueError("x"),
    ],
    ids=["hub-5xx", "plain-oserror", "permission", "value-error"],
)
def test_other_errors_are_not_eligible(error: BaseException) -> None:
    assert classify_reranker_error(error) is None


@pytest.mark.parametrize("with_network", [False, True], ids=["alone", "with-network"])
@pytest.mark.parametrize(
    "offline", [LocalEntryNotFoundError("nothing cached"), OfflineModeIsEnabled("off")]
)
def test_offline_not_cached_is_excluded_even_with_a_network_error_below(
    offline: BaseException, with_network: bool
) -> None:
    if with_network:
        offline = caused_by(offline, httpx.ConnectError("refused"))
    assert classify_reranker_error(caused_by(OSError("load"), offline)) is None


def test_model_classifier_output_is_unchanged_for_local_entry_not_found() -> None:
    error = caused_by(LocalEntryNotFoundError("x"), httpx.ConnectError("refused"))
    assert classify_model_error(error) is not None


def test_an_existing_unavailable_error_is_returned_as_is() -> None:
    error = RerankerUnavailableError(RerankSkipReason.MODEL_TIMEOUT)
    assert classify_reranker_error(error) is error
