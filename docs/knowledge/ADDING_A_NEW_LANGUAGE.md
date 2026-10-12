# Adding a new CCL language later

Do not fork the RAG application per language.

For each newly supported language:

1. Add/update the language in `config/language_registry.json`.
2. Add approved Way2Australia product content for that language.
3. Add the current NAATI language-specific policy if one exists.
4. Mark language-specific documents with:
   - `language_scope: language_specific`
   - `lote_languages: ["<internal-code>"]`
5. Keep shared CCL rules as `lote_languages: ["*"]`.
6. Add retrieval/evaluation questions in:
   - English;
   - the LOTE;
   - natural English+LOTE mixed queries where relevant.
7. Measure retrieval metrics separately by language before enabling it publicly.
8. Do not assume Malayalam rules (dialects, English borrowing, number conversion) apply to another language.
