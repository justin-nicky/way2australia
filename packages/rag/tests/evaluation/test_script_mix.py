"""Script-mix slice keys (Spec 010 R7)."""

import unicodedata

import pytest
from conftest import live_suite_rows
from way2australia_rag.script_mix import script_mix

_LATIN = "ABCDEFHIKLMNOPRSTWabcdefghijklmnopqrstuvwxyz"
_MALAYALAM = "അആഇഉഎഏഒകഖഗങചജഞടഡണതഥദധനപബഭമയരറലളഴവശഷസൻർൽൾ"

# Letters from v3 golden queries: Unicode name prefix (Script property) per letter.
SCRIPT_FIXTURE: dict[str, str] = {
    **{ch: "latin" for ch in _LATIN},
    **{ch: "malayalam" for ch in _MALAYALAM},
}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("123", "none"),
        ("...", "none"),
        ("₹", "none"),
        ("   ", "none"),
        ("a\u200db", "latin"),
        ("a\u200cb", "latin"),
        ("mock-ൽ", "latin+malayalam"),
        ("₹1,300 mock-ൽ", "latin+malayalam"),
    ],
)
def test_non_letters_add_no_script(text: str, expected: str) -> None:
    assert script_mix(text) == expected


@pytest.mark.parametrize(
    ("ch", "word"),
    [
        ("\u0d4d", "ക"),  # MALAYALAM SIGN VIRAMA
        ("\u0d3e", "ക"),  # MALAYALAM VOWEL SIGN AA
    ],
)
def test_virama_and_vowel_sign_add_no_script(ch: str, word: str) -> None:
    assert script_mix(f"{word}{ch}") == "malayalam"


def test_g062_is_latin_only() -> None:
    rows = {r["id"]: r for r in live_suite_rows("golden_answerable")}
    assert script_mix(rows["g062"]["query"]) == "latin"


@pytest.mark.parametrize("lang", ["en", "ml", "mixed"])
def test_representative_v3_queries(lang: str) -> None:
    rows = [
        r
        for r in live_suite_rows("golden_answerable")
        if r.get("query_language") == lang
    ]
    assert rows
    for row in rows[:3]:
        mix = script_mix(row["query"])
        assert mix in {"latin", "malayalam", "latin+malayalam", "none"}


def test_every_v3_query_letter_matches_script_fixture() -> None:
    for row in live_suite_rows("golden_answerable"):
        query = row["query"]
        mix = script_mix(query)
        scripts: set[str] = set()
        for ch in query:
            if not unicodedata.category(ch).startswith("L"):
                continue
            if ch not in SCRIPT_FIXTURE:
                pytest.fail(f"unmapped letter {ch!r} in {row['id']}")
            prefix = unicodedata.name(ch, "").split(" ", 1)[0].lower()
            assert prefix == SCRIPT_FIXTURE[ch]
            scripts.add(SCRIPT_FIXTURE[ch])
        expected_mix = "+".join(sorted(scripts)) if scripts else "none"
        assert mix == expected_mix
