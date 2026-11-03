# 009 — Chunking Experiments: Retrospective Review

## Round 1 — 2026-11-03

- **Spec:** `009-chunking-experiments`
- **Diff reviewed:** `main...spec/009` (head `bb09cbd`, base `d21dc41`); `graphify-out/` excluded. Working tree at review start was clean at that head.
- **Reviewer host / model:** Cursor, Grok 4.6, run as a subagent of the orchestrator. Intended tier BEST (`Grok 4.6` in `agent-skills/MODEL_PREFERENCES.md`): matches. Fresh session; not the implementer's session (implementer ran as Composer / Grok 4.6 mix).
- **Outcome:** `PASS`
- **Usage:** n/a (Cursor)

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `HF_HOME=/tmp/w2a-spec-review-empty-hf` (+ hub/transformers caches under it) `HF_HUB_OFFLINE=1` `TRANSFORMERS_OFFLINE=1` `make verify` | exit 0 | ruff all passed, 168 files formatted, pyright 0 errors, skills mirrors match (6 skills), `validate-knowledge: OK, 0 problems`, `validate-evaluation: OK, 0 problems`, pytest **1120 passed, 2 skipped** (opt-in BGE-M3 smokes; autouse `hub_offline_empty_cache`). Qdrant reachable, so Docker integration tests ran inside verify on throwaway collections |
| `make test-integration` | exit 0 | **27 passed**, 1095 deselected |
| `make eval-security` | exit 0, `eval-security: PASS` | 3 chunkers × 5 paths; 74 queries each; heading 2000 / structure 64 `title_and_headings` / recursive 48 title; 13 seed documents; 2238 ms; result `experiments/results/tmp/security-evaluation-20261103T164830Z.json` (schema 1.3) |
| `make validate-knowledge` | OK, 0 problems | also part of verify |
| `make validate-evaluation` | OK, 0 problems | also part of verify |
| `git diff --name-status main...spec/009 -- evaluation knowledge config` | `M config/ingestion.yaml` only | T6 promotion (R10); nothing under `evaluation/` or `knowledge/` |
| `git diff main...spec/009` of `retrieval/fusion.py`, `hybrid.py`, `fallback.py`, `access.py`, `availability.py`, `lexical/tokenizer.py`, `retrieval/bm25.py` | empty | unchanged-code rule holds |
| `graphify query` (before source reads) | ran | 4400-node graph; scoped subgraph used |

### Extra checks (user-requested)

| Check | Result |
|---|---|
| **1. Cross-index eval-compare (read-only)** `make eval-compare BASE=experiments/results/retrieval-evaluation-idx-v1-20261103T104346Z.json CANDIDATE=experiments/results/retrieval-evaluation-idx-v2-20261103T104934Z.json COMPARE_ARGS=--cross-index` | **PASS**, matches **D071**: `eval-compare: PASS (hits 68 -> 68, MRR 0.9094 -> 0.9208)`; overall Recall@5 **0.9855 → 0.9783**; `en` (54) HitRate@5 / Recall@5 **1.0000 → 0.9815**, MRR **0.9352 → 0.9321**; flips `WARNING flipped hit->miss: g026 v1`, `WARNING flipped miss->hit: g061 v1`; cross-index lines collection `w2a-realcheck-idx-v1` → `w2a-realcheck-idx-v2`, `idx-v1` → `idx-v2`, chunker heading 1 → recursive 1, ingestion_config `config/ingestion.yaml` → `experiments/configs/chunking/recursive-128.yaml` |
| **2. Hub-free verify** | **PASS**: empty `HF_HOME` + `HF_HUB_OFFLINE=1` → **1120 passed, 2 skipped** (expected; autouse fixture plus opt-in smokes) |
| **3. Carry-over coverage** | **PASS after this round's docs.** Before reconciliation, Known issues named `relevant_section_ids`, Malayalam stemming, and Spec 008 HTTP-route items, but not stale yaml keys, size vs prefix, `g026` lost, FAQ pairs, or semantic chunking (those lived in Spec 009 implemented bullets / Next step / D071 / ROADMAP). This round added a Spec 009 Known issues block covering every listed item; Notes for the next spec (below) repeats them. |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 tokenizer | `ingestion/tokenization.py` (`ChunkTokenizer`, `BgeM3Tokenizer`, `FakeTokenizer`, `build_tokenizer`, `embedder_for_run`); `tokenizers` + `huggingface_hub` base deps | `test_tokenization.py`; hub-free `make verify` 1120/2; T1 `uv tree` (torch only under `bge-m3` extra) | SATISFIED |
| R2 truncation guard | `ingestion/guard.py` `check_chunks`; `service.py` per-document try; `lexical/build.py` `production_entries` | `test_guard.py`, `test_service.py`, `test_lexical_cli.py` (exit 2, no file) | SATISFIED |
| R3 structure v1 | `ingestion/structure.py` `StructureChunker`; heading-path `section_id`; `DuplicateSectionError` | `test_structure.py`; seed snapshots | SATISFIED |
| R4 recursive v1 | `ingestion/recursive.py` `RecursiveChunker`; prefix half-target; overlap trim | `test_recursive.py`; T2/T6 BGE-M3 counts 34 / max 4 | SATISFIED |
| R5 config and settings 1.1 | `ingestion/config.py`, `chunker_build.py`, `settings.py`; experiment yamls | `test_config_schema_11.py`; Docker 1.0 collection binds (`test_recursive_integration.py`) | SATISFIED |
| R6 lexical identity / freshness | `lexical/store.py` 1.1; `freshness.py` `verify_fresh` (no re-chunk, no tokenizer); `opening.py` has no `build_tokenizer` | `test_lexical_standalone.py`; T6 idx-v1 rebuild digest `6045203b…` / 13 chunks | SATISFIED |
| R7 distinct-document metrics | `evaluation/retrieval_eval.py` retrieve at D, `dedupe_documents`[:k], result 2.3 | `test_retrieval_eval.py`; T6 `chunk_stats` 34/13/4/17 | SATISFIED |
| R8 cross-index compare | `evaluation/compare.py` `--cross-index`; Makefile `COMPARE_ARGS` | `test_compare.py`; extra check 1 re-run matches D071 | SATISFIED |
| R9 security across chunkers | `security_eval.py` `security_gate_chunkers()` (heading / structure 64 / recursive 48); result 1.3 | parameterized `test_security_eval.py`; `test_security_integration.py`; `make eval-security` PASS | SATISFIED |
| R10 real runs / default index | T6 result files; `config/ingestion.yaml` = `recursive-128.yaml`; D071 | extra check 1; promotion rule holds (hits 68→68, MRR up, no `ml`/`mixed` hit→miss) | SATISFIED |
| R11 docs, decisions, clean-ups | D064–D071; public `chunk_identity`; settings docstring; `test_wrong_vector_count_is_a_per_document_failure`; autouse hub fixture | T7 review round 2; this round's remaining docs | SATISFIED (after this round's reconciliation) |
| Definition of Done | all of the above | this round | SATISFIED, pending the user's approval and merge |

### Protected-data check

`git diff --stat main...spec/009 -- evaluation/ knowledge/ config/` → `config/ingestion.yaml | 20 ++++++++++----------` only. Required by R10 after promotion (schema 1.1, `idx-v2`, recursive 128/16/title, byte copy of `recursive-128.yaml`). Nothing under `evaluation/` or `knowledge/`. No unrequired change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION (docs) | R11 / T7 | Spec 009 carry-overs (stale yaml keys, size vs prefix, `g026` lost, FAQ pairs, semantic chunking) were recorded in D071 / Next step / Spec 009 implemented bullets / ROADMAP but not in `CURRENT_STATE.md` **Known issues**. `relevant_section_ids` still said "revisit with the chunking spec". **Reconciled in this round** (Spec 009 Known issues block; Notes below). |
| F2 | MINOR | IMPLEMENTATION (docs) | R11 / T7 | Design `## As-built notes` recorded T2 counts and the confounded arm, not `chunker_build.py`, `embedder_for_run` / `chunker_identity_for_run`, the promoted schema-1.1 yaml, or the T7 hub-offline fixture. **Reconciled in this round**. |
| F3 | MINOR | IMPLEMENTATION (docs) | R6, R11 / T7 | `COMMANDS.md` said `make index-lexical` needs "no model". True for PyTorch / the embedder; token-based chunkers (default `idx-v2`) still need BGE-M3 tokenizer files for packing and the guard. **Reconciled in this round**. |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/CURRENT_STATE.md` | Current goal and Spec 009 row: retrospective round 1 `PASS` pending user approval; Spec 009 Known issues block with every carry-over; `relevant_section_ids` wording; Next step item 10 | F1; implemented reality |
| `docs/project/ROADMAP.md` | Item 7 status: retrospective round 1 `PASS` pending user approval; deferred list includes `g026` and the full HTTP-route set | F1; match code |
| `docs/project/COMMANDS.md` | `make index-lexical`: no PyTorch; tokenizer files required for token-based chunkers; standalone open still tokenizer-free | F3 |
| `.kiro/specs/009-chunking-experiments/design.md` | As-built: retrospective round 1 deviations (`chunker_build.py`, identity-for-run, promoted yaml, hub fixture, `configured_lexical`) | F2 |
| `.kiro/specs/009-chunking-experiments/review.md` | this round | required record |

`DECISIONS.md` (D064–D071), `TECH_STACK.md` (`tokenizers`, `huggingface_hub`) and `ARCHITECTURE.md` (ingestion, lexical, result 2.3 / `--cross-index` / security 1.3) already matched the code. D060 was not rewritten; D067 is the amendment. `requirements.md`, `tasks.md`, code, tests, `evaluation/`, `knowledge/` and `config/` not edited.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| Whitespace-collapsed chunk-body invariant; recursive overlap trim | change log 2026-11-02 (T2 round 2 user-approved); design amended |
| Recursive prefix half-target rule (same as structure) | change log 2026-11-02 (T3); design amended |
| T4 follow-ups (E2E `run_retrieval_evaluation`, 2.3 vs 2.3 chunker refusal, real 2.2 fixtures) | change log 2026-11-02; T5 boxes |
| Recursive security arm `target_tokens` 48 not 32 | change log 2026-11-02 (R9/T5); `security_gate_chunkers()` |
| `embedder_for_run` so `--embedder fake` uses `FakeTokenizer` | T1 review F1, user-approved round 2 |
| `chunker_identity_for_run` / persist `chunker.identity` from the built chunker | T3 review F1, user-approved round 2 |
| `ingestion/chunker_build.py` extracted from `cli.py` | T3 implementation notes; As-built this round (F2) |
| `config/ingestion.yaml` promoted to schema 1.1 / `idx-v2` | R10; T6 user-approved 2026-11-03 |
| Autouse hub-offline empty cache; `configured_lexical` uses `FakeTokenizer` + `chunker_identity(config)` | T7 round 2, user-approved 2026-11-03 |
| T6 "If not promoted" checkbox left unchecked | N/A: the promoted path was taken |

### Cross-task consistency

- **One tokenizer constructor.** `build_tokenizer` is the only production constructor; `embedder_for_run` makes `--embedder fake` yield `FakeTokenizer`. Standalone and hybrid-fallback open paths never call `build_tokenizer` (`opening.py` grep empty); they use `chunker_identity_for_run`.
- **One identity value.** `ChunkerIdentity` is built without loading tokenizer files (`chunker_identity` / `chunker_identity_for_run`), stored on IndexSettings 1.1 and lexical settings 1.1, compared by `verify_fresh` and `check_identity`, copied onto result 2.3 and security 1.3. `--embedder fake` persists the built chunker's identity (`fake-tokenizer@1`), not the yaml's BGE-M3 string (T3 F1).
- **One guard.** Ingestion and `production_entries` share `check_chunks`; oversized lexical builds exit 2 with no file.
- **One metric unit.** `eval-retrieval` retrieves at fusion `candidate_depth` (50), dedupes documents, scores k distinct documents; `eval-compare` refuses a `metric_unit` mismatch and requires `--cross-index` for collection / `index_version` / chunker / `ingestion_config`.
- **Authorization unchanged.** `access.py` and `bm25.py` have no diff vs `main`. Security gate covers five paths × three chunkers with forbidden points nearest by construction. Fallback still uses the same `ResolvedAccess`.
- **Unchanged surfaces.** `fusion.py`, `hybrid.py`, `fallback.py`, `availability.py`, `lexical-v1`, `HeadingChunker` output, `PointPayload` (17 fields), `INGESTION_NAMESPACE` untouched. Legacy `make retrieval-baseline` snapshot still passes.
- **Promotion record.** Hits 68→68, MRR 0.9094→0.9208, no `ml`/`mixed` hit→miss; Recall@5 and the `en` slice are written in D071 even though they are not in the R10 gate.

### Scope-drift review

- No headed knowledge documents, no suite v3, no `relevant_section_ids` fill, no FAQ indexing, no semantic chunker, no `heading` v1 / `idx-v1` rebuild, no Malayalam stemming, no HTTP route, no circuit breaker, no Phase 2 release workflow.
- Protected paths: only `config/ingestion.yaml`, as R10 required after promotion.
- Developer-tooling commits on `spec/009` vs `main` (Cursor always-on rule, skill-mirror nits, `MODEL_PREFERENCES` Cursor BEST `Grok 4.7` → `Grok 4.6`, WORKFLOW usage-line wording, `.gitignore` `/.local/pytest-hf-empty/`): not chunking scope. The pytest-hf ignore is T7; the rest is D063-adjacent tooling that will land with this merge. Not Phase 2.
- Spec-file amendments after approval have dated `## Change log` lines (T2 fidelity/overlap, T3 prefix rule, T4 follow-ups, R9 at 48 tokens).

### Patterns in `task-reviews.md`

- 7 tasks. FAIL then PASS: T1 (2 rounds), T2 (3), T3 (2), T7 (2). PASS round 1: T4, T5. T6 was user-owned wrap-up with no separate code review round.
- Repeated theme: a **warm Hugging Face cache hides tests** that construct `BgeM3Tokenizer` (T1 F1 BLOCKING; T7 F3 MAJOR). Round 2 of T7 added autouse empty `HF_HOME` + `configured_lexical` FakeTokenizer. This retrospective re-ran verify that way.
- Repeated theme: **composed token count and source-span fidelity** on the new chunkers (T2 F1/F2 twice). Settled by the whitespace-collapsed invariant and overlap-trim amendment.
- T4 PASS noted follow-ups (E2E runner, 2.3 chunker refusal, real 2.2 fixtures) that T5 closed the same day.
- Implementer: Composer (T1–T3, T5, T7) and Grok 4.6 (T4). Reviewer: Grok 4.7 (T1–T3) then Grok 4.6 (T4, T5, T7). Usage mostly `n/a (Cursor)`.
- `graphify update .` ran per code task (unlike Spec 008, where the orchestrator often did it).

### Remediation required

None. F1–F3 are MINOR and reconciled in docs this round. No RM tasks. Spec `Status:` stays `all tasks approved (2026-11-03)`.

### Notes for the next spec

The next spec on the roadmap path that consumes this one is the HTTP retrieval route (or whichever spec first runs retrieval in a long-lived process), plus later knowledge/eval work for headed documents. Carry-overs — each also under `CURRENT_STATE.md` Known issues:

- **Stale yaml keys.** `config/ingestion.yaml` and `experiments/configs/chunking/recursive-128.yaml` still carry ignored top-level `knowledge_release_id` / `evaluation_suite_id` (`public-eval-v1` on the latter). Strip them at the next `index_version`; do not strip them from this promotion's byte copy (D071; arm `ingestion_config` hash).
- **Empty `relevant_section_ids`.** Every evaluation case still has none, so section-level `eval-retrieval` reports zero measurable cases. Headed documents, a new `document_version`, and suite v3 are a later spec. `structure` v1 heading-path IDs are ready once documents gain headings.
- **Size vs prefix confounding (D071 arm).** Default `idx-v2` is recursive 128 tokens *and* title prefix together. Do not attribute the MRR lift (0.9094 → 0.9208) or the Recall/`en` drop to either treatment alone. A later experiment should split them (128/none vs 128/title vs heading+title).
- **`g026` lost on promotion.** `en`, mock, `business_006_mock_assessments`: hybrid hit on `idx-v1`, miss on `idx-v2`. Overall HitRate@5 stayed 0.9855 (68/69); English HitRate/Recall 1.0 → 0.9815. R10 allowed it. Revisit with reranking (roadmap 9) or the size-vs-prefix split. `g061` is now a hit (distinct rank 5 on the arm).
- **FAQ pairs.** `knowledge/structured/owner_approved_faq_pairs.jsonl` is still not indexed (own spec).
- **Semantic chunking.** Still out of scope.
- **Malayalam stemming.** `lexical-v1` is exact tokens only; legacy chillu sequence still distinct from atomic chillu (D051, roadmap 8). Hybrid keeps the six `ml` goldens; on `idx-v2` their MRR is 1.0 (was 0.7917 on heading hybrid).
- **Spec 008 HTTP-route items** (008 retrospective / T8 hand-off, still open): startup and reopen policy for a missing or stale lexical file (open-time fallback lasts the whole process); circuit breaker (D058); Qdrant client lifecycle (`open_retrieval` closes the client only on the hybrid fallback path; `OpenedRetrieval.close()` does not close it; fold duplicated standalone wiring, 008 F4, and add the `bind_to`-scroll fallback test, 008 F5); async freshness (`verify_fresh` uses `asyncio.run`); freshness cost (D067 still reads every eligible document for `content_hash`); fallback-stage observability (open vs query); Qdrant 5xx eligibility (D062); API surface (fixed reason vocabulary, server-resolved access only).
- **Per-scope lexical files** when roles land (D050).
- **Hub-free verify.** Keep the autouse empty-cache fixture. Any test that calls `build_tokenizer` against production `bge_m3` yaml will pass on a laptop with a warm cache and fail in CI. Re-run `make verify` with empty `HF_HOME` + `HF_HUB_OFFLINE=1`.
- **Operator setup.** Default is `make ingest` then `make index-lexical` for `idx-v2`. Real lexical builds need tokenizer files; unit tests must not. `heading-idx-v1.yaml` still selects `idx-v1`.
- **Reference results** (suite `public-eval-v2` v2, BAAI/bge-m3 @ `5617a9f`): heading 2.3 `…idx-v1-20261103T104346Z.json` (68/69, MRR 0.9094, equal to the Spec 008 hybrid 2.2 reference) and recursive 2.3 `…idx-v2-20261103T104934Z.json` (68/69, MRR 0.9208). Binding-check file `…idx-v2-20261103T105358Z.json` has `git_dirty: true` (not a reference).
- **Still deferred from earlier specs:** device pinning (D038); open Spec 004 nits (T3 F1, T7 F2, T7 F5, T8 r2 F1, Retro F1); Spec 006 retrospective F1 (byte-identity around runners).

### Final handoff

`PASS`. No BLOCKING or MAJOR findings; three MINOR findings (F1–F3, all documentation, reconciled this round). Extra checks: cross-index compare matches D071; hub-free verify 1120 passed, 2 skipped; carry-overs now appear in both Known issues and Notes for the next spec. Documentation reconciled in `CURRENT_STATE.md`, `ROADMAP.md`, `COMMANDS.md` and the design As-built notes. No RM tasks. All changes are uncommitted for the orchestrator to commit after the user's approval. Merging `spec/009` into `main` can proceed once the user approves this round. No `Status:` was set to verified.

Learning notes: /Users/justin/learning/way2australia/specs/009-chunking-experiments/debrief.md
