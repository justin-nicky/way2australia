"""Legacy Malayalam chillu spellings mapped to atomic chillu letters (Spec 010 R5).

Source: The Unicode Standard, Version 16.0, Chapter 12 (South and Central
Asian Scripts), section «Malayalam», subsection «Chillu Characters». Each row
below matches the standard’s pairing of an atomic chillu with the earlier
representation (consonant + U+0D4D VIRAMA + U+200D ZWJ). Checked against that
text on 2026-11-04.

U+0D54–U+0D56 (MALAYALAM LETTER CHILLU M / Y / LLL) have no legacy ZWJ
sequence in that table and are omitted.
"""

# (legacy sequence, atomic chillu) — code points only, longest sequences first
# for the replacement scan.
SEQUENCE_EQUIVALENTS: tuple[tuple[str, str], ...] = (
    ("\u0d23\u0d4d\u200d", "\u0d7a"),  # NNA + virama + ZWJ -> CHILLU NN
    ("\u0d28\u0d4d\u200d", "\u0d7b"),  # NA + virama + ZWJ -> CHILLU N
    ("\u0d30\u0d4d\u200d", "\u0d7c"),  # RA + virama + ZWJ -> CHILLU RR (legacy)
    ("\u0d32\u0d4d\u200d", "\u0d7d"),  # LA + virama + ZWJ -> CHILLU L
    ("\u0d33\u0d4d\u200d", "\u0d7e"),  # LLA + virama + ZWJ -> CHILLU LL
    ("\u0d15\u0d4d\u200d", "\u0d7f"),  # KA + virama + ZWJ -> CHILLU K
)
