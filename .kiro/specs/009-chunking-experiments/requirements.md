# 009 — Chunking Experiments Requirements

Status: approved (2026-11-01)

## Goal

Make chunking measurable and safe, and test one alternative chunking against the current index (roadmap item 7). Concretely:

- chunk sizes are counted in the embedding model's own tokens (BGE-M3 tokenizer, pinned to the embedder's model ID and revision), instead of the Spec 004 character cap, through a tokenizer that needs no PyTorch;
- no chunk is ever silently truncated: tokens are counted before embedding and a chunk longer than the model's maximum sequence length (or the configured cap) fails ingestion for that document;
- two new chunkers exist next to `heading` v1: a structure-aware chunker (heading sections, block-boundary splits, heading-path `section_id`s that do not depend on order, optional parent-heading context) and a recursive token chunker (structure-blind, token target plus overlap);
- index settings, the lexical file identity and evaluation results record the chunker identity; lexical freshness compares documents (not re-chunked text), so standalone `bm25` needs no tokenizer;
- document metrics are computed at k distinct documents, so indexes with several chunks per document are measured fairly; `eval-compare` gains an explicit cross-index mode;
- the security gate covers every chunker;
- user-owned real runs compare two arms (the current `idx-v1` baseline and one recursive arm at a small token target), and a promotion rule decides the default index.

Repository facts that shape the scope (checked 2026-11-01 with the cached BGE-M3 tokenizer at revision `5617a9f`): the 13 eligible documents have no headings and are 110–378 tokens each (591–1702 characters), so every document is one chunk under any cap considered and far below BGE-M3's 8192-token limit. The truncation guard therefore cannot fire on today's corpus, and the structure chunker would also produce one chunk per document; it is verified on synthetic headed fixtures. Only a small-target recursive arm changes chunk granularity on this corpus, which is why the real runs compare the baseline against the recursive arm only. `g061` (needs one bullet of `official_002_candidate_rules_setup`) is observed, not an acceptance criterion.

## Dependencies

- Spec 008: retrieval fallback (verified, merged `1107b67`): `open_retrieval`, `FallbackRetriever`, standalone lexical open, `IndexIdentity`, `verify_fresh` (D060), result 2.2, security result 1.2 with five gated paths (D061).
- Spec 007: lexical store with `dense_identity` copy and `source_chunk_digest` (D050), `lexical-v1` (D051), `HybridRetriever`, `config/retrieval.yaml` (`default_strategy: hybrid`, candidate depth 50, D055), `eval-compare` identity rules (D054).
- Spec 006: governed suite loader, `make eval-retrieval`, `make eval-security`, `make eval-compare` and the D044 gate; `evaluation/sections.py` (section-level reporting, unchanged here).
- Spec 005: `ResolvedAccess`, `build_access_filter`, `check_hit` (D035, D040), `DenseIndex` binding that ignores chunker fields (D036).
- Spec 004: `Chunker` Protocol, `HeadingChunker` (`heading` v1), `slugify` (D026), `IndexSettings` and mismatch refusal by new `index_version` (D028), `IngestionService`, `config/ingestion.yaml`, the BGE-M3 adapter (D027).
- Spec 002: `LocalDocumentRepository`, `content_hash` (`content-hash-v1`), `GUEST_PUBLIC_POLICY`.
- Reference results (suite `public-eval-v2` v2, `w2a-realcheck-idx-v1`, BAAI/bge-m3 @ `5617a9f`): hybrid `experiments/results/retrieval-evaluation-idx-v1-20261028T123121Z.json` and `...20261101T070736Z.json` (68 of 69, MRR 0.9094); BM25 `...20261028T123109Z.json` (64 of 69, MRR 0.7082).
- Retrospective notes: `.kiro/specs/007-hybrid-retrieval/review.md` and `.kiro/specs/008-retrieval-fallback/review.md`, "Notes for the next spec".
- New runtime dependency: `tokenizers` (Rust wheel, no PyTorch) as a base dependency of `packages/rag`. The BGE-M3 tokenizer file is read from the Hugging Face cache at the pinned revision (downloaded once; works offline afterwards).
- The real runs (R10) need `make setup-bge-m3`, Docker Qdrant and the user's `w2a-realcheck` collections. They are run by the user.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-11-01, with these choices:

- **Name.** `009-chunking-experiments`.
- **Sections (Q1: c).** The 13 knowledge documents stay unchanged. No headed documents and no suite v3 in this spec; `relevant_section_ids` stays empty and is deferred to a later spec. The structure chunker is verified on synthetic headed fixtures.
- **FAQ pairs (Q2: a).** `knowledge/structured/owner_approved_faq_pairs.jsonl` is not indexed here; FAQ-aware indexing gets its own spec.
- **Tokenizer (Q3: a).** `tokenizers` becomes a base dependency. Lexical freshness compares, per eligible document, `document_id`, `document_version` and `content_hash`, plus the chunker identity, instead of re-chunking; standalone `bm25` needs no tokenizer and no `bge-m3` extra. This also addresses the D060 large-corpus cost (no chunking or chunk hashing at open time).
- **Measuring (Q4).** Document metrics at k distinct documents; an explicit cross-index `eval-compare` mode that keeps the D044 gate and every other identity refusal.
- **Carry-overs (Q5).** Per-scope lexical files and Malayalam stemming are notes only.
- **Real runs.** At most two arms: the current baseline (`idx-v1`, `heading` v1) and one recursive arm at a small token target. The promotion rule (R10) is the one proposed in the brief.
- **Shape.** About seven tasks: tokenizer and truncation guard; structure and recursive chunkers; index settings, lexical identity and per-document freshness; metrics, result 2.3 and cross-index compare; security gate; user real runs; docs, decisions and three carry-over clean-ups.
- **Consequence to note.** `heading` v1 and `idx-v1` stay unchanged (character cap) because changing them would need a new index. If the recursive arm is not promoted, the default index keeps the character-capped `heading` v1, protected by the token guard (R2); token-capped chunking then exists but is not the default.

## R1 — Chunk tokenizer

Chunk sizes are measured with the embedding model's own tokenizer, without PyTorch.

### Acceptance criteria

- One `ChunkTokenizer` interface counts the tokens of a text exactly as the embedder would see it (including special tokens), and reports its identity (name, model ID, revision) and the model's maximum sequence length.
- The BGE-M3 implementation uses `tokenizers` (a base dependency), loads the tokenizer for the configured embedder model ID and pinned revision, and never imports PyTorch or `sentence-transformers`.
- A deterministic fake tokenizer (no files, no network) pairs with the fake embedder; unit tests and `make verify` need neither the `bge-m3` extra nor the tokenizer file.
- The tokenizer is always derived from the embedder configuration; there is no separate, independently configurable tokenizer model.
- A missing tokenizer file (not cached and offline, or a wrong revision) is a configuration error (exit 2, advice names the setup step), never a fallback and never a silent default.
- A test pins that the BGE-M3 tokenizer's count for a fixed text equals the count from the model adapter's own tokenizer when the extra is installed (opt-in, skipped without the extra).

## R2 — Truncation guard

No chunk is embedded if the model would truncate it.

### Acceptance criteria

- Before embedding, ingestion counts the tokens of the exact text sent to the embedder for every chunk. A chunk above the model's maximum sequence length, or above the chunker's configured token cap when it has one, is refused.
- A refusal is a per-document failure: no points are written or deleted for that document, the run report names the document ID, section ID, position, token count and limit (never chunk text), and the run exits non-zero. Other documents proceed as today.
- Chunking runs inside the per-document error handling, so a chunker exception also becomes a per-document failure instead of aborting the run (closes Spec 004 T7 F1).
- The guard applies to every chunker, including `heading` v1 on `idx-v1`; it changes no vectors or settings, so `idx-v1` needs no rebuild.
- Tests: an oversized chunk with the fake tokenizer and fake embedder is refused with the expected report and no writes; a chunker exception becomes a per-document failure; documents within the limit are unaffected.

## R3 — Structure-aware chunker

A structure-aware chunker splits on headings and block boundaries under a token cap, with order-independent section IDs.

### Acceptance criteria

- A new chunker (name and version set in design, e.g. `structure` v1) splits on ATX headings outside code fences (as `heading` v1 does). Text before the first heading is section `main`.
- `section_id` is the `slugify`d heading path (ancestor headings plus the heading). Adding, removing or reordering other sections never changes a section's ID; the same heading under different parents gives different IDs.
- Two sibling headings whose paths slug to the same `section_id` are refused (a chunker configuration or document error, reported per document by ingestion), not numbered by order. A synthetic fixture covers it.
- Inside a section, pieces split only at block boundaries (paragraphs, list items, fenced blocks) and are packed up to the token cap; a single block above the cap is split at sentence, then whitespace boundaries; no piece exceeds the cap.
- An optional context prefix (title and heading path; on or off by configuration) is part of the chunk text, counts against the cap and is recorded in the chunker identity.
- The chunker is pure and deterministic, has no language-specific behaviour and uses the R1 tokenizer interface.
- Tests on synthetic headed fixtures (nested headings, duplicate headings under different parents, duplicate siblings, fences, long lists, a long Malayalam paragraph, an oversized block) and on the 13 seed documents (one chunk each, `section_id` `main`).

## R4 — Recursive chunker

A structure-blind recursive token chunker exists as the recursive baseline.

### Acceptance criteria

- A new chunker (e.g. `recursive` v1) splits text by a fixed separator hierarchy (paragraph, line, sentence, whitespace) into pieces of at most a configured token target, with a configured token overlap.
- Configuration validation: target at least a minimum set in design, overlap at least 0 and less than half the target; invalid values are a configuration error.
- Chunks carry one `section_id` (`main`) and consecutive positions, so point IDs stay unique and stable for unchanged content.
- Deterministic and language-agnostic; the optional context prefix (title) follows R3 rules.
- Tests: no piece above the target; overlap present between neighbours; identical output on repeat; seed documents split into several chunks at a small target and one chunk at a large one.

## R5 — Chunker configuration and index settings

The chunker and its parameters are index-defining settings, and existing indexes stay usable.

### Acceptance criteria

- `config/ingestion.yaml` selects the chunker by name and version with its parameters (cap unit and value, overlap, context prefix). A config schema version bump is validated; `idx-v1`'s current file content remains valid.
- `IndexSettings` gets a new schema version that records the chunker name, version and all its parameters, plus the tokenizer identity when one is used. A difference in any of them is a mismatch refused by the D028 rule (new `index_version`).
- Settings stored with schema 1.0 (`idx-v1`) are still read, compared and bound without re-ingestion.
- `DenseIndex` binding still ignores chunker fields (D036).
- Each experiment arm uses its own `index_version` (collection `<base>-<index_version>`).

## R6 — Lexical identity and per-document freshness

The lexical file records the chunker identity, and freshness no longer re-chunks.

### Acceptance criteria

- The lexical file records the full chunker identity from R5 next to its dense identity copy; standalone `check_identity` compares it with configuration.
- Standalone freshness compares the set of (`document_id`, `document_version`, `content_hash`) of eligible repository documents with the set recorded in the file, plus chunker identity equality. It does not chunk, tokenize or load the tokenizer. Refusals report counts only (documents only in the repository, only in the file, changed).
- Standalone `bm25` and the hybrid fallback still need neither Qdrant nor the `bge-m3` extra nor the tokenizer file (test with the tokenizer made unavailable).
- `make index-lexical` and `make ingest` with a token-based chunker need the tokenizer; with the fake embedder they use the fake tokenizer.
- The `bind_to` path keeps its chunk-digest comparison with the live collection.
- An `idx-v1` lexical file built before this spec is either still accepted or refused with rebuild advice; the design states which, and a test covers it. The Qdrant collection itself is never rebuilt for this.
- The D060 large-corpus caveat is updated: chunking and chunk hashing are no longer paid at open time.

## R7 — Distinct-document metrics at k

Document metrics compare fairly across indexes with different chunk counts per document.

### Acceptance criteria

- `make eval-retrieval` retrieves to the candidate depth (at most `MAX_TOP_K`), removes duplicate documents in rank order and computes HitRate@k, Recall@k and MRR over the first k distinct documents.
- On an index with one chunk per document the per-case ranked document IDs and all metrics equal the 2.2 computation (test against a frozen fixture and the reference rows).
- Result format 2.3 records the chunker identity, the metric semantics (distinct documents at k, retrieval depth) and chunks-per-document statistics; all 2.2 fields keep their meaning.
- `make retrieve` is unchanged (top-k chunks). Section-level reporting is unchanged (no case has `relevant_section_ids`).

## R8 — Cross-index comparison

`eval-compare` can compare two indexes only when asked to, and never across metric semantics silently.

### Acceptance criteria

- Without the new explicit flag, `eval-compare` behaves as today (a different `index_version` or collection is refused, D054). When both sides are result 2.3, a difference in chunker identity is refused (exit 2), naming the field.
- With the flag, differences in collection, `index_version` and chunker identity are allowed and printed. The suite, embedder pair, lexical tokenizer, `top_k`, served-strategy rules (D061) and every other identity refusal still apply, and the D044 gate is unchanged.
- Cross-index mode requires result 2.3 on both sides. Comparing a 2.3 file with an earlier format is allowed only under the equivalence condition the design defines (one chunk per document on both sides); otherwise it is refused with advice to re-run.
- Tests cover each allowed difference, each still-refused difference, the format rule and the gate.

## R9 — Security gate across chunkers

Authorization is unchanged by chunking.

### Acceptance criteria

- `make eval-security` passes all five Spec 008 paths (`dense`, standalone `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`) for `heading` v1, the structure chunker and the recursive chunker on the throwaway corpus with the fake embedder and fake tokenizer, with forbidden points still nearest by construction. The throwaway `recursive` v1 arm uses `target_tokens` 48, `overlap_tokens` 4 and `title` (not 32), because the T3 prefix rule refuses `official_003_booking_fees_validity` at 32+title with `FakeTokenizer`.
- The security result (new minor version) records the chunker identity per run; the gate inside `make verify` covers every chunker.
- No new authorization path: the same `ResolvedAccess`, `build_access_filter`, SQL access clause and `check_hit`.

## R10 — User-owned real runs and the default index

Two real arms are compared and the default index is chosen by a fixed rule.

### Acceptance criteria

- The user runs, on suite `public-eval-v2` v2 with BGE-M3 @ `5617a9f` and the default strategy `hybrid`:
  - the baseline: `idx-v1` (`heading` v1, unchanged collection) re-evaluated with result 2.3; it must equal the 2.2 hybrid reference (68 of 69, MRR 0.9094) under `eval-compare`;
  - one recursive arm at a small token target (value set in design) in a new `index_version`, after `make ingest` and `make index-lexical`;
  - `make eval-compare` in cross-index mode, recursive arm against the baseline.
- Promotion rule (from the brief, as in Spec 007 R13): the recursive arm becomes the default index in `config/ingestion.yaml` only if it passes the `eval-compare` gate, neither hits nor MRR drop and at least one improves, and no `ml` or `mixed` case flips from hit to miss. Otherwise `idx-v1` stays the default. The decision is recorded with the numbers.
- Result files are recorded and committed; the agent checks their fields (identity, `git_dirty`, served strategies, chunk statistics) and records any deviation for the user to accept. `g061` is reported, not gated.

## R11 — Documentation, decisions and carry-over clean-ups

The repository records what was built.

### Acceptance criteria

- `DECISIONS.md` gets new decisions (D063 onward) for the tokenizer dependency, the truncation guard, the chunkers and section IDs, settings and lexical identity with per-document freshness (amending the D060 cost caveat), distinct-document metrics and result 2.3, cross-index comparison, the security result version and the default-index decision.
- `ARCHITECTURE.md`, `TECH_STACK.md` (`tokenizers`), `COMMANDS.md`, `ROADMAP.md` (item 7 status) and `CURRENT_STATE.md` match the code.
- Carry-over clean-ups: `lexical/build.py`'s `_identity` becomes public and `freshness.py` stops importing a private name (Spec 008 note); the `settings.py` `max_length` docstring is corrected (Spec 004 T5 F2); a test covers the "embedder returned a wrong number of vectors" guard (Spec 004 T7 F3).
- Every code task's verification runs `graphify update .`; every post-approval amendment gets a dated `## Change log` line (Spec 008 retrospective F3).
- Protected paths: nothing under `knowledge/` or `evaluation/` changes; under `config/` only `ingestion.yaml` (and only as R5 and R10 require).

## Out of scope

- Headed or otherwise edited knowledge documents, a new `document_version` or Knowledge Release, suite `public-eval-v3`, and `relevant_section_ids` in evaluation cases (a later spec).
- FAQ-aware indexing or retrieval of `knowledge/structured/owner_approved_faq_pairs.jsonl` (its own spec).
- Semantic chunking.
- Changing `heading` v1 or rebuilding the `idx-v1` collection.
- A query-length guard for dense queries (input limits, roadmap 12) and any query transformation.
- Per-scope lexical files and non-guest roles (roles spec; D050).
- Malayalam stemming, the legacy chillu sequence and any `lexical-v1` change (roadmap 8; D051).
- Reranking, context building and generation (roadmap 9–10).
- The Spec 008 HTTP-route carry-overs: startup and reopen policy for a missing or stale lexical file, circuit breaker, Qdrant client lifecycle (with Spec 008 retrospective F4/F5), async freshness, fallback-stage observability, Qdrant 5xx eligibility (D062), API surface.
- Device pinning (D038); the Phase 2 "compare shared cases" mode; Phase 2 work; the other open Spec 004 nits and Spec 006 retrospective F1, unless a task touches the same code.

## Definition of Done

- R1–R11 satisfied and traced to approved tasks.
- R10 user-owned runs recorded, checked and committed; the default-index decision recorded.
- `make verify` (no extra, no tokenizer file, no Docker), `make test-integration` and `make eval-security` pass.
- Protected-path check: `git diff --name-status main...HEAD -- evaluation knowledge config` lists at most `config/ingestion.yaml`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `TECH_STACK.md`, `COMMANDS.md`, `ROADMAP.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | `test_tokenization.py` (fake counts, dispatch, monkeypatched cache hit/miss/offline/revision, no-path messages, no-torch import pin); opt-in BGE-M3 count and `max_seq_length` equality; `make verify` |
| R2 | T1 | `test_guard.py`; `test_service.py` (per-document failure, chunker exception inside the try, no text in reports); `test_lexical_build.py` (build refused); `make verify` |
| R3 | T2 | `test_structure.py` (synthetic headed fixtures, duplicate refusal, ID stability, cap, sentence-end rule); seed snapshots; `make verify` |
| R4 | T2 | `test_recursive.py` (target, overlap, repeatability, validation, sentence-end rule); seed snapshots; As-built chunk counts |
| R5 | T3 | config 1.0/1.1 tests; `chunker_identity` equality; settings 1.0 read and compare; D036 unchanged; `make test-integration` (recursive ingestion, 1.0 collection binds) |
| R6 | T3, T6 | lexical 1.0 refusal and rebuild digest equality; per-document freshness tests; `bm25` and fallback with `build_tokenizer` raising; T6 real rebuild with digest and count recorded |
| R7 | T4, T6 | one-chunk equivalence with 2.2; multi-chunk and MRR@k tests; depth-check boundary tests; result 2.3 keys; T6 `chunk_stats` check |
| R8 | T4, T6 | `test_compare.py` matrix (cross-index allowed/refused, format rule, gate); T6 baseline-vs-reference and cross-index compares |
| R9 | T5 | parameterized `test_security_eval.py`; `test_security_integration.py`; `make eval-security` (five paths × three chunkers) |
| R10 | T6 | user runs; `make eval-compare` outputs; promotion decision and, if promoted, the ordered promotion steps; field checks in `CURRENT_STATE.md` |
| R11 | T1–T7 | clean-up tests (vector-count guard); D063+; docs review against code; `graphify update .` per code task; protected-path diff |
| Definition of Done | T7 | `make verify`, `make test-integration`, `make eval-security`, `make validate-knowledge`, `make validate-evaluation`; `git diff --name-status main...HEAD -- evaluation knowledge config`; retrospective |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-11-01 — design (found while drafting tasks, before tasks approval): the ingestion, lexical, retrieval and `eval-retrieval` CLIs already have `--config PATH` for the ingestion config, so the design's new `--ingestion-config` option is dropped and the existing `--config` is used; design and tasks updated. No requirement text changed. No task re-opened (no tasks approved yet).
- 2026-11-02 — R3/R4: T2 review clarification (user-approved during round 2). Chunk bodies must equal the source apart from whitespace; the test collapses whitespace runs in the body and in the document, then requires the collapsed body to be a substring of the collapsed document (exact byte-level substrings are not required, because `structure` v1 normalizes joins). `recursive` v1 overlap takes the longest trailing run of whole units within `overlap_tokens` (content tokens), then drops units from the front until `count(prefix + tail + next unit) <= target_tokens`, and never repeats a unit that alone exceeds the budget. Design amended. T2 re-opened for implementer round 3.
- 2026-11-02 — R4/T3: apply the `structure` v1 prefix rule to `recursive` v1 — if the prefix alone leaves less than half of `target_tokens`, that document fails with a configuration error; test and regenerate `recursive` v1 snapshots if outputs change. Must land before T6 indexes `recursive` v1. Design and tasks T3 amended.
- 2026-11-02 — R7/R8/T5: T4 review follow-ups — E2E `run_retrieval_evaluation` on a fake multi-chunk index; refuse 2.3 vs 2.3 compare when chunker identity differs without `--cross-index`; real 2.2 fixture in the compare matrix. R8 amended. T5 amended (follow-up boxes added).
- 2026-11-02 — R9/T5: accept `recursive` v1 security gate at `target_tokens` 48 (was 32) with `overlap_tokens` 4 and `title`; T3 prefix rule blocks `official_003_booking_fees_validity` at 32+title on the seed corpus. Design amended.
