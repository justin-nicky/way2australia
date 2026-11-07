"""Map query script mix to a message language code (Spec 012 R3, D-D)."""

from way2australia_rag.script_mix import script_mix

# Product default when no non-English script maps; not a content-language branch.
_FALLBACK_MESSAGE_LANGUAGE = "en"


def message_language(query: str, script_to_language: dict[str, str]) -> str:
    """First mapped non-English code from the query's scripts, else the fallback."""
    mix = script_mix(query)
    if mix == "none":
        return _FALLBACK_MESSAGE_LANGUAGE
    for script in mix.split("+"):
        code = script_to_language.get(script)
        if code and code != _FALLBACK_MESSAGE_LANGUAGE:
            return code
    return _FALLBACK_MESSAGE_LANGUAGE
