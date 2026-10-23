# 006 — Evaluation Framework Requirements

Status: approved (2026-10-23)

## Goal

Turn the Spec 005 stand-in baseline into a governed, reproducible evaluation framework that can say "better", "worse" or "unsafe" before later specs change retrieval:
- a governed loader and validator for the versioned Evaluation Suite (`public-eval-v1`) and its case datasets, replacing `retrieval/goldens.py`;
- `make eval-retrieval`: document-level HitRate@5, Recall@5 and MRR over the active golden cases, sliced by query language, category and source authority, with small-corpus caveats, on a real-embedder index only;
- `make eval-security`: the retrieval-side authorization cases and every golden query run against an isolated fixture index; a forbidden document is never returned (hard gate, deterministic, no model, no Docker);
- `make eval-compare`: compares two result files (baseline vs candidate) with an explicit tolerance rule;
- inactive candidate cases (`status: suggested`) that propose fixes for known evaluation-data gaps, for later human approval.

This spec is roadmap item 5 (evaluation framework). Spec 007 (hybrid retrieval) and later specs measure against it. It also closes Spec 005 retrospective F3 (no Docker authorization isolation test).

## Dependencies

- Spec 005: dense retrieval baseline (verified, merged `b33462e`). Provides `DenseIndex`, `DenseRetriever`, `resolve_access`, `build_access_filter`, `check_hit`, `retrieval/metrics.py`, `safe_text`, the `retrieval_baseline` result format (`schema_version` 1.0, D037) and `make retrieval-baseline`.
- Spec 004: ingestion baseline (verified). Provides `Embedder`, `FakeEmbedder`, `BgeM3Embedder`, `IndexSettings`, `QdrantIndexStore`, `PointPayload`, point identity, `make ingest`.
- Spec 002: document model and repository (verified). Provides `LocalDocumentRepository`, the manifest, `EligibilityPolicy`, `GUEST_PUBLIC_POLICY`, and the isolated security repository over `tests/fixtures/security/`.
- Evaluation assets, read only: `evaluation/suites/public-eval-v1.json` (version 1, 85 cases), `evaluation/schemas/evaluation_case.schema.json`, `evaluation/datasets/golden_public.jsonl` (63), `unanswerable_public.jsonl` (12), `security_public.jsonl` (10).
- Comparison point: the committed real BGE-M3 baseline `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (HitRate@5 0.9524, Recall@5 0.9524, MRR 0.8783, N=13, k=5, misses `g004`, `g026`, `g061`).
- Spec 005 retrospective: `.kiro/specs/005-dense-retrieval-baseline/review.md` ("Notes for the next spec").
- A real `make eval-retrieval` run needs `make setup-bge-m3` and a real-embedder index (for example the existing `w2a-realcheck-idx-v1`). That run is user-owned and not a gate.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-10-23: option (a) for Q1–Q10, with four changes (Q1, Q2, Q6, Q9 below). Six follow-up choices were settled at requirements approval (2026-10-23) and are folded in below (legacy fake output unchanged, `source_authority` slice name, MRR tolerance 1/n, no section-ID candidates, default collection allowed, R8 runtime bound).

- **Scope boundary with Spec 005 (Q1):**
  - A governed suite loader in a new `packages/rag/src/way2australia_rag/evaluation/` package replaces `retrieval/goldens.py`. `retrieval/metrics.py` is reused.
  - `make eval-retrieval` is the quality command. It refuses a fake-embedder index outright and has no `--allow-fake`.
  - `make retrieval-baseline` is documented as **legacy**. It keeps `--allow-fake` and its exact behavior and output format (`schema_version` 1.0), including its default output location (where `--allow-fake` writes is unchanged too).
  - Existing 1.0 result files stay readable.
- **Suite governance in Phase 1 (Q2):**
  - Deterministic loader and validator. `make validate-evaluation` runs inside `make verify`.
  - Type-specific required fields come from new, named schema files: `evaluation/schemas/evaluation_suite.schema.json` and `evaluation/schemas/evaluation_case_types.schema.json`.
  - Only `active` cases run. Other statuses are counted and reported. `suggested` cases never run and never count.
  - `evaluation/` is a protected path (D022, C6). Adding those two schema files and the candidates file (Q9) is the only change allowed under `evaluation/`. No existing case, dataset, schema or the suite manifest is edited.
  - No approval workflow (Phase 2).
- **Case types run (Q3):**
  - Answerable goldens: document-level metrics. Section-level metrics are implemented but report zero measurable cases while every `relevant_section_ids` is empty.
  - Unanswerable/refusal cases: reported as not evaluable before generation. Only an informational top-1 score distribution is reported, with no gate and no threshold.
  - Security cases: the retrieval-side authorization cases (`authorization_bypass`, `filter_injection`, `paid_content_exfiltration`, `context_exfiltration`, `privacy_exfiltration`) run against an isolated fixture index. The others (`system_prompt_extraction`, `ungrounded_generation`, `citation_manipulation`, `indirect_prompt_injection`, `denial_of_wallet`) are reported as deferred to the generation and security specs.
- **Slices (Q4):**
  - `query_language`, `category`, and a `source_authority` slice derived from the relevant documents' manifest `source_authority`. It is named `source_authority`, not "domain", to avoid confusion with `knowledge_domain`.
  - Every slice carries `n` and a small-sample flag.
  - Languages enabled in `config/language_registry.json` that have no cases (today pure `ml`) are reported as absent.
- **Result format and comparison (Q5):**
  - New result kind `retrieval_evaluation`, `schema_version` 2.0, a superset of the 1.0 fields.
  - `make eval-compare BASE=... CANDIDATE=...` reads 1.0 and 2.0 files and refuses to compare unlike runs.
- **Regression gates (Q6, changed):**
  - Hard gate: authorization regression. It runs deterministically in `make verify` (fake embedder, in-memory Qdrant), and its Docker variant runs in `make test-integration`.
  - Quality gate (in `eval-compare`, real runs, run manually, not CI): the candidate **fails** only if overall HitRate@5 drops by more than one case (63 cases today), or if overall MRR drops by more than 1/n, where n is the number of compared cases (the most one case can move MRR; 1/63 ≈ 0.0159 today).
  - Every flipped case (hit to miss, or miss to hit) is listed **by `case_id` as a warning, not a failure**, because embedding-device noise can flip borderline cases.
  - Everything else (slices, latency, score distributions) is informational.
- **CI (Q7):** make targets only. GitHub Actions stays in roadmap item 15. The hard gates run inside `make verify` without the model and without Docker.
- **Fake vs real and isolation (Q8):**
  - `eval-retrieval` refuses a fake index.
  - Pipeline and authorization checks use the fake embedder in throwaway collections, or in-memory Qdrant, created and removed by the run.
  - Security fixtures are never in a quality index.
  - Evaluation never writes to a quality or production collection.
  - Results from fake runs go only to a git-ignored path or to an explicit `--output`.
- **Evaluation-data gaps (Q9, changed, definite):**
  - The spec produces `evaluation/candidates/006-candidates.jsonl`. Every row is `status: suggested`, inactive, never referenced by a suite and never loaded as a case.
  - It proposes pure-`ml` golden cases and a resolution proposal (options only) for the `g004`/`u001` conflict. `relevant_section_ids` proposals are not made: every seed document is one headingless chunk with `section_id` `main`, so they are revisited with the chunking spec (roadmap 7).
  - Malayalam candidates are explicitly marked as needing review by a fluent speaker before any approval.
  - Until a human resolves it, `g004` stays an active golden and a counted miss.
- **Retro items (Q10):**
  - Absorbed: Spec 005 F3 (Docker authorization isolation test) and the fake-output location for the new commands.
  - Deferred: the Spec 004 nits (T3 F1, T5 F2, T7 F1/F2/F3/F5, T8 r2 F1, `manifest.py` docstring) and device pinning (D038).

## R1 — Governed Evaluation Suite loader

A single loader in `packages/rag/src/way2australia_rag/evaluation/` shall read a suite manifest and its datasets into typed models. It replaces `retrieval/goldens.py`.

### Acceptance criteria

- The loader reads the suite manifest (`evaluation_suite_id`, `version`, `status`, `introduced_in_release`, `datasets[]` with `type` and `path`) and every listed dataset. Dataset types are `golden_answerable`, `unanswerable_refusal` and `security`.
- A dataset type the loader does not know is refused with a configuration error. It is never skipped silently.
- Every case is typed by its dataset type and keeps `case_id`, `case_version`, `status` and `evaluation_suite_id`.
- Unknown extra case fields are tolerated and never break loading.
- Paths that resolve outside the repository are refused.
- Error messages name the file and line, never absolute paths or case text.
- A case's `access_context` is loaded only to be ignored. No case field can set role, scope or tenant (D033, D034).
- The loader is read-only: it never writes, renames or reorders any file.
- `retrieval/goldens.py` is removed or reduced to a thin re-export, and `make retrieval-baseline` uses the new loader with unchanged behavior (see R12).
- Unit tests cover:
  - a valid suite;
  - an unknown dataset type;
  - a path escaping the repository;
  - a malformed line;
  - an ignored `access_context`;
  - that no file is modified.

## R2 — Evaluation schemas and `make validate-evaluation`

New schema files and a validator shall make suite and case consistency a deterministic check inside `make verify`.

### Acceptance criteria

- Exactly two new schema files are added. No existing schema is edited.
  - `evaluation/schemas/evaluation_suite.schema.json`: the suite manifest shape.
  - `evaluation/schemas/evaluation_case_types.schema.json`: type-specific required fields that build on `evaluation_case.schema.json`.
    - `golden_answerable`: `query`, `answerable: true`, non-empty `relevant_document_ids`, `query_language`, `category`.
    - `unanswerable_refusal`: `query`, `answerable: false`, `expected_behavior`.
    - `security`: `query`, `attack_type`, `expected_behavior`.
- `make validate-evaluation` checks:
  - the suite and every case against these schemas;
  - unique `case_id` within the suite;
  - every case's `evaluation_suite_id` equals the suite's;
  - the suite's `case_count` equals the number of cases;
  - every `relevant_document_id` exists in the document manifest and is eligible under `GUEST_PUBLIC_POLICY`;
  - candidate files (R14) are valid and not referenced by any suite.
- It exits 0 on the current repository, 1 on validation errors (listing each, with file and line) and 2 on configuration errors.
- `make verify` runs it and needs neither the model nor Docker.
- Tests use temporary copies to show each check failing.

## R3 — Case status and case-type handling

Runs shall use only active cases, and report everything they did not run.

### Acceptance criteria

- Only `status: active` cases are run.
- Cases with any other status (`review_required`, `potentially_obsolete`, `deprecated`, `replaced`, `suggested`) are excluded and counted by status in the run summary and the result.
- `suggested` cases never run and never count toward any metric, even when they appear in a suite dataset.
- An active golden without `relevant_document_ids` fails validation (R2). It is never silently excluded from a quality run.
- Security cases whose `attack_type` is not retrieval-side are listed as deferred with their `case_id` and `attack_type`, and the result names the roadmap item that owns them. An unrecognized `attack_type` is listed as deferred with reason `unclassified`, never dropped.
- The retrieval-side attack types are one constant in code. Adding a type is a code change, never a dataset or LLM decision.
- No run edits, deprecates or rewrites a case (C6). A test checks that the dataset files are byte-identical before and after a run.

## R4 — Retrieval evaluation (`make eval-retrieval`)

A quality command shall run the active golden cases through the real dense retriever and compute document-level metrics.

### Acceptance criteria

- `make eval-retrieval` runs every active golden case through `DenseRetriever`, using one server-resolved `ResolvedAccess` from `resolve_access` for all cases, with `check_hit` on every hit (D035, D040).
- It computes, by reusing `retrieval/metrics.py` (documents deduplicated at their best rank, never chunk or point IDs, C13):
  - document-level HitRate@k, Recall@k and MRR, overall and per slice (R5);
  - p50 and p95 retrieval latency after one unmeasured warm-up query;
  - the random expectation `min(1, k/N)`.
- `top_k` defaults to 5, bounded as in Spec 005.
- An index whose recorded `embedder_is_fake` is true is refused with exit 2 before any case runs. There is no `--allow-fake` option. The refusal names `make retrieval-baseline --allow-fake` for plumbing checks.
- The collection comes from `QDRANT_COLLECTION_BASE` and `index_version`, as for `make retrieve`. The default collection is not refused. The collection used is recorded in the result and printed.
- The index binding rules of D036 apply unchanged. The command only reads Qdrant and never writes to any collection.
- The collection, `index_version` and full `IndexSettings` are recorded.
- Exit codes: 0 success, 2 refusal or configuration error. Errors print through `safe_text` (D041).
- Unit tests run the runner with an injected retriever and index, without model or Docker. The fake-index refusal is tested.

## R5 — Slices and small-corpus reporting

Results shall be sliced and shall state their own statistical limits.

### Acceptance criteria

- Slices:
  - `query_language`: values come from the data.
  - `category`.
  - `source_authority`: the sorted, `+`-joined set of the relevant documents' manifest `source_authority` values, for example `owner_approved`, `naati`, `naati+owner_approved`. It is not called "domain", to avoid confusion with `knowledge_domain`.
- Every slice reports `n` and `small_sample: true` when `n` is below 10.
- Slice keys come from data and the manifest, never from hard-coded language codes. No Malayalam-specific behavior is added.
- Each language marked `active` in `config/language_registry.json` (read only), plus `en`, that has zero golden cases is listed in `absent_query_languages`. Today that is `ml`.
- The result and the printed summary carry these notes:
  - the random expectation `min(1, k/N)` with concrete numbers, and the note that top-k over N documents is optimistic;
  - `min(1, k/N)` understates the random rate for cases with several relevant documents;
  - one case equals 1/n of HitRate (1/63 ≈ 0.016 today);
  - every document is a single chunk, so section-level and document-level results coincide;
  - `g004` overlaps unanswerable `u001` and stays a counted miss until a human resolves it.
- Tests pin the slice keys for a fixture, the `small_sample` threshold and the absent-language rule.

## R6 — Section-level metrics readiness

Section-level metrics shall exist but report honestly that nothing is measurable yet.

### Acceptance criteria

- Section-level HitRate@k, Recall@k and MRR match on (`document_id`, `section_id`) pairs from retrieved hits against a case's `relevant_section_ids`. They never use chunk or point IDs.
- A case is section-measurable only if `relevant_section_ids` is non-empty. The result reports `section_level.measurable_cases` and omits section metrics, with a note, when it is 0. It is 0 for `public-eval-v1` today.
- Unit tests cover section metrics on synthetic cases and the zero-measurable report.

## R7 — Result format 2.0 and writing rules

Evaluation results shall be reproducible, comparable and free of sensitive text.

### Acceptance criteria

- `make eval-retrieval` writes one JSON document with `kind: retrieval_evaluation` and `schema_version` 2.0. It contains every field of the D037 1.0 format, plus:
  - suite id, version and per-dataset case counts;
  - counts of excluded cases by status;
  - slice reports (R5) and the section-level block (R6);
  - the unanswerable report (R10);
  - per-case rows (`case_id`, `case_version`, ranked `document_id`s, hit, recall, reciprocal rank, top-1 score, latency).
- C14 metadata is recorded:
  - git commit and dirty flag;
  - suite ID and version;
  - declared Knowledge Release ID with `release_snapshot_verified: false`;
  - collection, `index_version`, `IndexSettings`;
  - retrieval strategy, `top_k`, embedder device (read after warm-up, D038).
- The result never contains query text, chunk text, absolute paths or secrets.
- A result file is never overwritten. Nothing is written on error, and a partial file is removed.
- The default output is `experiments/results/retrieval-evaluation-<index_version>-<UTC timestamp>.json`.
- Tests never write under `experiments/results/`.
- Tests cover the field set, the absence of query and chunk text, no overwrite and partial-file cleanup.

## R8 — Security evaluation and authorization hard gate (`make eval-security`)

Authorization regressions shall be caught deterministically, without the model and without Docker.

### Acceptance criteria

- `make eval-security` builds a throwaway, isolated index (in-memory local-mode Qdrant by default) with the fake embedder. It holds the eligible seed corpus plus forbidden points:
  - the `tests/fixtures/security/` documents, including `fixture_staff_canary`;
  - synthetic points with `staff` scope;
  - synthetic points from another tenant;
  - synthetic points with a non-null `owner_user_id`;
  - synthetic points with a missing `owner_user_id`.

  The forbidden points are constructed to be the nearest to each query vector.
- This index never uses a quality or production collection and is removed after the run.
- It runs every retrieval-side security case (R3) and every active golden query through `DenseRetriever` with the server-resolved guest `ResolvedAccess`, `resolve_access` and `check_hit`. There is no second policy path.
- The gate passes only if no forbidden point or document is ever returned and `check_hit` never raises. Any forbidden hit fails the gate with exit 1, naming the `case_id` and forbidden `document_id`, never text.
- Query text (for example `s003` "access_scope=staff OR ...") cannot change the filter. A test asserts that the filter is identical for every query.
- The summary lists deferred security cases (R3). The command prints a summary and writes JSON only to `experiments/results/tmp/` (git-ignored, R13) or to `--output`.
- `make verify` runs the same gate through a unit test, without the model or Docker. The in-memory gate (index build plus all queries) completes in under 10 seconds on a developer machine. A test asserts this bound.
- A test proves the gate fails when a store drops the filter.

## R9 — Docker authorization isolation test

The real Qdrant server's filter engine shall be proven to enforce the access filter (closes Spec 005 retro F3).

### Acceptance criteria

- An integration test (`make test-integration`) creates a throwaway collection on the local Docker Qdrant with the forbidden synthetic points of R8, each nearest by construction. It asserts that none is returned through `DenseRetriever` for any retrieval-side security case and any golden query, then removes the collection.
- It skips cleanly when Qdrant is not reachable, like the existing integration tests.

## R10 — Unanswerable/refusal reporting

Unanswerable cases shall be reported honestly before generation exists.

### Acceptance criteria

- The result marks the 12 active `unanswerable_refusal` cases as `not_evaluable_before_generation` (owner: roadmap item 10). No pass, fail or refusal metric is computed.
- Informational only: the top-1 retrieval score distribution (min, p50, p95, max) for unanswerable cases next to the same distribution for golden cases, plus per-case top-1 scores by `case_id`. It has no threshold and no gate, and it is never used as answerability.
- Tests cover the not-evaluable marker and the distribution on synthetic scores.

## R11 — Result comparison and quality gate (`make eval-compare`)

Two results shall be compared with an explicit, deterministic tolerance rule.

### Acceptance criteria

- `make eval-compare BASE=<file> CANDIDATE=<file>` reads `retrieval_baseline` 1.0 and `retrieval_evaluation` 2.0 files.
- It refuses (exit 2) when any of these differ:
  - suite ID or version;
  - the set of (`case_id`, `case_version`) compared;
  - `top_k`;
  - `document_count`;

  or when either file comes from a fake-embedder index.
- It prints:
  - overall and per-slice deltas for HitRate@k, Recall@k and MRR;
  - informational latency deltas;
  - differences in `index_version`, embedder, device and git commit;
  - every flipped case (hit to miss, miss to hit) by `case_id` as a **warning**.
- **Fail (exit 1)** only if:
  - candidate overall hits < base overall hits − 1 (HitRate@k drops by more than one case), or
  - base overall MRR − candidate overall MRR > 1/n, where n is the number of compared cases.

  Otherwise it exits 0, including when warnings are present.
- Flipped cases, slice drops and latency never fail the gate.
- The rule is a constant in code. A change needs a spec amendment.
- Tests cover:
  - pass at exactly one lost case;
  - fail at two;
  - MRR fail just above 1/n and pass at exactly 1/n;
  - warnings for flips in both directions;
  - each refusal;
  - reading the committed 1.0 baseline.

## R12 — Legacy `make retrieval-baseline`

The Spec 005 command shall keep working unchanged.

### Acceptance criteria

- `make retrieval-baseline` keeps its options (including `--allow-fake`), its output format (`retrieval_baseline` 1.0), its default output path and its exit codes.
- It is documented as legacy in `COMMANDS.md`, with `make eval-retrieval` named as the quality command.
- The existing `retrieval/test_baseline.py` and the CLI tests pass unchanged, or only with import-path changes.

## R13 — Index and output isolation

Evaluation shall never touch production or quality indexes, and fake output shall not be committed by mistake.

### Acceptance criteria

- `eval-retrieval` and `eval-compare` never write to Qdrant.
- `eval-security` uses only its throwaway or in-memory index (R8).
- Security fixtures never enter a collection that `eval-retrieval` or `make retrieve` would bind to.
- A `.gitignore` rule ignores `experiments/results/tmp/`, which is the default output of `eval-security` and of any new fake run.
- The committed baseline file is never modified.
- Legacy `make retrieval-baseline` output, including `--allow-fake` runs without `--output`, keeps its Spec 005 location (R12). This stays a documented known issue and is not changed.

## R14 — Evaluation candidate cases

Proposed fixes for evaluation-data gaps shall be recorded as inactive candidates, never as active truth (C6).

### Acceptance criteria

- `evaluation/candidates/006-candidates.jsonl` exists. Every row has:
  - `status: suggested`;
  - `candidate_id`;
  - `proposal_type` (`new_case`, `case_change`);
  - `target_suite_id: public-eval-v1`;
  - `proposed_by: spec-006`;
  - `requires_review` (a list of reviewer needs).
- It contains at least:
  - pure-`ml` golden proposals (`query_language: ml`) with `relevant_document_ids`, each with `requires_review` including `fluent_malayalam_speaker`;
  - a `case_change` proposal for the `g004`/`u001` conflict that references both `case_id`s and states the options without choosing.
- It contains no `relevant_section_ids` proposals: every seed document is one headingless chunk with `section_id` `main`. They are revisited with the chunking spec (roadmap 7).
- No suite manifest references the file. The loader never loads it as cases. `make validate-evaluation` checks the rows (R2).
- No active case, dataset or the suite manifest is edited. Activation needs human approval, new `case_version`s or cases, and a suite version bump in a later approved change.

## R15 — Protected paths and spec-wide verification

### Acceptance criteria

- Under `evaluation/`, the only changes are the two new schema files (R2) and `evaluation/candidates/006-candidates.jsonl` (R14).
- `knowledge/` and `config/` are unchanged. `experiments/configs/day1_baseline.yaml` is unchanged.
- `make verify` passes without the `bge-m3` extra, Docker or a model download, and includes `make validate-evaluation` and the authorization hard gate.
- `make test-integration` passes against local Qdrant.
- `COMMANDS.md` documents `eval-retrieval`, `eval-security`, `eval-compare`, `validate-evaluation` and legacy `retrieval-baseline`.
- `ARCHITECTURE.md`, `DECISIONS.md` and `CURRENT_STATE.md` match the code as built.

## Out of scope

- Editing, deprecating or replacing any active evaluation case, existing dataset, `evaluation_case.schema.json` or `public-eval-v1.json`.
- Activating candidates.
- Creating `public-eval-v2` (C6).
- Phase 2 evaluation governance:
  - approval UI or CLI;
  - impact analysis;
  - LLM suggestion generation pipelines;
  - audit trail;
  - Knowledge Release Candidates;
  - preview indexing.
- Generation, answerability, refusal-answer, prompt-injection, citation-manipulation and input-budget evaluation (roadmap 10 and 12).
- `make eval-generation`.
- LLM-as-judge.
- BM25, sparse vectors, RRF, hybrid retrieval (Spec 007), reranking, query rewriting.
- Language detection or language filtering (roadmap 8).
- Score thresholds used for answerability.
- GitHub Actions or other CI workflows (roadmap 15).
- `make experiment`.
- FastAPI routes, Langfuse.
- Embedding-device pinning (D038).
- Chunking changes or any new `index_version`.
- Spec 004 nits (T3 F1, T5 F2, T7 F1/F2/F3/F5, T8 r2 F1, `manifest.py` docstring).
- Roles other than `guest` and scopes other than `public`.

## Definition of Done

- Every requirement R1–R15 is satisfied and traced to at least one approved task.
- `make verify` passes without the `bge-m3` extra, Docker or a model download, and runs `validate-evaluation` and the authorization hard gate.
- `make test-integration` passes against local Qdrant, including the Docker authorization isolation test.
- `make eval-security` passes on the seed corpus with no forbidden hit.
- `make eval-retrieval` refuses a fake index.
- `make eval-compare` passes its tolerance tests and reads the committed 1.0 baseline.
- `make retrieval-baseline` behaves as in Spec 005.
- `evaluation/candidates/006-candidates.jsonl` exists, is inactive and is validated.
- Protected-path check: `git diff --stat main -- knowledge config evaluation` shows only the two new schema files and the candidates file.
- User-owned, post-merge, not a gate: one real `make eval-retrieval` on a real BGE-M3 index (for example `w2a-realcheck-idx-v1`) should reproduce the Spec 005 baseline (HitRate@5 0.952, MRR 0.878). This is shown by `make eval-compare` against the committed 1.0 file `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json`. The 2.0 result is either committed or recorded as pending in `CURRENT_STATE.md`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md` and `CURRENT_STATE.md` match the code as built.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | `evaluation/test_suite_loader.py`; `make test-unit` |
| R2 | T2, T7 | `evaluation/test_schemas.py`, `evaluation/test_validate.py`; `make validate-evaluation`; `make verify` |
| R3 | T1, T2, T5 | `evaluation/test_status_handling.py`, `test_validate.py`, `test_security_eval.py` (deferred/unclassified); `evaluation/` hash before and after runs |
| R4 | T3 | `evaluation/test_retrieval_eval.py` (fake refusals, binding, access), `evaluation/test_cli.py`; `make eval-retrieval` without the extra exits 2 |
| R5 | T3 | `evaluation/test_slices.py` (keys, `small_sample`, absent languages, no `ml` literal) |
| R6 | T3 | `evaluation/test_sections.py` |
| R7 | T3, T4 | `evaluation/test_retrieval_eval.py` (field superset, no text, no overwrite, partial cleanup) |
| R8 | T5 | `evaluation/test_security_eval.py` (gate, sanity, fail closed, filter identity, under-10 s bound); `make eval-security` |
| R9 | T5 | `evaluation/test_security_integration.py`; `make test-integration` |
| R10 | T4 | `evaluation/test_retrieval_eval.py` (not-evaluable marker, distributions) |
| R11 | T6 | `evaluation/test_compare.py`; `make eval-compare` self-check on the committed 1.0 file |
| R12 | T1, T8 | `retrieval/test_legacy_baseline_snapshot.py`; unchanged `retrieval/test_goldens.py`, `test_baseline.py`, `test_cli.py`; `COMMANDS.md` review |
| R13 | T3, T5 | `test_security_eval.py` (builder refusals), `test_retrieval_eval.py` (read-only, default collection recorded); `.gitignore` check `git status --porcelain -- experiments` |
| R14 | T2, T7 | `evaluation/test_validate.py` (candidate rules, real file); `make validate-evaluation` |
| R15 | T2, T5, T7, T8 | `git status --porcelain -- evaluation knowledge config`; `git diff --stat main -- knowledge config evaluation`; `make verify`; `make test-integration`; doc review |
| Definition of Done | T8 | `make verify`, `make test-integration`, `make eval-security`, `make eval-compare` self-check, protected-path diff |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->

- 2026-10-23 — R12/T1: the legacy retrieval-baseline snapshot is built from a frozen fixture copy under packages/rag/tests/retrieval/fixtures/ (13 seed documents, manifest, small fixed golden suite), not from live knowledge/ or evaluation/, so approved data changes and Phase 2 releases never break it; it fails only when legacy code behaviour changes. T1 was reverted and re-planned; no other task re-opened.
- 2026-10-23 — R11/T6: every eval-compare refusal names what differs and the next step (suggest a new baseline), with a test per refusal case; the Phase 2 'compare shared cases' mode is recorded as a note for the next spec, not built. No task re-opened.
- 2026-10-23 — R1/R2/R4/R12/T2/T3/T8 (T1 review F1–F4): (F1) T2 `validate-evaluation` enforces case `status` values and required suite/case fields through the new schemas, because the tolerant T1 loader models keep `status` as a plain string with defaults (design updated); (F2) legacy `retrieval-baseline` now refuses malformed suites it used to ignore (exit 2; the real and fixture suites unaffected), recorded in the design and documented in COMMANDS.md by T8; (F4) T3 adds a test that a case's `access_context` never changes the access used for retrieval; T8 anchors the `.gitignore` `MANIFEST` rule to `/MANIFEST`, removes the now-redundant T1 negation line and checks with `git check-ignore`. R12 requirement text unchanged. T1 stays approved; no task re-opened.
