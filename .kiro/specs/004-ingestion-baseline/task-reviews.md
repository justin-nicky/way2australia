# 004 — Task reviews

## T1 — round 1

### Implementation
- Model: claude-sonnet-5-5
- Files changed: `packages/rag/src/way2australia_rag/repositories/manifest.py` (new `DATE_FIELDS` and shared `date_problems()`, called from `check_manifest_documents`); `packages/rag/src/way2australia_rag/repositories/validate.py` (private date check and its constants removed; dates now reported through the shared helper); `packages/rag/tests/test_date_and_policy.py` (new); `.kiro/specs/004-ingestion-baseline/tasks.md`
- Verification run: `make test-unit` → pass (175 passed, 13 deselected); `make test-integration` → pass (13 passed); `make validate-knowledge` → OK, 0 problems; `make verify` → pass (188 tests, ruff and pyright clean)
- Notes: The helper lives in `manifest.py` because both the loader (`_read_all` → `check_manifest_documents`) and `validate-knowledge` already go through it, so the two cannot diverge. Date fields are `last_reviewed_at`, `effective_from`, `effective_to` (the only date-like fields in `document_metadata.schema.json`). A bad date makes the loader raise `ManifestValidationError` with a line `doc_a: <field>: must be a YYYY-MM-DD date` (no absolute path). Tests cover each field with four bad values, valid values, seed corpus load, and `config/access_policy.yaml` vs `GUEST_PUBLIC_POLICY` (guest == ["public"], equal scopes, every named scope is an `AccessScope` member). `make format` briefly reformatted an unrelated test file; that change was reverted. Nothing under `knowledge/`, `config/` or `evaluation/` was touched. Model check: running model matches the intended tier note (no mismatch recorded).
- Usage: 93K tokens · 19 tool uses · 1:39

### Review
- Model: claude-opus-5-5 (matches task-reviewer tier BEST = Opus; implementer was claude-sonnet-5-5)
- Verdict: PASS
- Commands: `make test-unit` → pass (175 passed, 13 deselected; 18 new in `test_date_and_policy.py`); `make validate-knowledge` → OK, 0 problems; `make test-integration` → pass (13 collected, 13 passed); `make verify` → exit 0 (ruff clean, pyright 0 errors, 188 passed, validate-knowledge OK); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R3] The scope check is one-way (`named <= members`): a new `AccessScope` member added without a config entry would not fail the test. R3 says the enum values "match" the configured scopes; the task checklist only asks for the subset. → Optionally assert equality (`named == members`) in a later task.
- Summary for user (PASS only):
  - Changed: one shared strict `YYYY-MM-DD` check (`date_problems`, `DATE_FIELDS` in `repositories/manifest.py`) now runs inside `check_manifest_documents`, which both `LocalDocumentRepository` and `make validate-knowledge` use. The old private check in `validate.py` (which covered only the effective dates) is gone; `last_reviewed_at` is now checked as well. New tests are in `packages/rag/tests/test_date_and_policy.py`.
  - Verified by: the commands above. The tests cover each of the 3 date fields with 4 bad values, plus valid dates, the seed corpus loading unchanged, and `config/access_policy.yaml` against `GUEST_PUBLIC_POLICY`.
  - Worth your attention: the R3 test checks enum values in one direction only (F1). Nothing under `knowledge/`, `config/` or `evaluation/` changed.
- Usage: 74K tokens · 11 tool uses · 27:21

### User decision
- 2026-10-15 — approved

## T2 — round 1

### Implementation (reconstructed by the orchestrator from the implementer's report)
- Model: claude-sonnet-5-5
- Files changed: new package `packages/rag/src/way2australia_rag/ingestion/` (`__init__.py`, `errors.py` with `IngestionError`, `IngestionConfigurationError`, `IndexSettingsMismatchError`, `OptionalDependencyError`; `chunking.py` with frozen `Chunk`, the `Chunker` Protocol, `HeadingChunker` (name `heading`, version `1`, default cap 2000 characters) and `slugify`); new tests `packages/rag/tests/ingestion/test_chunking.py` (15 tests); `tasks.md` (T2 boxes, State).
- Verification run: `make test-unit` → pass (190 passed, 13 deselected); `make verify` → exit 0 (ruff and pyright clean, 203 tests, validate-knowledge OK). No Docker or integration beyond `make verify`.
- Notes: slug word characters use a character loop (`isalnum()` or Unicode category `M*`), not regex `\w`, because `\w` splits Indic words at vowel signs; no language-specific code; Malayalam, Chinese and Cyrillic headings tested. Duplicate slugs get `-2`, `-3`; `main` is reserved when a preamble exists. The size cap includes the heading line plus its blank line; a very long heading prefix is truncated to half the cap. The seed-corpus test (13 documents, one `main`/0 chunk each) is documented as a baseline and runs in `make test-unit`. T1 carry-over F1 (two-way scope check) left untouched as out of T2 scope. Nothing under `knowledge/`, `config/` or `evaluation/` changed.
- Usage: 91K tokens · 12 tool uses · 8:35

### Review
- Model: claude-opus-5-5 (matches task-reviewer tier BEST = Opus; no mismatch)
- Verdict: FAIL
- Commands: `make test-unit` → pass (190 passed, 13 deselected; 15 new in `packages/rag/tests/ingestion/test_chunking.py`); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 203 passed); `make test-integration` → pass (13 collected, 13 passed, all pre-existing); `git status --porcelain -- evaluation/ knowledge/ config/` → empty
- Findings:
  - F1 [MAJOR, IMPLEMENTATION, workflow] This file's working-tree copy was overwritten: the committed content (T1 round 1 Implementation, Review and "User decision: approved") was deleted and replaced with 40 identical lines `- Usage: 91K tokens · 12 tool uses · 8:35`, and there is no T2 round 1 Implementation block. Committing it would erase the T1 approval record. → Restore the file from `git show HEAD:.kiro/specs/004-ingestion-baseline/task-reviews.md`, append a proper T2 round 1 Implementation block (model, files, verification, notes, usage) followed by this Review block, and find the step that wrote the repeated Usage lines.
  - F2 [MINOR, IMPLEMENTATION, R4] `HeadingChunker` accepts `max_chunk_chars >= 2`, but caps 2–4 make `_split_words` loop forever on any headed section (budget `cap - cap//2 - 2` ≤ 0), reproduced with a 5 s alarm. For small caps the heading prefix is also cut to `cap//2`, so a piece no longer starts with the full heading line. Realistic caps (default 2000) are not affected. → Raise the minimum so the budget is always ≥ 1, or reject a cap that cannot hold the heading line; add a test.
  - F3 [MINOR, IMPLEMENTATION, R4] The slug word-character rule differs from the design's "Unicode-aware `\w`": it uses `isalnum()` plus combining marks, so `_` becomes `-`, and ZWJ/ZWNJ (used in Malayalam text) split a word with `-` (for example `ന‍ന്‍` becomes `ന-ന്`). The change is sound, since plain `\W+` turns `ഫീസ്` into `ഫ-സ-`, but it is not recorded. → Note the rule in design/DECISIONS (T9), and decide whether Cf joiners should be dropped instead of becoming separators.
- Usage: 89K tokens · 15 tool uses · 2:33
- Orchestrator note: F1 was caused by the orchestrator, not the implementer. While recording usage, a `sed` matched no line and rewrote the whole file. The file was restored from git (T1 blocks and the T1 user decision intact); the T2 Implementation block below was reconstructed from the implementer's hand-back report, not written by the implementer. F1 is resolved; F2 and F3 remain for round 2.

## T2 — round 2

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/chunking.py`, `packages/rag/tests/ingestion/test_chunking.py`, `tasks.md` (State only). Earlier blocks in this file not touched (F1 was already fixed by the orchestrator).
- Verification run: `make test-unit` → pass (193 passed, 13 deselected; 3 new tests); `make verify` → exit 0 (ruff, pyright, skills-check, validate-knowledge, 206 tests). No integration tests run beyond `make verify`.
- F2 fixed: `HeadingChunker` now rejects `max_chunk_chars < MIN_CHUNK_CHARS` (16) with `IngestionConfigurationError` (was `ValueError`, cap >= 2). With cap >= 16 the body budget `cap - cap//2 - 2` is always >= 6, so `_split_words` cannot loop. The full heading line is kept on every piece whenever it fits in half the cap; only a heading longer than `cap//2` is truncated (unchanged behavior, documented in a code comment). Tests: caps 0, 1, 2, 4, 15 rejected; the minimum cap terminates within 5 s (thread with timeout) and every piece stays within the cap and starts with the full short heading.
- F3 fixed (rule for T9 docs): `slugify` drops all Unicode category `Cf` (format) characters after NFKC and lower-casing, before the word/separator pass. ZWJ (U+200D), ZWNJ (U+200C), zero-width space, BOM and similar never split a word and never become `-`. Word characters remain `isalnum()` or category `M*`; `_` and other punctuation become `-`. Tests: `ന<ZWJ>ന്<ZWJ>` → `നന്`, `ക്<ZWNJ>ഷ` → `ക്ഷ`, `a<ZWSP>b <BOM>c` → `ab-c`. This deviates from design's "Unicode-aware `\w`" wording; T9 should record it in design/DECISIONS. No language-specific code was added.
- Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 72K tokens · 10 tool uses · 1:06

### Review
- Model: claude-opus-5-5 (matches task-reviewer tier BEST = Opus; implementer was claude-sonnet-5-5; no mismatch)
- Verdict: PASS
- Commands: `make test-unit` → pass (193 passed, 13 deselected; 18 in `packages/rag/tests/ingestion/test_chunking.py`); `make test-integration` → pass (13 collected, 13 passed, all pre-existing); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 206 passed); `git status --porcelain -- evaluation/ knowledge/ config/` → empty; `git diff HEAD -- .kiro/specs/004-ingestion-baseline/task-reviews.md` → additions only (T1 blocks and T1 user decision intact). Extra reviewer check (scratchpad script, not committed): 3000 random documents with caps 16–80 (headings, code fences, Malayalam, 40-character words) all terminated, no piece exceeded the cap, `(section_id, position)` unique.
- Round 1 findings: F1 resolved (file restored by the orchestrator; only additions vs HEAD). F2 resolved: `max_chunk_chars < MIN_CHUNK_CHARS` (16) raises `IngestionConfigurationError`, so the body budget is ≥ 6 and `_split_words` always advances; tests cover rejected caps and termination at the minimum cap. F3 resolved in code: `slugify` drops category `Cf` characters (ZWJ, ZWNJ, ZWSP, BOM) before the word pass; tests cover it. The deviation from the design's "Unicode-aware `\w`" wording is still unrecorded in design/DECISIONS (carried to T9).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R4] A heading line longer than `max_chunk_chars // 2` is still truncated, so its pieces do not start with the full heading line (checklist says each piece starts with its heading line). Not reachable with realistic headings at the default cap 2000; documented in a code comment. → Optionally note it with the slug rule in T9.
  - F2 [MINOR, IMPLEMENTATION (docs follow-up for T9), R4] The slug rule (`isalnum()` or category `M*` are word characters; `Cf` dropped; `_` becomes `-`) differs from design wording. → Record in design/DECISIONS in T9, as the implementer noted.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/ingestion/` package (`errors.py` with the `IngestionError` hierarchy; `chunking.py` with frozen `Chunk`, `Chunker` Protocol, `HeadingChunker` `heading`/`1`, default cap 2000, minimum 16, and `slugify`); tests in `packages/rag/tests/ingestion/test_chunking.py`. Round 2 fixed the infinite loop at tiny caps and made zero-width joiners stop splitting Malayalam slugs.
  - Verified by: `make test-unit`, `make test-integration`, `make verify` (206 tests), plus a 3000-document random check of cap and termination.
  - Worth your attention: the slug rule is not plain `\w` (needed for Indic vowel signs and joiners) and very long headings are truncated in chunk text; both should be written into design/DECISIONS in T9. Nothing under `knowledge/`, `config/` or `evaluation/` changed.
- Usage: 74K tokens · 11 tool uses · 2:30

### User decision
- 2026-10-15 — not approved yet. Verbatim: "Not approved yet — three quick checks first: 1. Slug rule: it changes how `section_id` (a stable ID) is derived, so record it in the spec now via `spec-planner` (design.md + a Change log line), not only in T9. The rule itself is fine. 2. Is heading text NFC-normalized before slugging? If not, add it (plus a test that NFC and NFD forms of the same Malayalam heading give the same slug) in this task. 3. Confirm `section_id` comes from the full heading, never the truncated chunk text (add a test if missing)."
- Orchestrator routing: item 1 is spec feedback (T2 `blocked — spec issue` until the design amendment is logged); items 2 and 3 are implementation feedback for the next implementer round (round 3). Note: `slugify` applies NFKC, which already includes canonical composition, so NFC/NFD equivalence is expected to hold; the implementer must prove it with a test.


## T2 — round 3

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/tests/ingestion/test_chunking.py` (2 new tests, `import unicodedata`), `tasks.md` (two new T2 boxes ticked, State). No production code changed: both checks passed against the existing `slugify` and `HeadingChunker`. Earlier blocks in this file were not modified (append only).
- Tests: `test_nfc_and_nfd_malayalam_headings_give_same_slug` (NFC and NFD forms of a Malayalam heading containing U+0D4A differ as strings, give the same `slugify` result and the same `(section_id, position)` from `HeadingChunker`); `test_section_id_comes_from_full_heading_not_truncated_chunk_text` (cap 40, heading longer than half the cap: `section_id` equals `slugify(full heading)`, the chunk text omits the heading tail, every piece is within the cap).
- Verification run: `make test-unit` -> pass (195 passed, 13 deselected; 2 new); `make verify` -> see result below. No integration tests run beyond `make verify`.
- Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- `make verify` result: exit 0 (ruff, pyright, skills-check, validate-knowledge, 208 passed).
- Usage: 71K tokens · 8 tool uses · 1:45

### Review
- Model: claude-opus-5-5 (matches task-reviewer tier BEST = Opus; implementer was claude-sonnet-5-5; no mismatch)
- Verdict: PASS
- Commands: `make test-unit` → pass (195 passed, 13 deselected; 20 in `packages/rag/tests/ingestion/test_chunking.py`, 2 new); `make test-integration` → pass (13 collected, 13 passed, all pre-existing); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 208 passed); `git status --porcelain -- evaluation/ knowledge/ config/` → empty; `git diff HEAD -- .kiro/specs/004-ingestion-baseline/task-reviews.md` → additions only (T1 blocks, T1 user decision and T2 rounds 1–2 intact). Extra reviewer check (not committed): the NFC and NFD strings differ but give the same slug, and the truncated heading prefix slugs to `very-long-heading`, not the full-heading ID, so the round-3 test tells the two apart.
- User round-2 items: (1) design.md HeadingChunker step 3 (slug sub-rules 1–5), step 5 (suffix skipping, `main` reserved with a preamble) and step 6 (hard-split of long words, minimum cap 16 with `IngestionConfigurationError`, heading truncated to `max_chunk_chars // 2` in chunk text only) match `chunking.py` exactly: NFKC then `lower()`, `Cf` dropped before the word pass, word chars `isalnum()` or `M*`, runs to one `-`, trimmed, `section` fallback, `_unique_slug` loop, `has_preamble` reservation, `prefix = heading_line[: cap // 2]`, `section_id` from `heading_text`. Change log line in requirements.md is present and dated. (2) `test_nfc_and_nfd_malayalam_headings_give_same_slug` covers U+0D4A through `slugify` and `HeadingChunker`; no code change was needed because NFKC already composes. (3) `test_section_id_comes_from_full_heading_not_truncated_chunk_text` covers it. Round 2 MINOR F1 and F2 are resolved by the design amendment.
- Findings: none
- Summary for user (PASS only):
  - Changed: round 3 added two tests to `packages/rag/tests/ingestion/test_chunking.py` (NFC/NFD Malayalam heading gives the same slug and `section_id`; `section_id` is the slug of the full heading even when chunk text truncates it). No production code changed. The planner's design.md amendment (exact slug rule, suffix and `main` rules, minimum cap 16, chunk-text-only heading truncation) and the Change log line match the code.
  - Verified by: `make test-unit` (195), `make test-integration` (13), `make verify` (208 tests, ruff, pyright, skills-check, validate-knowledge).
  - Worth your attention: the T2 checklist box in tasks.md still uses the old short wording ("Unicode-aware non-word runs"); design.md is now the precise source of the rule. Nothing under `knowledge/`, `config/` or `evaluation/` changed.
- Usage: 84K tokens · 12 tool uses · 1:34

### User decision (round 3)
- 2026-10-15 — approved
