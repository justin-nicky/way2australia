# 009 — Chunking Experiments Tasks

Status: approved (2026-11-01)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-11-01). Design: `design.md` (approved 2026-11-01).

Rules for every task:
- **Protected paths.** `evaluation/` and `knowledge/` never change in this spec. `config/` changes only in T6, and only `config/ingestion.yaml`, only if R10 promotes the arm. Every task checks `git status --porcelain -- evaluation knowledge config` and the reviewer compares the output with the task's allowed list.
- **Unchanged code.** `retrieval/fusion.py`, `hybrid.py`, `fallback.py`, `access.py`, `availability.py`, the BM25 query logic, `lexical/tokenizer.py` (`lexical-v1`), `HeadingChunker`'s output, `PointPayload` (17 fields), `INGESTION_NAMESPACE` and point IDs are not edited. The legacy `make retrieval-baseline` snapshot test passes untouched (D046).
- **`heading` v1 and `idx-v1` rankings stay identical.** Existing tests may change only where a signature changes (`Chunker.identity`, `IndexSettings` 1.1, lexical settings 1.1, `verify_fresh`, result 2.3, security result 1.3). Ranks, scores, document IDs and ordering in their assertions never change.
- **`make verify` never needs Docker, PyTorch, the `bge-m3` extra, the tokenizer files or the network.** Unit tests use `FakeEmbedder`, `FakeTokenizer`, a monkeypatched `hf_hub_download`, `QdrantClient(":memory:")` and SQLite files under `tmp_path`. Tests that need the real tokenizer or the extra are opt-in and skip otherwise.
- **No live-count literals in new tests.** Counts come from the data being tested; literal counts appear only in synthetic fixtures the test builds and in chunker snapshot files.
- **Real systems.** Agents never write to, delete or re-ingest a `w2a-realcheck-*` or `way2australia-*` collection and never run the real model. Docker runs use throwaway bases (`w2a-t009-<8 hex>`, `w2a-sectest-<8 hex>`) and delete them afterwards. Reading the user's cached tokenizer files read-only is allowed (T2).
- **Results.** Tests never write under `experiments/results/` (use `tmp_path`). Throwaway CLI output goes to `experiments/results/tmp/`. Committed result files are never modified.
- **Messages.** Reports, refusals and output never contain chunk text, file paths of the Hugging Face cache, URLs or exception text from the Hugging Face stack.
- After code changes, run `graphify update .` (D048) as part of the task's verification, not left to the orchestrator.
- **Amendments.** Any task box or design edit added after approval gets a dated `## Change log` line in `requirements.md` (Spec 008 retrospective F3).
- **`task-reviews.md`** is edited only by exact, targeted edits.

## T1 — Tokenizer and truncation guard

**State:** approved (2026-11-02)
**Requirements:** R1, R2, R11

- [x] `packages/rag/pyproject.toml`: add `tokenizers` and `huggingface_hub` to the base dependencies; `uv lock`. Confirm with `uv tree` that neither brings `torch`.
- [x] New `ingestion/tokenization.py`: `TokenizerIdentity`, `ChunkTokenizer` Protocol, `FakeTokenizer` (count `2 + Σ ceil(len(word)/4)` after NFKC, `max_sequence_length` default 512), `BgeM3Tokenizer(model_id, revision)` (cache first with `local_files_only=True`, download only when missing and `HF_HUB_OFFLINE` is unset; reads `tokenizer.json` and `sentence_bert_config.json`; floating revisions refused; every failure becomes `IngestionConfigurationError` with model ID and revision only), `build_tokenizer(embedder_config)`.
- [x] `ingestion/config.py`: optional `embedder.fake_max_sequence_length` (default 512), accepted in schema 1.0 and 1.1 files.
- [x] New `ingestion/guard.py`: `ChunkTooLongError(document_id, section_id, position, tokens, limit)` and `check_chunks(document_id, chunks, tokenizer, cap)` with limit `min(max_sequence_length, cap)`.
- [x] `ingestion/service.py`: move `chunker.chunk(document)` and the point-ID computation inside the per-document `try` (closes Spec 004 T7 F1); call `check_chunks` before embedding; per-document failure reasons `chunk_too_long` (with the structured fields) and the class name for other errors; `OptionalDependencyError` re-raise unchanged; exit status on failures unchanged.
- [x] `ingestion/cli.py` builds the tokenizer with `build_tokenizer` and passes it to the service (`heading` v1 cap is `None`).
- [x] `lexical/build.py` `production_entries` runs the same guard (tokenizer passed in); `lexical/cli.py` builds it; a violation refuses the atomic build (exit 2, no file written).
- [x] Tests:
  - `tests/ingestion/test_tokenization.py`: fake counts on fixed strings (English, Malayalam, empty); `build_tokenizer` dispatch; `BgeM3Tokenizer` with a monkeypatched `hf_hub_download` (hit, miss offline, miss online, wrong revision, floating revision) and the message contains no path; import pin: importing `tokenization` and building `BgeM3Tokenizer` against fixture files never imports `torch` or `sentence_transformers`.
  - opt-in `W2A_RUN_BGE_M3_SMOKE=1` with the extra: BGE-M3 `count` equals `len(model.tokenizer(text)["input_ids"])` for fixed English and Malayalam texts, and `max_sequence_length == model.max_seq_length`.
  - `tests/ingestion/test_guard.py`: at the limit passes, above it raises with the right fields; cap `None` uses the model maximum.
  - `tests/ingestion/test_service.py` additions: an oversized chunk is a per-document failure with no upsert or delete for that document while others proceed; a chunker that raises is a per-document failure (no longer aborts the run); report and logs contain no chunk text.
  - `tests/lexical/test_lexical_build.py` addition: an oversized chunk refuses the build and leaves no file.

Allowed protected-path changes: none.

### Verification

- `make verify` passes (new tests included; no extra, no tokenizer file, no Docker).
- `uv tree --package way2australia-rag` shows `tokenizers` and `huggingface_hub` without `torch` in the base set (output in the handoff).
- `git status --porcelain -- evaluation knowledge config` is empty.
- `graphify update .`

## T2 — Structure and recursive chunkers

**State:** not started
**Requirements:** R3, R4

- [ ] `ingestion/chunking.py`: `ChunkerIdentity` (name, version, sorted params, tokenizer); `Chunker` Protocol gains `identity` and drops `max_chunk_chars`; `HeadingChunker.identity` (params `{"max_chunk_chars": N}`, tokenizer `None`), output unchanged; shared sentence-end splitter (`.`, `?`, `!`, `।` followed by whitespace or end of text).
- [ ] New `ingestion/structure.py`: `StructureChunker` (`structure` v1) per the design: heading paths, `section_id = slugify(" / ".join(path))`, `DuplicateSectionError` (including a heading slugged `main` next to a preamble), blocks (fences, list items, paragraphs), prefix `none` or `title_and_headings`, packing by counting the composed string, oversized-block fallback (line, sentence end, whitespace, character), cap from 32 to the model maximum, prefix-too-long error.
- [ ] New `ingestion/recursive.py`: `RecursiveChunker` (`recursive` v1): separators, packing, overlap of trailing units at most `overlap_tokens`, prefix `none` or `title`, `target_tokens >= 32`, `0 <= overlap_tokens < target_tokens / 2`, `section_id` `main`, positions `0..n-1`.
- [ ] Snapshot files under `packages/rag/tests/ingestion/snapshots/` per chunker and version: seed corpus (with `FakeTokenizer`) and synthetic fixtures. A changed output fails the test and needs a version bump.
- [ ] Record the real chunk counts for the R10 arm (`recursive` v1, 128 / 16, `title`) on the 13 seed documents with the cached BGE-M3 tokenizer, read-only, through a throwaway script outside the repository or the opt-in smoke test; add them to the design's `## As-built notes` beside the design's prototype table (34 chunks, at most 4 per document). If the real tokenizer is not available to the agent, note that T6's `chunk_stats` is the record.
- [ ] Tests (`tests/ingestion/test_structure.py`, `test_recursive.py`, `test_chunking.py` additions):
  - `structure` v1 synthetic fixtures: nested headings; the same heading under different parents gives different IDs; duplicate siblings and a `main` collision raise `DuplicateSectionError`; fences are atomic and never parsed as headings; long lists split only between items; a long Malayalam paragraph; an oversized block; both prefix modes; IDs unchanged when another section is reordered, inserted or removed; every chunk `count <= cap`; the 13 seed documents give one chunk each with `section_id` `main`.
  - `recursive` v1: no chunk above `target_tokens`; neighbours share an overlap of at most `overlap_tokens`; identical output on repeat; invalid parameters refused; seed documents split into several chunks at 32 fake tokens and one chunk at a large target.
  - sentence-end rule (both chunkers): splits after `.`, `?`, `!` and `।` followed by a space, a newline or the end of text; no split inside `1.5`, `A$20.00`, `naati.com.au` or the inner dot of `e.g.`; a Malayalam sentence ending in `।` followed by a space splits.
  - `HeadingChunker` output on the seed corpus and the existing fixtures unchanged; `identity` as designed.
  - no language-specific branches: a test asserts the chunker modules contain no script-range or language-code literals other than `।` in the shared sentence-end set.

Allowed protected-path changes: none.

### Verification

- `make verify` passes.
- `git status --porcelain -- evaluation knowledge config` is empty.
- `graphify update .`

## T3 — Configuration, index settings, lexical identity and per-document freshness

**State:** not started
**Requirements:** R5, R6

- [ ] `ingestion/config.py`: `IngestionConfig` schema 1.1 with a discriminated `chunker` union (`heading` / `structure` / `recursive` and their parameters); 1.0 files still valid (`heading` only); `chunker_identity(config)` without loading a tokenizer (tokenizer identity string from the embedder configuration).
- [ ] `ingestion/cli.py`: `build_chunker` dispatches on the name and validates the cap against the built tokenizer's maximum; the existing `--config PATH` option of `ingestion/cli.py`, `lexical/cli.py`, `retrieval/cli.py` and `evaluation/cli.py retrieval` selects a 1.1 file unchanged; a test runs each CLI's config loading with `recursive-128.yaml`.
- [ ] `ingestion/settings.py`: `IndexSettings` 1.1 (`chunker_params`, `chunker_tokenizer` in place of `chunker_max_chunk_chars`); 1.0 records upgraded in memory and never rewritten; `compare` ignores `schema_version` and `hash_contract`; new collections written as 1.1; mismatch message lists the chunker fields.
- [ ] `lexical/store.py`: lexical settings 1.1 with the `ChunkerIdentity` fields; `open` refuses a 1.0 file with the rebuild advice from the design; `check_identity(expected, chunker_identity, hash_contract)`; `document_versions()`; `chunks_per_document()`; `bind_to` compares the chunker identity with the dense settings' 1.1 view and keeps the chunk-digest comparison.
- [ ] `lexical/freshness.py`: `verify_fresh(lexical, repository, chunker_identity)` compares the eligible `(document_id, document_version, content_hash)` set with `document_versions()`; refusal with counts and advice; no chunker, no tokenizer.
- [ ] `retrieval/opening.py`: the standalone and fallback paths use `chunker_identity(config)` from the config the CLI's `--config` selected; `build_tokenizer` is never called on these paths.
- [ ] New `experiments/configs/chunking/recursive-128.yaml` (schema 1.1, `idx-v2`, `recursive` v1, 128 / 16, `title`, embedder block equal to `config/ingestion.yaml`) and `experiments/configs/chunking/heading-idx-v1.yaml` (byte copy of `config/ingestion.yaml`).
- [ ] Tests:
  - config 1.0 and 1.1 parsing and refusals (unknown chunker, bad parameters); `chunker_identity(config)` equals `build_chunker(config).identity` for all three chunkers.
  - a stored 1.0 `IndexSettings` record matches a `heading` v1 configuration and is not rewritten; a 1.1 mismatch lists the chunker fields; `DenseIndex` binding still ignores chunker fields (D036).
  - a 1.0 lexical fixture file is refused with the advice; rebuilding it through `build_lexical_index` gives a 1.1 file with the same `source_chunk_digest` and chunk count.
  - per-document freshness: fresh passes; an edited, removed or added document is refused with the right counts; a chunker identity difference is refused by name.
  - with `build_tokenizer` patched to raise, `--strategy bm25` and the hybrid open-time and per-query fallbacks still serve (`open_retrieval` and CLI tests).
  - `heading-idx-v1.yaml` is byte-identical to `config/ingestion.yaml` (this test is removed or inverted in T6 only if the arm is promoted); `recursive-128.yaml`'s embedder block equals `config/ingestion.yaml`'s.
  - Docker (`make test-integration`): a fake-embedder ingestion with `recursive` v1 into a throwaway base gives several chunks per document and a second run reports 0 added, updated and deleted; a collection whose settings record is 1.0 binds and ingests unchanged.

Allowed protected-path changes: none.

### Verification

- `make verify` passes.
- `make test-integration` passes (Docker Qdrant running).
- `make index-lexical LEXICAL_ARGS="--embedder fake"` with `QDRANT_COLLECTION_BASE=w2a-t009-<8 hex>` and a throwaway `W2A_LEXICAL_INDEX_DIR` writes a 1.1 file; the throwaway files and collections are removed afterwards.
- `git status --porcelain -- evaluation knowledge config` is empty.
- `graphify update .`

## T4 — Distinct-document metrics, result 2.3 and cross-index compare

**State:** not started
**Requirements:** R7, R8

- [ ] `evaluation/retrieval_eval.py`: retrieve each case at `D = fusion.candidate_depth`; `ranked = dedupe_documents(hits)[:k]`; hit, recall and reciprocal rank on that list (MRR@k); leg ranks unchanged.
- [ ] Depth check after binding: `m` from `chunks_per_document()` (lexical file bound) or the dense `chunk_identities()`; refuse (exit 2) unless `(k − 1) · m + 1 <= D`, naming `m`, `k`, `D` and the advice.
- [ ] `evaluation/results.py`: result 2.3 adds `metric_unit`, `retrieval_depth`, `chunk_stats {chunk_count, document_count, max_chunks_per_document, required_depth}`, `chunker` (from the bound settings, or the lexical file on standalone and fallback paths) and `ingestion_config {path, sha256}`; every 2.2 field keeps its meaning.
- [ ] `evaluation/compare.py`: read 2.3; `--cross-index` allows collection, `index_version`, `chunker` and `ingestion_config` differences (printed) and keeps every other refusal (suite and version, embedder pair, lexical tokenizer, `top_k`, `metric_unit`, mixed served strategies, Spec 006 refusals) and the D044 gate; the chunk digest is not compared across indexes; cross-index needs 2.3 on both sides; without the flag, 2.3 against 2.0–2.2 only under the one-chunk-per-document rule, else refused with "re-run both with result 2.3".
- [ ] `evaluation/cli.py` `compare --cross-index`; `Makefile` `eval-compare` passes `$(COMPARE_ARGS)`; usage line updated.
- [ ] Tests:
  - on a frozen one-chunk-per-document fixture (fake index) per-case ranked documents, hits, recall, reciprocal ranks and aggregates equal the 2.2 computation for `dense`, `bm25` and `hybrid`.
  - a multi-chunk fake index: a document whose second chunk ranks 6 is still found at k distinct documents; a relevant document at distinct rank 7 gives reciprocal rank 0.
  - depth check: passes at the boundary `(k − 1) · m + 1 == D`, refuses one above it, with the message fields.
  - result 2.3 keys and values (including `chunk_stats` from the data, `chunker` on the fallback path from the lexical file).
  - compare matrix: each allowed difference passes with `--cross-index` and is refused without it; each still-refused difference is refused with it; 2.3 against a 2.2 one-chunk file passes without the flag; 2.3 multi-chunk against 2.2 refused; cross-index with a 2.2 side refused; the gate fails on a constructed regression.
  - the legacy snapshot test passes untouched.

Allowed protected-path changes: none.

### Verification

- `make verify` passes.
- `make eval-compare BASE=... CANDIDATE=... COMPARE_ARGS=--cross-index` on two synthetic 2.3 files written by a test into `experiments/results/tmp/` runs and prints the chunker difference; the files are removed. (`make eval-retrieval` refuses a fake embedder by design, so the real 2.3 runs are T6's.)
- `git status --porcelain -- evaluation knowledge config` is empty.
- `graphify update .`

## T5 — Security gate across chunkers

**State:** not started
**Requirements:** R9

- [ ] `evaluation/security_index.py` and `security_eval.py`: run the five paths (`dense`, standalone `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`) for `heading` v1 (2000 characters), `structure` v1 (`max_chunk_tokens` 64, `title_and_headings`) and `recursive` v1 (`target_tokens` 32, `overlap_tokens` 4, `title`) with `FakeEmbedder` and `FakeTokenizer`; forbidden and canary points built per chunker, nearest by construction; lexical identity checks use `ChunkerIdentity`.
- [ ] Security result 1.3: `runs: [{chunker, paths: {...1.2 shape...}}]` and overall `pass`.
- [ ] `test_security_eval.py` parameterized over the three chunkers (inside `make verify`); `test_security_integration.py` covers at least the `recursive` v1 run on Docker.
- [ ] No new authorization code: `git diff main -- packages/rag/src/way2australia_rag/retrieval/access.py packages/rag/src/way2australia_rag/retrieval/bm25.py` shows no change to the access clause or `check_hit`.

Allowed protected-path changes: none.

### Verification

- `make verify` passes.
- `make eval-security` passes for all five paths and three chunkers (output in the handoff).
- `make test-integration` passes.
- `git status --porcelain -- evaluation knowledge config` is empty.
- `graphify update .`

## T6 — User-owned real runs and the default index

**State:** not started
**Requirements:** R10

Run by the user (real model, `w2a-realcheck` collections); the agent prepares the commands, then checks and records the files. Before the runs: the tree (including `graphify-out/`) is clean and earlier result files are committed.

- [ ] **Lexical rebuild for `idx-v1`.** Before rebuilding, record the old file's `source_chunk_digest` and chunk count with a read-only SQLite query. Then `QDRANT_COLLECTION_BASE=w2a-realcheck make index-lexical` (no extra, no Qdrant, no weights; the guard uses the cached tokenizer files). Check that the new file is lexical settings 1.1 with the same digest and chunk count (13), and record both in `CURRENT_STATE.md`. The Qdrant collection is not touched.
- [ ] **Baseline.** `make setup-bge-m3`; `QDRANT_COLLECTION_BASE=w2a-realcheck make eval-retrieval` (result 2.3, `idx-v1`, `hybrid`); `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v1-20261101T070736Z.json CANDIDATE=<baseline 2.3>` must pass with 68 → 68 hits, MRR 0.9094 → 0.9094 and no flips. A difference stops T6 for a spec decision.
- [ ] **Arm.** With `QDRANT_COLLECTION_BASE=w2a-realcheck`: `make ingest INGEST_ARGS="--config experiments/configs/chunking/recursive-128.yaml"` (builds `w2a-realcheck-idx-v2`), `make index-lexical LEXICAL_ARGS="--config experiments/configs/chunking/recursive-128.yaml"`, `make eval-retrieval EVAL_ARGS="--config experiments/configs/chunking/recursive-128.yaml"`. Ingestion must report no `chunk_too_long` failures.
- [ ] **Depth check from `chunk_stats`.** The agent reads the arm's `chunk_stats`: `chunk_count` (expected about 34), `max_chunks_per_document` (expected about 4, at most 12) and `required_depth <= retrieval_depth` (50); records the numbers and any difference from the T2 counts.
- [ ] **Compare.** `make eval-compare BASE=<baseline 2.3> CANDIDATE=<arm 2.3> COMPARE_ARGS=--cross-index`.
- [ ] **Promotion rule.** Promote only if the gate passes, neither hits nor MRR drop, at least one improves, and no `ml` or `mixed` case flips from hit to miss; a tie keeps the baseline. Record the decision with the numbers, flips by `case_id`, the `g061` rank in both runs, and that the result belongs to "128 tokens + title prefix" together.
- [ ] **If promoted**, in this order:
  1. `make ingest INGEST_ARGS="--config experiments/configs/chunking/recursive-128.yaml"` without `QDRANT_COLLECTION_BASE` (real BGE-M3, collection `way2australia-idx-v2`); the `w2a-realcheck-idx-v2` collection already exists from the arm run (re-running there reports 0 changes and is optional);
  2. `make index-lexical LEXICAL_ARGS="--config experiments/configs/chunking/recursive-128.yaml"` for the same base;
  3. then the config change: `config/ingestion.yaml` takes the content of `recursive-128.yaml`; the T3 byte-copy test is updated to pin `heading-idx-v1.yaml` to the old content (from git) instead;
  4. check that `make retrieve QUERY="..."` and `make eval-retrieval` without `--config` bind to `idx-v2`, and that `--config experiments/configs/chunking/heading-idx-v1.yaml` still binds to `idx-v1`;
  5. `make setup` restores the default environment.
- [ ] **If not promoted:** `config/ingestion.yaml` unchanged; default stays `heading` v1 / `idx-v1`.
- [ ] The agent checks each result file: suite, `index_version`, collection, embedder pair, `chunker`, `ingestion_config` hash, `git_commit`, `git_dirty` false, served strategies, `fallback_counts` empty; any deviation is recorded for the user to accept. Result files are committed.

Allowed protected-path changes: `config/ingestion.yaml`, only if promoted.

### Verification

- The two `make eval-compare` outputs (baseline vs reference, arm vs baseline cross-index) recorded in `CURRENT_STATE.md` "Next step".
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists nothing, or only `config/ingestion.yaml` if promoted.
- If promoted: `make verify` passes after the config change; `graphify update .`

## T7 — Documentation, decisions, carry-over clean-ups and hand-off

**State:** not started
**Requirements:** R11, Definition of Done

- [ ] Clean-ups: rename `lexical/build.py` `_identity` to public `chunk_identity` and import only public names in `freshness.py` and `security_eval.py` (Spec 008 note); correct the `settings.py` `max_length` docstring (Spec 004 T5 F2); add a test for the embedder returning the wrong number of vectors in `IngestionService._embed` (Spec 004 T7 F3).
- [ ] `DECISIONS.md` D063 onward: tokenizer dependency and loading; truncation guard (closes Spec 004 T7 F1); `structure` v1 and `recursive` v1, heading-path `section_id`s and the duplicate refusal, the sentence-end rule; `ChunkerIdentity`, settings 1.1 and lexical settings 1.1 with per-document freshness, amending D060's large-corpus caveat; distinct-document metrics, the depth check and result 2.3; cross-index compare and the format rule (extends D054); security result 1.3 (extends D061); the default-index decision from T6, stating that the arm's result belongs to "128 tokens + title prefix" together.
- [ ] `ARCHITECTURE.md` (ingestion and lexical sections, chunkers, freshness), `TECH_STACK.md` (`tokenizers`, `huggingface_hub`), `COMMANDS.md` (`--config` with `experiments/configs/chunking/*.yaml`, `COMPARE_ARGS=--cross-index`, the one-time lexical rebuild), `ROADMAP.md` item 7 status, `CURRENT_STATE.md` (implemented reality, spec status, known issues, carry-overs: headed documents and `relevant_section_ids`, FAQ pairs, semantic chunking, separating size from prefix, per-scope lexical files, Malayalam stemming, the HTTP-route items).
- [ ] Design `## As-built notes` for every difference from the approved design.
- [ ] Spec-wide checks and the protected-path diff.

Allowed protected-path changes: none beyond T6.

### Verification

- `make verify`, `make test-integration`, `make eval-security`, `make validate-knowledge` and `make validate-evaluation` pass; counts in the handoff.
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists at most `config/ingestion.yaml`.
- `graphify update .`
- Docs reviewed against the code; ready for the `spec-reviewer` retrospective.
