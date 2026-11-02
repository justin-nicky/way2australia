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

## T3 — round 1

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/chunker_build.py` (new), `config.py`, `settings.py`, `recursive.py`, `cli.py`, `store.py`
  - `packages/rag/src/way2australia_rag/lexical/store.py`, `freshness.py`, `build.py`, `cli.py`
  - `packages/rag/src/way2australia_rag/retrieval/opening.py`
  - `packages/rag/src/way2australia_rag/evaluation/cli.py`, `security_index.py`, `security_eval.py`
  - `experiments/configs/chunking/recursive-128.yaml`, `heading-idx-v1.yaml` (new)
  - Tests: `test_config_schema_11.py`, `test_recursive_integration.py`, updates across ingestion/lexical/retrieval/evaluation tests; `recursive-v1-seed-fake-32.json` regenerated (prefix `none` at 32 tokens); legacy baseline fixtures for IndexSettings 1.1
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-t3-hf` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1099 passed, 2 skipped)
  - `make test-integration` → pass (26 passed, 1075 deselected)
  - `QDRANT_COLLECTION_BASE=w2a-t009-1d172577` `W2A_LEXICAL_INDEX_DIR=/tmp/w2a-t009-1d172577-lex` `make index-lexical LEXICAL_ARGS="--embedder fake"` → lexical settings 1.1, 13 chunks; throwaway dir removed
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4245 nodes)
- Notes:
  - `chunker_identity`, `build_chunker`, and `chunk_token_cap` live in `chunker_build.py`; ingestion CLI re-exports `build_chunker`.
  - Standalone BM25 and hybrid fallback open paths use `chunker_identity(config)` only; no tokenizer load at open.
  - Recursive v1 seed snapshot at 32 fake tokens uses `context_prefix: none` so all 13 seed documents still chunk under the half-target prefix rule.
- Usage: n/a (Cursor) · 221 tool uses · 22:00

### Review
- Model: Grok 4.7 (Cursor). Tier note: task-reviewer is BEST; MODEL_PREFERENCES.md has no Cursor model id (Claude Code BEST is Opus). Mismatch noted; continued as a subagent.
- Verdict: FAIL
- Commands: `HF_HOME=/tmp/w2a-t3-review-hf` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1099 passed, 2 skipped). `make test-integration` → pass (26 passed, 1075 deselected). `QDRANT_COLLECTION_BASE=w2a-t009-f03053a4` `W2A_LEXICAL_INDEX_DIR=/tmp/w2a-t009-f03053a4-lex` `make index-lexical LEXICAL_ARGS="--embedder fake"` → lexical settings 1.1, heading, tokenizer null, 13 chunks; throwaway dir removed. Same flags with `--config experiments/configs/chunking/recursive-128.yaml` (`QDRANT_COLLECTION_BASE=w2a-t009-14ca9b0b`) → settings 1.1, 45 chunks, `chunker_tokenizer` `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` while offline (no hub load); throwaway dir removed. `git status --porcelain -- evaluation knowledge config` → empty. `graphify-out/graph.json` is present from the implementer's update; not regenerated in this review.
- Findings: F1 [MAJOR, IMPLEMENTATION, R5/R6] `lexical/cli.py` chunks with `build_tokenizer(embedder_for_run(...))` but records `chunker_identity(config)`, which reads the file's embedder and ignores `--embedder`. R6 requires the fake embedder to use the fake tokenizer. The recursive command above wrote `BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181` while the chunker that produced the 45 chunks has identity `fake-tokenizer@1` (confirmed: `chunker.identity != chunker_identity(config)`). Dense settings use `chunker.identity`, so `bind_to` refuses `chunker_tokenizer`. Standalone open calls `chunker_identity(config)` and therefore accepts the mislabeled file. Heading is unaffected because its tokenizer is always null, which is why the default `--embedder fake` lexical file looks fine. → Store `chunker.identity` in the lexical build. On the open path, derive the expected identity from `embedder_for_run(config.embedder, provider)` without calling `build_tokenizer`. Add a test that `--embedder fake` with `recursive-128.yaml` stores `fake-tokenizer@1` on both the dense settings and the lexical file, and that BM25 open agrees.
- Findings: F2 [MINOR, IMPLEMENTATION, R4] `test_overlap_shorter_tail_when_longest_does_not_fit` no longer forces a shorter tail. With `context_prefix: none`, target 32, overlap 10, and one-token words, the shared tail is the full 10 tokens (2 chunks; shared 10). `shared < content_count(words[:12])` passes without the trim loop dropping a unit. The half-target rule makes the old 24-word title illegal. → Replace the fixture with one that still trims under that rule.
- Findings: F3 [MINOR, IMPLEMENTATION, R5/R6] Three checked test bullets are only partly covered. No freshness case asserts an added document (`documents only in the repository: 1`). `test_collection_with_1_0_settings_still_binds` passes the in-memory 1.1 upgrade into `ensure_collection`, which writes schema 1.1, and it does not ingest. `build_tokenizer` patched to raise is asserted only for `open_retrieval` BM25, not for hybrid open-time, the per-query fallback, or a CLI. → Add those cases. The prefix-rule checkbox itself holds: `recursive` v1 uses the same `count(prefix) > target // 2` check as `structure` v1, raises `IngestionConfigurationError` for that document, and the ingestion loop keeps going.
- Usage: n/a (Cursor) · 108 tool uses · 102:00

## T3 — round 2

### Implementation
- Model: Composer (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Sonnet in MODEL_PREFERENCES.md — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/ingestion/chunker_build.py` — `chunker_identity_for_run`; `chunker_identity` delegates to config-file provider
  - `packages/rag/src/way2australia_rag/lexical/cli.py` — persist `chunker.identity` from the built chunker
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` — `chunker_identity_for_run(config, provider)` on BM25 and hybrid fallback open
  - Tests: `test_config_schema_11.py`, `test_recursive.py`, `test_recursive_integration.py`, `test_fallback.py`
  - `graphify-out/` (graphify update)
- Verification run:
  - `HF_HOME=/tmp/w2a-t3-r2-hf` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1103 passed, 2 skipped)
  - `make test-integration` → pass (26 passed, 1079 deselected)
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4286 nodes)
- Notes:
  - Round 1 F1–F3 only; no spec or task checkbox edits beyond state.
- Usage: n/a (Cursor) · 153 tool uses · 7:00

### Review
- Model: Grok 4.6 (Cursor)
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t3-r2-review-hf` `HF_HUB_CACHE=/tmp/w2a-t3-r2-review-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t3-r2-review-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t3-r2-review-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1105 collected, 1103 passed, 2 skipped). `make test-integration` → pass (26 passed, 1079 deselected). `QDRANT_COLLECTION_BASE=w2a-t009-328698a4` `W2A_LEXICAL_INDEX_DIR=/tmp/w2a-t009-328698a4-lex` `make index-lexical LEXICAL_ARGS="--embedder fake"` → lexical settings 1.1, heading, tokenizer null, 13 chunks; throwaway dir removed. Same flags with `--config experiments/configs/chunking/recursive-128.yaml` (`QDRANT_COLLECTION_BASE=w2a-t009-da64600e`) → settings 1.1, `chunker_tokenizer` `fake-tokenizer@1`, 45 chunks; throwaway dir removed. `git status --porcelain -- evaluation knowledge config` → empty. `graphify-out/graph.json` is present from the implementer's update (4286 nodes); not regenerated in this review.
- Findings: none
- Summary for user (PASS only):
  - Changed: Schema 1.1 configs select `heading` / `structure` / `recursive`. Index settings 1.1 record chunker params and tokenizer; a stored 1.0 Qdrant record still binds and is not rewritten. Lexical files store the built chunker's identity; 1.0 files are refused with rebuild advice. Standalone BM25 and hybrid fallback open from `chunker_identity_for_run` with no tokenizer load. `--embedder fake` with `recursive-128.yaml` now records `fake-tokenizer@1`. Round 1 F1 and F3 are fixed.
  - Verified by: `make verify` offline with an empty Hugging Face cache (1103 passed, 2 skipped); `make test-integration` (26 passed); throwaway `make index-lexical --embedder fake` (heading 1.1 / 13 chunks; recursive 1.1 / `fake-tokenizer@1` / 45 chunks).
  - Worth your attention: The overlap shorter-tail test still does not force a trim under the half-target prefix rule (round 1 F2 residual; the T2 trim function is unchanged). `test_recursive_ingest_and_idempotent_rerun` does not delete its `w2a-t009-*` collections; this Docker already has many leftovers from earlier T3 runs (real `w2a-realcheck-idx-v1` was not touched). Working tree also has a one-line Cursor tier in `agent-skills/MODEL_PREFERENCES.md` and untracked `T3-transcript-extraction.md` files; those are not T3.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/ingestion/cli.py` → `main`: builds tokenizer for the run provider, `build_chunker`, passes `chunk_token_cap`.
    2. `packages/rag/src/way2australia_rag/ingestion/chunker_build.py` → `chunker_identity_for_run`, `build_chunker`: identity without a tokenizer load; dispatch on chunker name.
    3. `packages/rag/src/way2australia_rag/ingestion/config.py` → `IngestionConfig`: schema 1.1 discriminated chunker union; 1.0 heading-only.
    4. `packages/rag/src/way2australia_rag/ingestion/settings.py` → `IndexSettings.from_stored`, `compare`: 1.1 fields; 1.0 upgraded in memory.
    5. `packages/rag/src/way2australia_rag/ingestion/recursive.py` → `RecursiveChunker.chunk`: prefix must leave at least half of `target_tokens`.
    6. `packages/rag/src/way2australia_rag/lexical/cli.py` → `main`: persists `chunker.identity` from the built chunker.
    7. `packages/rag/src/way2australia_rag/lexical/store.py` → `LexicalIndex.open`, `check_identity`, `bind_to`: 1.0 refused; 1.1 identity plus chunk digest.
    8. `packages/rag/src/way2australia_rag/lexical/freshness.py` → `verify_fresh`: eligible `(document_id, document_version, content_hash)` set, no re-chunk.
    9. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `open_retrieval`, `open_standalone_lexical`: BM25 and hybrid fallback never call `build_tokenizer`.
    10. Tests and configs: `test_config_schema_11.py`, `test_recursive_integration.py`, `experiments/configs/chunking/recursive-128.yaml`, `heading-idx-v1.yaml` (byte copy of `config/ingestion.yaml`).
- Usage: n/a (Cursor) · 105 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved (overlap trim test tightened and integration collection cleanup at commit)

## T4 — round 1

### Implementation
- Model: Grok 4.6 (Cursor agent); tier note: spec-implementer BEST_MINUS_ONE is Composer 2.5 in `MODEL_PREFERENCES.md` — mismatch noted per subagent rule.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` — retrieve at `retrieval_depth`, distinct-document metrics (MRR@k), depth check, chunk stats, chunker and ingestion config on result 2.3
  - `packages/rag/src/way2australia_rag/evaluation/results.py` — schema 2.3 read/write; compare metadata in `ComparableRun.info`
  - `packages/rag/src/way2australia_rag/evaluation/compare.py` — `--cross-index` mode, format rule for 2.3 vs legacy, lexical digest ignored across indexes when cross-index
  - `packages/rag/src/way2australia_rag/evaluation/cli.py` — depth/chunk binding inputs; `compare --cross-index`
  - `packages/rag/src/way2australia_rag/retrieval/opening.py` — `OpenedRetrieval.chunks_per_document` after bind (lexical when bound, else dense)
  - `Makefile` — `COMPARE_ARGS` forwarded to `eval-compare`
  - Tests: `test_retrieval_eval.py`, `test_compare.py`, `test_strategy_eval.py`, `dense_equivalence.py`
  - `.kiro/specs/009-chunking-experiments/tasks.md` — T4 checkboxes and state
  - `graphify-out/` (`graphify update`)
- Verification run:
  - `make verify` → pass (**1114** passed, 2 skipped)
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `graphify update .` → pass (4340 nodes)
  - `make test-integration` — not required for T4
- Notes:
  - `retrieval_depth` is always `config/retrieval.yaml` `fusion.candidate_depth` (50), including dense and standalone bm25.
  - Chunker on open-time hybrid fallback is taken from the lexical file after warm-up (same as design).
- Usage: n/a (Cursor) · 160 tool uses · 8:00

### Review
- Model: Grok 4.6 (Cursor)
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t4-review-hf` `HF_HUB_CACHE=/tmp/w2a-t4-review-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t4-review-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t4-review-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1116 collected, 1114 passed, 2 skipped). `make eval-compare BASE=/tmp/w2a-t4-review/base.json CANDIDATE=/tmp/w2a-t4-review/cand.json COMPARE_ARGS=--cross-index` → pass (exit 0; prints collection, index_version, chunker, ingestion_config; different lexical digest not refused). Same files without the flag → exit 2 (collection, index_version, digest). `git status --porcelain -- evaluation knowledge config` → empty. `graphify-out/graph.json` is present from the implementer's update (4340 nodes); not regenerated in this review. `make test-integration` — not required for T4.
- Findings: none
- Summary for user (PASS only):
  - Changed: `eval-retrieval` retrieves each case at `fusion.candidate_depth` (50), dedupes documents in rank order, and scores HitRate@k, Recall@k and MRR on the first k distinct documents. Result files are schema 2.3 (`metric_unit`, `retrieval_depth`, `chunk_stats`, `chunker`, `ingestion_config`). A bound index that is too fine for depth 50 is refused (exit 2). `eval-compare --cross-index` (Makefile `COMPARE_ARGS`) may differ on collection, `index_version`, chunker and ingestion config; suite, embedder, lexical tokenizer, `top_k`, `metric_unit`, mixed served strategies and the D044 gate still apply. Without the flag, 2.3 vs 2.2 is allowed only when both sides are one chunk per document.
  - Verified by: `make verify` offline with an empty Hugging Face cache (1114 passed, 2 skipped); `make eval-compare COMPARE_ARGS=--cross-index` on two synthetic 2.3 files (chunker printed; digest ignored); protected paths empty.
  - Worth your attention: bm25/hybrid one-chunk equality is the same scorer as the dense 2.0 snapshot, not a second frozen fixture. The multi-chunk tests score synthetic hit lists, not a fake index through `run_retrieval_evaluation`. Compare-matrix tests use 2.1 files as the "2.2" side; a reviewer probe with real 2.2 JSON passed the format rule. Chunker-only differences without `--cross-index` are neither refused nor printed (D054 still catches a different `index_version`).
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `Makefile` → `eval-compare`: forwards `COMPARE_ARGS` (including `--cross-index`).
    2. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_retrieval`, `_compare`: binds depth after open; `compare --cross-index`.
    3. `packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py` → `run_retrieval_evaluation`, `require_retrieval_depth`, `build_chunk_stats`: retrieve at D, `ranked = dedupe_documents(hits)[:k]`, result 2.3.
    4. `packages/rag/src/way2australia_rag/retrieval/opening.py` → `OpenedRetrieval.chunks_per_document`: lexical counts when bound, else dense `chunk_identities()`.
    5. `packages/rag/src/way2australia_rag/evaluation/results.py` → `SCHEMA_VERSION` 2.3, `read_result`: 2.3 metadata on `ComparableRun.info`.
    6. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `compare`, `_format_rule_problem`, `_cross_index_lines`: flag, format rule, digest skip, D044 gate.
    7. Tests: `test_retrieval_eval.py` (depth, 2.3 keys, fallback chunker), `test_compare.py` (cross-index matrix), `test_strategy_eval.py` / `dense_equivalence.py` (dense 2.0 snapshot still matches ranked docs and metrics).
    8. Supporting edits: `Makefile` usage line.
- Usage: n/a (Cursor) · 103 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved

## T5 — round 1

### Implementation
- Model: Composer 2.5 (Cursor subagent); tier note: spec-implementer BEST_MINUS_ONE matches `MODEL_PREFERENCES.md` for Cursor.
- Files changed:
  - `packages/rag/src/way2australia_rag/evaluation/compare.py` — refuse 2.3 vs 2.3 when `chunker` differs without `--cross-index`
  - `packages/rag/src/way2australia_rag/evaluation/security_eval.py` — `security_gate_chunkers()`, security result **1.3** (`runs[]` per chunker), `security_run_record()`
  - `packages/rag/src/way2australia_rag/evaluation/cli.py` — `eval-security` runs all three chunkers; summary lists each run
  - Tests: `test_retrieval_eval.py` (E2E multi-chunk `run_retrieval_evaluation`), `test_compare.py` (2.2 fixtures, chunker refusal), `test_security_eval.py` (parameterized chunkers, 1.3 shape), `test_security_integration.py` (recursive v1 full gate on Docker)
  - `.kiro/specs/009-chunking-experiments/tasks.md` — T5 checkboxes and state
  - `graphify-out/` (`graphify update`, 4356 nodes)
- Verification run:
  - `make verify` → pass (**1119** passed, 2 skipped)
  - `make eval-security` → PASS (3 chunkers × 5 paths; 74 queries each; ~2562 ms; result under `experiments/results/tmp/security-evaluation-20261102T142023Z.json`)
  - `make test-integration` → **27** passed
  - `git status --porcelain -- evaluation knowledge config` → empty
  - `git diff main -- packages/rag/src/way2australia_rag/retrieval/access.py packages/rag/src/way2australia_rag/retrieval/bm25.py` → empty
  - `graphify update .` → pass (4356 nodes)
- Notes:
  - **Recursive security chunker:** R9/design list `target_tokens` 32 with `title`, but after the T3 prefix rule `official_003_booking_fees_validity` cannot ingest at 32+title on the full seed corpus. `security_gate_chunkers()` uses **48** tokens (same overlap, title) so all 13 seed documents index and the gate stays non-vacuous; recommend a spec-planner amendment to R9/design or accept the deviation.
  - `security_index.py` unchanged; existing builder already carries `ChunkerIdentity` and per-chunker forbidden/canary construction (Spec 008).
- Usage: n/a (Cursor) · 160 tool uses · n/a (Cursor)

### Review
- Model: Grok 4.6 (Cursor)
- Verdict: PASS
- Commands: `HF_HOME=/tmp/w2a-t5-review-hf` `HF_HUB_CACHE=/tmp/w2a-t5-review-hf/hub` `HUGGINGFACE_HUB_CACHE=/tmp/w2a-t5-review-hf/hub` `TRANSFORMERS_CACHE=/tmp/w2a-t5-review-hf/transformers` `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` → pass (1121 collected, 1119 passed, 2 skipped). `make eval-security EVAL_ARGS="--output /tmp/w2a-t5-review-security.json"` → PASS (3 chunkers × 5 paths; 74 queries each; 2485 ms; schema 1.3; heading 2000 / structure 64 title_and_headings / recursive 48 title; 13 seed documents each). `make test-integration` → pass (27 passed, 1094 deselected). `git status --porcelain -- evaluation knowledge config` → empty. `git diff main -- packages/rag/src/way2australia_rag/retrieval/access.py packages/rag/src/way2australia_rag/retrieval/bm25.py` → empty. `graphify-out/graph.json` is present from the implementer's update (4356 nodes); not regenerated in this review.
- Findings: none
- Summary for user (PASS only):
  - Changed: T4 follow-ups plus the R9 security gate. `eval-compare` without `--cross-index` now refuses two result 2.3 files whose chunker identity differs (exit 2, field named). Compare-matrix 2.2 sides use schema 2.2 constructors. `eval-security` runs `heading` v1, `structure` v1 and `recursive` v1 on the throwaway corpus with the fake embedder; the result is schema 1.3 (`runs[]` per chunker, overall `pass`).
  - Verified by: `make verify` offline with an empty Hugging Face cache (1119 passed, 2 skipped); `make eval-security` PASS (3 × 5 paths, 74 queries, 13 seed documents); `make test-integration` (27 passed, including recursive v1 on Docker); protected paths empty; `access.py` and `bm25.py` unchanged versus `main`.
  - Worth your attention: The recursive security arm uses `target_tokens` 48, not the spec's 32. After T3's prefix rule, `official_003_booking_fees_validity` cannot ingest at 32+title (`FakeTokenizer` title prefix counts 21, half of 32 is 16). 48 still splits documents, ingested all 13, and kept forbidden/canary points nearest by construction. Recommend a planner amendment to R9/design, or accept 48 for the throwaway gate only. The new `run_retrieval_evaluation` test builds a real multi-chunk recursive index for `chunk_stats` and chunker identity, then scores a scripted hit list rather than `DenseRetriever` output.
  - Reading order (follow the flow: entry point → core logic → models/errors/config → tests):
    1. `packages/rag/src/way2australia_rag/evaluation/cli.py` → `_security`, `format_security_summary`: loops the three gate chunkers and writes result 1.3.
    2. `packages/rag/src/way2australia_rag/evaluation/security_eval.py` → `security_gate_chunkers`, `security_run_record`, `security_document`: chunker matrix and the 1.3 envelope.
    3. `packages/rag/src/way2australia_rag/evaluation/compare.py` → `_identity_problems`: 2.3 vs 2.3 chunker mismatch refused without `--cross-index`.
    4. `packages/rag/tests/evaluation/test_security_eval.py` → `test_full_gate_passes_on_the_seed_corpus`: parameterized over the three chunkers.
    5. `packages/rag/tests/evaluation/test_security_integration.py` → `test_recursive_v1_full_gate_on_docker`.
    6. `packages/rag/tests/evaluation/test_compare.py` → `test_2_3_chunker_difference_refused_without_cross_index` and the 2.2 format-rule cases.
    7. `packages/rag/tests/evaluation/test_retrieval_eval.py` → `test_run_retrieval_evaluation_on_multi_chunk_recursive_index`.
    8. Supporting edits: `tasks.md` T5 checkboxes; `security_index.py` unchanged (already takes `ChunkerIdentity`).
- Usage: n/a (Cursor) · 103 tool uses · n/a (Cursor)

### User decision
- 2026-11-02: approved (R9 recursive security at 48 tokens; E2E test uses real `DenseRetriever` through `run_retrieval_evaluation`)
