# 007 — Hybrid Retrieval Requirements

Status: approved (2026-10-25)

## Goal

Add a lexical (BM25) retrieval leg and Reciprocal Rank Fusion (RRF) with the existing dense leg, and measure dense, BM25 and hybrid retrieval against a new governed Evaluation Suite version:
- `public-eval-v2`: the 85 `public-eval-v1` cases plus the six owner- and fluent-speaker-approved pure-Malayalam goldens from `evaluation/candidates/006-candidates.jsonl` (91 cases);
- a user-owned real dense baseline on `public-eval-v2`, recorded before any hybrid change, so every later strategy is compared against v2 from the start;
- a language-neutral tokenizer (`lexical-v1`) and a derived, git-ignored SQLite FTS5 lexical index built from the same chunks and eligibility rules as the dense index;
- a BM25 retriever and a hybrid retriever that apply authorization inside every leg before fusion (D035, D040);
- `--strategy {dense,bm25,hybrid}` for `make retrieve` and `make eval-retrieval`, with `eval-compare` comparing strategies on otherwise identical runs;
- authorization hard-gate coverage of the BM25 and hybrid paths in `make eval-security` and on Docker Qdrant;
- a user-owned real comparison of the three strategies and an evidence-based decision on the default strategy.

This spec is roadmap item 6 (hybrid retrieval: BM25, RRF, dense vs sparse vs hybrid comparisons). The lexical index is designed so the later graceful-degradation spec (roadmap 13: dense failure → BM25, Qdrant failure → SQLite FTS5) can reuse it, but no fallback is wired here.

## Dependencies

- Spec 006: evaluation framework (verified, merged `ab28d89`). Provides the governed suite loader, `make validate-evaluation`, `make eval-retrieval` (result `retrieval_evaluation` 2.0, D043), `make eval-security` (D045, D047), `make eval-compare` (D044) and the candidates file.
- Spec 005: dense retrieval baseline (verified, merged `b33462e`). Provides `AccessContext`, `resolve_access`, `ResolvedAccess`, `build_access_filter`, `check_hit`, `DenseIndex`, `DenseRetriever`, `retrieval/metrics.py`, `safe_text`, `make retrieve`, the frozen legacy `make retrieval-baseline`.
- Spec 004: ingestion baseline (verified). Provides `HeadingChunker`, `PointPayload` (17 fields), UUIDv5 point IDs, `IndexSettings`, `config/ingestion.yaml` (`idx-v1`).
- Spec 002: `LocalDocumentRepository`, `EligibilityPolicy`, `GUEST_PUBLIC_POLICY`, the isolated security repository.
- Evaluation assets: `evaluation/suites/public-eval-v1.json` (version 1, `case_count` 85 = 63 goldens + 12 unanswerable + 10 security), the three datasets, `evaluation/candidates/006-candidates.jsonl` (6 approved `ml` candidates, `g004`/`u001` decided `keep_both`, all on 2026-10-25).
- Committed reference results: `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (1.0) and `experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` (2.0, suite `public-eval-v1` v1: HitRate@5 0.9524, MRR 0.8783, N=13, k=5, misses `g004`, `g026`, `g061`).
- Retrospective notes: `.kiro/specs/005-dense-retrieval-baseline/review.md` and `.kiro/specs/006-evaluation-framework/review.md` ("Notes for the next spec").
- The real runs (R2, R13) need `make setup-bge-m3` and the user's existing `w2a-realcheck-idx-v1` collection, used read-only. They are run by the user.
- SQLite FTS5 from the Python standard library (`sqlite3`); available in the project environment (SQLite 3.53.1). No new runtime dependency is expected.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-10-25: recommended defaults for Q1–Q8, with the additions below.

- **Suite layout (Q1).**
  - New manifest `evaluation/suites/public-eval-v2.json`: `evaluation_suite_id: public-eval-v2`, `version: 2`, `status: active`, `introduced_in_release: seed-v1`, `case_count: 91`, with its own dataset files.
  - The 85 v1 rows are copied into the v2 datasets with only `evaluation_suite_id` changed; `case_id`, `case_version` and every other field are unchanged.
  - The v1 dataset files stay byte for byte unchanged. The v1 manifest changes only its `status`, to `replaced`.
  - Because `eval-retrieval` refuses a suite that is not `active`, the committed v1 2.0 result becomes a closed reference: it can be read and compared with other v1 files but not re-run.
  - Fixed mapping: `cand006_ml_001` … `cand006_ml_006` → `g064` … `g069`, in order; `ml_002` and `ml_003` use their reworded queries (the `proposed_case.query` value).
  - Each promoted candidate row's `review` object gains `promoted_as: {suite_id, case_id}`; candidate rows stay `status: suggested`.
- **Release manifest (Q2).** No new Knowledge Release and no `knowledge/` edit. `knowledge/releases/seed-v1.json` keeps naming `public-eval-v1` version 1 (the release is declared, not verified, D037); recorded as a known issue for Phase 2 releases.
- **v1 → v2 continuity (Q3).** No Phase 2 "compare shared cases" mode. The new v2 dense result is the only reference for this spec. Continuity is checked once, outside the product code (R2).
- **Lexical store (Q4).** SQLite FTS5. The lexical index is a derived, git-ignored artifact, built from the same chunks and eligibility rules as `idx-v1`, never from the security fixtures. It records its own settings (index version, tokenizer name and version, source chunk set). The BM25 retriever refuses a mismatch the way `DenseIndex` does. Authorization (scope, tenant, owner) runs in the SQL `WHERE` clause, followed by the same fail-closed `check_hit` re-check (D040). Qdrant sparse vectors and BGE-M3 learned sparse weights are not used.
- **Tokenizer (Q5).** `lexical-v1`: NFC normalization, lowercase Latin text, Malayalam vowel signs and the virama kept attached to their base letters, ZWJ/ZWNJ (chillu forms) treated the same way every time, no stemming, no stopwords, no language-specific code path. Unit tests use real Malayalam words from the corpus and from `ml_001`–`ml_006`.
- **Fusion and strategy contract (Q6).** Client-side RRF (k = 60, equal weights, per-leg candidate depth 50), deterministic tie-breaks, fail closed if any leg fails its authorization re-check. An empty BM25 leg leaves the dense order unchanged. `eval-compare` allows a difference in strategy and shows it as an identity line; every other identity field (suite, index, embedder) must still match or the comparison is refused.
- **Default strategy (Q7).** `dense` stays the default until the user-owned comparison. The default becomes `hybrid` only if all hold: it passes the `eval-compare` gate against dense on v2; it improves hits or MRR; no `ml` or `mixed` case goes from hit to miss. The `ml` and `mixed` slices are reported in the decision.
- **Security (Q8).** `eval-security` covers the BM25 and hybrid paths with forbidden lexical rows that rank first without the filter. The FTS5 injection test shows that a raw query is never passed to `MATCH`: every token is quoted after tokenization.
- The v2 dense baseline (R2) and the strategy comparison (R13) are user-owned real runs. Agents never write to, delete or re-ingest the `w2a-realcheck-*` collections and never run the real model.

## R1 — Evaluation Suite `public-eval-v2`

A new active suite version adds the six approved Malayalam goldens under C6/D042, as the only change under `evaluation/` in this spec.

### Acceptance criteria

- `evaluation/suites/public-eval-v2.json` exists with `evaluation_suite_id: public-eval-v2`, `version: 2`, `status: active`, `introduced_in_release: seed-v1`, `case_count: 91`, and three datasets of its own: 69 `golden_answerable`, 12 `unanswerable_refusal`, 10 `security` rows (69 + 12 + 10 = 91).
- The 85 rows copied from v1 differ from their v1 rows only in `evaluation_suite_id` (`public-eval-v2`). A test compares every copied row with its v1 row field by field.
- Six new goldens `g064`–`g069` map, in order, from `cand006_ml_001`–`cand006_ml_006`. Each has `id` and `case_id` equal to the new ID, `case_version: 1`, `status: active`, `introduced_in_release: seed-v1`, `evaluation_suite_id: public-eval-v2`, `answerable: true`, and `query`, `relevant_document_ids`, `expected_facts`, `query_language` (`ml`), `category` (`multilingual`) and `access_context` equal to the candidate's `proposed_case` (so `g065` and `g066` carry the reworded queries).
- The v1 dataset files are byte-for-byte unchanged (hash test). The v1 manifest differs from its committed version only in `status: replaced`.
- In `evaluation/candidates/006-candidates.jsonl`, each of the six promoted rows gains `review.promoted_as: {"suite_id": "public-eval-v2", "case_id": "<g064…g069>"}`; no other field changes and every row keeps `status: suggested`. The `cand006_change_g004_u001` row is unchanged; `g004` and `u001` are carried into v2 unchanged (`keep_both`).
- `make validate-evaluation` validates both suites and passes. It also checks, for every candidate row with `review.promoted_as`, that the named suite exists, that it holds the named case, and that the case's `query`, `relevant_document_ids`, `expected_facts` and `query_language` equal the candidate's `proposed_case`; a mismatch is a validation problem.
- The candidate rows' `target_suite_id` (`public-eval-v1`) stays valid because the v1 manifest remains in the repository.
- `make eval-retrieval` and `make eval-security` default to `evaluation/suites/public-eval-v2.json`. The legacy `make retrieval-baseline` keeps its v1 default and its frozen behavior (D046).
- `make eval-retrieval --suite evaluation/suites/public-eval-v1.json` is refused (exit 2) because the suite is `replaced`.
- Tests that read the real suite follow the v2 default and use consistency checks, not hard-coded live counts; the frozen legacy fixture under `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/` is not touched.
- `make eval-security` passes on v2 (its golden queries now include `g064`–`g069`).
- The suite change is recorded in the `## Change log` below and in `CURRENT_STATE.md`. `knowledge/` is not edited.

## R2 — v2 dense baseline (user-owned gate)

Before any lexical or hybrid code, the user records a real dense `make eval-retrieval` result on `public-eval-v2`.

### Acceptance criteria

- R1 is approved and committed on `spec/007` before the run, so the result has `git_dirty: false` and a `git_commit` that contains the v2 suite.
- The user runs, with the `bge-m3` extra installed and `QDRANT_COLLECTION_BASE=w2a-realcheck`, `make eval-retrieval` (default suite v2, `top_k` 5) against `w2a-realcheck-idx-v1` (read-only), then `make setup`.
- The result file is checked and committed: `kind: retrieval_evaluation`, suite `public-eval-v2` version 2, `retrieval_strategy: dense`, 69 golden cases evaluated, 12 unanswerable cases reported, `embedder_is_fake: false`, collection `w2a-realcheck-idx-v1`, `index_version: idx-v1`, `top_k: 5`, `document_count: 13`, `git_dirty: false`.
- Continuity check (one-off, scratch script, not committed product code): the 63 shared goldens (same `case_id` and `case_version`) in the v2 result are compared with the committed v1 2.0 result. The expected outcome is 60 hits and MRR 0.8783 over those 63 cases; any difference is listed by `case_id` and explained (device noise, D038) in `CURRENT_STATE.md`.
- The overall, `en`, `mixed` and `ml` metrics of the v2 result are recorded in `CURRENT_STATE.md` as the Spec 007 reference. `ml` is no longer an absent query language.
- No task that adds lexical or hybrid code starts before this gate is approved.

## R3 — Tokenizer `lexical-v1`

One deterministic, language-neutral tokenizer is used both to index chunk text and to tokenize queries.

### Acceptance criteria

- The tokenizer has a name (`lexical-v1`) and version that are recorded in the lexical index settings and in results.
- Text is normalized to NFC. Uppercase letters are lowercased (no effect on scripts without case).
- Token characters are Unicode letters, numbers and combining marks (`Mn`, `Mc`); every other character separates tokens. Malayalam vowel signs and the virama therefore stay attached to their base letters, and no Malayalam word is split inside a grapheme cluster.
- ZWJ (U+200D) and ZWNJ (U+200C) never split a token and are handled by one documented rule, applied identically at index time and at query time. A test pins the result for a legacy chillu sequence (consonant + virama + ZWJ) and for the corresponding atomic chillu letter.
- No stemming, no stopword list and no language-specific branch: the code contains no language code literal (such as `ml`) and no script-specific table beyond Unicode character properties.
- Unit tests tokenize real Malayalam words taken from the corpus (`business_008_public_samples`) and from the queries of `g064`–`g069`, mixed-script text such as `dialogue-ൽ` (giving `dialogue` and `ൽ`), and English text, and pin the exact token lists.
- The same input always gives the same tokens (no randomness, no locale dependence).

## R4 — Lexical index build (`make index-lexical`)

A command builds the derived SQLite FTS5 lexical index for one Qdrant index identity.

### Acceptance criteria

- `make index-lexical` builds the lexical index from `DocumentRepository` documents that pass `GUEST_PUBLIC_POLICY`, chunked by the same chunker and settings as the dense index (`config/ingestion.yaml`), with the same UUIDv5 point IDs and the full `PointPayload` for each chunk.
- It never reads `tests/fixtures/security/`, `sources/raw/`, `evaluation/`, `docs/` or other non-production roots.
- Chunk text is tokenized with `lexical-v1` before it is stored; FTS5's own tokenizer is not relied on to split Malayalam (its default `unicode61` tokenizer splits Malayalam words at vowel signs).
- The index stores its own settings: lexical settings schema version, the `index_version` and collection it belongs to, tokenizer name and version, FTS5/BM25 parameters, and the source chunk set (every `point_id` with its `document_id`, `document_version` and `content_hash`, plus a digest of that set).
- The file lives in a git-ignored location whose default is derived from the collection name and `index_version`, so throwaway and real collections never share a file. It is never written under `knowledge/`, `evaluation/`, `config/` or a committed path.
- A build is a full rebuild written to a temporary file and moved into place atomically; a failed build leaves any previous file intact and no partial file.
- The build needs no embedding model, no PyTorch and no Qdrant writes. It prints the index path relative to the repository root (or the configured path), the chunk count and the source-chunk digest, and no chunk text, absolute paths or secrets.
- Exit codes follow the existing CLIs: `0` success, `2` refusal or configuration error.

## R5 — Lexical index binding

The lexical index is bound to the dense index and to the query tokenizer, and refuses a mismatch, like `DenseIndex.open` (D036).

### Acceptance criteria

- Opening the lexical index is read-only. It refuses (configuration error, exit 2 in the CLIs) a missing file, a missing or malformed settings record, an unknown settings schema version, a tokenizer name or version different from the code's, and an `index_version` or collection different from the dense index it is used with.
- When used together with a Qdrant index (hybrid, and whenever the run binds the dense index), the lexical source chunk set must equal the set of `(point_id, document_id, document_version, content_hash)` read read-only from the Qdrant index; otherwise the run is refused, naming the differing fields and the count of differing points, never chunk text.
- Refusal messages give retrieval-side advice (rebuild the lexical index with `make index-lexical` for this collection and `index_version`), consistent with D036's wording rules.
- Opening and binding perform no writes to Qdrant or to the lexical file.

## R6 — BM25 retriever and authorization

The BM25 leg ranks chunks with FTS5 `bm25()` and applies authorization inside its own query.

### Acceptance criteria

- `BM25Retriever.retrieve(query, access, top_k)` (name indicative) takes the same server-resolved `ResolvedAccess` as `DenseRetriever` and validates `query` and `top_k` with the same rules (non-empty query, integer 1–50).
- The authorization condition is part of the SQL query's `WHERE` clause: `access_scope` in the policy's allowed scopes, `tenant_id` equal to the server tenant, `owner_user_id IS NULL`. It is built only from `ResolvedAccess` by one function next to `build_access_filter` in `retrieval/access.py`, with bound parameters; no second scope list exists and no query text, flag or evaluation case can change it.
- `check_hit` re-validates every returned row's payload before any hit is returned; a violation raises `RetrievalAuthorizationError` (fail closed).
- The raw query is never passed to `MATCH`. The query is tokenized with `lexical-v1`, every token is quoted (with embedded quotes escaped), and the tokens are joined with `OR`. A query that yields no tokens returns zero hits without running `MATCH`.
- An injection test runs hostile queries (FTS5 operators such as `NEAR`, `AND`, `NOT`, `*`, column filters like `access_scope:staff`, unbalanced quotes, parentheses, SQL fragments) and shows that the `MATCH` argument is always the quoted token list, the SQL text is constant, and results stay authorized.
- Hits carry the same identity fields as dense hits (`point_id`, `document_id`, `section_id`, title, language fields) and a BM25 score, sorted best first with a deterministic tie-break.
- The BM25 leg never embeds the query.

## R7 — RRF fusion and hybrid retriever

The hybrid retriever fuses already-authorized dense and BM25 hits.

### Acceptance criteria

- The hybrid retriever runs the dense leg and the BM25 leg with the same `ResolvedAccess`, each with its own in-query authorization and `check_hit`, at a per-leg candidate depth of 50, then fuses with RRF: `score(p) = Σ 1 / (k + rank_leg(p))` over the legs that returned point `p`, with k = 60 and equal weights. Fusion operates on point IDs; metrics stay document-level.
- Authorization is never applied after fusion; fusion only ever receives hits that passed `check_hit` in their leg (D040). A test with a leg that returns a forbidden hit shows the whole hybrid query raises `RetrievalAuthorizationError` and returns nothing.
- Any leg error (authorization, binding, store failure) fails the hybrid query; there is no silent fallback to a single leg (graceful degradation is roadmap 13).
- Ordering is deterministic: fused score descending, then best rank in either leg, then `point_id`. Unit tests pin hand-computed fused scores and orders.
- An empty BM25 leg (for example a pure-`ml` query with no matching tokens) leaves the dense order unchanged: a test shows the hybrid ranking equals the dense ranking for that case.
- The result is truncated to `top_k` after fusion. Each hit records its fused score and its rank in each leg (or absence).
- RRF k, weights and candidate depth come from configuration (R8), not from query input.

## R8 — Strategy selection and configuration

Strategies are selected explicitly and configured in a reviewed file.

### Acceptance criteria

- A new `config/retrieval.yaml` holds the default strategy (`dense` in this spec until R13), RRF k (60), leg weights (equal) and per-leg candidate depth (50). It is validated on load; an unknown key or value is a configuration error.
- `make retrieve` and `make eval-retrieval` accept `--strategy {dense,bm25,hybrid}`; without it the configured default is used. There is still no option for role, scope or tenant.
- `make retrieve` prints the strategy in its header and, for hybrid, each hit's leg ranks; payload text still goes through `safe_text` (D041), with no bodies, absolute paths or secrets.
- The `dense` strategy behaves exactly as before this spec (same hits, scores and order); existing dense tests pass unchanged.

## R9 — Evaluation results for every strategy

`make eval-retrieval` records which strategy produced a result and enough per-leg detail to explain changes.

### Acceptance criteria

- The result records `retrieval_strategy` (`dense`, `bm25` or `hybrid`), the fusion parameters for hybrid, and the lexical index identity (path label relative to the repository or configured root, tokenizer name and version, source-chunk digest) whenever the lexical index is used.
- For hybrid and BM25 runs, each per-case row records the rank of each relevant document in each leg used (or absence).
- The unanswerable report labels its score kind (`dense_cosine`, `bm25`, `rrf`) and stays informational.
- Latency p50/p95 is reported overall and per leg for hybrid, after the warm-up rule of D037.
- When a query's lexical terms are cut at the design's term cap, the result records it per case and as a count; a test covers it.
- All new fields are IDs, scores, ranks and counts only; no query or chunk text, absolute paths or secrets. Results are never overwritten and nothing is written on error (D043).
- Existing 1.0 and 2.0 result files, including the R2 v2 dense baseline and the closed v1 reference, stay readable by `eval-compare`. If the additions require a new `schema_version`, the reader supports 1.0, 2.0 and the new version.

## R10 — `eval-compare` across strategies

Comparisons between strategies are allowed; comparisons between different systems are not.

### Acceptance criteria

- A difference in `retrieval_strategy` (and the lexical index identity that comes with it) is allowed and printed as an identity line, for example `identity differs, retrieval_strategy: dense -> hybrid`.
- In addition to the existing refusals (suite ID or version, case set, `top_k`, document count, fake embedder; D044), a comparison is refused (exit 2, `not comparable:` message naming old -> new) when the collection, `index_version` or embedder identity (model ID and revision) differ.
- A collection difference is refused with a message that names both collections (for example `collection changed w2a-a-idx-v1 -> w2a-b-idx-v1`).
- Missing collection rule: when either file does not record a collection (absent or `null`), the two runs are compared by `index_version` only, and an informational line says so, naming the file without a collection. `index_version` and embedder identity are still required to match.
- Lexical identity: when both runs used the lexical leg (`bm25` or `hybrid`), their lexical index identity (tokenizer name and version, source-chunk digest) must also match, or the comparison is refused naming old -> new. A run without a lexical leg (`dense`, or a 1.0/2.0 file) has no lexical identity, and that alone is never a refusal; it is shown as an identity line.
- Device, `git_commit` and latency differences stay informational identity or latency lines (D038).
- The gate rule (more than 1 fewer hit case, or an MRR drop above `1/n`) is unchanged.
- The existing comparison `BASE=experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (1.0) `CANDIDATE=experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` (2.0) still passes, and a test covers it.
- Tests cover a dense vs hybrid comparison that passes, the missing-collection rule, a lexical-identity refusal, a dense vs lexical run that is not refused, and each new refusal.

## R11 — Security gate coverage for BM25 and hybrid (`make eval-security`)

The authorization hard gate exercises every strategy.

### Acceptance criteria

- `make eval-security` builds, next to its throwaway `w2a-sectest-<8 hex>` collection, a throwaway lexical index in a temporary location, deleted in the same `finally` as the collection. It is built by the production lexical builder from the eligible seed corpus plus forbidden rows; the quality lexical index is never used.
- Forbidden rows cover the same variants as D045 (`staff_scope`, `other_tenant`, `owned`, `missing_owner`, the staff-only canary) and contain each query's own tokens, so BM25 ranks a forbidden row first without the filter.
- An unfiltered sanity check per leg must find a forbidden point or row first; otherwise it is a harness error (exit 2), never a pass.
- The gate runs the active retrieval-side security cases and every active golden query through the production `dense`, `bm25` and `hybrid` retrievers at `top_k` 50 with `resolve_access(guest_access(settings))`. Any forbidden document returned, or a `RetrievalAuthorizationError`, is a violation (exit 1) that names the strategy.
- The security result records the strategies covered and, for each violation, the strategy. It still holds IDs, counts and verdicts only.
- The gate still runs inside `make verify` through its unit tests, without Docker or a model.

## R12 — Docker isolation test for the hybrid path

The hybrid path is proven against the real Qdrant server, not only local mode.

### Acceptance criteria

- A `make test-integration` test builds a throwaway collection with a unique base on Docker Qdrant and a throwaway lexical index, with forbidden points and rows nearest by construction in each leg, and shows that `dense`, `bm25` and `hybrid` retrieval never return them.
- It deletes its collections and files afterwards, including on failure, and never touches `w2a-realcheck-*` collections. It skips when Qdrant is not reachable, like the existing integration tests.

## R13 — Strategy comparison and default-strategy decision (user-owned gate)

The user records real BM25 and hybrid results on v2, and the default strategy is decided from that evidence.

### Acceptance criteria

- With all code tasks approved and committed, the user builds the lexical index for `w2a-realcheck-idx-v1` (`make index-lexical`, local file only, no Qdrant writes) and runs `make eval-retrieval --strategy bm25` and `--strategy hybrid` on v2 against the read-only `w2a-realcheck-idx-v1`, then `make eval-compare BASE=<R2 dense result> CANDIDATE=<hybrid result>` (and the same for BM25, informational).
- First step of the gate: a real dense `make eval-retrieval` on v2 (result 2.1) passes `make eval-compare` against the R2 dense baseline with no flipped cases; otherwise the gate stops and the dense change is fixed first.
- The BM25 and hybrid result files are checked like R2 (suite v2, not fake, clean commit, same collection, `index_version`, embedder, `top_k` and document count) and committed.
- The default strategy becomes `hybrid` in `config/retrieval.yaml` only if all hold: the hybrid run passes the `eval-compare` gate against the R2 dense result; it improves hits or MRR; and no `ml` or `mixed` case goes from hit to miss. Otherwise the default stays `dense`.
- A decision in `DECISIONS.md` records the outcome with the numbers: overall, `en`, `mixed` and `ml` slices for dense, BM25 and hybrid, every flipped case, the fate of `g004`, `g026` and `g061`, and latency per leg.

## R14 — Unchanged behavior, protected paths and spec-wide verification

### Acceptance criteria

- Dense retrieval, the dense index binding, ingestion and the payload are unchanged in behavior; no new `index_version` and no change to `config/ingestion.yaml`. The legacy `make retrieval-baseline` stays byte-for-byte as pinned by its characterization test (D046).
- `evaluation/` changes only through R1. `config/` changes only by adding `config/retrieval.yaml` (R8) and, if R13's conditions hold, its default strategy. `knowledge/` is not changed. `.gitignore` gains the lexical index location.
- `make verify` passes without the `bge-m3` extra, Docker or a model download (lexical tests use temporary SQLite files or in-memory databases and the fake embedder).
- `make test-integration` passes, including R12.
- `make eval-security` passes on v2 for all three strategies.
- Agents never write to, delete or re-ingest a `w2a-realcheck-*` collection and never run the real model; tests never write under `experiments/results/` (throwaway output goes to `experiments/results/tmp/` or a temporary directory).
- No secrets in code, config, fixtures, results or docs.

## R15 — Documentation and decisions

### Acceptance criteria

- New decisions (from D049) record: the v2 suite promotion and the closed v1 reference; SQLite FTS5 as the lexical store (vs Qdrant sparse vectors), its binding and location; the `lexical-v1` tokenizer rule (including ZWJ/ZWNJ); RRF parameters, fail-closed fusion and the empty-leg rule; the `eval-compare` identity rules; the R13 default-strategy outcome.
- `ARCHITECTURE.md` (retrieval and target query flow: dense and BM25 legs implemented, authorization inside each leg before RRF), `COMMANDS.md` (`make index-lexical`, `--strategy`, new refusals, security coverage), `TECH_STACK.md` (FTS5 use, no new dependency) and `CURRENT_STATE.md` describe the code as built.
- `CURRENT_STATE.md` records the R2 and R13 results, the continuity check, the `seed-v1` release still naming suite v1 (known issue for Phase 2), and the corpus-wide BM25 statistics note: today only eligible public chunks are indexed, so IDF reveals nothing; a later roles spec must consider per-scope statistics.

## Out of scope

- Graceful degradation: dense failure → BM25, Qdrant failure → SQLite FTS5, reranker fallback (roadmap 13). The lexical index only stays reusable for it.
- Qdrant sparse vectors, BGE-M3 learned sparse weights, SPLADE or any second lexical implementation.
- Stemming, stopwords, transliteration, query transformation, language detection or language filtering (roadmap 8).
- Reranking, deduplication and context building (roadmap 9); generation (roadmap 10).
- Chunking changes, a new dense `index_version`, re-ingestion, `relevant_section_ids` (roadmap 7).
- The Phase 2 "compare shared cases" mode of `eval-compare`, new Knowledge Releases, any approval workflow, edits to `knowledge/`.
- Changes to any evaluation case beyond R1; activation of any other candidate.
- An HTTP retrieval route, Langfuse, CI workflows, non-guest roles, device pinning (D038).
- The open Spec 004 nits and Spec 006 retrospective F1, unless a task touches the same code.

## Definition of Done

- R1–R15 satisfied and traced to approved tasks.
- R2 and R13 user-owned runs recorded, checked and committed; the default strategy set by R13's rule and recorded in a decision.
- `make verify` (no extra, Docker or model), `make test-integration` and `make eval-security` pass.
- Protected-path check: under `evaluation/` only the R1 changes; under `config/` only `retrieval.yaml`; nothing under `knowledge/`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | `make validate-evaluation`; `test_suite_v2.py`; v1 dataset diff empty; `make eval-security` |
| R2 | T2 | user run; scratch field and continuity checks; self-compare; `CURRENT_STATE.md` |
| R3 | T3 | tokenizer tests in `packages/rag/tests/lexical/` (incl. legacy chillu pin) |
| R4 | T3 | build tests; `make index-lexical` (throwaway base) |
| R5 | T3 | open/bind refusal tests (in-memory Qdrant) |
| R6 | T4 | `test_bm25.py` (authorization, injection, truncation); `test_access.py` |
| R7 | T5 | `test_fusion.py`, `test_hybrid.py` (hand-computed RRF, empty leg, fail closed) |
| R8 | T5, T6 | `test_strategy.py`; CLI tests; manual `make retrieve --strategy` (throwaway) |
| R9 | T6 | dense equivalence test; 2.1 key and truncation tests; reader tests |
| R10 | T7 | `test_compare.py` additions; committed 1.0 vs 2.0 compare exit 0 |
| R11 | T8 | `test_security_eval.py` additions; `make eval-security` |
| R12 | T8 | `test_security_integration.py` via `make test-integration` |
| R13 | T9, T10 | user runs; dense 2.1 compare with no flips; rule check; decision in T10 |
| R14 | T1, T3, T4, T5, T6, T8, T9, T10 | `make verify`; per-task protected-path check; final `git diff --name-status main...HEAD` |
| R15 | T10 | doc review against code; `DECISIONS.md` D049+ |
| Definition of Done | T10 | `make verify`, `make test-integration`, `make eval-security`; protected-path output |

## Change log

- 2026-10-25 — Decision Brief (user): `public-eval-v2` is a new manifest with its own datasets. "v1 stays byte for byte" means the v1 dataset files; the v1 manifest changes only `status` to `replaced`. The v1 2.0 result `experiments/results/retrieval-evaluation-idx-v1-20261024T193140Z.json` becomes a closed reference, because `eval-retrieval` refuses a non-active suite.
- 2026-10-25 — Decision Brief (user): fixed promotion mapping `cand006_ml_001`…`cand006_ml_006` → `g064`…`g069` in order; `ml_002` (`g065`) and `ml_003` (`g066`) use their reworded queries; each promoted candidate row's `review` gains `promoted_as: {suite_id, case_id}`; rows stay `status: suggested`.
- 2026-10-25 — R10 (user, at requirements approval, with the transcription check, R10 and the R1 test updates approved): a file without a collection is compared by `index_version` only (informational line); lexical identity must match when both runs used the lexical leg, and its absence on a dense run is not a refusal; a collection refusal names both collections; the committed 1.0-vs-2.0 comparison must still pass, with a test.
- 2026-10-25 — Design approval (user): the legacy chillu sequence stays distinct from the atomic chillu letter in `lexical-v1` (test pinned; known issue for roadmap 8); the lexical settings hold a copy of the bound dense identity so the file is self-describing, and BM25 without Qdrant is a note for the fallback spec; result formats 2.1 and security 1.1; a query cut at 64 lexical terms is recorded per case and as a count (R9 bullet added, with a test); existing dense tests may only gain the new default fields, and a real dense 2.1 run must pass `eval-compare` against the R2 baseline with no flips (first step of the R13 gate).
- 2026-10-25 — T10 (user decision on T1 review finding F1): T10 gains one test-only checkbox: remove the unused `LEGACY_SUITE` constant from `packages/rag/tests/conftest.py`, or use it in `packages/rag/tests/retrieval/test_baseline.py` instead of the literal v1 suite path. No requirement changes; no task re-opened.
- 2026-10-25 — Design As-built notes (user decision on the T3 round 1 review): `make index-lexical` has `--embedder {bge_m3,fake}`, `--output` and `--config`; `LexicalIndex.bind_to` compares `hash_contract`; relative `W2A_LEXICAL_INDEX_DIR`/`--output` resolve against `--repo-root`. No requirement changes; no task re-opened.
- 2026-10-26 — T10 (user decision on T3 round 3 review finding F1): T10 gains one code/test checkbox: `check_target_allowed` in `lexical/cli.py` allows only targets that `git check-ignore` reports as ignored, replacing the tracked-file check, keeping the protected-folder guard; a test refuses an existing un-ignored folder such as `.local/other/`. No requirement changes; no task re-opened.
- 2026-10-27 — T6, T8, T10 and design As-built notes (user decision on the T4 round 1 review): T8 gains the F1 checkbox (clause-dropping BM25 test parametrized over the four forbidden row types); T6 gains the F2 checkbox (one latency span per leg ending after `check_hit`, `DenseRetriever` updated to match; rule recorded in the design); T10 gains the F3 checkbox (lexical test helpers moved to a shared fixture module or `conftest.py`, `sys.path` insert and pyright ignore removed from `test_bm25.py`); the accepted T4 decisions (`LexicalIdentity` in `retrieval/models.py`, BM25 score `-bm25() + 0.0`, non-object `payload_json` fails closed) recorded as As-built notes. No requirement changes; no task re-opened.
- 2026-10-28 — Design As-built notes (user decision on the T5 round 2 review): `FusionConfig` lives in `retrieval/fusion.py` (avoids an import cycle with `hybrid.py`); `HybridRetriever` takes `Retriever` Protocol legs, with result identity from the dense leg and a duplicate point in one leg counting only its first rank. No requirement changes; no task re-opened.
- 2026-10-28 — Design As-built notes, T7, T9 and T10 (user decision on the T6 round 2 review): design records `RetrievalResult.leg_document_ranks` (set only by `HybridRetriever`; result 2.1 `leg_ranks` derived from it; dense output unchanged); T10 gains the F1 test-only checkbox (`# noqa: E402` removed and the exact hybrid dense rank pinned in `test_strategy_eval.py`); T7 gains a note that `info["retrieval_strategy"]`, `info["lexical"]` and the 2.1 `source_authority` compare are already done in T6; T9 gains three F2 analysis boxes (dense and BM25 `leg_ranks` with common-term matches for every case hybrid ranks lower than dense, BM25 candidates per query by language, and a "stopword list or minimum BM25 score/IDF floor" retrospective note if the default decision fails because of it; no fix in Spec 007). No requirement changes; no task re-opened.
