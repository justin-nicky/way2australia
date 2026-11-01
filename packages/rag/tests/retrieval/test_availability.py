"""Failure classification tables (Spec 008 R1)."""

from typing import Any

import httpx
import pytest
from qdrant_client.http.exceptions import (
    ResponseHandlingException,
    UnexpectedResponse,
)
from way2australia_rag.ingestion.errors import OptionalDependencyError
from way2australia_rag.retrieval.availability import (
    MAX_CAUSE_LINKS,
    classify_model_error,
    classify_qdrant_error,
)
from way2australia_rag.retrieval.errors import (
    FallbackReason,
    RetrievalError,
    RetrievalUnavailableError,
)

REQUEST = httpx.Request("GET", "http://qdrant.invalid:6333/collections")


def caused_by(outer: BaseException, cause: BaseException) -> BaseException:
    """`outer` with an explicit `__cause__` (what `raise outer from cause` sets)."""
    outer.__cause__ = cause
    return outer


def reason(result: RetrievalUnavailableError | None) -> FallbackReason | None:
    return None if result is None else result.reason


# ---- the error type -------------------------------------------------------


@pytest.mark.parametrize("member", list(FallbackReason))
def test_unavailable_error_message_comes_from_the_reason_only(
    member: FallbackReason,
) -> None:
    error = RetrievalUnavailableError(member)
    assert isinstance(error, RetrievalError)
    assert error.reason is member
    assert member.value in str(error)
    assert "http" not in str(error) and "/" not in str(error)


def test_reasons_are_the_closed_set() -> None:
    assert {m.value for m in FallbackReason} == {
        "qdrant_unavailable",
        "qdrant_timeout",
        "model_unavailable",
    }


# ---- Qdrant ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (httpx.ConnectError("refused"), FallbackReason.QDRANT_UNAVAILABLE),
        (httpx.ReadError("reset"), FallbackReason.QDRANT_UNAVAILABLE),
        (httpx.ConnectTimeout("slow"), FallbackReason.QDRANT_TIMEOUT),
        (httpx.ReadTimeout("slow"), FallbackReason.QDRANT_TIMEOUT),
        (httpx.WriteTimeout("slow"), FallbackReason.QDRANT_TIMEOUT),
        (httpx.PoolTimeout("slow"), FallbackReason.QDRANT_TIMEOUT),
    ],
)
def test_transport_errors_are_eligible_bare_and_wrapped(
    error: Exception, expected: FallbackReason
) -> None:
    assert reason(classify_qdrant_error(error)) is expected
    assert reason(classify_qdrant_error(ResponseHandlingException(error))) is expected


@pytest.mark.parametrize(
    "error",
    [
        ResponseHandlingException(ValueError("bad body")),
        ResponseHandlingException(OSError("disk")),
        UnexpectedResponse(404, "Not Found", b"", httpx.Headers()),
        UnexpectedResponse(503, "Service Unavailable", b"", httpx.Headers()),
        ValueError("x"),
        OSError("x"),
        RuntimeError("x"),
    ],
)
def test_other_qdrant_errors_are_not_eligible(error: Exception) -> None:
    assert classify_qdrant_error(error) is None


def test_the_wrapper_is_unwrapped_one_level_only() -> None:
    inner = ResponseHandlingException(httpx.ConnectError("refused"))
    assert classify_qdrant_error(ResponseHandlingException(inner)) is None


def handled_error(wrap: bool) -> Exception:
    """A ValueError raised while handling a ConnectError (implicit `__context__`)."""
    try:
        try:
            raise httpx.ConnectError("refused")
        except httpx.ConnectError:
            raise ValueError("unrelated") from None
    except ValueError as error:
        return ResponseHandlingException(error) if wrap else error


@pytest.mark.parametrize("wrap", [False, True])
def test_unrelated_error_raised_while_handling_a_network_error_is_not_eligible(
    wrap: bool,
) -> None:
    error = handled_error(wrap)
    assert (error.source if wrap else error).__context__ is not None  # type: ignore[union-attr]
    assert classify_qdrant_error(error) is None


def test_qdrant_cause_and_context_are_not_followed() -> None:
    explicit = caused_by(RuntimeError("x"), httpx.ConnectError("refused"))
    assert classify_qdrant_error(explicit) is None


# ---- model load -----------------------------------------------------------


class LocalEntryNotFoundError(FileNotFoundError):
    """Stand-in for huggingface_hub.errors.LocalEntryNotFoundError."""


class RevisionNotFoundError(Exception):
    """Stand-in for huggingface_hub.errors.RevisionNotFoundError."""


class RepositoryNotFoundError(Exception):
    """Stand-in for huggingface_hub.errors.RepositoryNotFoundError."""


class GatedRepoError(RepositoryNotFoundError):
    """Stand-in for huggingface_hub.errors.GatedRepoError."""


def status_error() -> httpx.HTTPStatusError:
    response = httpx.Response(404, request=REQUEST)
    return httpx.HTTPStatusError("404", request=REQUEST, response=response)


@pytest.mark.parametrize(
    "error",
    [
        caused_by(OSError("We couldn't connect"), httpx.ConnectError("refused")),
        caused_by(OSError("We couldn't connect"), httpx.ReadTimeout("slow")),
        caused_by(OSError("slow"), TimeoutError("slow")),
        caused_by(OSError("down"), ConnectionError("down")),
        caused_by(
            OSError("We couldn't connect"),
            caused_by(LocalEntryNotFoundError("locate"), httpx.ConnectError("x")),
        ),
        httpx.ReadError("raw hub error propagated unchanged"),
    ],
    ids=["connect", "timeout", "builtin-timeout", "connection", "hub-chain", "raw"],
)
def test_network_cause_is_eligible(error: BaseException) -> None:
    assert reason(classify_model_error(error)) is FallbackReason.MODEL_UNAVAILABLE


@pytest.mark.parametrize(
    "error",
    [
        caused_by(
            OSError("not a valid git identifier"),
            caused_by(RevisionNotFoundError("rev"), status_error()),
        ),
        caused_by(
            OSError("not a valid model identifier"),
            caused_by(RepositoryNotFoundError("repo"), status_error()),
        ),
        caused_by(OSError("gated"), caused_by(GatedRepoError("gated"), status_error())),
        OSError("plain"),
        PermissionError("denied"),
        LocalEntryNotFoundError("local_files_only, nothing cached"),
        ValueError("x"),
        OptionalDependencyError("bge-m3 extra missing"),
    ],
    ids=[
        "missing-revision",
        "missing-model-id",
        "gated",
        "plain-oserror",
        "permission",
        "local-only",
        "value-error",
        "optional-dependency",
    ],
)
def test_configuration_errors_fail_closed(error: BaseException) -> None:
    assert classify_model_error(error) is None


def test_context_without_from_is_not_eligible() -> None:
    try:
        try:
            raise httpx.ConnectError("refused")
        except httpx.ConnectError:
            raise OSError("handled, no cause") from None
    except OSError as error:
        assert error.__context__ is not None or error.__suppress_context__
        assert classify_model_error(error) is None

    try:
        try:
            raise httpx.ConnectError("refused")
        except httpx.ConnectError:
            raise OSError("implicit context")  # noqa: B904 - the point of the test
    except OSError as error:
        assert isinstance(error.__context__, httpx.ConnectError)
        assert error.__cause__ is None
        assert classify_model_error(error) is None


def test_offline_mode_is_excluded_even_though_it_is_a_connection_error() -> None:
    class OfflineModeIsEnabled(ConnectionError):
        pass

    from way2australia_rag.retrieval import availability

    # The stand-in is registered the way the real class would be.
    excluded = (*availability._EXCLUDED_TYPES, OfflineModeIsEnabled)
    original = availability._EXCLUDED_TYPES
    availability._EXCLUDED_TYPES = excluded
    try:
        offline = caused_by(
            OSError("offline"),
            caused_by(LocalEntryNotFoundError("x"), OfflineModeIsEnabled("offline")),
        )
        assert classify_model_error(offline) is None
        both = caused_by(
            OfflineModeIsEnabled("offline"), httpx.ConnectError("also a network")
        )
        assert classify_model_error(both) is None
    finally:
        availability._EXCLUDED_TYPES = original


def test_the_real_offline_class_is_excluded_when_the_hub_is_installed() -> None:
    errors: Any = pytest.importorskip("huggingface_hub.errors")
    offline = caused_by(
        OSError("offline"),
        caused_by(
            errors.LocalEntryNotFoundError("x"), errors.OfflineModeIsEnabled("offline")
        ),
    )
    assert classify_model_error(offline) is None


def test_cause_chain_stops_at_the_link_limit() -> None:
    error: BaseException = httpx.ConnectError("deep")
    for _ in range(MAX_CAUSE_LINKS - 1):
        error = caused_by(OSError("wrapper"), error)
    assert classify_model_error(error) is not None  # the network error is link 10
    error = caused_by(OSError("one more"), error)
    assert classify_model_error(error) is None  # now link 11


def test_a_cause_cycle_terminates() -> None:
    first, second = OSError("a"), OSError("b")
    first.__cause__ = second
    second.__cause__ = first
    assert classify_model_error(first) is None
