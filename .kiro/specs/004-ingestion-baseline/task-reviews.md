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


## T3 — round 1

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/embedding.py` (new: frozen `EmbedderInfo`, `Embedder` Protocol with separate `embed_documents`/`embed_query`, `FakeEmbedder`), `packages/rag/tests/ingestion/test_embedding.py` (new), `tasks.md` (T3 boxes ticked, State). Earlier blocks in this file were not modified (append only).
- Verification run: `make test-unit` -> pass (209 passed, 13 deselected); `make verify` -> exit 0 (ruff, pyright, skills-check, validate-knowledge, 222 passed). No separate integration run beyond `make verify`.
- Notes: FakeEmbedder expands SHA-256(counter || utf-8 text) blocks to the vector size, maps bytes to [-1, 1], then L2-normalizes; model ID `fake-hash-embedder`, revision `1`, default size 64, `is_fake=True`, `normalize=True`. A vector size below 1 raises `IngestionConfigurationError` (small internal choice). `EmbedderInfo.settings` defaults to `{}`. The no-PyTorch test runs a subprocess and checks `torch`/`sentence_transformers` are not in `sys.modules`. Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 79K tokens · 12 tool uses · 4:19

### Review
- Model: claude-opus-5-5 (matches BEST tier; different model from the implementer)
- Verdict: PASS
- Commands: `make test-unit` → pass (209 passed, 13 deselected); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check 5 mirrors match, validate-knowledge 0 problems, 222 passed); `make test-integration` → pass (13 collected, 13 passed); `pytest packages/rag/tests/ingestion/test_embedding.py` → 14 passed. Protected paths (`evaluation/ knowledge/ config/`) unchanged.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R5] `test_info_reports_fake_identity` asserts immutability with `pytest.raises(Exception)`; a narrower `pydantic.ValidationError` would avoid passing on an unrelated error.
  - F2 [MINOR, IMPLEMENTATION, R5] `test_no_pytorch_import` cannot fail in the current environment because `torch` is not installed; it becomes meaningful once T4's `bge-m3` group is installed. No action needed now.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/ingestion/embedding.py` with frozen `EmbedderInfo`, the `Embedder` Protocol (`embed_documents` / `embed_query`) and `FakeEmbedder` (`fake-hash-embedder`, revision `1`, default size 64, SHA-256 counter-expanded, L2-normalized, dense-only); tests in `packages/rag/tests/ingestion/test_embedding.py`.
  - Verified by: `make test-unit`, `make verify`, `make test-integration`; 14 new tests cover determinism (incl. Malayalam text), sizes 1–1024, normalization, query vs document agreement, fake identity, protocol conformance, invalid size, no PyTorch import.
  - Worth your attention: vector size below 1 raises `IngestionConfigurationError` (small choice not in the spec); `FakeEmbedder.info.settings` is empty. Two MINOR test-tightness notes above.
- Usage: 70K tokens · 9 tool uses · 1:56

### User decision
- 2026-10-15 — approved


## T4 — round 1

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/bge_m3.py` (new: `BgeM3Embedder`), `packages/rag/tests/ingestion/test_bge_m3.py` (new), `packages/rag/pyproject.toml` (`bge-m3` optional group: `sentence-transformers>=3.0.0`), `uv.lock` (additions only; resolves torch 2.14.1, transformers 5.20.0, sentence-transformers), `Makefile` (`setup-bge-m3` target and `.PHONY`), `tasks.md` (T4 boxes ticked, State). Earlier blocks in this file were not modified (append only).
- Resolved BGE-M3 revision (for `config/ingestion.yaml` in T8): `5617a9f61b028005a4858fdac845db406aefb181`. Source: `https://huggingface.co/api/models/BAAI/bge-m3` and `.../revision/main` both returned this `sha` (lastModified 2024-07-03) on 2026-10-15. Not written to any config file yet (`config/ingestion.yaml` is T8). The smoke test uses it as the default, overridable by `W2A_BGE_M3_REVISION`.
- Verification run: `make verify` -> exit 0 (ruff, pyright, skills-check, validate-knowledge, 233 passed, 1 skipped); `make test-unit` -> 220 passed, 1 skipped, 13 deselected; skipped test is the BGE-M3 smoke test (reason: smoke not enabled / optional group not installed). `pytest test_bge_m3.py` -> 11 passed, 1 skipped. `uv pip list` confirms torch and sentence-transformers are NOT installed in the default environment. Only `uv lock` was run for the new group (no `make setup-bge-m3`, no model download).
- Not run: the real-model smoke test and `make setup-bge-m3` (user-owned, per task). Not verified that `uv sync --all-packages --group dev --extra bge-m3` resolves/installs end to end (lock resolves; install not exercised).
- Notes: revision refusal covers None, empty, whitespace, `main`, `latest` (case-insensitive). Model loaded lazily once per instance via `_load_model` (import inside it with targeted pyright ignore; `ImportError` -> `OptionalDependencyError` naming `make setup-bge-m3`); `encode(..., batch_size, normalize_embeddings=True)`. Batch size is a constructor argument (default 16; config wiring is T8); batch size below 1 raises `IngestionConfigurationError` (small choice). `make format` also reformatted an unrelated file, `packages/rag/tests/test_content_hash.py`; that change was reverted. Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 78K tokens · 13 tool uses · 1:43

### Review
- Model: claude-opus-5-5 (matches BEST tier; different model from the implementer)
- Verdict: PASS
- Commands: `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check, validate-knowledge, 234 collected: 233 passed, 1 skipped); `make test-unit` → pass (220 passed, 1 skipped, 13 deselected); `pytest packages/rag/tests/ingestion/test_bge_m3.py -rs` → 11 passed, 1 skipped (reason: "optional 'bge-m3' group not installed; run `make setup-bge-m3`"); `make test-integration` → pass (13 collected, 13 passed). Independent checks: `find_spec` for `torch`, `sentence_transformers`, `transformers`, `numpy` in `.venv` → all absent, before and after `make verify`; HF hub API `api/models/BAAI/bge-m3`, `.../revision/main` and `.../commits/main` (2026-10-15) all give head `5617a9f61b028005a4858fdac845db406aefb181` (2024-07-03), matching the notes; `uv.lock` parsed old vs new: 0 removed lines, 0 packages removed or changed except `way2australia-rag` gaining the `bge-m3` extra (`sentence-transformers>=3.0.0`, marker `extra == 'bge-m3'`), 41 packages added, lock header unchanged, `uv lock --check` → consistent. Protected paths (`evaluation/ knowledge/ config/`) unchanged. Real-model smoke test and `make setup-bge-m3` not run (user-owned per the task's verification block).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R6] The smoke test hard-codes the revision SHA as its default; once T8 creates `config/ingestion.yaml` the SHA lives in two places. T8 should read the default from the config.
  - F2 [MINOR, IMPLEMENTATION, R6/R7] `BgeM3Embedder.info.settings` is empty; the design example lists `batch_size`/`max_length` there. Batch size does not change vectors, so this is harmless unless T5 decides those settings belong in `IndexSettings`.
  - F3 [MINOR, IMPLEMENTATION, R6] "Loaded once per process" (R6) is met per instance (as the task says); this holds as long as the T8 entry point builds one embedder per run.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/ingestion/bge_m3.py` (`BgeM3Embedder`: `BAAI/bge-m3`, 1024, dense, normalized; refuses missing/`main`/`latest` revisions; lazy one-time load with `revision=`; batched `encode`); tests in `packages/rag/tests/ingestion/test_bge_m3.py`; `bge-m3` optional extra in `packages/rag/pyproject.toml`; `make setup-bge-m3` in `Makefile`; `uv.lock` additions only.
  - Verified by: `make verify`, `make test-unit`, `make test-integration`; confirmed PyTorch/sentence-transformers absent from the default env; confirmed the pinned SHA against the Hugging Face API myself; checked that the lock diff only adds packages.
  - Worth your attention: pinned revision `5617a9f61b028005a4858fdac845db406aefb181` (goes into `config/ingestion.yaml` in T8). The lock now includes Linux CUDA wheels (torch 2.14.1, nvidia-*), so `make setup-bge-m3` is a large download, and `make setup` removes the group again. The real-model smoke test is yours to run: `make setup-bge-m3`, `W2A_RUN_BGE_M3_SMOKE=1 make test-unit`, then `make setup`. Three MINOR notes above.
- Usage: 86K tokens · 19 tool uses · 2:06

### User decision
- 2026-10-16 — approved


## T5 — round 1

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/settings.py` (new: frozen `IndexSettings`, `build_index_settings`, `compare`, `mismatch_message`, `collection_name`), `payload.py` (new: frozen `PointPayload`, `build_payload`, `IDENTITY_FIELDS`), `identity.py` (new: `INGESTION_NAMESPACE`, `point_id`), `packages/rag/tests/ingestion/test_index_contract.py` (new), `tasks.md` (T5 boxes ticked, State). Earlier blocks in this file were not modified (append only).
- Verification run: `make verify` -> exit 0 (ruff, pyright, skills-check, validate-knowledge, 257 passed, 1 skipped; bge-m3 group not installed); `make test-unit` -> 244 passed, 1 skipped, 13 deselected; `make test-integration` -> 13 passed.
- Notes: T4 F2 decision: `batch_size` and `max_length` are NOT index settings. They do not change vectors, and the design's `IndexSettings` field list does not include them; `EmbedderInfo.settings` stays informational. `IndexSettings` also carries `schema_version` "1.0". `build_index_settings(index_version, embedder_info, chunker, hash_contract=HASH_CONTRACT)` takes the index version directly because `config/ingestion.yaml` does not exist until T8. `collection_name(base, index_version)` is the single derivation. `mismatch_message` is the refusal text (lists each differing field, points to a new `index_version` in `config/ingestion.yaml`) for T6 to raise via `IndexSettingsMismatchError`. `INGESTION_NAMESPACE` = `533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2` (uuid4, generated once); DECISIONS.md entry is left to the task that records decisions (not edited here). `PointPayload` enum fields are stored as strings; `lote_languages` as a list. `make format` reformats the unrelated `packages/rag/tests/test_content_hash.py`; that change was reverted each time. Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 94K tokens · 26 tool uses · 34:27

### Review
- Model: claude-opus-5-5 (matches BEST tier `Opus`; no mismatch; different model from the implementer)
- Verdict: PASS
- Commands: `make test-unit` → pass (244 passed, 1 skipped, 13 deselected); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 257 passed, 1 skipped); `make test-integration` → pass (13 passed, 245 deselected); `git status --porcelain -- evaluation/ knowledge/ config/` → empty.
- Checks: `PointPayload` fields equal the design's 17-row table exactly (pinned by `test_payload_field_set_equals_design_table`, `extra="forbid"`). Hash-coverage subset test is real: non-identity fields (13) ⊆ `CONTENT_HASH_METADATA_FIELDS` ∪ {`chunk_text`, `content_hash`}, and that set excludes `persona_scope`, `last_reviewed_at`, `introduced_in_release`, so adding any uncovered field fails. `persona_scope`, `last_reviewed_at` and eligibility-only fields absent. `IndexSettings` fields match the design plus `schema_version` "1.0" (required by the task). `compare()` iterates all model fields except `hash_contract`; per-field and exhaustive tests cover it. `collection_name()` is the only `<base>-<index_version>` derivation in the package. `INGESTION_NAMESPACE` documented in `identity.py` and pinned; the DECISIONS.md entry is explicitly listed in T9's checklist, so deferral is acceptable. `batch_size`/`max_length` excluded from `IndexSettings`: consistent with the design's field list and config (no `max_length` in config or code).
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R9] `test_point_id_distinct_across_document_section_and_position` lists `("doc_a", "main1", 0)` twice and asserts `len(ids) == 6` over 7 entries; correct but misleading. → Remove the duplicate and assert 6 over 6 entries (any later round).
  - F2 [MINOR, IMPLEMENTATION, R7] `settings.py` docstring says `max_length` never changes vectors; that holds only while inputs fit the model's token limit (true today: 2000-char cap, `max_length` not configurable). → If `max_length` ever becomes configurable, revisit whether it belongs in `IndexSettings`.
- Summary for user (PASS only):
  - Changed: new `ingestion/settings.py` (frozen `IndexSettings`, `build_index_settings`, `compare` ignoring `hash_contract`, `mismatch_message`, `collection_name`), `ingestion/payload.py` (frozen 17-field `PointPayload`, `build_payload`, `IDENTITY_FIELDS`), `ingestion/identity.py` (`INGESTION_NAMESPACE`, UUIDv5 `point_id`), tests in `packages/rag/tests/ingestion/test_index_contract.py`.
  - Verified by: `make test-unit`, `make verify`, `make test-integration` (counts above).
  - Worth your attention: `INGESTION_NAMESPACE` = `533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2` is now fixed forever; its DECISIONS.md entry lands in T9. `batch_size`/`max_length` are not index settings (per design). Two MINOR test/doc nits above.
- Usage: 86K tokens · 12 tool uses · 1:45

### User decision
- 2026-10-16 — approved


## T6 — round 1

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/store.py` (new: `QdrantIndexStore`, `IndexPoint`, `IndexedDocument`), `packages/rag/tests/ingestion/test_store.py` (new, in-memory), `packages/rag/tests/ingestion/test_store_integration.py` (new, marker `integration`), `packages/rag/pyproject.toml` (`qdrant-client>=1.19.0,<2.0`), `uv.lock` (additions only: qdrant-client 1.19.1 and its dependencies), `packages/rag/tests/ingestion/test_index_contract.py` (T5 F1: duplicate tuple removed from the point-ID distinctness test), `tasks.md` (T6 boxes ticked, State). Earlier blocks in this file were not modified (append only).
- Verification run: `make verify` -> exit 0 (ruff, pyright, skills-check, validate-knowledge, 277 passed, 3 skipped; bge-m3 group not installed, no Docker needed; with Qdrant stopped the 2 integration tests and the BGE-M3 smoke test are the skips). `make test-unit` -> 264 passed, 1 skipped, 15 deselected. `make test-integration` with Qdrant down -> 13 passed, 2 skipped (reason: "Qdrant is not reachable at http://localhost:6333 (...); run `docker compose up -d qdrant`").
- Integration test run for real: Docker Desktop was not running; I started it (`open -a Docker`), ran `docker compose up -d qdrant` (image `qdrant/qdrant:v1.19.2`) and `make test-integration` -> 15 passed (13 existing + the 2 new tests against live Qdrant). `GET /collections` was empty before and after the run (no stray collections; the test fixture deletes its unique `w2a-it-<hex>` main and `-settings` collections). I then ran `docker compose stop qdrant` (container stopped, volume kept).
- Notes / decisions: `QdrantIndexStore(client, collection_base, index_version)` derives the name via `collection_name()`; `ensure_collection` raises `IngestionConfigurationError` if `settings.index_version` differs from the store's. Settings point ID is a fixed constant UUID (`SETTINGS_POINT_ID`). `IndexPoint(point_id, vector, payload: PointPayload)` is the argument type of `replace_document` (design said only "points"). Startup table: main absent -> create main (named `dense` COSINE vector, five keyword indexes), create settings collection, write settings (also covers a leftover settings collection); exists + settings equal -> proceed; differs -> `IndexSettingsMismatchError` via `mismatch_message`; non-empty without settings -> refuse (unknown provenance); empty without settings -> write settings. Nothing is ever deleted. `read_state` scrolls with a payload include list (`document_id`, `document_version`, `content_hash`) and no vectors, paginating; if one document's points disagree on version or hash (half-written state) it reports version 0 and empty hash so the service sees it as changed (small choice, T7 must treat it as update). `replace_document` with no points only deletes. Client 1.19.1 vs server v1.19.2: the client warns "Failed to obtain server version" against the live server in tests (compatibility check only, harmless); in-memory "payload indexes have no effect" warning is filtered in `test_store.py`. `make setup` was run to install qdrant-client into the dev env. `make format` reformats unrelated `packages/rag/tests/test_content_hash.py`; reverted. Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 97K tokens · 17 tool uses · 5:01

### Review
- Model: claude-opus-5-5 (matches BEST tier `Opus`; no mismatch; different model from the implementer)
- Verdict: PASS
- Commands: with Qdrant stopped and the bge-m3 group absent (`import torch` / `import sentence_transformers` fail): `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 277 passed, 3 skipped); `make test-unit` → pass (264 passed, 1 skipped, 15 deselected); `pytest -m integration -rs` → 13 passed, 2 skipped, reason "Qdrant is not reachable at http://localhost:6333 (ResponseHandlingException); run `docker compose up -d qdrant`". Then `docker compose up -d qdrant` (v1.19.2) + `make test-integration` → pass (15 passed, 265 deselected). `git status --porcelain -- evaluation/ knowledge/ config/` → empty. `git diff HEAD -- uv.lock` → 138 insertions, 0 deletions (adds qdrant-client 1.19.1, grpcio, h2, hpack, hyperframe, portalocker, pywin32; no existing pin changed).
- Checks: Qdrant was stopped at review start (container exited, `/collections` unreachable). After starting it, `/collections` was empty before and after the run. I also ran a scratch probe (outside the repo) of `ensure_collection` against the live server: named `dense` COSINE vector and keyword payload indexes on all five fields confirmed; the probe deleted its collections. I then ran `docker compose stop qdrant`: container exited, no collections left. The five startup-table rows match the design; nothing in `store.py` deletes a collection; replace deletes by a `document_id` filter, then makes one upsert; `delete_documents` uses `MatchAny`; `read_state` scrolls an include-list payload with `with_vectors=False` and paginates (tested with 300 points). Implementer decisions accepted: version 0/empty hash for an internally inconsistent document always differs from its target, so the document is rewritten (T7 also compares point-ID sets); `IndexPoint` is a reasonable concrete type for the design's "points"; the `index_version` guard keeps the derived collection name and the recorded label in agreement (R7 single source). T5 F1 fix in `test_index_contract.py` is correct.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R10] No test covers the `read_state` inconsistent-document fallback (version 0, empty hash). → Add a unit test (later round, or in T7's half-written-document tests).
  - F2 [MINOR, IMPLEMENTATION, R13] No test asserts that the payload indexes or the `dense` vector config exist on the server. In-memory mode cannot show indexes, and the integration test does not inspect `get_collection().payload_schema`. Verified manually above. → Add a `payload_schema`/vector-params assertion to the integration test.
  - F3 [MINOR, IMPLEMENTATION, R7] A malformed or foreign settings payload makes `_read_settings` raise a pydantic `ValidationError` instead of an `IngestionError`. → T8's CLI must map it to exit 2, or wrap it as `IndexSettingsMismatchError`.
  - F4 [MINOR, IMPLEMENTATION, R7] If creating the main collection succeeds but payload-index creation or the settings write fails, the next run takes the "exists, empty, no settings" row and writes settings without recreating the indexes. Edge case, does not affect correctness. → Optionally re-ensure the payload indexes on that row.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/ingestion/store.py` (`QdrantIndexStore` with `ensure_collection`, `read_state`, `replace_document`, `delete_documents`; `IndexPoint`, `IndexedDocument`); settings stored in a companion `<collection>-settings` collection; tests in `packages/rag/tests/ingestion/test_store.py` (in-memory) and `test_store_integration.py` (Docker, marker `integration`); `qdrant-client>=1.19.0,<2.0` added to `packages/rag/pyproject.toml`; `uv.lock` only gains packages.
  - Verified by: `make verify` with no Docker and no bge-m3 group, `make test-unit`, `make test-integration` with Qdrant down (2 clean skips) and up (15 passed); live check of the vector and payload-index config. Qdrant was stopped again afterwards and no collections were left.
  - Worth your attention: the store never deletes collections, and a settings mismatch refuses with no writes. The installed client is 1.19.1 against server v1.19.2. It warns "Failed to obtain server version" against the live server; the warning is harmless. Four MINOR notes above.
- Usage: 97K tokens · 18 tool uses · 3:15

### User decision
- 2026-10-16 — approved


## T7 — round 1

### Implementation
- Model: claude-sonnet-5-5 (matches BEST_MINUS_ONE tier; no mismatch)
- Files changed: `packages/rag/src/way2australia_rag/ingestion/service.py` (new: `IngestionService`, `RunReport`, `DocumentFailure`), `packages/rag/tests/ingestion/test_service.py` (new, 17 tests, in-memory Qdrant), `packages/rag/src/way2australia_rag/ingestion/store.py` (public `index_version` attribute; `_read_settings` wraps a pydantic `ValidationError` into `IndexSettingsMismatchError`), `tasks.md` (T7 boxes ticked, State). Earlier blocks in this file were not modified (append only).
- Verification run: `make verify` -> exit 0 (ruff, pyright 0 errors, skills-check, validate-knowledge, 296 passed, 3 skipped; no Docker running, bge-m3 group not installed); `make test-unit` -> 283 passed, 1 skipped, 15 deselected; `make test-integration` (Qdrant down) -> 13 passed, 2 skipped (clean Qdrant-unreachable skips). Docker/Qdrant was not started for this task; no container or collection left.
- Notes / decisions: Service follows design steps 1-7. Deletions run first (one `delete_documents` call over `sorted(state - target)`), then per document in `document_id` order: chunk, compute expected point IDs, classify (not in state = added; hash, version or point-ID set differs = updated; else unchanged); changed documents are embedded in `batch_size` batches (wrong vector count raises), then `replace_document`, each in its own try/except. T6 F1: the version 0 / empty-hash fallback is classified as updated (covered by `test_inconsistent_state_is_classified_as_updated`, which corrupts one point's hash in place). T6 F3: handled in the store, so any caller gets an `IngestionError` subclass (`IndexSettingsMismatchError`, message lists invalid field names only, never payload values); T8's CLI maps `IngestionError` to exit 2. `RunReport.failures` is a list of `DocumentFailure(document_id, reason)`; `reason` is the exception class name, plus the message only for `IngestionError` subclasses (path-free by contract), so no document text, paths or client messages leak. A failed bulk delete records a failure for each stale `document_id` and the run continues. Added/updated/deleted lists contain only successful documents; a failed document appears only in `failures` (so it is retried next run). Settings mismatch propagates as an exception before any write (test asserts zero embedding calls and zero writes). Tests use a `ListRepository` (in-memory `DocumentRepository`), a `CountingEmbedder`, and a `CountingStore` subclass for counting wrappers; the seed-corpus test uses the real `LocalDocumentRepository` over `knowledge/` with the fake embedder (13 documents, one chunk each, second run idempotent, no embedding calls, no writes); the security-fixture test uses the existing `security_repository` fixture. The seed-corpus test is a plain unit test (not marked `integration`). `make format` reformats unrelated `packages/rag/tests/test_content_hash.py`; reverted. Nothing under `knowledge/`, `config/` or `evaluation/` changed. Not committed.
- Usage: 105K tokens · 21 tool uses · 4:01

### Review
- Model: claude-opus-5-5 (matches BEST tier `Opus`; no mismatch; different model from the implementer)
- Verdict: PASS
- Commands: no Docker running, bge-m3 group absent. `make test-unit` → pass (283 passed, 1 skipped, 15 deselected); `make verify` → exit 0 (ruff clean, pyright 0 errors, skills-check OK, validate-knowledge OK, 296 passed, 3 skipped; `test_service.py` 19 collected incl. parametrized cases); `make test-integration` → exit 0 (13 passed, 2 skipped: Qdrant unreachable, as expected). `git status --porcelain -- evaluation/ knowledge/ config/` → empty. No Qdrant container started or left running.
- Checks: `service.py` gets its target only from `list_eligible_documents(repository, policy)` (never `list_documents()`); the test harness and the T8 CLI pass `GUEST_PUBLIC_POLICY`. Deletion is exactly `sorted(set(state) - target_ids)`. Classification compares `content_hash`, `document_version` and the expected point-ID set. `_embed` runs before `replace_document` in the same try block, so an embedding failure leaves the old points in place. The test checks this: same point IDs, old hash, `a` not in `replaced`. Per-document try/except lets the run continue past a failed document. The counting wrappers are real: `CountingStore` subclasses the real store and counts `replace_document`/`delete_documents`, which are the service's only write paths, and `ensure_collection` writes settings only on create or when they are absent. Idempotency asserts `calls == 0`, `replaced == []` and `deleted == []`, both on synthetic documents and on the seed corpus (13 documents, one chunk each). Ineligible documents (staff, user_private, synthetic, pending_review, retrieval-disabled, deprecated) and the security fixtures (which load, per `test_eligibility.py`) never reach the index. The leak test shows an embedder message carrying "secret document text" is reduced to `RuntimeError`. The report dump has no body text and no `/`. Store change: `ValidationError` is wrapped in `IndexSettingsMismatchError` with field names only (tested: payload value absent from the message); the public `index_version` is used by the service and the report. Implementer decisions accepted: a failed document appears only in `failures`, so it is retried next run and the CLI exits 1. The failure reason is the class name only for non-`IngestionError` exceptions, because client and model messages can carry URLs or text; `IngestionError` messages are path-free by contract.
- Findings:
  - F1 [MINOR, IMPLEMENTATION, R10] `self._chunker.chunk(document)` and the point-ID computation run outside the per-document try/except, so an unexpected chunker exception would abort the whole run instead of being recorded as one document's failure. `HeadingChunker.chunk` has no raising path today besides internal asserts. → Move chunking and classification inside the per-document try, or accept the risk explicitly.
  - F2 [MINOR, IMPLEMENTATION] `QdrantIndexStore` now holds both `_index_version` and `index_version` with the same value. → Keep one attribute (for example, use `self.index_version` in `ensure_collection`).
  - F3 [MINOR, IMPLEMENTATION, R13] No test exercises the "embedder returned a wrong number of vectors" guard. The service-level counting wrappers do not cover raw client writes (sufficient today, since the store's only other write is in `ensure_collection`). → Optionally add a short-result embedder test.
  - F4 [MINOR, IMPLEMENTATION] Design "Observability" asks for INFO logs at stage boundaries; the service logs only WARNING on failures. → Add INFO lines (counts and IDs only), here or in T8.
  - F5 [MINOR, IMPLEMENTATION, R13] `test_security_fixtures_never_reach_the_index` does not itself assert that the fixtures loaded (`list_documents()` non-empty), so it relies on `test_eligibility.py` to be non-vacuous. → Optionally assert `len(await repo.list_documents()) == 2` in the test.
- Summary for user (PASS only):
  - Changed: new `packages/rag/src/way2australia_rag/ingestion/service.py` (`IngestionService`, `RunReport`, `DocumentFailure`): deletes non-eligible `document_id`s, classifies documents as added, updated or unchanged by hash, version and point-ID set, embeds before replacing, and records each failure while the run continues. `store.py` now exposes `index_version` and turns a malformed settings payload into `IndexSettingsMismatchError`. New tests in `packages/rag/tests/ingestion/test_service.py`.
  - Verified by: `make verify` (296 passed, 3 skipped), `make test-unit`, `make test-integration` (Qdrant down, 2 clean skips). The seed corpus indexes 13 documents with one chunk each, and a second run makes zero embedding calls and zero writes.
  - Worth your attention: a failed document appears only under failures, not under added or updated. Failure reasons show only the exception class unless it is an ingestion error. The five MINOR findings above can be done in a later round or in T8. The most relevant is F1 (chunking sits outside the per-document error handling).
- Usage: 95K tokens · 15 tool uses · 2:46

### User decision
- 2026-10-16 — approve
