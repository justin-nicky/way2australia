"""Deterministic document hashing (`content-hash-v1`).

Three SHA-256 hashes, each with one job:

- manifest `sha256`: integrity of the raw file bytes, frontmatter included;
- manifest `body_sha256`: integrity of the normalized body text alone;
- `content_hash`: the ONLY change-detection signal for ingestion. It covers
  `body_sha256` plus the retrieval-affecting metadata listed in
  `CONTENT_HASH_METADATA_FIELDS`, serialized as canonical JSON.

Excluded on purpose: `document_id`, `document_version` (identity),
`last_reviewed_at`, `introduced_in_release` (change without changing what is
retrieved), and `path`, `sha256`, `schema_version` (storage bookkeeping), so
moving a file or bumping a review date never changes `content_hash`.

Changing the field list or the recipe requires a new `HASH_CONTRACT` value,
which makes every document appear changed to ingestion.
"""

import hashlib
import json
from collections.abc import Mapping
from datetime import date
from typing import Any

HASH_CONTRACT = "content-hash-v1"

CONTENT_HASH_METADATA_FIELDS: tuple[str, ...] = (
    "title",
    "knowledge_domain",
    "tenant_id",
    "access_scope",
    "owner_user_id",
    "content_language",
    "language_scope",
    "lote_languages",
    "source_authority",
    "source_type",
    "source_url",
    "approval_status",
    "lifecycle_status",
    "retrieval_enabled",
    "synthetic",
    "effective_from",
    "effective_to",
)


def normalize_body(body: str) -> str:
    """CRLF/CR to LF, then strip leading and trailing whitespace."""
    return body.replace("\r\n", "\n").replace("\r", "\n").strip()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_body_sha256(body: str) -> str:
    return sha256_hex(normalize_body(body).encode("utf-8"))


def _canonical_value(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | str):
        return value
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, list | tuple):
        return [_canonical_value(v) for v in value]
    enum_value = getattr(value, "value", None)  # str-valued Enum
    if isinstance(enum_value, str):
        return enum_value
    raise TypeError(f"cannot canonicalize {type(value).__name__}")


def canonical_json(data: Mapping[str, Any]) -> str:
    """Sorted keys, no insignificant whitespace, UTF-8 characters kept."""
    return json.dumps(
        _canonical_value_mapping(data),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _canonical_value_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: (
            _canonical_value_mapping(v)
            if isinstance(v, Mapping)
            else _canonical_value(v)
        )
        for key, v in data.items()
    }


def compute_content_hash(body: str, metadata: Mapping[str, Any]) -> str:
    """`content-hash-v1` of a document body and its metadata.

    `metadata` may carry extra keys; only the listed fields are hashed. Absent
    optional fields hash as `null`. `lote_languages` keeps its stored order.
    """
    payload = {
        "hash_contract": HASH_CONTRACT,
        "body_sha256": compute_body_sha256(body),
        "metadata": {f: metadata.get(f) for f in CONTENT_HASH_METADATA_FIELDS},
    }
    return sha256_hex(canonical_json(payload).encode("utf-8"))
