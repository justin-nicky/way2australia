"""The `lexical-v1` tokenizer (Spec 007 R3).

One deterministic, language-neutral tokenizer used for indexing and for queries:

1. NFC normalization;
2. ZWJ (U+200D) and ZWNJ (U+200C) are dropped, so they never split a token and
   never survive into one (the same rule as `ingestion.chunking.slugify`, which
   drops every `Cf` character). Consequence, pinned by a test: a legacy chillu
   sequence (consonant + virama + ZWJ) becomes consonant + virama, which is not
   equal to the atomic chillu letter;
3. lower-casing;
4. token characters are Unicode letters, numbers and combining marks
   (`Mn`, `Mc`); every other character separates tokens.

No stemming, no stopwords, no script-specific table.
"""

import unicodedata
from typing import NamedTuple

TOKENIZER_NAME = "lexical-v1"
TOKENIZER_VERSION = "1"
MAX_QUERY_TERMS = 64

_DROPPED = {"\u200d", "\u200c"}  # ZWJ, ZWNJ


def _is_token_char(char: str) -> bool:
    category = unicodedata.category(char)
    return category in ("Mn", "Mc") or category[0] in ("L", "N")


def tokenize(text: str) -> list[str]:
    """Tokens in text order, duplicates kept."""
    normalized = unicodedata.normalize("NFC", text)
    kept = "".join(c for c in normalized if c not in _DROPPED).lower()
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


class QueryTerms(NamedTuple):
    terms: list[str]
    truncated: bool


def query_terms(text: str) -> QueryTerms:
    """Distinct tokens in first-seen order, at most `MAX_QUERY_TERMS`."""
    distinct = list(dict.fromkeys(tokenize(text)))
    if len(distinct) > MAX_QUERY_TERMS:
        return QueryTerms(distinct[:MAX_QUERY_TERMS], True)
    return QueryTerms(distinct, False)
