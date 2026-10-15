# 002 — Spec Review (retrospective)

Optional end-of-spec retrospective (`agent-skills/spec-reviewer`). Append-only; newest round at the bottom.

## Round 1 — 2026-10-15

- **Spec:** `002-document-model-and-repository`
- **Diff reviewed:** `main...spec/002` (head `47d802d`, merge-base `673934c`); T1–T2 code (`packages/core/.../documents/`) is already on `main` and was read directly
- **Reviewer host / model:** Claude Code (subagent, fresh session) / `claude-opus-5-5`
- **Outcome:** `SPEC_DEFECTS FOUND` (one MINOR spec defect; no RM tasks; advisory, does not gate verification)

### Verification run

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | pass (exit 0) | ruff clean; pyright 0 errors; skills mirrors match; `validate-knowledge: OK, 0 problems`; 170 tests collected, 170 passed (1 Starlette deprecation warning, unrelated) |
| `make test-integration` | pass | 13 passed, 157 deselected |
| `make validate-knowledge` | pass | `validate-knowledge: OK, 0 problems` on the 13-document seed corpus |
| `git diff --stat main...spec/002 -- evaluation/ knowledge/ config/` | empty | no protected data changed |
| `git merge-tree --write-tree main spec/002` | clean | `main` has 3 workflow-skill commits not on `spec/002` (`ed4efe2`, `ce95d79`, `44e4fd8`); they touch only skills, `WORKFLOW.md` and Spec 003 requirements |
| Commit trailers `main..spec/002` | ok | one `Spec-Task: 002/T3` … `002/T9` each |
| Frontmatter keys vs `KnowledgeDocument` (ad-hoc script) | 2 keys dropped | `schema_version` and `persona_scope` (all 13 seed docs) are not model fields; see F2 |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 model | `packages/core/.../documents/models.py`, `enums.py` (T1, on `main`) | `packages/core/tests/test_document_models.py` (58 cases) | SATISFIED |
| R2 identity/version | `document_id` pattern, `document_version` strict int ≥1; no path/chunk fields; duplicate pair rejection in `manifest.load_manifest` | model tests; `test_manifest_validation.py`; `test_content_hash.py` (path move keeps hash) | PARTIAL — "approved content changes increment `document_version`" is not checked anywhere (no version history; manifest allows one version per ID). Acceptable for Phase 1; see F4 |
| R3 repository abstraction | `base.py` (`DocumentRepository` Protocol, `DocumentQuery`), `errors.py`, `local.py` | `test_repository_contract.py` (in-memory fake), `test_local_repository.py` | SATISFIED |
| R4 local repository | `local.py` (`DEFAULT_APPROVED_ROOTS`, manifest-driven, `under_root`) | `test_local_repository.py` (excluded locations, CWD independence, language data-driven) | SATISFIED |
| R5 manifest | `manifest.py` (`load_manifest`, `check_manifest_documents`, `compare_manifest_to_metadata`, `check_integrity_hashes`) | `test_manifest_validation.py`, `test_validate_knowledge.py` | SATISFIED |
| R6 metadata validation | JSON Schema + Pydantic; `validate.py` lists every problem | `test_manifest_validation.py`, `test_validate_knowledge.py` | SATISFIED — scopes validated by the `AccessScope` enum, not cross-checked with `config/access_policy.yaml` (F3) |
| R7 content hashing | `hashing.py` (`content-hash-v1`, 17 fields), design "Content hashing", D024 | `test_content_hash.py` (25) | SATISFIED — hash input is the raw frontmatter mapping (F1) |
| R8 eligibility | `eligibility.py` (`EligibilityPolicy`, `GUEST_PUBLIC_POLICY`, `list_eligible_documents` re-check) | `test_eligibility.py` (22), `test_seed_corpus.py`, isolated `security_repository` fixture | SATISFIED |
| R9 language neutrality | language rule only in `DocumentQuery.matches`; no `ml` branch in code | `test_eligibility.py`, `test_local_repository.py` | SATISFIED |
| R10 portability | Protocol exposes no `Path`; parsing in `local.py` / `frontmatter.py`; no S3 code | `test_repository_contract.py` | SATISFIED — an S3 adapter must reuse `compute_content_hash` on the raw mapping (F1) |
| R11 tests | 7 rag test files + core model tests; security fixtures loaded only through an isolated `tmp_path` repository | `make verify` (170) | SATISFIED |

Definition of Done:

| Item | Status |
|---|---|
| typed document model exists | SATISFIED |
| `DocumentRepository` exists | SATISFIED |
| `LocalDocumentRepository` loads the seed corpus | SATISFIED (13 docs, integration tests) |
| manifest/schema validation works | SATISFIED |
| `make validate-knowledge` runs inside `make verify` | SATISFIED (`Makefile` `verify:` target) |
| content hashing works | SATISFIED |
| eligibility filtering works | SATISFIED |
| deterministic tests pass | SATISFIED |
| RAG/application code needs no direct filesystem access for knowledge | SATISFIED (only the local adapter and the `validate` CLI touch paths; `apps/` does not read knowledge) |
| `make verify` passes | SATISFIED |
| `CURRENT_STATE.md` updated | SATISFIED, with stale lines (F5) |

### Protected-data check

`git diff --stat main...spec/002 -- evaluation/ knowledge/ config/` → empty. No seed, evaluation or config file changed on the branch; security fixtures under `tests/fixtures/security/` are unchanged by this branch (their complete metadata predates `spec/002`).

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R7, R10 / T5, T7 | `content_hash` is computed from the raw frontmatter mapping (`local.document_fields` → `compute_content_hash(body, metadata)`), not from validated `KnowledgeDocument` values, and the `YYYY-MM-DD` date check that makes the two agree exists only in `validate-knowledge` (`validate._date_problems`), not in `LocalDocumentRepository`. Carried from T5 F1 / T7 F3 and never closed. Consequences: a document loaded outside `make verify` with `effective_from: 2026-01-01T00:00:00` loads and hashes the raw string; `content_hash` cannot be recomputed from a `KnowledgeDocument`; a future `S3DocumentRepository` must replicate the raw-mapping path exactly. Harmless for the current seed (all dates plain). |
| F2 | MINOR | SPEC_DEFECT | R1, R7 / T1, T5 | The metadata schema and all 13 seed documents carry `persona_scope` (`["guest", "future_authenticated_public_user"]`), but the spec never mentions it. `document_fields` silently drops it (and `schema_version`), so it is neither in `KnowledgeDocument` nor in `content-hash-v1`, and design "Content hashing" lists `schema_version` as excluded but says nothing about `persona_scope`. If persona ever affects retrieval, adding it changes the hash recipe (needs `content-hash-v2`). → `spec-planner`: decide whether `persona_scope` is a model field / hash input or explicitly ignored, and record it in design. |
| F3 | MINOR | IMPLEMENTATION | R6, R8 / T1, T6 | Access scopes and source authorities are hard-coded enums; `GUEST_PUBLIC_POLICY` hard-codes `guest → public`; nothing reads or cross-checks `config/access_policy.yaml` or `config/source_precedence.yaml`, and the JSON Schema types `access_scope` as a plain string. The values agree today, but drift between code and config would go undetected. |
| F4 | MINOR | IMPLEMENTATION | R2, R3, R5 / T3, T4 | `manifest.py` docstring says the manifest lists "one record per document version", but `load_manifest` rejects any repeated `document_id`, so only one version per document can exist. `get_document`'s latest-version selection and `version=` argument are therefore only exercisable through fakes, and the R2 "version increments on approved change" rule is unenforced (no history to compare). Fine for Phase 1, but docs and code disagree. |
| F5 | MINOR | IMPLEMENTATION | DoD / T9 | Docs drift: `ARCHITECTURE.md` "DocumentRepository" still sketches `list_documents(status: str = "active")` instead of `DocumentQuery`; `CURRENT_STATE.md` still says Spec 002 is "on branch `spec/002` (not yet on `main`; merge after T9 approval)" and that the skills are "not yet exercised on real work (dry run is Spec 003 T9)", although the dry run ran on Spec 002 T3. The orchestrator should refresh these at merge. |
| F6 | MINOR | IMPLEMENTATION | R6 / T4, T7 | Two document-validation paths: the loader (`LocalDocumentRepository._build`) reports only the first Pydantic error and no date check; `validate._model_problems` re-reads the file and lists every error plus the date check. Per-document checks added in T7 (outside-root entries, unlisted files, dates, corpus safety) live in the CLI module rather than a reusable validation module (T7 F2). Behaviour is consistent today; ingestion that needs the full checks would have to call the CLI's `validate_knowledge` or duplicate it. |

### Cross-task consistency

- Interfaces agree: every consumer of filters goes through `DocumentQuery.matches` (T8 removed the duplicate in `local.py`); errors are the four design error types plus `ValidationProblem`; no message carries an absolute path (tested in T4, T5, T7).
- Hash contract is stated identically in `design.md`, `hashing.py` docstring and D024.
- Findings were carried forward deliberately between tasks (T3 F2→T4, T4 F2/F3→T7, T6 F1–F3→T8, T3 F1→T9). Not closed: T5 F1 / T7 F3 (F1 here), T7 F1 (some problems hide others), T7 F2 (F6 here), T8 F1 (`from conftest import` fragility).
- `validate._corpus_problems` re-checks the guest-eligible set for properties the policy already guarantees; harmless redundancy.

### Scope-drift review

- No chunking, chunk IDs, embeddings, Qdrant, FTS5, ingestion orchestration, S3 or Phase 2 workflow code.
- Additions beyond the design's package list (`eligibility.py`, `hashing.py`, `frontmatter.py`) are design-described behaviour split into modules, not new scope.
- `DocumentQuery.matches` (public method added in T8, a tests task) is recorded in D024; no Protocol change.
- `validate-knowledge` is broader than "eligible public document must be safe" (any active, retrieval-enabled doc in the public roots must be public/approved/non-synthetic; unlisted files fail). Reported to and approved by the user in T7.
- Spec edits: the only post-approval amendment (T9 DoD item reword, requirements `Status:` re-dated 2026-10-15) has a `## Change log` line. No unrecorded spec edits found.

### Task-review patterns

- Implementer model `claude-sonnet-5-5` on T3–T9; task reviewer `claude-opus-5-5` on every round. T1–T2 predate task review (code read here; no issue found).
- Seven tasks, eight review rounds: T3–T8 PASS in round 1; T9 FAIL in round 1 (MAJOR spec defect inherited from the Spec 003 migration of `tasks.md`, plus stale `CURRENT_STATE.md`), PASS in round 2.
- From T6 on, implementations were left uncommitted for review and committed on approval; worked without incident.
- Recurring MINOR theme: date/hash canonicalisation and "report every problem" completeness.

### Remediation required

- RM tasks: none (all IMPLEMENTATION findings are MINOR; recorded under known issues in `CURRENT_STATE.md`).
- SPEC_DEFECT for `spec-planner`: F2 (`persona_scope` treatment in model and hash contract). Best settled in the next spec that reads `KnowledgeDocument` (ingestion, Spec 004) before its design is approved.

### Notes for the next spec

- **Ingestion (Spec 004) must call `list_eligible_documents(repo, GUEST_PUBLIC_POLICY, …)`,** not `list_documents()`: the bare call returns every stored document, ineligible ones included.
- **Change detection:** use `content_hash` only (D024). It changes on body or retrieval-affecting metadata, not on review dates, release or path. Any change to the hashed field list (e.g. adding `persona_scope`, F2) requires `content-hash-v2` and a full re-index.
- **Date canonicalisation (F1):** if ingestion or any non-`make verify` path loads documents, move the `YYYY-MM-DD` check into the loader or hash from validated model values first.
- **Versions (F4):** the manifest currently holds one version per `document_id`. If ingestion needs version history (previous version for deletes/supersede), the manifest rule and `load_manifest` must change through a spec decision.
- **Authorization config (F3):** when retrieval adds roles or reads the access policy, derive `EligibilityPolicy` from `config/access_policy.yaml` or add a test that the enums and config agree. Fallback retrieval must use the same policy object.
- **Editing knowledge:** any edit to a knowledge file, even whitespace, fails `make verify` until the manifest `sha256`/`body_sha256` are updated. There is no hash-refresh tool yet; consider one (a deterministic script, not a Phase 2 workflow).
- **Test helpers:** tests import constants via `from conftest import …` (T8 F1); move them to a helper module before adding a second `conftest.py`.
- **Workflow lesson:** migrating an in-flight spec to a new workflow left stale checklist text that only surfaced at the last task (T9 FAIL). When the workflow changes, grep in-flight specs for retired statuses at migration time.
- **Merge:** `main` has 3 skill/workflow commits not on `spec/002`; `git merge-tree` shows a clean merge.

### Final handoff

No BLOCKING or MAJOR findings; no RM tasks. Merging `spec/002` into `main` can proceed after the user's go-ahead. Take F2 to `spec-planner`; F1, F3–F6 are recorded as known issues in `CURRENT_STATE.md`.
