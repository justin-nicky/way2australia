"""Lexical tokenizers (Spec 007 R3; Spec 010 R5).

One deterministic, language-neutral tokenizer family used for indexing and
queries. Module-level ``tokenize`` and ``query_terms`` remain ``lexical-v1``
aliases (D051 pin and existing imports).
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable
from typing import NamedTuple, Protocol

from way2australia_rag.lexical.equivalents import SEQUENCE_EQUIVALENTS

TOKENIZER_NAME = "lexical-v1"
TOKENIZER_VERSION = "1"
MAX_QUERY_TERMS = 64

_DROPPED = {"\u200d", "\u200c"}  # ZWJ, ZWNJ


class QueryTerms(NamedTuple):
    terms: list[str]
    truncated: bool


class LexicalTokenizer(Protocol):
    name: str
    version: str

    def tokenize(self, text: str) -> list[str]: ...
    def query_terms(self, text: str) -> QueryTerms: ...


def _is_token_char(char: str) -> bool:
    category = unicodedata.category(char)
    return category in ("Mn", "Mc") or category[0] in ("L", "N")


def replace_sequences(
    text: str, equivalents: tuple[tuple[str, str], ...] = SEQUENCE_EQUIVALENTS
) -> str:
    """Longest-match replacement of listed sequences (generic, not script-named)."""
    if not equivalents:
        return text
    by_len = sorted(equivalents, key=lambda pair: len(pair[0]), reverse=True)
    out: list[str] = []
    i = 0
    while i < len(text):
        matched = False
        for seq, repl in by_len:
            if text.startswith(seq, i):
                out.append(repl)
                i += len(seq)
                matched = True
                break
        if not matched:
            out.append(text[i])
            i += 1
    return "".join(out)


def _tokenize_after_nfc(text: str) -> list[str]:
    kept = "".join(c for c in text if c not in _DROPPED).lower()
    tokens: list[str] = []
    current: list[str] = []
    for char in kept:
        if _is_token_char(char):
            current.append(char)
        elif current:
            tokens.append("".join(current))
            current = []
    if current:
        tokens.append("".join(current))
    return tokens


def _tokenize_v1(text: str) -> list[str]:
    return _tokenize_after_nfc(unicodedata.normalize("NFC", text))


def _tokenize_v2(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFC", text)
    replaced = replace_sequences(normalized)
    return _tokenize_after_nfc(replaced)


def _query_terms_from(tokenize_fn: Callable[[str], list[str]], text: str) -> QueryTerms:
    distinct = list(dict.fromkeys(tokenize_fn(text)))
    if len(distinct) > MAX_QUERY_TERMS:
        return QueryTerms(distinct[:MAX_QUERY_TERMS], True)
    return QueryTerms(distinct, False)


class _V1Tokenizer:
    name = "lexical-v1"
    version = "1"

    tokenize = staticmethod(_tokenize_v1)
    query_terms = staticmethod(lambda text: _query_terms_from(_tokenize_v1, text))


class _V2Tokenizer:
    name = "lexical-v2"
    version = "2"

    tokenize = staticmethod(_tokenize_v2)
    query_terms = staticmethod(lambda text: _query_terms_from(_tokenize_v2, text))


_V1 = _V1Tokenizer()
_V2 = _V2Tokenizer()

TOKENIZERS: dict[str, LexicalTokenizer] = {
    _V1.name: _V1,
    _V2.name: _V2,
}


def tokenizer_named(name: str, version: str) -> LexicalTokenizer:
    from way2australia_rag.lexical.store import LexicalIndexBindingError

    tokenizer = TOKENIZERS.get(name)
    if tokenizer is None or tokenizer.version != str(version):
        raise LexicalIndexBindingError(
            f"lexical index tokenizer {name!r} v{version!r} is not supported; "
            "run `make index-lexical` for this collection and index_version."
        )
    return tokenizer


def tokenize(text: str) -> list[str]:
    """Tokens in text order, duplicates kept (`lexical-v1`)."""
    return _tokenize_v1(text)


def query_terms(text: str) -> QueryTerms:
    """Distinct tokens in first-seen order, at most `MAX_QUERY_TERMS` (`lexical-v1`)."""
    return _query_terms_from(_tokenize_v1, text)
