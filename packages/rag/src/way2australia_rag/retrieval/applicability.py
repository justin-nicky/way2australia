"""LOTE applicability filters and hit re-check (Spec 010 R2–R4)."""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from qdrant_client import models

from way2australia_rag.ingestion.payload import PointPayload
from way2australia_rag.retrieval.access import (
    ResolvedAccess,
    build_access_filter,
    build_sql_access_clause,
)
from way2australia_rag.retrieval.errors import (
    LanguageApplicabilityError,
    RetrievalConfigurationError,
)

_LANGUAGE_CODE = re.compile(r"^[a-z]{2,3}$")


@dataclass(frozen=True, slots=True)
class ResolvedLote:
    code: str


def _active_list(active_codes: Sequence[str]) -> str:
    return ", ".join(sorted(active_codes))


def resolve_lote(code: str | None, active_codes: Sequence[str]) -> ResolvedLote | None:
    if code is None:
        return None
    if not code.strip():
        raise RetrievalConfigurationError(
            f"lote must not be empty (active codes: {_active_list(active_codes)})."
        )
    value = code.strip()
    if value == "*":
        raise RetrievalConfigurationError(
            "lote value '*' is not allowed "
            f"(active codes: {_active_list(active_codes)})."
        )
    if value == "en":
        raise RetrievalConfigurationError(
            "'en' is not a LOTE: lote names the non-English side of the CCL pair "
            f"(active codes: {_active_list(active_codes)})."
        )
    if value not in active_codes:
        raise RetrievalConfigurationError(
            f"lote value {value!r} is not active "
            f"(active codes: {_active_list(active_codes)})."
        )
    return ResolvedLote(code=value)


def valid_lote_languages(value: object) -> bool:
    if not isinstance(value, list) or not value:
        return False
    if not all(isinstance(item, str) for item in value):
        return False
    if len(set(value)) != len(value):
        return False
    if "*" in value:
        return value == ["*"]
    return all(_LANGUAGE_CODE.fullmatch(code) for code in value)


def encode_lote_column(codes: list[str]) -> str:
    if not valid_lote_languages(codes):
        raise ValueError("lote_languages is missing or malformed.")
    return "|" + "|".join(sorted(codes)) + "|"


def build_lote_condition(lote: ResolvedLote) -> models.FieldCondition:
    return models.FieldCondition(
        key="lote_languages",
        match=models.MatchAny(any=["*", lote.code]),
    )


def build_sql_lote_clause(lote: ResolvedLote) -> tuple[str, tuple[str, str]]:
    return (
        "(c.lote_languages = ? OR instr(c.lote_languages, ?) > 0)",
        ("|*|", f"|{lote.code}|"),
    )


def dense_query_filter(
    access: ResolvedAccess, lote: ResolvedLote | None
) -> models.Filter:
    access_filter = build_access_filter(access)
    if lote is None:
        return access_filter
    must = access_filter.must
    if must is None:
        must_list: list[models.Condition] = []
    elif isinstance(must, list):
        must_list = must
    else:
        must_list = [must]
    return models.Filter(must=[*must_list, build_lote_condition(lote)])


def sql_access_with_lote(
    access: ResolvedAccess, lote: ResolvedLote | None
) -> tuple[str, tuple[str, ...]]:
    where, params = build_sql_access_clause(access)
    if lote is None:
        return where, params
    lote_sql, lote_params = build_sql_lote_clause(lote)
    return f"{where} AND {lote_sql}", (*params, *lote_params)


def check_applicable(payload: PointPayload, lote: ResolvedLote) -> None:
    raw = payload.lote_languages
    if not valid_lote_languages(raw):
        raise LanguageApplicabilityError(
            f"hit for document '{payload.document_id}' has a malformed "
            "lote_languages field.",
            document_id=payload.document_id,
        )
    if raw == ["*"] or lote.code in raw:
        return
    raise LanguageApplicabilityError(
        f"hit for document '{payload.document_id}' is not applicable to "
        f"lote {lote.code!r}.",
        document_id=payload.document_id,
    )
