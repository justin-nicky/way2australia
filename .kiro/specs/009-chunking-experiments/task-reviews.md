# Spec 009 — Task reviews

## T1 — round 1

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/pyproject.toml`, `uv.lock` — base deps `tokenizers`, `huggingface_hub`
  - `packages/rag/src/way2australia_rag/ingestion/tokenization.py` (new), `guard.py` (new)
  - `packages/rag/src/way2australia_rag/ingestion/config.py`, `service.py`, `cli.py`
  - `packages/rag/src/way2australia_rag/lexical/build.py`, `cli.py`, `freshness.py`
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` — `verify_fresh` / `production_entries` need tokenizer (T3 may refine standalone path)
  - `packages/rag/src/way2australia_rag/evaluation/security_index.py`, `security_eval.py`
  - Tests: `tests/ingestion/test_tokenization.py`, `test_guard.py`, `test_service.py`; `tests/lexical/test_lexical_build.py`; caller updates in lexical/retrieval/evaluation tests
  - `packages/rag/tests/ingestion/fixtures/bge_m3/` (tokenizer.json, sentence_bert_config.json)
  - `graphify-out/` (graphify update)
- Verification run:
  - `make verify` → pass (1046 passed, 2 skipped)
  - `uv tree --package way2australia-rag --no-dev` → `huggingface-hub`, `tokenizers` in base; `torch` only under optional `bge-m3` extra
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass
- Notes:
  - `IngestionService` takes `tokenizer` and optional `chunk_token_cap`; heading v1 uses cap `None`.
  - `ChunkTooLongError` reason string is `chunk_too_long: section_id=… position=… tokens=… limit=…` (no chunk text).
  - Standalone BM25 open builds tokenizer via `build_tokenizer` so freshness matches lexical build until T3’s `chunker_identity`-only path.
- Usage: n/a (Cursor) · 169 tool uses · 24:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: FAIL
- Commands: `make verify` with `HF_HOME=/tmp/w2a-t1-empty-hf`, `HF_HUB_CACHE` and `HUGGINGFACE_HUB_CACHE` under that directory, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1` → fail (38 failed, 990 passed, 2 skipped, 18 errors; 1048 collected). Lint, pyright, skills-check, validate-knowledge and validate-evaluation passed before pytest. `python3 -m uv tree --package way2australia-rag --no-dev` → `huggingface-hub` and `tokenizers` are base dependencies; `torch` appears only under the `bge-m3` extra. `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4038 nodes). `make test-integration` → pass (24 passed, 1024 deselected).
- Findings: F1 [BLOCKING, IMPLEMENTATION, R1] `ingestion/cli.py`, `lexical/cli.py`, and both standalone paths in `retrieval/opening.py` call `build_tokenizer` on the config file's embedder. `config/ingestion.yaml` has `provider: bge_m3`, so `--embedder fake` and `open_retrieval(..., provider="fake")` still construct `BgeM3Tokenizer`. The fake embedder is then guarded with the BGE-M3 tokenizer, and `fake_max_sequence_length` is unused on those runs. With the Hugging Face cache hidden, `make verify` fails as above (including `test_open_retrieval_bm25_builds_no_embedder_and_no_client` and `test_success_summary_and_digest_stability`). A cache-present run can pass; this machine has the BGE tokenizer cached, which hides the dependency. → Pass `build_tokenizer` an embedder config whose `provider` is the provider selected for that run (`model_copy(update={"provider": provider})` when they differ). `provider` `fake` must yield `FakeTokenizer` and leave the hub untouched. Re-run `make verify` with `HF_HUB_OFFLINE=1` and an empty `HF_HOME`. Keeping a tokenizer on `verify_fresh` until T3 is fine when it follows that same provider.
- Findings: F2 [MAJOR, IMPLEMENTATION, R2] `test_oversized_chunk_refuses_production_entries` expects `ChunkTooLongError` from `production_entries`, then asserts `tmp_path / "lex.sqlite"` is absent. The test never writes that path, and it never calls the lexical CLI or `build_lexical_index`, so exit 2 and "no file written" are unlocked. The CLI returns 2 today because `ChunkTooLongError` is an `IngestionError` and `build_lexical_index` runs only after `production_entries`. → Drive `lexical.cli.main` with an oversized chunk, assert exit code 2, and assert the target file is absent (or unchanged if one was already there).
- Findings: F3 [MINOR, IMPLEMENTATION, R2] The new service tests check the run report for chunk text and for the chunker exception message. They do not capture logs. The service log line is the exception class name. → Assert with `caplog` that the chunk text and the chunker exception message are absent from the log.
- Usage: n/a (Cursor) · 98 tool uses · 10:00

## T1 — round 2

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/tokenization.py` — `embedder_for_run()`; callers pass run-selected provider into `build_tokenizer`
  - `packages/rag/src/way2australia_rag/ingestion/cli.py`, `lexical/cli.py`, `retrieval/opening.py` — use `embedder_for_run(config.embedder, provider)`
  - `packages/rag/tests/lexical/test_lexical_cli.py` — `test_oversized_chunk_refuses_cli_exit_2_and_writes_no_file`
  - `packages/rag/tests/lexical/test_lexical_build.py` — drop vacuous sqlite assertion from production_entries test
  - `packages/rag/tests/ingestion/test_service.py` — `caplog` on chunk-text / chunker-message tests
  - `packages/rag/tests/evaluation/test_strategy_eval.py` — `lexical_env` patches `opening.build_tokenizer` so bm25 eval tests stay hub-free while keeping bge dense identity
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-t1-empty-hf` `HF_HUB_CACHE`/`HUGGINGFACE_HUB_CACHE` under that dir, `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1047 passed, 2 skipped)
  - `uv tree --package way2australia-rag --no-dev` → `huggingface-hub`, `tokenizers` in base; `torch` only under optional `bge-m3` extra
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass
- Notes:
  - F1: `--embedder fake` / `open_retrieval(..., provider="fake")` now construct `FakeTokenizer` and never touch the hub; evaluation bm25 tests still record bge dense identity but patch tokenizer construction in `opening` only within `lexical_env` (eval CLI has no embedder override).
- Usage: n/a (Cursor) · 83 tool uses · 7:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t1-r2-hf` `HF_HUB_CACHE=/tmp/w2a-t1-r2-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t1-r2-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t1-r2-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1049 collected, 1047 passed, 2 skipped). `make test-integration` → pass (24 passed, 1025 deselected). `python3 -m uv tree --package way2australia-rag --no-dev` → `huggingface-hub` and `tokenizers` are base dependencies; `torch` appears only under the `bge-m3` extra. `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4046 nodes).
- Findings: none
- Summary for user (PASS only):
  - Changed: Chunk length is measured with a tokenizer that follows the embedder selected for that run. `--embedder fake` uses `FakeTokenizer` and does not touch the Hugging Face hub. Ingestion counts tokens after chunking and before embedding; a too-long chunk fails that document only, with section, position, token count and limit, and no chunk text in the report or logs. The lexical build uses the same guard and exits 2 without writing the file.
  - Verified by: `make verify` with `HF_HUB_OFFLINE=1` and an empty Hugging Face cache (1047 passed, 2 skipped opt-in BGE-M3 smokes); `make test-integration` (24 passed); `uv tree` shows `tokenizers` and `huggingface-hub` without `torch` in the base set.
  - Worth your attention: Standalone BM25 freshness still builds a tokenizer until T3. Evaluation tests whose config provider is `bge_m3` stub that construction so `make verify` stays offline; a real `eval-retrieval` BM25 run still needs the cached tokenizer files. The security index uses `FakeTokenizer` directly, matching its fake-embedder-only harness.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/ingestion/cli.py` → `main`: builds the tokenizer for the selected provider and passes it into ingestion.
    2. `packages/rag/src/way2australia_rag/ingestion/tokenization.py` → `embedder_for_run`, `build_tokenizer`: `fake` yields `FakeTokenizer`; `bge_m3` loads tokenizer files only.
    3. `packages/rag/src/way2australia_rag/ingestion/guard.py` → `check_chunks`: refuses the first chunk over the limit.
    4. `packages/rag/src/way2australia_rag/ingestion/service.py` → `IngestionService.run`: chunking, the guard and point IDs sit inside the per-document try.
    5. `packages/rag/src/way2australia_rag/lexical/cli.py` → `main`: same tokenizer selection; a violation exits 2 before any file is written.
    6. `packages/rag/src/way2australia_rag/lexical/build.py` → `production_entries`: runs the same guard.
    7. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`: standalone and fallback freshness follow the run's provider.
    8. `packages/rag/src/way2australia_rag/ingestion/config.py` → `EmbedderConfig.fake_max_sequence_length`.
    9. Tests: `test_tokenization.py`, `test_guard.py`, `test_service.py` (`caplog`), `test_lexical_cli.py` (exit 2, no file).
    10. Supporting edits: lexical freshness signature, security index/eval wiring, `pyproject.toml`, `uv.lock`, `graphify-out/`.
- Usage: n/a (Cursor) · 79 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved

## T2 — round 1

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/chunking.py` — `ChunkerIdentity`, shared sentence-end and token-budget splitting, `HeadingChunker.identity`, `legacy_chunker_max_chunk_chars`
  - `packages/rag/src/way2australia_rag/ingestion/structure.py` (new), `recursive.py` (new)
  - `packages/rag/src/way2australia_rag/ingestion/settings.py`, `lexical/cli.py`, `lexical/store.py`, `evaluation/security_index.py` — legacy max-chars via identity until T3
  - Tests: `test_structure.py`, `test_recursive.py`, `snapshot_support.py`, `test_chunking.py` (protocol/identity); snapshots under `tests/ingestion/snapshots/`
  - `.kiro/specs/009-chunking-experiments/design.md` — `## As-built notes` with BGE-M3 seed counts
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-empty` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1075 passed, 2 skipped)
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4135 nodes)
- Notes:
  - BGE-M3 cached tokenizer on seed corpus: `recursive` v1 128/16/title → counts `3 4 3 3 3 4 3 2 2 2 3 3 1`, total 36, max 4/doc (prototype table had 34; T6 `chunk_stats` is promotion record).
  - `DuplicateSectionError` and prefix-too-long surface as per-document `IngestionError` until ingestion maps `duplicate_section` explicitly (if needed in T3).
  - Production paths still build `HeadingChunker` only; new chunkers are tested and snapshotted, wired in T3.
- Usage: n/a (Cursor) · 121 tool uses · 5:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: FAIL
- Commands: `HF_HOME=/tmp/w2a-t2-empty-hf` `HF_HUB_CACHE=/tmp/w2a-t2-empty-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t2-empty-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t2-empty-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1077 collected, 1075 passed, 2 skipped). `make test-integration` → pass (24 passed, 1053 deselected). `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4137 nodes). Read-only BGE-M3 check of the cached tokenizer at the pinned revision: seed `recursive` v1 128/16/title counts `3 4 3 3 3 4 3 2 2 2 3 3 1`, total 36, max 4, no chunk over 128, minimum slack 4.
- Findings: F1 [BLOCKING, IMPLEMENTATION, R3/R4] Packed chunk text is not a span of the source. `split_to_token_budget` splits an oversized line with `str.split` and `_merge_line_pieces` joins those pieces with `\n`. A body of repeated `word ` at cap 32 comes back as `word\nword\n…` (77 newlines; no chunk is a substring of the source). A run of sentences takes the same path (5 chunks, 25 newlines, not substrings). `RecursiveChunker._recursive_split` uses `str.split`, which drops `\n\n` and `\n`, and `_join_units` inserts a single space when neither side still contains a newline, so two paragraphs or two lines packed into one chunk lose their break. On the 13 seed documents at fake target 32 / overlap 4 / title, all 13 have at least one chunk body that is not a substring of `document.content` (284 chunks). → Keep each unit as a span of the original string, with the separator it was split on still attached, and concatenate those spans. Sentence-end splits drop the whitespace after `.` `?` `!` `।` as the design specifies; other separators stay the characters they were. The whitespace fallback rejoins with spaces. Add tests that fail on today's output: an oversized `word ` block stays space-separated; two paragraphs packed together still contain `\n\n`; two lines packed together still contain `\n`. Regenerate the v1 snapshots after the fix (nothing is indexed with these chunkers yet). Re-measure the BGE-M3 128/16/title seed counts and replace the T2 line under `## As-built notes`.
- Findings: F2 [MAJOR, IMPLEMENTATION, R3/R4] Budgets sum per-piece `count()` values. Structure `_pack_blocks` uses `body_cap = cap - (count(prefix) + 2)` and then `count(body)`. The design counts `prefix + "\n\n" + body` and says tokens are counted on the composed string. Recursive uses `body_budget = target_tokens - count(prefix)` and then `count(piece)`; the design counts `prefix + chunk`. `_overlap_tail` sums `count(unit)`, which includes special tokens; the design's overlap is the trailing units' combined count without special tokens. With `FakeTokenizer` and `overlap_tokens=4`, each overlapped suffix is one `termNNN` word (full count 4, content tokens 2); two such words are 4 content tokens and belong in the overlap. The cached BGE-M3 seed arm matches the as-built note and stays under 128, with every chunk at least 4 tokens short of the target. `test_no_chunk_above_target` and `test_overlap_at_most_configured` only check the upper bound with full `count()`, so they pass. → Accept a packed chunk only when `count` of the composed text is within the cap. For overlap, sum content tokens and take the longest trailing run that fits in `overlap_tokens` and still leaves the next composed chunk within `target_tokens`. Assert that overlap in content tokens.
- Findings: F3 [MINOR, IMPLEMENTATION, R3/R4] Several checked cases are only partly locked. The sentence-end tests call `split_at_sentence_ends` and cover `.` plus space, `।` plus space, and the non-splitting examples; they omit `?`, `!`, and a newline (the function does handle those). `test_section_ids_stable_when_other_sections_change` inserts a section and does not reorder or remove one. `test_malayalam_paragraph_packs` uses two short sentences that fit in the cap. `test_no_language_specific_literals_in_chunker_modules` does not read `chunking.py`, where the shared sentence-end set lives. → Extend those tests while fixing F1 and F2.
- Findings: F4 [MINOR, IMPLEMENTATION, R3] `DuplicateSectionError`'s message is `duplicate section_id …`, so a per-document ingestion failure is reported as `DuplicateSectionError: …`. The design's reason is `duplicate_section`, the same way `ChunkTooLongError` puts `chunk_too_long:` in its message. → Start the message with `duplicate_section:` and keep section id and document id only.
- Usage: n/a (Cursor) · 66 tool uses · 11:00

## T2 — round 2

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/chunking.py` — span-preserving `split_on_separator` / `split_on_spaces`; `split_to_token_budget` merges by concatenation and optional `fits`; whitespace fallback merges with spaces
  - `packages/rag/src/way2australia_rag/ingestion/structure.py` — `_compose_chunk` / `_pack_blocks` budget on composed prefix+body; `DuplicateSectionError` reason prefix
  - `packages/rag/src/way2australia_rag/ingestion/recursive.py` — span splits, `chunk_fits` on prefix+body, overlap via `content_count`
  - `packages/rag/src/way2australia_rag/ingestion/tokenization.py` — `content_count` on fake and BGE-M3 tokenizers
  - Tests and snapshots: `test_structure.py`, `test_recursive.py`; regenerated `tests/ingestion/snapshots/*.json`
  - `.kiro/specs/009-chunking-experiments/design.md` — BGE-M3 as-built counts (total 34)
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-t2-r2-empty-hf` `HF_HUB_CACHE`/`HUGGINGFACE_HUB_CACHE`/`TRANSFORMERS_CACHE` under that dir, `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1078 passed, 2 skipped)
  - BGE-M3 seed `recursive` v1 128/16/title re-measure (cached tokenizer, read-only): counts `2 4 2 3 3 4 3 2 2 2 3 3 1`, total 34, max 4
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4153 nodes)
- Notes:
  - F1–F4: chunk bodies are source substrings (except whitespace-fallback joins); packing/overlap use composed and content token counts respectively.
- Usage: n/a (Cursor) · 79 tool uses · 7:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent. Incoming state was `task review (round 2)` (missing "in"); round-2 implementation is present, so the review continued.
- Verdict: FAIL
- Commands: `HF_HOME=/tmp/w2a-t2-r2b-empty-hf` `HF_HUB_CACHE=/tmp/w2a-t2-r2b-empty-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t2-r2b-empty-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t2-r2b-empty-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1080 collected, 1078 passed, 2 skipped). Lint, pyright, skills-check, validate-knowledge and validate-evaluation passed before pytest. `make test-integration` → pass (24 passed, 1056 deselected). `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4155 nodes). Read-only BGE-M3 check at the pinned revision: seed `recursive` v1 128/16/title counts `2 4 2 3 3 4 3 2 2 2 3 3 1`, total 34, max 4, largest chunk 127, no chunk over 128, and all 34 bodies are substrings of the source.
- Findings: F1 [BLOCKING, IMPLEMENTATION, R3/R4] Finer splits still drop a separator that a coarser split had kept, so packed text is not a span of the source. `split_on_separator` attaches `\n\n` and `\n`, then `split_at_sentence_ends` treats the attached newline after `.` `?` `!` `।` as sentence whitespace and drops it. One newline of the blank line remains as its own unit, and `_join_units` concatenates it, so the chunk has a single `\n` where the source has `\n\n`. When the next unit does not start with whitespace, `_join_units` inserts a space instead, so `self-paced mock.\n- Materials` becomes `self-paced mock. - Materials`. On the 13 seed documents at fake target 32 / overlap 4 / title, 20 of 278 chunk bodies (9 documents) are not substrings of `document.content`. `test_chunk_bodies_are_source_substrings` only checks a `word ` run and a short `\n\n` pair that fits in one unit; the seed snapshot records the current bodies, so it stays green. The BGE 128/16/title arm does not hit this path (34 substring bodies). → Keep the coarser separator attached through finer splits. Sentence-end splitting drops whitespace only inside the remainder, not a newline already attached by `split_on_separator`. `_join_units` may insert a space only where the dropped sentence whitespace was a space. Assert that every fake-32 seed body is a substring of `document.content` (whitespace-fallback space joins excepted), including `Way2Australia.\n\nCoaching` and `self-paced mock.\n- Materials`. Regenerate the v1 snapshots. Re-measure the BGE 128/16/title counts and replace the T2 as-built line if they move.
- Findings: F2 [MAJOR, IMPLEMENTATION, R4] The overlap tail is not shortened to what still fits in the next chunk. `_overlap_tail` takes the longest run whose summed `content_count` is at most `overlap_tokens`. If that full tail plus the next unit exceeds `target_tokens`, `_pack_with_overlap` sets `current = [unit]` and drops the tail. With `FakeTokenizer`, a title of 24 `abcd` words (prefix count 26), target 32 and overlap 10, body words `w00`–`w39` share 0 content tokens between neighbours. Each chunk holds 6 body words (content count 6 ≤ 10); six plus the next word is 33 tokens, while five trailing words plus the next word fit in 32. The `termNNN` case at overlap 4 correctly shares content count 4. `test_overlap_at_most_configured` only asserts `best <= overlap` with `context_prefix="none"`. → Drop units from the front of the tail until `count(prefix + tail + next unit) <= target_tokens`. Do not repeat a unit that alone exceeds the budget. Assert the content-token overlap on a case where the full tail does not fit and a shorter tail does.
- Findings: F3 [MINOR, IMPLEMENTATION, R3] `test_section_ids_stable_when_other_sections_change` inserts and reorders. It does not remove a section. Removing `# Gamma` from a document that also has `# Alpha` and `# Beta` leaves ids `alpha` and `beta`. → Assert that removal as well. F4 is fixed: `DuplicateSectionError` is `duplicate_section: section_id=… document_id=…`.
- Usage: n/a (Cursor) · 73 tool uses · 20:00

## T2 — round 3

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in `MODEL_PREFERENCES.md` — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/recursive.py` — `_overlap_for_next_chunk`: trim overlap tail from the front until `count(prefix + tail + next unit) <= target_tokens`; skip units that alone exceed the budget
  - `packages/rag/tests/ingestion/snapshot_support.py` — whitespace-collapse helpers; structure/recursive fidelity assertions on chunk bodies vs `document.content`
  - `packages/rag/tests/ingestion/test_recursive.py` — seed/synthetic fidelity tests; overlap shorter-tail case; section tests unchanged from round 2 extensions
  - `packages/rag/tests/ingestion/test_structure.py` — section removal stability; seed/synthetic fidelity tests
  - `packages/rag/tests/ingestion/snapshots/recursive-v1-seed-fake-32.json` — regenerated after overlap fix
  - `.kiro/specs/009-chunking-experiments/design.md` — T2 as-built BGE counts (round 3 re-measure, unchanged)
  - `.kiro/specs/009-chunking-experiments/tasks.md` — T2 test checkbox; state
  - `graphify-out/` (`graphify update`)
- Verification run:
  - `HF_HOME=/tmp/w2a-t2-r3-empty-hf` with `HF_HUB_CACHE` / `HUGGINGFACE_HUB_CACHE` / `TRANSFORMERS_CACHE` under that dir, `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (**1082** passed, 2 skipped)
  - BGE-M3 seed `recursive` v1 128/16/title re-measure (cached tokenizer, read-only): counts `2 4 2 3 3 4 3 2 2 2 3 3 1`, total 34, max 4, largest chunk 127
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4166 nodes)
- Notes:
  - Round 2 F1 (byte-exact substrings) replaced by the amended whitespace-collapsed body fidelity invariant; prefix/title lines are checked separately for `recursive` v1 with `title`.
  - Round 2 F2 overlap trimming implemented; F3 section removal asserted.
- Usage: n/a (Cursor) · 64 tool uses · 3:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t2-r3-review-hf` `HF_HUB_CACHE=/tmp/w2a-t2-r3-review-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t2-r3-review-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t2-r3-review-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1084 collected, 1082 passed, 2 skipped). `make test-integration` → pass (24 passed, 1060 deselected). `git status --porcelain -- evaluation knowledge config` → empty. `graphify update .` → pass (4168 nodes).
- Findings: none
- Summary for user (PASS only):
  - Changed: `structure` v1 and `recursive` v1 sit beside `heading` v1. Chunkers now carry a `ChunkerIdentity`. Structure chunks follow heading paths and pack blocks by the composed token count. Recursive chunks pack to a token target and overlap by the amended rule: the longest trailing run within `overlap_tokens` content tokens, then drop units from the front until the next chunk fits. Chunk bodies match the source after whitespace is collapsed; byte-exact substrings are not required.
  - Verified by: `make verify` offline with an empty Hugging Face cache (1082 passed, 2 skipped); `make test-integration` (24 passed). A read-only BGE-M3 remeasure of the 128/16/title arm on the 13 seed documents reproduced `2 4 2 3 3 4 3 2 2 2 3 3 1` (total 34, max 4, largest 127). Collapsed bodies on that arm are substrings of the source.
  - Worth your attention: Joins are normalized on purpose (`\n` between consecutive list items, `\n\n` otherwise; a sentence-end split drops the whitespace after the punctuation). On the round-2 overlap case (24-word title, target 32, overlap 10), each chunk holds 6 body words and repeats 5. `max_chunk_chars` is no longer on the `Chunker` protocol; heading v1 still stores it on `identity`, and the index, lexical, and security settings read it through `legacy_chunker_max_chunk_chars` until T3.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/ingestion/chunking.py` → `Chunker`, `split_at_sentence_ends`, `HeadingChunker.identity`: shared identity and the sentence-end rule; heading output is unchanged.
    2. `packages/rag/src/way2australia_rag/ingestion/structure.py` → `StructureChunker.chunk`: heading paths, block packing, composed token count.
    3. `packages/rag/src/way2australia_rag/ingestion/recursive.py` → `RecursiveChunker.chunk`, `_overlap_for_next_chunk`: separator split and the overlap trim.
    4. `packages/rag/src/way2australia_rag/ingestion/tokenization.py` → `FakeTokenizer.content_count`, `BgeM3Tokenizer.content_count`: overlap counted without special tokens.
    5. `packages/rag/tests/ingestion/test_structure.py`: fixtures, cap, section-id stability, collapsed fidelity.
    6. `packages/rag/tests/ingestion/test_recursive.py`: target, shorter-tail overlap, collapsed fidelity, seed snapshots.
    7. `packages/rag/tests/ingestion/snapshot_support.py` → `collapse_whitespace`: the shared fidelity check.
    8. Supporting edits: `legacy_chunker_max_chunk_chars` in settings, lexical CLI/store, and the security index; snapshots under `packages/rag/tests/ingestion/snapshots/`; design `## As-built notes`.
- Usage: n/a (Cursor) · 76 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved
