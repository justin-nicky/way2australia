"""Per-document freshness of a lexical file (Spec 009 R6, Spec 013 R3)."""

import asyncio
import threading
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

from way2australia_rag.ingestion.chunking import ChunkerIdentity
from way2australia_rag.lexical.store import (
    REBUILD_ADVICE,
    LexicalIndex,
    LexicalIndexBindingError,
)
from way2australia_rag.repositories import GUEST_PUBLIC_POLICY, DocumentRepository
from way2australia_rag.repositories.eligibility import list_eligible_documents

T = TypeVar("T")


def run_sync(coro_factory: Callable[[], Coroutine[Any, Any, T]]) -> T:
    """Run `coro_factory()` to completion where this thread has no loop to share.

    With no running loop, `asyncio.run`. Inside a running loop, `asyncio.run` on
    a short-lived thread that is joined before this returns. The factory is
    called on that loop, so the coroutine is created where it runs.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())

    outcome: dict[str, T] = {}
    failure: list[BaseException] = []

    def _target() -> None:
        try:
            outcome["value"] = asyncio.run(coro_factory())
        except BaseException as exc:  # noqa: BLE001 - re-raised on the caller
            failure.append(exc)

    thread = threading.Thread(target=_target, name="lexical-freshness")
    thread.start()
    thread.join()
    if failure:
        raise failure[0]
    return outcome["value"]


def verify_fresh(
    lexical: LexicalIndex,
    repository: DocumentRepository,
    chunker_identity: ChunkerIdentity,
) -> None:
    """Return when the file matches the repository; else `LexicalIndexBindingError`."""
    recorded_identity = lexical.settings.chunker_identity()
    if recorded_identity != chunker_identity:
        raise LexicalIndexBindingError(
            f"lexical index '{lexical.label}' chunker identity does not match "
            f"the configured chunker (chunker_name: recorded "
            f"{recorded_identity.name!r}, wanted {chunker_identity.name!r}). "
            f"{REBUILD_ADVICE}"
        )

    def versions() -> Coroutine[Any, Any, set[tuple[str, int, str]]]:
        return _eligible_document_versions(repository)

    expected = run_sync(versions)
    recorded = lexical.document_versions()
    if expected == recorded:
        return
    expected_by_id = {
        document_id: (version, content_hash)
        for document_id, version, content_hash in expected
    }
    recorded_by_id = {
        document_id: (version, content_hash)
        for document_id, version, content_hash in recorded
    }
    only_repository = len(set(expected_by_id) - set(recorded_by_id))
    only_file = len(set(recorded_by_id) - set(expected_by_id))
    changed = sum(
        1
        for document_id in set(expected_by_id) & set(recorded_by_id)
        if expected_by_id[document_id] != recorded_by_id[document_id]
    )
    raise LexicalIndexBindingError(
        f"lexical index '{lexical.label}' is stale against the document "
        f"repository (documents only in the repository: {only_repository}; "
        f"only in the lexical index: {only_file}; with changed version or hash: "
        f"{changed}). {REBUILD_ADVICE}"
    )


async def _eligible_document_versions(
    repository: DocumentRepository,
) -> set[tuple[str, int, str]]:
    documents = await list_eligible_documents(repository, GUEST_PUBLIC_POLICY)
    return {
        (document.document_id, document.document_version, document.content_hash)
        for document in documents
    }
