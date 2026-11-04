# 010 — Multilingual Retrieval: Retrospective Review

## Round 1 — 2026-11-04

- **Spec:** `010-multilingual-retrieval`
- **Diff reviewed:** `main...spec/010` (head `0d2f71c`, base `5a6deb7`); `graphify-out/` excluded. Working tree at review start was clean at that head.
- **Reviewer host / model:** Cursor, Grok 4.6, run as a subagent of the orchestrator. Intended tier BEST (`Grok 4.6` in `agent-skills/MODEL_PREFERENCES.md`): matches. Fresh session; not the implementer's session (implementer ran as Composer / Composer 2.5 Fast).
- **Outcome:** `PASS`
- **Usage:** n/a (Cursor)

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `HF_HOME=<mktemp> HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 make verify` (full permissions; sandbox breaks temp-repo `.git` tests) | exit 0 | ruff all passed, 177 files formatted, pyright 0 errors, skills mirrors match (6 skills), `validate-knowledge: OK, 0 problems`, `validate-evaluation: OK, 0 problems`, pytest **1257 passed, 2 skipped** (opt-in BGE-M3 smokes; autouse `hub_offline_empty_cache`). Qdrant reachable, so Docker integration tests ran inside verify on throwaway collections |
| `make test-integration` | not run as a separate target | User asked for `make verify` once; those Docker tests ran and passed as part of verify |
| `make eval-security` | skipped | User instruction: skip unless product code changes; this round edited docs only |
| `git diff --name-status main...spec/010 -- evaluation knowledge config` | T1 `evaluation/` + `config/retrieval.yaml` only | nothing under `knowledge/` |
| `git diff main...spec/010` of `retrieval/access.py`, `fusion.py`, `availability.py`, `index.py`, ingestion package, `config/ingestion.yaml` | empty | unchanged-code rule holds |
| `graphify query` / `explain` (before source reads) | ran | 4728-node graph; `languages.py` at package root; `applicability.py`; `continuity.py:_identity_refusals` |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 suite v3 | `evaluation/suites/public-eval-v3.json` (`case_count` 112); `datasets/v3/`; v2 `status: replaced`; `candidates/010-candidates.jsonl` (21 promoted); `candidate_row` `oneOf`; `DEFAULT_SUITE` v3 | `test_suite_v3.py`; `make validate-evaluation` OK 0 problems; T1 user "Approve both" confirmed in `task-reviews.md` | SATISFIED |
| R2 `lote` request | `resolve_lote` / `ResolvedLote` (`applicability.py`); CLI `--lote`; result top-level `lote` | `test_applicability.py`; retrieve/eval CLI tests; older files read `lote` as null | SATISFIED |
| R3 applicability on every path | `build_lote_condition`, `build_sql_lote_clause`, `dense_query_filter`, `sql_access_with_lote`; lexical settings 1.2 `lote_languages` column; 1.1 refused with `--lote` | per-path tests (dense, bm25, hybrid, fallback open/query); store parity; seed-corpus `lote: ml` equality; `access.py` diff empty | SATISFIED |
| R4 fail-closed re-check | `check_applicable`; `LanguageApplicabilityError` sibling of `RetrievalAuthorizationError`; `FallbackRetriever` catches only `RetrievalUnavailableError` | dropped-filter injection tests; error-class tests | SATISFIED |
| R5 `lexical-v2` | `equivalents.py` six Unicode 16.0 chillu pairs; `_tokenize_v2` NFC then `replace_sequences` then v1; module-level aliases stay v1 | pair tests; corpus/query v1 equality; D051 pin; file queried with its own tokenizer | SATISFIED |
| R6 tokenizer selection | `config/retrieval.yaml` schema 1.2, default **`lexical-v2`** after T5; `--tokenizer`; `W2A_LEXICAL_INDEX_DIR` second file; `.gitignore` `/.local/` | CLI/strategy tests; T5 realcheck builds (34 chunks, same digest) | SATISFIED |
| R7 result 2.4 / script mix | `script_mix.py` (`unicodedata` name prefix); `by_script_mix`; per-case `script_mix`; romanized Malayalam → `latin` | `test_script_mix.py` (v3 letter fixture, virama/vowel pins, `g062`) | SATISFIED |
| R8 `eval-compare` | `--cross-tokenizer`; `lote` refusal; `--cross-index` still skips digest/chunk_count (T3 round 2) | `test_compare.py` | SATISFIED |
| R9 security 1.4 | dual `lote` modes; `zz` rows; `staff_scope_lote`; split violation lists | `test_security_eval.py`; `test_security_integration.py`; T4 `make eval-security` PASS (not re-run this round) | SATISFIED |
| R10 real runs / promotion | four v3 `lote: ml` result files; continuity module exit 0 (69 shared goldens); both `--cross-tokenizer` compares tied; default `lexical-v2` | T5 `task-reviews.md`; files `…T105123Z` / `…T105259Z` / `…T105300Z` / `…T105321Z`; D072 numbers | SATISFIED |
| R11 unchanged / protected / verify | no `lote` keeps prior behaviour; `knowledge/` empty; `evaluation/` only T1; `config/` only tokenizer schema/default | this round's verify 1257/2; protected-path diff | SATISFIED |
| R12 docs / D072 | D072; ARCHITECTURE, COMMANDS, SCHEMA_AND_METADATA, ROADMAP, CURRENT_STATE; design As-built notes | this round's remaining doc nits (F1–F5) reconciled | SATISFIED (after this round's reconciliation) |
| Definition of Done | all of the above | this round | SATISFIED, pending the user's approval and merge |

### Protected-data check

`git diff --stat main...spec/010 -- evaluation/ knowledge/ config/` → eight files, all required:

- `evaluation/candidates/010-candidates.jsonl`, `evaluation/datasets/v3/*`, `evaluation/suites/public-eval-v3.json` (R1)
- `evaluation/suites/public-eval-v2.json` (`status: replaced` only)
- `evaluation/schemas/evaluation_case_types.schema.json` (`candidate_row.proposed_case` `oneOf`; dated change-log 2026-11-04)
- `config/retrieval.yaml` (T3 schema 1.2 + T5 `lexical.tokenizer: lexical-v2`)

Nothing under `knowledge/`. No unrequired change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION (docs) | R12 / T6 | `ARCHITECTURE.md` retrieval module table listed `languages.py` with `applicability.py` under the `packages/rag/.../retrieval/` intro; the file is `packages/rag/src/way2australia_rag/languages.py`. **Reconciled in this round.** |
| F2 | MINOR | IMPLEMENTATION (docs) | R12 / T6 | `COMMANDS.md` `make eval-security` said a query with no `lexical-v1` terms skips the lexical check. After T5 the file tokenizer may be `lexical-v2`. **Reconciled** to “no lexical terms”. |
| F3 | MINOR | IMPLEMENTATION (docs) | R12 / T6 | `COMMANDS.md` `make eval-continuity` said lexical identity is refused “unless you use cross-mode compares elsewhere”. `evaluation/continuity.py:_identity_refusals` always compares `lexical_index` and has no `--cross-tokenizer` / `--cross-index`. **Reconciled** (parenthetical dropped). |
| F4 | MINOR | IMPLEMENTATION (docs) | R12 / T6 | `COMMANDS.md` implemented-today list and the “All four run one module” sentence omitted `make eval-continuity` (separate module `way2australia_rag.evaluation.continuity`). **Reconciled in this round.** |
| F5 | MINOR | IMPLEMENTATION (docs) | R12 / T6 | `TECH_STACK.md` sparse retrieval still named only `lexical-v1` tokens (D051) after the T5 default became `lexical-v2`. **Reconciled** (D072). |

No BLOCKING or MAJOR finding.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/ARCHITECTURE.md` | Retrieval intro and module table: `languages.py` at package root, not under `retrieval/` | F1 |
| `docs/project/COMMANDS.md` | Implemented-today list + eval CLI vs continuity module; security skip “no lexical terms”; continuity identity always compared | F2, F3, F4 |
| `docs/project/TECH_STACK.md` | Sparse retrieval default `lexical-v2` (D072); script mix uses stdlib `unicodedata` | F5; R7 no new dependency |
| `docs/project/CURRENT_STATE.md` | Retrospective PASS pending approval; Spec 010 status; F1–F5 known-issues block; Spec 007 chillu item closed by D072; Next step | implemented reality |
| `docs/project/ROADMAP.md` | Item 8 status: retrospective round 1 `PASS` pending user approval | match code |
| `.kiro/specs/010-multilingual-retrieval/design.md` | As-built: registry parsing owned by `languages.py` at package root | F1 |
| `.kiro/specs/010-multilingual-retrieval/review.md` | this round | required record |

`DECISIONS.md` (D072) and `docs/knowledge/SCHEMA_AND_METADATA.md` already matched the code. `requirements.md`, `tasks.md`, code, tests, `evaluation/`, `knowledge/` and `config/` not edited.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| `candidate_row.proposed_case` `oneOf` golden or unanswerable (`query_language` required on unanswerable candidates) | change log 2026-11-04; T1 user “Approve both” |
| Default tokenizer `lexical-v2` (tie promotes; no measured gain) | R10 rule; T5 user-approved 2026-11-04 |
| R10 continuity invoked as the Python module, not `make eval-continuity` (GNU make maps exit 1 → 2) | T3 round 2 F5; T5 command; design As-built |
| `--cross-index` skips lexical digest/chunk_count (restores D069 after T3 round-1 regression) | T3 round 2 F1; design As-built |
| `make retrieve` does not print the lexical tokenizer name | T5 user-accepted deviation; design As-built |
| `open_retrieval` does not compare file tokenizer to `config/retrieval.yaml` | T5 carry-over; design As-built; Known issues |
| T5 “If not promoted” checkbox left unchecked (`N/A (promoted)`) | N/A: the promoted path was taken |
| T1 F2 dead schema-test clause; T2 DenseRetriever docstring; T3 chillu comments / BM25 docstring; T4 `staff_scope_lote` parametrize / Docker docstring | user-approved same-commit fixes, no re-review |

### Cross-task consistency

- **One `lote` value, every path.** CLIs and evaluation runners call `resolve_lote`; retrievers take `ResolvedLote | None` only. Dense, BM25, hybrid and both fallback wrappers pass the same object; `check_hit` then `check_applicable`. `access.py` output unchanged.
- **One applicability shape.** `valid_lote_languages` is `["*"]` or distinct codes without `*`; lexical builder refuses invalid payloads; `check_applicable` stops a raw Qdrant upsert. SQL column is pipe-separated; Qdrant uses `MatchAny(["*", code])`.
- **Tokenizer vs schema.** Lexical settings 1.2 is the file layout (`lote_languages` column); tokenizer name/version is independent. Queries always use the file's tokenizer. Config default is only for `make index-lexical` without `--tokenizer`. `open_retrieval` does not yet refuse a stale file tokenizer (Known issues / roadmap 10).
- **Result and compare.** New writes are 2.4 / security 1.4; readers accept 2.0–2.4 and 1.x. `eval-compare` refuses `lote` mismatch in every mode; `--cross-tokenizer` relaxes only tokenizer identity; `--cross-index` still skips digest/chunk_count. Continuity is a separate command and always compares lexical identity.
- **Authorization first.** `LanguageApplicabilityError` is not a `RetrievalAuthorizationError` and is not fallback-eligible. Security 1.4 counts dual failures as authorization. Non-applicable rows exist only in the throwaway corpus (`zz`).
- **No language literal in generic retrieval.** Active codes come from `config/language_registry.json`. `en` is refused in `resolve_lote` with an explanatory message. Script mix uses `unicodedata` name prefixes, not a Malayalam table.

### Scope-drift review

- No query translation/transliteration, Malayalam stemming, n-grams, per-script fusion, HTTP route, reranking, knowledge-content edits, new `index_version`, re-ingestion, or Phase 2 release workflow.
- Protected paths match R1/R6/R10 only.
- Spec-file amendment after approval has a dated `## Change log` line (T1 unanswerable `proposed_case`).
- `.gitignore` `/.local/` is T3 (git_dirty for T5 side-by-side lexical dirs), not tooling drift.

### Patterns in `task-reviews.md`

- 6 tasks. FAIL then PASS: T2 (2 rounds), T3 (2), T5 (FAIL then PASS same day after pin/lint fixes). PASS round 1: T1, T4, T6.
- Repeated theme: **required tests named in the task box were incomplete on round 1** (T2 fallback-open/query and BM25 lote injection; T3 script-mix letter fixture, own-tokenizer query, BM25 auth over both tokenizers, `--cross-index` digest regression).
- T5 FAIL was **promotion pins and lint**, not the real-run numbers: config moved to `lexical-v2` before tests that still asserted `lexical-v1`; ruff E501 from a T4 same-commit docstring wrap.
- Implementer: Composer / Composer 2.5 Fast. Reviewer: Grok 4.6. Usage mostly `n/a (Cursor)` or orchestrator.
- Process (P3): T3 recorded **12 `make verify` runs** (11 before last code edit); T4 recorded **8**. Hub-free verify was kept (empty `HF_HOME` + `HF_HUB_OFFLINE=1`).
- `graphify update .` ran per code task (separate graph commits).

### Remediation required

None. F1–F5 are MINOR and reconciled in docs this round. No RM tasks. Spec `Status:` stays `all tasks approved (2026-11-04)`.

### Notes for the next spec

- **Query translation / transliteration** (including Latin-script Malayalam) is the intended fix for **`g067`–`g069`** on BM25-only and on the hybrid **fallback** path. BM25-only `ml` MRR **0.2396** (n=16) on v3 realcheck `…20261104T105321Z.json`; `malayalam` script-mix slice 0.0 / 0.0 (n=10). Out of scope here.
- **`g056` / `g057`:** hybrid fusion demotes a dense rank-1 relevant document to reciprocal rank 0.5. Inputs for **roadmap item 9** reranking, not a retrieval-filter bug.
- **`open_retrieval` tokenizer vs config:** a stale `lexical-v1` file would serve silently after the v2 promotion. Group with roadmap **item 10** startup policy (missing/stale lexical file; Spec 008 F4 duplicate open helpers; Qdrant client lifecycle; async freshness).
- **`lexical-v2` is a correctness default**, not a measured gain: seed corpus and v3 queries contain no legacy chillu ZWJ sequences; T5 cross-tokenizer compares were identity ties. Do not cite T5 numbers as BM25 Malayalam improvement.
- **No Malayalam knowledge content** was added (`knowledge/` unchanged). Stemming and per-script fusion weighting were declined.
- **Script mix** uses Unicode **name** prefixes, not Scripts.txt; romanized Malayalam counts as **`latin`** (reporting only).
- **Per-scope lexical files** remain a roles-spec item (D050). Access did not change here.
- **Verify-budget:** T3/T4 implementer transcripts ran `make verify` far more than twice before the last code edit. Consider `chore/verify-budget` before Spec 011. Keep hub-free verify (`HF_HUB_OFFLINE=1`, empty `HF_HOME`).
- **Do not put `lote` inside `AccessContext`.** Language and authorization stay separate (C4, D072). Fallback must keep passing the same `ResolvedLote`.
- Spec **009** carry-overs remain: ignored yaml keys until the next `index_version`, size vs prefix confounding, `g026` en miss, FAQ pairs, semantic chunking, shallow-clone v2 hash-test skip.

### Final handoff

Outcome **PASS**. Five MINOR documentation findings, all reconciled this round. No RM tasks, no product-code edits, no `make eval-security` re-run. `review.md` and the doc edits are uncommitted. Merge `spec/010` only after the user's approval of this retrospective.

**User approval (2026-11-04):** Verbatim: "approved: retrospective round 1 PASS. go to merge."
