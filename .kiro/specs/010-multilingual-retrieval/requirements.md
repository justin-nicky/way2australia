# 010 — Multilingual Retrieval Requirements

Status: approved (2026-11-04)

## Goal

Make retrieval language-aware without mixing language and authorization (roadmap item 8, constitution C4). Concretely:

- a request may name the target CCL language (`lote`); when it does, only knowledge that applies to that language (`lote_languages` is `["*"]` or contains the code) can be retrieved, on every retrieval path, as a filter applied before ranking and re-checked on every hit, fail-closed but separate from the authorization check;
- the lexical tokenizer gains a version `lexical-v2` that maps legacy chillu sequences to the atomic chillu letters, from a Unicode-sourced table with no Malayalam-specific code path;
- evaluation results report a script-mix slice (which scripts a query's letters use), so mixed-query behaviour is visible per script combination;
- a new suite `public-eval-v3` grows the `ml` and `mixed` slices to at least 12 goldens each plus 3 unanswerable `ml` cases, drafted by an agent and corrected and approved by the user (fluent speaker and owner);
- the security gate proves applicability on all five gated paths;
- user-owned real runs on v3 compare `lexical-v1` and `lexical-v2` (hybrid and BM25-only), and a no-regression rule, fixed here before any run, decides whether `lexical-v2` becomes the default.

Repository facts that shape the scope (checked 2026-11-04):

- All 13 eligible documents have `content_language: en`. The only Malayalam script in the corpus is 14 words of a sample dialogue in `business_008_public_samples`. Malayalam stemming, n-grams or normalization therefore cannot move the `ml`/`mixed` numbers measurably; `lexical-v2` is a correctness fix, not an expected improvement.
- `g067`–`g069` (BM25-only misses) are Malayalam-script spellings of English words (for example "മോക്ക് ടെസ്റ്റുകളും" for "mock tests"); no tokenizer change can match them against English text. Their fix is query translation or transliteration (out of scope, carry-over).
- On the Spec 009 reference `experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json` (hybrid, `idx-v2`), `ml` is HitRate@5 1.0 / MRR 1.0 (n=6) and `mixed` HitRate@5 1.0 / MRR 0.80 (n=9). The `mixed` MRR loss is `g056` and `g057` (dense rank 1, fused rank 2) and `g061` (rank 5). Per-script fusion weighting would be tuned on 2 of 9 cases; that ordering problem goes to the reranker (roadmap item 9).
- 11 documents are `lote_languages: ["*"]` and 2 are `["ml"]` (`business_008_public_samples`, `language_ml_001_naati_policy`); `ml` is the only active code in `config/language_registry.json`. A `lote: ml` filter therefore excludes nothing on today's corpus; applicability is proven on synthetic fixtures (for example a `["ta"]` document) in tests and the security gate.
- Qdrant already has a keyword payload index on `lote_languages` (`ingestion/store.py`). The lexical `chunks` table has no `lote_languages` column; the value is only inside `payload_json`.

## Dependencies

- Spec 009 (verified, merged `5a6deb7`): default index `idx-v2` (recursive 128 + title, D071), lexical settings 1.1 with chunker identity, per-document `verify_fresh`, result 2.3 with distinct-document metrics, `eval-compare --cross-index`, security result 1.3 over three chunkers (D064–D071). Reference result above.
- Spec 008: `open_retrieval`, `FallbackRetriever` (open-time and per-query fallback), standalone `bm25` without Qdrant or the extra, five gated paths, result 2.2, security 1.2 (D056–D062).
- Spec 007: `lexical-v1` (D051), SQLite FTS5 store and `build_sql_access_clause` (D050), `HybridRetriever`/RRF (D052), `eval-compare` identity rules (D054), suite `public-eval-v2` (D049).
- Spec 006: governed suite loader, `make validate-evaluation`, candidate rows and the C6 promotion pattern (Spec 006 T7, Spec 007 T1), slices and `small_sample` (threshold 10).
- Spec 005: `AccessContext`, `ResolvedAccess`, `build_access_filter`, `check_hit` (D035, D040).
- Spec 002: `KnowledgeDocument.lote_languages` validation (`["*"]` for `global`, explicit codes for `language_specific`), `ALL_LOTE_LANGUAGES`.
- `config/language_registry.json`: the active product languages (`product_support.*.internal_code` with `status: active`).
- Retrospective notes: `.kiro/specs/009-chunking-experiments/review.md` "Notes for the next spec" (Malayalam stemming / chillu D051; hub-free verify discipline; per-scope lexical files D050 only if access changes, which it does not here).
- The real runs (R10) need `make setup-bge-m3`, Docker Qdrant and the user's `w2a-realcheck-idx-v2` collection. They are run by the user. No new runtime dependency.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-11-04, with these choices:

- **Name.** `010-multilingual-retrieval`.
- **Target language (Q1: a).** An optional `lote` value per request, checked against the active codes in `config/language_registry.json`; an unknown or inactive code exits 2. No value means no applicability filter, recorded as `lote: null`. The evaluation runs of this spec use `lote: ml`.
- **Lexical (Q2: a).** `lexical-v2` adds legacy-chillu → atomic-chillu normalization only, from Unicode data, with no Malayalam special-casing. No stemming and no n-gram arm (the corpus is English; an expected null result is not worth a cycle).
- **Mixed queries (Q3: b).** A script-mix slice (Latin only / Malayalam only / both) in the evaluation result. No per-script BM25 weighting; `g056`/`g057` are recorded as roadmap item 9 (reranking) inputs.
- **Cases (Q4).** The agent drafts candidates; the user corrects and approves them (as in Spec 006 T7). Target: at least 12 `ml` and 12 `mixed` goldens in total, plus 3 unanswerable `ml` cases.
- **Fail-closed applicability (Q5).** A separate `LanguageApplicabilityError`, fail-closed like the access check, not counted as an authorization failure.
- **Shape.** Six tasks: T1 suite `public-eval-v3` (user-owned approval); T2 `lote` applicability on all paths; T3 `lexical-v2`, lexical rebuild, `eval-compare` tokenizer-change flag and script-mix slice; T4 security gate with applicability, result 1.4; T5 user-owned real runs on v3; T6 docs, decisions, hand-off.
- **At requirements approval (2026-11-04).** An explicit `lote_languages` column in the lexical `chunks` table, with a lexical schema version separate from the tokenizer version, and a refusal for an old file only when a `lote` is given (R3); the `lote` refusal in `eval-compare` accepted (R8); script-mix rules for characters without a script and generic Unicode detection (R7); the R10 continuity check is a committed, tested command, not a scratch script.
- **Promotion rule for `lexical-v2`** (R10), no-regression, fixed before T5: the `eval-compare` gate passes for both hybrid and BM25-only; no hit lost in any language; overall MRR not lower. A tie promotes it (correctness fix).

## R1 — Evaluation Suite `public-eval-v3`

A new active suite version grows the `ml` and `mixed` slices with human-approved cases, as the only change under `evaluation/` in this spec (C6, D042).

### Acceptance criteria

- `evaluation/candidates/010-candidates.jsonl` holds agent-drafted candidate rows (`status: suggested`, the Spec 006 candidate row shape) for new `ml` goldens, new `mixed` goldens and 3 unanswerable `ml` cases. Each golden candidate names only eligible public documents in `relevant_document_ids`. Candidates are never loaded as cases.
- The user corrects and approves the candidates; only approved candidates are promoted, with the user's corrections. The approval and every correction are recorded verbatim in `task-reviews.md`.
- `evaluation/suites/public-eval-v3.json` exists with `evaluation_suite_id: public-eval-v3`, `version: 3`, `status: active`, its own three datasets under `evaluation/datasets/v3/`, a correct `case_count`, and `replaces` naming `public-eval-v2` v2.
- After promotion, v3 has at least 12 `query_language: ml` and at least 12 `query_language: mixed` goldens, and at least 3 unanswerable cases with `query_language: ml`, so neither golden slice is `small_sample`.
- Every v2 row is carried into v3 and differs from its v2 row only in `evaluation_suite_id`; a test compares them field by field. New cases take the next free IDs (goldens from `g070`, unanswerable from the next free `u` number), `case_version: 1`, `status: active`.
- A candidate row's `proposed_case` may have the `golden_answerable` shape or the `unanswerable_refusal` shape (`candidate_row` in `evaluation/schemas/evaluation_case_types.schema.json` accepts exactly one of the two). An unanswerable candidate carries `query`, `answerable: false`, `expected_behavior` and `query_language`. The 006 candidate rows remain valid.
- Each promoted candidate row gains `review.promoted_as: {"suite_id": "public-eval-v3", "case_id": "<id>"}` and keeps `status: suggested`; `make validate-evaluation` checks that each promoted case equals its candidate's `proposed_case` (Spec 007 rule), after the recorded corrections.
- The v2 dataset files are byte-for-byte unchanged (hash test); the v2 manifest differs only in `status: replaced`. The v2 result files become closed references.
- `make eval-retrieval` and `make eval-security` default to `public-eval-v3`; a run on v2 is refused (exit 2, suite `replaced`). The legacy `make retrieval-baseline` keeps its v1 default (D046).
- `make validate-evaluation` passes on every suite. Tests that read the real suite use consistency checks, not hard-coded live counts.

## R2 — Target language (`lote`) on a retrieval request

The target CCL language is an explicit, validated request value that lives apart from the access context.

### Acceptance criteria

- A retrieval request carries an optional `lote` (a CCL language code) next to, not inside, `AccessContext` / `ResolvedAccess`. Nothing in the access policy, tenant or role depends on it, and nothing in `lote` can widen access.
- A given `lote` is accepted only if it is an active code in `config/language_registry.json` (`product_support.*.internal_code` with `status: active`). An unknown or inactive code, an empty value and the `*` marker are refused before any Qdrant or lexical query (exit 2 in the CLIs, message names the value and the active codes). No language code is written as a literal in generic retrieval code; the accepted set comes from the registry.
- No `lote` means no applicability filter: every eligible document is retrievable, exactly as before this spec.
- `make retrieve` and `make eval-retrieval` accept `--lote <code>`. `make retrieve` prints the `lote` it used (or `none`).
- Evaluation results record `lote` (the code, or `null`); result files written before this spec read as `lote: null`.

## R3 — Applicability filter on every retrieval path

When a `lote` is given, only applicable chunks are candidates, on every path, before ranking.

### Acceptance criteria

- A chunk is applicable to `lote` X when its `lote_languages` is `["*"]` or contains X. Applicability is evaluated on the chunk payload's `lote_languages` (copied from the document).
- There is one applicability builder per store, separate from the access builders: a Qdrant condition combined with `build_access_filter`'s filter in the same query, and an SQL condition combined with `build_sql_access_clause` in the same statement. Neither access builder changes its output.
- The filter is applied inside the query (Qdrant filter, SQL `WHERE`), never after retrieval; with a `lote`, `top_k` and candidate depth count only applicable chunks.
- The same `lote` reaches `dense`, standalone `bm25`, `hybrid` (both legs), and both fallback paths of `FallbackRetriever` (open-time and per-query); a test per path shows a non-applicable chunk that would otherwise rank first is not returned, and that with no `lote` it is.
- BM25 corpus statistics are unchanged by the filter (the lexical file is not split by language).
- The lexical `chunks` table gains an explicit `lote_languages` column, written by the builder from the chunk payload; the SQL applicability condition reads only that column (never `json_extract` on `payload_json`), as explicit as the access clause.
- The column is a lexical schema change with its own lexical settings (schema) version, kept separate from the tokenizer name and version: a `lexical-v1` file and a `lexical-v2` file can both have the new schema. A file built before this spec (no column) still opens and serves queries with no `lote` exactly as before; opened with a `lote`, it is refused (exit 2, message names `make index-lexical`), never silently unfiltered.
- With `lote: ml` on today's corpus, results equal the results with no `lote` (every document is `["*"]` or `["ml"]`); a test pins this on the seed corpus with the fake embedder.

## R4 — Fail-closed applicability re-check

A returned hit that does not apply to the requested `lote` stops the query, and is reported apart from authorization.

### Acceptance criteria

- Every hit returned with a `lote` is re-checked after the access re-check (`check_hit`); a non-applicable hit, or a hit whose `lote_languages` is missing or malformed, raises `LanguageApplicabilityError` naming `document_id` and the field only.
- `LanguageApplicabilityError` is not a `RetrievalAuthorizationError` and not a `RetrievalUnavailableError`: it never triggers fallback, and it is never counted as an authorization violation.
- `check_hit` (authorization) runs first and is unchanged; an access violation is still a `RetrievalAuthorizationError` whatever the `lote`.
- Tests: a store that ignores the applicability filter (filter dropped, by injection) makes the re-check raise on each path; with no `lote` no re-check runs.

## R5 — Tokenizer `lexical-v2`

Legacy chillu spellings and atomic chillu letters produce the same lexical tokens.

### Acceptance criteria

- `lexical-v2` is `lexical-v1` plus one step before ZWJ/ZWNJ are dropped: each legacy chillu sequence (consonant, virama, ZWJ) is replaced by its atomic chillu letter, using a mapping table that cites its Unicode source (The Unicode Standard, Malayalam chillu section) and lists code points only.
- The table is data applied by a generic step (sequence → replacement); the tokenizer has no script- or language-named branch. Adding another script's equivalence table would not change the code path.
- For every pair in the table, the legacy spelling and the atomic letter tokenize identically, inside a word and at word end; a test pins each pair. Text without a listed sequence tokenizes exactly as in `lexical-v1` (property test or corpus-wide comparison over the seed corpus and every suite query).
- `lexical-v1` stays available unchanged (its tests and the D051 legacy-chillu pin still pass), so existing lexical files keep working.
- The query side always tokenizes with the tokenizer recorded in the lexical file it searches; a file built with one version is never queried with the other.
- No stemming, stopwords, n-grams or transliteration.

## R6 — Lexical build and selection by tokenizer

Either tokenizer can build a lexical file, and the default is a reviewed config value.

### Acceptance criteria

- `make index-lexical` can build with `lexical-v1` or `lexical-v2`; the default tokenizer is a reviewed config value that only R10 may change, and an explicit option overrides it. The file's settings record tokenizer name and version (as today).
- Two files for the same collection with different tokenizers can exist side by side (for example via the existing `--output`), so R10 can run both arms against one Qdrant collection.
- Freshness (`verify_fresh`), identity checks and the standalone open accept either tokenizer; nothing else about the binding changes.
- Building with `lexical-v2` writes no Qdrant data, needs no PyTorch, and for the default `idx-v2` needs only the tokenizer files it needs today (D069).

## R7 — Result 2.4: `lote` and script-mix slice

The evaluation result shows the target language and per-script-combination metrics.

### Acceptance criteria

- `make eval-retrieval` writes `retrieval_evaluation` 2.4: the 2.3 keys plus `lote` (R2) and a `by_script_mix` slice beside `by_query_language`, with the same metric fields and `small_sample` flag.
- A query's script mix is the set of Unicode scripts of its letter characters; the slice keys are the sorted lower-case script names joined with `+` (for example `latin`, `malayalam`, `latin+malayalam`). A query with no lettered character has key `none`.
- Characters with no script of their own add no script: digits, punctuation, symbols, whitespace, ZWJ/ZWNJ and other format characters, and combining marks (they belong to the letter they attach to). Tests pin each of these, including a virama and vowel signs inside a Malayalam word, `₹1,300` and `-ൽ` (from `g057`).
- Script detection uses generic Unicode data only: character names from `unicodedata`, or a committed range table generated from the Unicode `Scripts.txt` with its source and Unicode version recorded. There is no Malayalam-specific table or branch. Any new dependency for this needs a recorded reason in the design and in `TECH_STACK.md`.
- Each case row carries its `script_mix`. A test pins the key for representative `en`, `ml` and `mixed` suite queries.
- Romanized Malayalam (Malayalam written in Latin letters, for example `g062` "Phone-il practice cheyyam") counts as `latin`; the docs (`COMMANDS.md` result description and the R12 decision) state this, because the `latin` slice then mixes English and romanized Malayalam queries.
- 2.0–2.3 files stay readable by `eval-compare`.

## R8 — `eval-compare` with a tokenizer change and with `lote`

Two runs that differ only in lexical tokenizer can be compared on purpose; runs with different `lote` cannot.

### Acceptance criteria

- A new explicit option (for example `COMPARE_ARGS=--cross-tokenizer`) allows the lexical tokenizer name and version to differ; every other identity refusal still applies (collection, `index_version`, chunker, embedder, suite, case set, `top_k`, document count, fake embedder, strategy-mix rules), and the lexical source-chunk digest and chunk count must still match. Without the option a tokenizer difference is still refused (exit 2), with advice naming the option.
- The identity output prints the tokenizer change (for example `lexical tokenizer: lexical-v1 v1 -> lexical-v2 v2`).
- A `lote` difference is refused (exit 2, `lote changed <old> -> <new>`); a file without `lote` reads as `null`.
- The D044 gate rule is unchanged. The comparisons the earlier specs pinned in tests still pass.
- Tests cover: tokenizer change refused without the option; accepted with it; another identity difference still refused with it; `lote` refusal; 2.3 vs 2.4 reading.

## R9 — Security gate with applicability (`make eval-security`)

The hard gate proves that applicability never widens access and that it excludes non-applicable knowledge on every path.

### Acceptance criteria

- The throwaway security corpus gains public, eligible, non-applicable rows (for example `lote_languages: ["ta"]`) that carry each query's own tokens and are nearest by construction in both legs; an unfiltered sanity check must find them first (otherwise harness error, exit 2).
- On all five gated paths (`dense`, standalone `bm25`, `hybrid`, `hybrid_fallback_open`, `hybrid_fallback_query`) and over the three chunkers (D070), with `lote` set to an active code:
  - no access-forbidden row is returned (as today), including access-forbidden rows whose `lote_languages` is `["*"]` or contains the requested code;
  - no non-applicable row is returned; a returned one, or a `LanguageApplicabilityError`, is an applicability violation (exit 1) reported apart from authorization violations.
- With no `lote`, the non-applicable public rows may be returned (they are eligible); access-forbidden rows never are. The gate checks both modes.
- `make eval-security` writes `security_evaluation` 1.4: the 1.3 keys plus the `lote` values covered and separate authorization and applicability violation counts; IDs, counts and verdicts only.
- The synthetic non-applicable rows exist only in the throwaway corpus (never under `knowledge/`). The gate keeps running inside `make verify` through its unit tests, without Docker or a model; the Docker isolation test covers the applicability filter on the real Qdrant server.

## R10 — Real runs on v3 and the `lexical-v2` decision (user-owned gate)

The user records real results on v3, and the pre-registered rule decides the default lexical tokenizer.

### Acceptance criteria

- With every code task approved and committed, the user builds two lexical files for `w2a-realcheck-idx-v2` (`lexical-v1` and `lexical-v2`; local files only, no Qdrant writes) and runs `make eval-retrieval --lote ml` on v3 for four arms: hybrid and BM25-only, each with `lexical-v1` and `lexical-v2`. Then `make eval-compare COMPARE_ARGS=--cross-tokenizer` with `lexical-v1` as base, for hybrid and for BM25-only.
- Continuity check first: on the 69 goldens carried from v2, the hybrid `lexical-v1` v3 run with `lote: ml` has the same hit, reciprocal rank and ranked document IDs per case as the Spec 009 reference `…idx-v2-20261103T104934Z.json`. A difference stops the gate until explained. Because `eval-compare` refuses the differing case set and `lote`, the check is a committed, tested command (a script or `make` target, with unit tests on fixture result files, delivered by a code task before T5); its full output is recorded in T5, not produced by an ad-hoc scratch script.
- The result files are checked like earlier user runs (suite v3, not fake, clean commit, same collection, `index_version`, chunker, embedder, `top_k`, document count, `lote: ml`) and committed.
- **Promotion rule (fixed here, before any run).** `lexical-v2` becomes the default tokenizer only if all hold: the `eval-compare` gate passes for both hybrid and BM25-only; no case goes from hit to miss in any language, in either strategy; overall MRR is not lower in either strategy. A tie promotes it. Otherwise the default stays `lexical-v1`.
- On promotion, the default tokenizer config value changes and the operator rebuilds with `make index-lexical`; no Qdrant change and no new `index_version`.
- A decision in `DECISIONS.md` records the outcome with numbers: overall and `en`/`ml`/`mixed` slices and the script-mix slice for all four arms, every flipped case, and the `g056`/`g057`/`g061`/`g067`–`g069` ranks.

## R11 — Unchanged behaviour, protected paths and spec-wide verification

### Acceptance criteria

- With no `lote`, every retrieval path returns exactly what it returned before this spec (existing tests unchanged, apart from new default fields). Dense index binding, ingestion, chunkers, the payload (17 fields), fusion, `FallbackRetriever`'s fallback eligibility, `INGESTION_NAMESPACE` and the legacy `make retrieval-baseline` are unchanged. No new `index_version`; no re-ingestion.
- `evaluation/` changes only through R1. `config/` changes only by the R6 default tokenizer value and, if R10's rule holds, its promotion. `knowledge/` is not changed.
- `make verify` passes without the `bge-m3` extra, Docker or a model download, and also with an empty `HF_HOME` and `HF_HUB_OFFLINE=1` (hub-free verify, Spec 009).
- `make test-integration` passes (Docker Qdrant), including the applicability isolation test.
- `make eval-security` passes on v3 for all five paths.
- Agents never write to, delete or re-ingest a `w2a-realcheck-*` collection and never run the real model; tests never write under `experiments/results/` outside `tmp/`.
- No secrets in code, config, fixtures, results or docs.

## R12 — Documentation and decisions

### Acceptance criteria

- New decisions (from D072) record: suite v3 and the closed v2 references; `lote` as a request value apart from access, its registry validation and the `null` default; the applicability filter (builders, in-query placement, every path) and `LanguageApplicabilityError`; `lexical-v2` and its Unicode table (amending D051); default-tokenizer selection; result 2.4 with the script-mix slice; the `eval-compare` tokenizer option and `lote` refusal; security result 1.4; the R10 outcome.
- `ARCHITECTURE.md` (query flow: access and applicability filters inside each leg; the four language concepts), `COMMANDS.md` (`--lote`, tokenizer option for `make index-lexical`, `--cross-tokenizer`, new refusals), `docs/knowledge/SCHEMA_AND_METADATA.md` (`lote_languages` now used at retrieval time) and `CURRENT_STATE.md` describe the code as built.
- Carry-overs recorded in `CURRENT_STATE.md` Known issues and the retrospective notes: query translation or transliteration as the fix for `g067`–`g069` on the BM25 fallback; `g056`/`g057` (fusion demotes dense rank 1) as roadmap item 9 inputs; Malayalam knowledge content; Malayalam stemming still not done; per-script fusion weighting declined.

## Out of scope

- Query translation or transliteration, including Latin-script Malayalam (the fix for `g067`–`g069` on the BM25 fallback; carry-over).
- Malayalam stemming, stopwords, character n-grams or any other lexical change beyond R5.
- Per-script fusion weighting or any change to RRF parameters (roadmap item 9 with reranking).
- Query language detection used for retrieval decisions (the script mix is reporting only).
- Malayalam (or any) knowledge content, and any edit under `knowledge/`.
- Reranking, context building (roadmap 9); generation (roadmap 10); an HTTP route.
- Semantic chunking, FAQ indexing, the chunk size vs title prefix experiment, headed documents and `relevant_section_ids`.
- Per-scope lexical files (D050): access does not change in this spec.
- A new dense `index_version`, re-ingestion, and removal of the stale `knowledge_release_id` / `evaluation_suite_id` yaml keys (they go at the next `index_version`, D071).
- Non-guest roles, other active CCL languages (adding one is a registry and knowledge change), Phase 2 release workflow, device pinning (D038).
- Open Spec 004 nits and the Spec 006 retrospective F1, unless a task touches the same code.

## Definition of Done

- R1–R12 satisfied and traced to approved tasks.
- R1 candidate approval and R10 user-owned runs recorded, checked and committed; the default tokenizer set by R10's rule and recorded in a decision.
- `make verify` (no extra, Docker or model; also hub-free), `make test-integration` and `make eval-security` pass.
- Protected-path check: under `evaluation/` only R1 changes; under `config/` only the default-tokenizer value; nothing under `knowledge/`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `SCHEMA_AND_METADATA.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

Planned mapping (confirmed at the tasks gate):

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | `make validate-evaluation`; v3 suite tests; v2 dataset hash test; user approval in `task-reviews.md` |
| R2 | T2 | request validation and CLI tests; result `lote` field tests |
| R3 | T2 | per-path applicability tests (dense, bm25, hybrid, both fallbacks); seed-corpus `lote: ml` equality test |
| R4 | T2 | injected-store re-check tests; error-class tests |
| R5 | T3 | tokenizer tests (each table pair; v1 equality on corpus and queries; D051 pin) |
| R6 | T3 | `make index-lexical` tokenizer option tests; side-by-side files; freshness/identity tests |
| R7 | T2, T3 | result 2.4 key tests; script-mix tests |
| R8 | T3 | `test_compare.py` additions |
| R9 | T4 | `test_security_eval.py` additions; `make eval-security`; Docker isolation test |
| R10 | T3, T5, T6 | continuity command and its tests (T3); user runs and recorded continuity output (T5); rule check; decision in T6 |
| R11 | T1–T6 | `make verify` (also hub-free); `make test-integration`; `make eval-security`; `git diff --name-status main...HEAD -- evaluation knowledge config` |
| R12 | T6 | doc review against code; `DECISIONS.md` D072+ |
| Definition of Done | T6 | the commands above; protected-path output |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-11-04 — R1, T1 (found in T1 round 1, when the candidates were drafted; user approved "Approve both"): the `candidate_row` schema required a `golden_answerable` `proposed_case`, so the 3 unanswerable `ml` candidates could not validate. `proposed_case` now accepts the `golden_answerable` or the `unanswerable_refusal` shape (`oneOf`). The promotion check for unanswerable cases compares `query`, `expected_behavior` and `query_language`. T1 gains a schema and validator box, and `evaluation/schemas/evaluation_case_types.schema.json` is added to its allowed paths. No task re-opened (T1 is in round 1).
