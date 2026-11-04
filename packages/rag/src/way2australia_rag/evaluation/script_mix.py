"""Script-mix keys for evaluation slices (Spec 010 R7)."""

import unicodedata


def script_mix(text: str) -> str:
    """Sorted lower-case script names from letter characters, or ``none``."""
    scripts = {
        unicodedata.name(ch, "").split(" ", 1)[0].lower()
        for ch in text
        if unicodedata.category(ch).startswith("L")
    }
    scripts.discard("")
    return "+".join(sorted(scripts)) or "none"
