"""`lexical-v1` tokenizer pins (Spec 007 R3)."""

import json
import re
import unicodedata
from pathlib import Path

import pytest
from conftest import REPO_ROOT, live_suite_rows
from way2australia_rag.lexical import tokenizer
from way2australia_rag.lexical.tokenizer import (
    MAX_QUERY_TERMS,
    TOKENIZER_NAME,
    TOKENIZER_VERSION,
    query_terms,
    tokenize,
)

BUSINESS_008 = REPO_ROOT / "knowledge/public/business/business_008_public_samples.md"

# Pinned token lists for the six approved Malayalam goldens (by case_id).
GOLDEN_TOKENS = {
    "g064": [
        "naati", "ccl", "പരീക്ഷയിൽ", "ആകെ", "എത്ര", "മാർക്കാണ്", "ഉള്ളത്",
        "ജയിക്കാൻ", "എത്ര", "വേണം",
    ],
    "g065": [
        "naati", "ccl", "ടെസ്റ്റ്", "അറ്റൻഡ്", "ചെയ്യാൻ", "ഏതൊക്കെ",
        "ഉപകരണങ്ങൾ", "വേണം", "ഏതൊക്കെ", "ഉപയോഗിക്കാൻ", "പാടില്ല",
    ],
    "g066": [
        "naati", "ccl", "ടെസ്റ്റ്", "ബുക്ക്", "ചെയ്തിട്ട്", "ക്യാൻസൽ",
        "ചെയ്താൽ", "പണം", "തിരികെ", "കിട്ടുമോ",
    ],
    "g067": [
        "മെറ്റീരിയൽസും", "മൂന്ന്", "മോക്ക്", "ടെസ്റ്റുകളും", "ഉള്ള",
        "പാക്കേജിന്", "എത്ര", "രൂപയാണ്",
    ],
    "g068": ["കോച്ചിംഗ്", "സെഷനുകളുടെ", "റെക്കോർഡിംഗ്", "കിട്ടുമോ"],
    "g069": [
        "മലയാളത്തിലേക്ക്", "ഇന്റർപ്രെറ്റ്", "ചെയ്യുമ്പോൾ", "സംഖ്യകൾ",
        "ഇംഗ്ലീഷിൽ", "തന്നെ", "പറഞ്ഞാൽ", "മതിയോ",
    ],
}  # fmt: skip


def test_identity_constants() -> None:
    assert (TOKENIZER_NAME, TOKENIZER_VERSION) == ("lexical-v1", "1")


@pytest.mark.parametrize("case_id", sorted(GOLDEN_TOKENS))
def test_golden_queries_pin_exact_tokens(case_id: str) -> None:
    rows = {r["id"]: r for r in live_suite_rows("golden_answerable")}
    assert tokenize(rows[case_id]["query"]) == GOLDEN_TOKENS[case_id]


def test_business_008_words_stay_whole() -> None:
    text = BUSINESS_008.read_text(encoding="utf-8")
    tokens = tokenize(text)
    # Words taken from the corpus file, pinned per word.
    for word in ("നമസ്കാരം", "താമസം", "വാഗ്ദാനങ്ങൾ", "ശ്രദ്ധിച്ചു"):
        assert word in text
        assert word in tokens
    assert tokenize("നമസ്കാരം! ഞാൻ ടോം.") == ["നമസ്കാരം", "ഞാൻ", "ടോം"]


def test_mixed_script_hyphen() -> None:
    assert tokenize("dialogue-ൽ") == ["dialogue", "ൽ"]


def test_english_punctuation_digits_and_case() -> None:
    assert tokenize("Fee: ₹8,499 (GST-incl.)") == ["fee", "8", "499", "gst", "incl"]
    assert tokenize("Hello,   World!") == ["hello", "world"]
    assert tokenize("") == []
    assert tokenize("... --- !!!") == []


def test_nfd_equals_nfc() -> None:
    text = "Café résumé — ഉള്ളത് ചെയ്യാൻ"
    assert tokenize(unicodedata.normalize("NFD", text)) == tokenize(
        unicodedata.normalize("NFC", text)
    )
    assert tokenize("é") == ["é"]


def test_zwj_and_zwnj_are_dropped_and_never_split() -> None:
    assert tokenize("a\u200db") == ["ab"]
    assert tokenize("a\u200cb") == ["ab"]
    assert "\u200d" not in "".join(tokenize("ന്\u200d ക്\u200c"))


def test_legacy_chillu_is_not_the_atomic_chillu() -> None:
    legacy = "ന്\u200d"  # consonant + virama + ZWJ
    atomic = "ൻ"  # MALAYALAM LETTER CHILLU N
    assert tokenize(legacy) == ["ന്"]  # consonant + virama
    assert tokenize(atomic) == [atomic]
    assert tokenize(legacy) != tokenize(atomic)


def test_deterministic() -> None:
    text = "NAATI CCL ടെസ്റ്റ് 2026"
    assert tokenize(text) == tokenize(text)


def test_query_terms_dedup_first_seen_order() -> None:
    result = query_terms("b a b c a")
    assert result.terms == ["b", "a", "c"]
    assert result.truncated is False


def test_query_terms_truncates_at_max() -> None:
    words = [f"w{i}" for i in range(MAX_QUERY_TERMS + 5)]
    result = query_terms(" ".join(words + words))
    assert MAX_QUERY_TERMS == 64
    assert result.terms == words[:MAX_QUERY_TERMS]
    assert result.truncated is True
    exact = query_terms(" ".join(words[:MAX_QUERY_TERMS]))
    assert len(exact.terms) == MAX_QUERY_TERMS
    assert exact.truncated is False


def test_module_has_no_language_code_literal() -> None:
    source = Path(tokenizer.__file__).read_text(encoding="utf-8")
    assert not re.search(r"""["']ml["']|\bml\b""", source)
    # No script-specific table: no Malayalam code points in the module.
    assert not re.search(r"[ഀ-ൿ]", source)


def test_golden_file_is_the_source_of_the_pins() -> None:
    path = REPO_ROOT / "evaluation/datasets/v2/golden_public.jsonl"
    ids = {json.loads(x)["id"] for x in path.read_text("utf-8").splitlines() if x}
    assert set(GOLDEN_TOKENS) <= ids
