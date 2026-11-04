# 010 — Multilingual Retrieval Tasks

Status: verified (2026-11-04, merged cae06c3)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-11-04). Design: `design.md` (approved 2026-11-04).

Rules for every task:
- **Protected paths.** `knowledge/` never changes. `evaluation/` changes only in T1. `config/` changes only in T3 (`config/retrieval.yaml` schema 1.2 with `lexical.tokenizer: lexical-v1`) and in T5 (that value, only if R10 promotes `lexical-v2`). Every task checks `git status --porcelain -- evaluation knowledge config`, and the reviewer compares the output with the task's allowed list.
- **Unchanged code.** These files are not edited: `retrieval/access.py`, `fusion.py`, `availability.py`, `index.py`, the ingestion package (chunkers, payload, `IndexSettings`, `INGESTION_NAMESPACE`), `config/ingestion.yaml`, and `lexical-v1` tokenization output. The legacy `make retrieval-baseline` snapshot test passes untouched (D046).
- **No-`lote` behaviour stays identical.** Existing tests may change only where a signature or format changes (`Retriever.retrieve` keyword, `document_count(access, lote)`, lexical settings 1.2, result 2.4, security result 1.4, `RetrievalConfig` 1.2). Ranks, scores, document IDs and ordering in their assertions never change.
- **`make verify` needs no Docker, PyTorch, `bge-m3` extra, tokenizer files or network.** It also passes with an empty `HF_HOME` and `HF_HUB_OFFLINE=1` (Spec 009 hub-free discipline; keep the autouse empty-cache fixture). Unit tests use `FakeEmbedder`, `FakeTokenizer`, `QdrantClient(":memory:")` and SQLite files under `tmp_path`.
- **No language literal in generic code.** Active codes come from `config/language_registry.json` (`languages.active_lote_codes`). Tests read them from the registry or use a temporary registry. Synthetic fixture codes (`zz`, a second code for parity tests) live only in tests and the security harness.
- **No live-count literals in new tests**, except in synthetic fixtures the test builds and in R1's stated minimums (at least 12 / 12 / 3).
- **Real systems.** Agents never write to, delete or re-ingest a `w2a-realcheck-*` or `way2australia-*` collection, and never run the real model. Docker runs use throwaway bases (`w2a-t010-<8 hex>`, `w2a-sectest-<8 hex>`) and delete them afterwards.
- **Results.** Tests never write under `experiments/results/` (use `tmp_path`). Throwaway CLI output goes to `experiments/results/tmp/`. Committed result files are never modified.
- **Messages.** Refusals and errors name fields, codes and document IDs only, never chunk text, paths or URLs.
- After code changes, run `graphify update .` (D048) as part of the task's verification.
- **Amendments.** Any task box or design edit added after approval gets a dated `## Change log` line in `requirements.md`.
- **`task-reviews.md`** is edited only by exact, targeted edits.

## T1 — Suite `public-eval-v3` (user-owned approval)

**State:** approved (2026-11-04)
**Requirements:** R1, R11

- [x] Draft `evaluation/candidates/010-candidates.jsonl`, using the Spec 006 candidate row shape with `status: suggested`, `target_suite_id: public-eval-v3` and a `proposed_case`.
  - Draft enough new `ml` and `mixed` goldens that v3 reaches at least 12 of each in total. Today there are 6 `ml` and 9 `mixed`, so that means at least 6 new `ml` and 3 new `mixed`; aim for a few extra, since some may be rejected.
  - Draft 3 unanswerable cases with `query_language: ml`.
  - Spread the goldens over the eligible documents. Each names only eligible public documents in `relevant_document_ids`, and each has `expected_facts` taken from the document text.
  - Include at least two romanized-Malayalam `mixed` queries (like `g062`).
  - Note any query that uses a legacy chillu spelling; this is optional, and the user decides.
  - Mark every candidate `requires_review: ["fluent_speaker_review", "owner_review"]`.
- [x] Stop for the user: present every candidate (query, relevant documents, facts). The user corrects and approves them. Record the decision and every correction verbatim in `task-reviews.md`. Only approved candidates go further. Mark rejected ones in the candidate file (`review.decision: rejected`); they keep `status: suggested`.
- [x] Create `evaluation/suites/public-eval-v3.json` and `evaluation/datasets/v3/` (`golden_public.jsonl`, `unanswerable_public.jsonl`, `security_public.jsonl`).
  - Copy every v2 row, changing only `evaluation_suite_id`.
  - Append the promoted cases: goldens from `g070`, unanswerable from the next free `u` ID; `case_version: 1`, `status: active`, `introduced_in_release: seed-v1`, `category` as approved.
  - Set a correct `case_count`, `replaces: public-eval-v2` v2, and notes.
- [x] Give each promoted candidate `review.promoted_as`. Set the v2 manifest to `status: replaced`; no other v2 change.
- [x] `evaluation/schemas/evaluation_case_types.schema.json`: `candidate_row.proposed_case` becomes a `oneOf` over `golden_answerable` and `unanswerable_refusal`, the latter with `query_language` required for candidates. The 006 candidate rows still validate. Tests cover one valid and one invalid row of each shape, and a row matching neither.
- [x] `evaluation/validate.py`: extend the promotion check to v3 (each promoted case equals its candidate's `proposed_case` after the recorded corrections, which are applied to `proposed_case` in the candidate file; goldens compare `query`, `relevant_document_ids`, `expected_facts` and `query_language`, and unanswerable cases compare `query`, `expected_behavior` and `query_language`). `make validate-evaluation` passes on every suite.
- [x] Switch the defaults of `make eval-retrieval` and `make eval-security` (`DEFAULT_SUITE`) to v3. A v2 run is refused (exit 2). The legacy baseline keeps v1.
- [x] Tests in `tests/evaluation/test_suite_v3.py`:
  - each v2 row equals its v3 copy except `evaluation_suite_id`;
  - v2 dataset files match their committed hashes;
  - the v2 manifest differs only in `status`;
  - the slice minimums (at least 12 `ml`, at least 12 `mixed`, at least 3 unanswerable `ml`);
  - every relevant document is eligible.
  
  Update tests that follow the default suite to use consistency checks.

Allowed protected-path changes: `evaluation/candidates/010-candidates.jsonl`, `evaluation/schemas/evaluation_case_types.schema.json` (`candidate_row` only), `evaluation/suites/public-eval-v2.json` (`status` only), `evaluation/suites/public-eval-v3.json`, `evaluation/datasets/v3/*`.

### Verification

- `make validate-evaluation`; `make verify`.
- `make eval-security` passes on v3 (the existing gate; applicability comes in T4).
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists only the allowed files.
- User approval and corrections recorded in `task-reviews.md`.

## T2 — `lote` applicability on every retrieval path

**State:** approved (2026-11-04)
**Requirements:** R2, R3, R4, R7 (the `lote` field), R11

- [x] New `way2australia_rag/languages.py` with `active_lote_codes(repo_root)`: the active `product_support` codes, without `en`. `evaluation/slices.active_registry_languages` reuses its registry parsing and keeps adding `en`.
- [x] New `retrieval/applicability.py` with:
  - `ResolvedLote` and `resolve_lote(code, active_codes)`, which refuses unknown, inactive, empty, `*` and `en` codes with `RetrievalConfigurationError`. The `en` message explains that `lote` names the non-English side of the CCL pair and lists the active codes;
  - `valid_lote_languages`, `build_lote_condition` (Qdrant `MatchAny(["*", code])`), `build_sql_lote_clause` (`(c.lote_languages = ? OR instr(c.lote_languages, ?) > 0)` with `("|*|", "|<code>|")`) and `check_applicable`.
  
  `retrieval/errors.py`: `LanguageApplicabilityError(RetrievalError)` with `document_id`, a sibling of `RetrievalAuthorizationError`.
- [x] Lexical settings 1.2 in `lexical/store.py` and `lexical/build.py`:
  - `chunks.lote_languages TEXT NOT NULL`, written as sorted codes between `|` separators;
  - the builder refuses a payload that fails `valid_lote_languages` (for example `["*", "ml"]`) with `LexicalIndexError`, and removes the temporary file;
  - `LexicalSettings.schema_version` accepts `1.1` and `1.2`, and the builder writes `1.2`;
  - `LexicalIndex.has_lote_column`; 1.0 is still refused.
  
  The tokenizer stays `lexical-v1` in this task.
- [x] `retrieval/base.py`: `Retriever.retrieve(..., *, lote: ResolvedLote | None = None)`. `RetrievalResult.lote`.
  - `DenseRetriever` uses the combined filter `Filter(must=[*access.must, condition])`, then `check_hit`, then `check_applicable`.
  - `BM25Retriever` uses the access clause `AND` the lote clause, then `check_hit`, then `check_applicable`. With a `lote` on a 1.1 file it raises `LexicalIndexBindingError` before SQL, naming `make index-lexical`.
  - `HybridRetriever` and `FallbackRetriever` pass `lote` to every leg and path.
  
  With no `lote`, the generated filter and SQL are byte-identical to today.
- [x] `retrieval/opening.py`: `OpenedRetrieval.document_count(access, lote)` on dense, lexical and fallback.
- [x] CLIs:
  - `make retrieve` takes `--lote` (in `RETRIEVE_ARGS`), validated before opening, and prints `lote: <code|none>`;
  - `make eval-retrieval` takes `--lote` (`EVAL_ARGS`) and writes result 2.4 with a top-level `lote`;
  - `results.read_result` reads 2.4, and older files read `lote` as `None`.
- [x] `eval-compare` refuses a `lote` difference (`lote changed <old> -> <new>`, `null` printed as `none`) in every mode.
- [x] Tests (`tests/retrieval/test_applicability.py` plus additions to the dense, bm25, hybrid, fallback, opening, store, build, CLI, results and compare tests):
  - `resolve_lote` cases, using a temporary registry;
  - builder outputs, and access-builder outputs unchanged;
  - **store parity:** the same tagged rows (`["*"]`, `[code]`, `[code, other]`, `[other]`) in an in-memory Qdrant collection and a temporary lexical file, queried with the active code, a second code and no `lote`, return identical document sets. A `["*", code]` row is refused by the lexical builder; on the Qdrant side, written by a raw upsert, it raises `LanguageApplicabilityError` for every `lote`;
  - `valid_lote_languages` cases;
  - per path (dense, standalone bm25, hybrid, fallback open, fallback query): a non-applicable chunk that ranks first is excluded with a `lote` and returned without one; a store with the filter dropped by injection makes `check_applicable` raise; `LanguageApplicabilityError` is not caught by `FallbackRetriever`;
  - hits with a `lote` are a subset of hits without one;
  - on the seed corpus with the fake embedder, the active code gives the same hits as no `lote`, on every strategy;
  - a 1.1 lexical file serves without a `lote` and is refused with one;
  - `--lote` refusals exit 2 before opening.

Allowed protected-path changes: none.

### Verification

- `make verify` (and again with `HF_HOME=$(mktemp -d) HF_HUB_OFFLINE=1`); `make test-integration` (existing tests still pass).
- `make eval-security` still passes (gate unchanged until T4).
- `git diff main...HEAD -- packages/rag/src/way2australia_rag/retrieval/access.py` is empty.
- `graphify update .`

## T3 — `lexical-v2`, tokenizer selection, script mix, `--cross-tokenizer`, continuity command

**State:** approved (2026-11-04)
**Requirements:** R5, R6, R7, R8, R10 (continuity command), R11

- [x] New `lexical/equivalents.py`: `SEQUENCE_EQUIVALENTS` (code points only), with a header citing the Unicode Standard Malayalam chillu section and the Unicode version checked. Check each of the six design rows against the cited text, and record the check (section and version) in the implementation notes. Add U+0D54–U+0D56 only if the standard defines a legacy sequence for them.
- [x] `lexical/tokenizer.py`:
  - `LexicalTokenizer` Protocol and the `TOKENIZERS` registry (`lexical-v1`, `lexical-v2`), plus `tokenizer_named`;
  - `lexical-v2` is NFC, then generic `replace_sequences`, then the `lexical-v1` steps, with no script-named branch;
  - module-level `tokenize` and `query_terms` stay `lexical-v1` aliases.
- [x] Lexical store:
  - `LexicalIndex._check` accepts any registered tokenizer and refuses an unknown one with rebuild advice;
  - `LexicalIndex.tokenizer`;
  - `BM25Retriever` uses `self._lexical.tokenizer.query_terms`;
  - `build_lexical_index(..., tokenizer)` records the tokenizer's name and version.
- [x] `config/retrieval.yaml` schema 1.2 with `lexical: {tokenizer: lexical-v1}`. `RetrievalConfig` validates the name, and a 1.1 file reads as `lexical-v1`.
  
  `make index-lexical`: `--tokenizer` (`LEXICAL_ARGS`), whose default is the config value. It prints the tokenizer and the lexical settings version.
  
  Document, and test, that a second file sits beside the first through `W2A_LEXICAL_INDEX_DIR`.
- [x] `.gitignore`: replace the three lines `/.local/lexical/`, `/.local/pytest-hf-empty/` and `/.local/workflow-reviews/` with a single `/.local/` (all machine-local state, under one comment).
  - Today `.local/lexical-v2/` is not ignored, and `git_state` ignores untracked files only under `experiments/results/`, so the T5 arm runs would record `git_dirty: true`.
  - Update `tests/lexical/test_lexical_cli.py` (the assertion that `.gitignore` contains `/.local/lexical/`) so it checks that the default lexical directory and `.local/lexical-v2/` are both ignored (for example with `git check-ignore`), not the exact line.
  - The temporary-repository tests that refuse an un-ignored `.local/other/` keep their own `.gitignore` and are unchanged.
- [x] New `evaluation/script_mix.py` with `script_mix(text)`: letters only, first word of the `unicodedata` name, lowercased, sorted, joined by `+`, `none` when the text has no letters.
  
  Result 2.4 gains `metrics.by_script_mix` and a per-case `script_mix`. `make eval-retrieval` prints the slice with the other slices.
- [x] `eval-compare`: `COMPARE_ARGS=--cross-tokenizer` relaxes only the tokenizer name and version. The digest and chunk count must still match, and the option can be combined with `--cross-index`. Without the option, a tokenizer difference gets the advice line.
- [x] New `evaluation/continuity.py` and a `make eval-continuity BASE=... CANDIDATE=...` target (`CONTINUITY_ARGS`):
  - reads 2.3 and 2.4 files;
  - refuses with exit 2 when collection, `index_version`, chunker, embedder pair, lexical identity, served strategy or `top_k` differ;
  - prints suite, `lote`, case-set and `git_commit` differences as lines;
  - compares `hit`, `reciprocal_rank` and `ranked_document_ids` for every golden shared by `case_id` and `case_version`;
  - exits 0 when nothing differs, 1 when something does, 2 when a file is unreadable.
  
  Add it to `COMMANDS.md` in T6.
- [x] Tests:
  - tokenizers: every table pair inside a word and at word end; `lexical-v2` equals `lexical-v1` on every seed chunk and every v3 query without a listed sequence; the D051 pin still holds; unknown tokenizer refused; a file is queried with its own tokenizer; files built with each tokenizer; `--tokenizer` and the config default; `RetrievalConfig` 1.1 and 1.2;
  - the BM25 authorization and applicability tests parametrized over both tokenizers;
  - `script_mix`: digits, punctuation, `₹`, whitespace, ZWJ/ZWNJ, virama and vowel signs add no script; `₹1,300 mock-ൽ` gives `latin+malayalam`; `g062` gives `latin`; representative `en`, `ml` and `mixed` v3 queries; for every letter in every v3 query, the name prefix equals the script in a small committed fixture of the letters' known Unicode `Script` values;
  - result 2.4 keys; readers for 2.0–2.4;
  - `--cross-tokenizer`: refused without it; accepted with it; another identity difference still refused with it;
  - `eval-continuity` on fixture result files under `tests/evaluation/fixtures/`: equal, differing, only-in-one-file, identity mismatch, unreadable.

Allowed protected-path changes: `config/retrieval.yaml` (schema 1.2, `lexical.tokenizer: lexical-v1`).

### Verification

- `make verify` (also hub-free); `make test-integration`; `make eval-security` still passes.
- `make index-lexical` with `QDRANT_COLLECTION_BASE=w2a-t010-<8 hex>`, `--embedder fake`, and a throwaway `W2A_LEXICAL_INDEX_DIR` under `.local/`, once per tokenizer. Settings are 1.2 and the tokenizer names are correct. Delete the files afterwards.
- `make eval-continuity` on two fixture files: exit 0 when equal, 1 when different.
- `graphify update .`

## T4 — Security gate with applicability, result 1.4

**State:** approved (2026-11-04)
**Requirements:** R9, R11

- [x] `evaluation/security_index.py`:
  - public, eligible, non-applicable rows (`lote_languages: ["zz"]`), one per gated query, carrying the query's own tokens so they are nearest in both legs;
  - a new access-forbidden variant `staff_scope_lote` with `lote_languages: [<active code>]`;
  - a harness guard: exit 2 if `zz` is an active code;
  - the rows exist only in the throwaway collection and lexical file.
- [x] `evaluation/security_eval.py`:
  - for each chunker (D070) and each of the five paths, run the gate in two modes: `lote: null` and `lote: <active code>`;
  - sanity check per leg: with the access filter alone, a non-applicable row ranks first, otherwise it's a harness error (exit 2). The existing unfiltered checks are kept;
  - with `lote: null`, an access-forbidden row or a `RetrievalAuthorizationError` is an authorization violation;
  - with a `lote`, the same is an authorization violation, and a non-applicable row or a `LanguageApplicabilityError` is an applicability violation;
  - `check_hit` runs first, so a row failing both counts as authorization.
- [x] Write security result 1.4: the 1.3 keys plus `lote_modes`, per-run `authorization_violations` and `applicability_violations`, and `non_applicable_rows_per_variant`. `passed` requires zero of both. Older 1.x readers are unchanged.
- [x] Docker isolation test `tests/evaluation/test_security_integration.py`: add non-applicable points, and assert that with a `lote` they are excluded on the real Qdrant server, alongside the existing forbidden points. Collections are cleaned up on failure, and the test skips without Qdrant.
- [x] Tests:
  - both modes, on every path and chunker;
  - a dropped applicability filter (injection) makes the gate fail with an applicability violation, not an authorization violation;
  - a dropped access filter still fails as authorization;
  - sanity-check failure gives exit 2;
  - the `zz` guard;
  - the 1.4 keys;
  - the existing 1.3 tests adapted without changing their verdicts.

Allowed protected-path changes: none.

### Verification

- `make verify` (also hub-free); `make test-integration`; `make eval-security` (PASS, both modes, five paths, three chunkers; record the summary line).
- `graphify update .`

## T5 — User-owned real runs on v3 and the `lexical-v2` decision

**State:** approved (2026-11-04)
**Requirements:** R10

Run by the user (real model, `w2a-realcheck-idx-v2`). The agent prepares the commands, then checks and records the files. Before the runs, the tree (including `graphify-out/`) is clean and earlier result files are committed.

- [x] **Two lexical files (local only, no Qdrant writes).** With `QDRANT_COLLECTION_BASE=w2a-realcheck`:
  - `make index-lexical`, which builds `lexical-v1` into `.local/lexical`;
  - `W2A_LEXICAL_INDEX_DIR=.local/lexical-v2 make index-lexical LEXICAL_ARGS="--tokenizer lexical-v2"`.
  
  Both must be settings 1.2 with the same `source_chunk_digest` and chunk count. Record both.
- [x] **Pre-run check.** After both `make index-lexical` builds, `git status --porcelain` is empty. If it isn't, stop before any `make eval-retrieval` run; a non-empty tree would record `git_dirty: true`.
- [x] **Four arms.** `make setup-bge-m3`. Then, with `QDRANT_COLLECTION_BASE=w2a-realcheck`, run `make eval-retrieval` with `EVAL_ARGS="--lote ml --strategy hybrid"` and `"--lote ml --strategy bm25"`, once with the default lexical directory and once with `W2A_LEXICAL_INDEX_DIR=.local/lexical-v2`.
- [x] **Continuity check** (copied word for word from R10): Continuity check first: on the 69 goldens carried from v2, the hybrid `lexical-v1` v3 run with `lote: ml` has the same hit, reciprocal rank and ranked document IDs per case as the Spec 009 reference `…idx-v2-20261103T104934Z.json`. A difference stops the gate until explained. Because `eval-compare` refuses the differing case set and `lote`, the check is a committed, tested command (a script or `make` target, with unit tests on fixture result files, delivered by a code task before T5); its full output is recorded in T5, not produced by an ad-hoc scratch script.
  - Command: `uv run python -m way2australia_rag.evaluation.continuity experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json <hybrid lexical-v1 v3 result>` (not through `make eval-continuity`: GNU make maps recipe exit 1 to 2). Record full stdout/stderr and the **module exit code** in `task-reviews.md`. T6 documents `make eval-continuity` vs the module in `COMMANDS.md`.
- [x] **Compares.** `make eval-compare COMPARE_ARGS=--cross-tokenizer`, with base `lexical-v1` and candidate `lexical-v2`, for hybrid and for BM25-only. Record both outputs.
- [x] **Promotion rule** (copied word for word from R10): **Promotion rule (fixed here, before any run).** `lexical-v2` becomes the default tokenizer only if all hold: the `eval-compare` gate passes for both hybrid and BM25-only; no case goes from hit to miss in any language, in either strategy; overall MRR is not lower in either strategy. A tie promotes it. Otherwise the default stays `lexical-v1`.
- [x] **If promoted:** set `config/retrieval.yaml` to `lexical.tokenizer: lexical-v2`. Rebuild with `make index-lexical`, for the realcheck base and, by the operator, for the default `way2australia-idx-v2`. Check that `make retrieve QUERY="..." RETRIEVE_ARGS="--lote ml"` reports the `lexical-v2` file. No Qdrant change and no new `index_version`. Then `make setup`.
- [ ] **If not promoted:** N/A (promoted) `config/retrieval.yaml` stays unchanged. Rebuild the default lexical file with `lexical-v1` (settings 1.2), so `--lote` works on the default index. Then `make setup`.
- [x] The agent checks each result file: suite v3, not fake, `git_dirty` false, same collection, `index_version`, chunker, embedder pair, `top_k`, document count, `lote: ml`, served strategies, empty `fallback_counts`, and the expected tokenizer. It records for each of the four arms: overall, `en`, `ml` and `mixed` slices, the `by_script_mix` slice, every flipped case, and the `g056`/`g057`/`g061`/`g067`–`g069` ranks. Any deviation is recorded for the user to accept. Result files are committed.

Allowed protected-path changes: `config/retrieval.yaml` (`lexical.tokenizer`), only if promoted.

### Verification

- The continuity output and both `eval-compare` outputs recorded in `task-reviews.md` and `CURRENT_STATE.md` "Next step".
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists only the T1 files, `config/retrieval.yaml` (T3), and the promotion if applied.
- If promoted: `make verify` passes after the config change; `graphify update .`

## T6 — Documentation, decisions and hand-off

**State:** approved (2026-11-04)
**Requirements:** R12, R11, Definition of Done

- [x] `DECISIONS.md` from D072:
  - suite v3 and the closed v2 references;
  - `lote` as a request value apart from access, registry validation, the `null` default and the `en` refusal;
  - the applicability filter (builders, in-query placement, every path, the shape rule that keeps Qdrant and SQL equal) and `LanguageApplicabilityError`;
  - lexical settings 1.2 (the `lote_languages` column; schema version separate from tokenizer version);
  - `lexical-v2` and its Unicode table (amends D051);
  - the default-tokenizer config key and its selection;
  - result 2.4 with `lote` and the script-mix slice, stating that romanized Malayalam counts as `latin`;
  - `--cross-tokenizer` and the `lote` refusal (extends D054);
  - `make eval-continuity`;
  - security result 1.4 (extends D070);
  - the T5 outcome with numbers.
- [x] Docs:
  - `ARCHITECTURE.md`: query flow with the access and applicability filters inside each leg; the four language concepts (C4); lexical settings 1.2; tokenizers;
  - `COMMANDS.md`: `--lote`, `--tokenizer` and `W2A_LEXICAL_INDEX_DIR` for a second file, `--cross-tokenizer`, `make eval-continuity`, the new refusals, the script-mix slice and romanized Malayalam as `latin`, the one-time lexical rebuild for `--lote`;
  - `docs/knowledge/SCHEMA_AND_METADATA.md`: `lote_languages` is now used at retrieval time;
  - `ROADMAP.md`: item 8 status;
  - `CURRENT_STATE.md`: implemented reality, spec status, known issues.
- [x] Carry-overs in `CURRENT_STATE.md` Known issues and the hand-off:
  - query translation or transliteration as the fix for `g067`–`g069` on the BM25 fallback;
  - `g056`/`g057` (fusion demotes dense rank 1) as roadmap item 9 inputs;
  - no Malayalam knowledge content;
  - Malayalam stemming not done;
  - per-script fusion weighting declined;
  - the script-mix name-prefix approximation;
  - the remaining Spec 009 carry-overs, unchanged.
- [x] Design `## As-built notes` for every difference from the approved design.
- [x] Spec-wide checks and the protected-path diff.

Allowed protected-path changes: none.

### Verification

- `make verify` (also hub-free), `make test-integration`, `make eval-security`: all pass; record the counts.
- `git diff --name-status main...HEAD -- evaluation knowledge config`: only the T1 files, `config/retrieval.yaml`, nothing under `knowledge/`.
- Docs reviewed against the code.
- `graphify update .`
