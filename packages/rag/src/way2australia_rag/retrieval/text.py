"""Safe printing of payload-derived text (Spec 005 T6, T5 review F1).

Titles and other payload text are untrusted data. A newline would forge extra
output lines and an escape sequence would drive the terminal, so every CLI that
prints payload-derived text goes through `safe_text`.
"""

import re
import unicodedata

# CSI (ESC [ ... final), OSC (ESC ] ... BEL or ST) and other two-byte escapes.
_ANSI = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)?"
    r"|\x1b[@-Z\\-_]"
)
_WHITESPACE = re.compile(r"\s+")


def safe_text(value: object) -> str:
    """One printable line: ANSI sequences removed, control characters and
    line breaks replaced by a space, runs of whitespace collapsed.

    Format characters such as ZWJ/ZWNJ are kept: Malayalam needs them.
    """
    text = _ANSI.sub("", str(value))
    text = "".join(
        " " if unicodedata.category(c) in ("Cc", "Zl", "Zp") else c for c in text
    )
    return _WHITESPACE.sub(" ", text).strip()
