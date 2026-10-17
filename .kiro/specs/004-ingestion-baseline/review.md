# 004 — Spec Review (retrospective)

Required end-of-spec retrospective (`agent-skills/spec-reviewer`, D031). Append-only; newest round at the bottom.

## Round 1 — 2026-10-17

- **Spec:** `004-ingestion-baseline`
- **Diff reviewed:** the merged result, not `main...spec/<NNN>`: at the user's request `spec/004` was merged into `main` (merge commit `dde5b35`) before this retrospective. Reviewed `git diff af659da dde5b35` (base `af659da` = branch base; code: `-- . ':!docs'`, plus `docs/`), task commits from `git log --grep "Spec-Task: 004/"` (`93e6227` T1 … `7b6680c` T9), and the non-task commits on the branch (`a3ff8f0`, `1248cd9`, `cfc365f`, `4602094`, `f5a8518`, `b25a6d3`). Working tree at `main` `19dd485`.
- **Reviewer host / model:** Claude Code (subagent, fresh session, did not implement the spec) / `claude-opus-5-5`. Matches the `spec-reviewer` tier BEST = Opus in `agent-skills/MODEL_PREFERENCES.md`; no mismatch.
- **Outcome:** `PASS` (no BLOCKING or MAJOR finding; MINOR findings recorded under known issues in `CURRENT_STATE.md`; docs reconciled)
- **Usage:** 188K tokens · 36 tool uses · 9:05

### Verification run

Environment: optional `bge-m3` extra absent (`find_spec("torch")` and `find_spec("sentence_transformers")` → `None`). Local Docker Qdrant `qdrant/qdrant:v1.19.2` was already running (healthy) with the user's `w2a-realcheck-idx-v1` collections from the pre-merge check; those were left untouched. The real-model smoke test was not run (user-owned; done by the user on 2026-10-17, see `task-reviews.md`).

| Command/check | Result | Notes |
|---|---|---|
| `make verify` | exit 0 | ruff "All checks passed!", pyright 0 errors, skills-check (5 mirrors match), validate-knowledge OK 0 problems, pytest 317 passed, 1 skipped. Qdrant was reachable, so the 2 Docker integration tests ran inside `make test` (they skip when it is not); the skip is the BGE-M3 smoke test |
| `make test-integration` | exit 0 | 15 passed, 303 deselected |
| `QDRANT_COLLECTION_BASE=w2a-retro-throwaway make ingest INGEST_ARGS="--embedder fake"` ×3 | exit 0 each | run 1 `added: 13  updated: 0  unchanged: 0  deleted: 0`; runs 2 and 3 `added: 0  updated: 0  unchanged: 13  deleted: 0` (DoD idempotency) |
| live collection check (REST `GET /collections/w2a-retro-throwaway-idx-v1`) | as designed | 13 points; named vector `dense` size 64 Cosine; keyword payload indexes `access_scope`, `content_language`, `document_id`, `lote_languages`, `tenant_id` (covers open T6 F2 manually) |
| `QDRANT_COLLECTION_BASE=w2a-retro-throwaway make ingest` (default `bge_m3`, extra absent) | exit 2 | `OptionalDependencyError` before any Qdrant call |
| cleanup | done | REST `DELETE` of both `w2a-retro-throwaway-idx-v1*` collections; only the user's `w2a-realcheck-*` collections remain; container left running as found |
| `ruff format --check apps packages tests scripts` | 1 file would be reformatted | `packages/rag/tests/test_content_hash.py` (last changed in Spec 002 T5); not part of `make verify`; see notes |
| `git diff --stat af659da dde5b35 -- evaluation knowledge config experiments tests/fixtures` | only `config/ingestion.yaml` (+17) | see protected-data check |

### Requirements traceability

| Requirement | Implementation evidence | Test/verification evidence | Status |
|---|---|---|---|
| R1 eligible-only target | `service.py` `run()`: `list_eligible_documents(repository, policy)`; `stale = sorted(set(state) - target_ids)` deleted; CLI passes `GUEST_PUBLIC_POLICY`; no `list_documents` in `ingestion/` | `test_service.py` (eligible-only, deprecated/retrieval-disabled/removed deleted, security fixtures and non-public never indexed) | SATISFIED |
| R2 loader date validation | `manifest.py` `DATE_FIELDS` + `date_problems()` inside `check_manifest_documents` (loader and `validate-knowledge`); schema date fields are exactly the three | `test_date_and_policy.py`; `make validate-knowledge` | SATISFIED |
| R3 policy vs config | `test_date_and_policy.py` | passes; the scope check is one-way (T1 F1, open MINOR) | SATISFIED (minor gap) |
| R4 chunker | `chunking.py` `HeadingChunker`, `slugify` (amended rule, change log 2026-10-15) | `test_chunking.py` (20 tests incl. NFC/NFD, truncated heading, seed baseline 13×`main`/0) | SATISFIED |
| R5 embedder + fake | `embedding.py` | `test_embedding.py` | SATISFIED |
| R6 BGE-M3 optional | `bge_m3.py` (lazy import, `find_spec` at construction, revision refusal); `pyproject.toml` `[project.optional-dependencies] bge-m3`; `make setup-bge-m3` | `make verify` without the extra; smoke test skipped here, run by the user (303 passed, 0 skipped) | SATISFIED |
| R7 settings + refusal | `settings.py`, `store.ensure_collection` (companion `-settings` collection, five-row table), `collection_name()` single derivation | `test_store.py`, `test_index_contract.py`, `test_store_integration.py` (Docker); live check above | SATISFIED |
| R8 payload | `payload.py` 17 fields, `IDENTITY_FIELDS` | `test_index_contract.py` (field set, hash-coverage subset, exclusions) | SATISFIED |
| R9 identity + replacement | `identity.py` `INGESTION_NAMESPACE`, `point_id`; `store.replace_document` delete-then-upsert | `test_index_contract.py`, `test_store.py` (3→2 no orphan) | SATISFIED |
| R10 change detection | `service.py` hash/version/point-ID-set classification, embed-then-replace, per-document try/except | `test_service.py` (idempotent second run with 0 embeds/writes, updates, review-date no-op, repair, failure isolation) | SATISFIED (chunking sits outside the per-document try: T7 F1, open MINOR, unreachable with `HeadingChunker`) |
| R11 run summary | `cli.format_summary`, `RunReport`; exit codes 0/1/2 | `test_cli_config.py`; `make ingest` ×3 above | SATISFIED |
| R12 entry point + config | `cli.py`, `config.py`, `config/ingestion.yaml`, `make ingest` | `test_cli_config.py` (config loading, `day1_baseline.yaml` agreement) | SATISFIED |
| R13 test strategy | fake embedder, in-memory Qdrant, `integration` marker with reachability skip, `W2A_RUN_BGE_M3_SMOKE` | `make verify` (no Docker/PyTorch needed), `make test-integration` | SATISFIED |
| R14 decisions + docs | D025–D030; TECH_STACK, COMMANDS, CURRENT_STATE | wording gaps found by T9 review and this round, reconciled below (D032) | SATISFIED after reconciliation |
| DoD: `make verify` without extra | — | exit 0 | SATISFIED |
| DoD: seed ingestion idempotent | — | fake: runs above; real BGE-M3: user's pre-merge check (run 2 added 0 / updated 0 / deleted 0) | SATISFIED |
| DoD: protected paths | — | only `config/ingestion.yaml` | SATISFIED |
| DoD: docs match reality | — | after this round's reconciliation | SATISFIED |

### Protected-data check

`git diff --stat af659da dde5b35 -- evaluation/ knowledge/ config/` → `config/ingestion.yaml | 17 +` only. Required by T8 and allowed by the DoD ("except a new ingestion configuration file if the design places one under `config/`"; design places it there). `experiments/configs/day1_baseline.yaml` and `tests/fixtures/` unchanged. No other protected change.

### Findings

| ID | Severity | Class | Requirement/Task | Finding |
|---|---|---|---|---|
| F1 | MINOR | IMPLEMENTATION | R14 / T9 (Spec 002 retro F4) | D026 says it "closes Spec 002 retrospective F4", but the code half of F4 is still there: `packages/rag/src/way2australia_rag/repositories/manifest.py:3` says the manifest lists "one record per document version", while `check_manifest_documents` (lines 203–212) allows one record per `document_id`. The decision (one version per `document_id`) is made; the docstring is stale. Docs reconciled (D032 says "decides", not "closes"); the docstring fix is a code change for a later spec. |
| F2 | MINOR | IMPLEMENTATION | R14 / T9 | Decision and stack wording did not match the code: D026 names the identity fields "`position`, chunk identity" (code: `document_id`, `document_version`, `section_id`, `chunk_position`); D027, TECH_STACK and CURRENT_STATE call `bge-m3` a "dependency group", but it is a `[project.optional-dependencies]` extra installed with `uv sync --extra bge-m3` (not a PEP 735 `--group`). Resolved in this round by D032 and edits to TECH_STACK/CURRENT_STATE (T9 review F2, F4). |
| F3 | MINOR | IMPLEMENTATION | R14 / T9 | `CURRENT_STATE.md` was out of date: it said Spec 004 is "on branch `spec/004`, not yet merged"; its open-findings list omitted T1 F1 (one-way scope check, `test_date_and_policy.py:67`) and T3 F1 (`pytest.raises(Exception)`, `test_embedding.py:48`); it still listed Spec 002 retro F1–F3 as open although Spec 004 T1 and D025 closed them; it called `spec-reviewer` optional (D031 made it required). Resolved in this round. |
| F4 | MINOR | IMPLEMENTATION | R10 / T7 | Open task-review findings carried forward, none affecting a requirement as written or the DoD: T5 F2 (`max_length` docstring), T6 F2 (no automated payload-index/vector-config assertion; checked manually in this round), T6 F4 (indexes not re-created on the "exists, empty, no settings" row), T7 F1 (chunking outside the per-document try), T7 F2 (duplicate `_index_version`/`index_version`), T7 F3 (no wrong-vector-count test), T7 F5 (security-fixture test does not assert fixtures loaded), T8 round 2 F1 (late `OptionalDependencyError` re-raise untested), T1 F1, T3 F1. No RM task: see "Remediation required". |

No BLOCKING or MAJOR finding. No SPEC_DEFECT.

### Documentation reconciled

| File | Change | Reason |
|---|---|---|
| `docs/project/DECISIONS.md` | new D032 (corrections to D026 and D027 wording; one-version rule "decided", code docstring stale; `bge-m3` is an extra; identity field names) | existing decisions are never rewritten; F1, F2 |
| `docs/project/TECH_STACK.md` | `bge-m3` described as an optional extra (`[project.optional-dependencies]`, `uv sync --extra bge-m3`); embedding device not pinned | F2; user's post-merge observation |
| `docs/project/ARCHITECTURE.md` | new "Ingestion (Phase 1 baseline, Spec 004)" section: components, package placement, data flow, index layout | spec added components and a data flow; ARCHITECTURE had none |
| `docs/project/COMMANDS.md` | `make ingest` options (`--repo-root`, `--config`, `--embedder`) and actual summary lines; `make verify`/`make test` run integration tests when Qdrant is reachable; `UV_HTTP_TIMEOUT` tip for `make setup-bge-m3`; extra wording | describe commands as they behave |
| `docs/project/CURRENT_STATE.md` | Spec 004 merged; retrospective round 1 PASS pending approval; `spec-reviewer` required; extra wording; open-findings list completed; Spec 002 retro items marked closed/decided by Spec 004; retrospective findings and next-spec observations | F3; implemented reality |
| `.kiro/specs/004-ingestion-baseline/design.md` | appended `## As-built notes` | required by the skill; deviations and where each was approved |

Not edited: code, tests, `evaluation/`, `knowledge/`, `config/`, `requirements.md`, `tasks.md`, the approved design text.

### Deviations from the approved plan

| Deviation | Where approved (change log / task-reviews round) or finding ID |
|---|---|
| Slug rule is not "Unicode-aware `\w`": NFKC, `Cf` dropped, `isalnum()`/`M*` word characters; min cap 16; heading truncated in chunk text only | `requirements.md` change log 2026-10-15 (design amended); T2 rounds 2–3 |
| `QdrantIndexStore(client, collection_base, index_version)` refuses settings whose `index_version` differs; `replace_document` takes `IndexPoint` values | T6 round 1 review (accepted) |
| `read_state` reports version 0 / empty hash for a document whose points disagree | T6 round 1 (accepted), tested in T7 |
| Malformed or foreign settings payload → `IndexSettingsMismatchError` (field names only) | T6 F3 → T7 round 1 |
| Missing extra detected at `BgeM3Embedder` construction (`find_spec`); late `OptionalDependencyError` re-raise kept in `service.py` | T8 round 1 user decision, T8 round 2 |
| CLI prints `DocumentRepositoryError` messages; non-ingestion exceptions print class name only; failure reasons class name only for non-`IngestionError` | T7 round 1, T8 round 2 |
| `build_embedder` refuses `bge_m3` with another `model_id` or `normalize: false`; `build_chunker` refuses anything but `heading`/`1`; vector size and batch size below 1 refused | T3, T4, T8 round 1 (accepted) |
| Summary first line also prints `index_version`, and the count line includes `unchanged` | T8 round 1 (accepted; design example was illustrative) |
| `EmbedderInfo.settings` empty for both embedders; `batch_size`/`max_length` not index settings | T4 F2, T5 round 1 |
| `IndexSettings` adds `schema_version` (required by the task text) | T5 round 1 |
| Workflow change (D031, required retrospective) and a ROADMAP note committed on the `spec/004` branch outside any task | user-directed process commits `cfc365f`, `1248cd9`; recorded in D031 and the Spec 003 change log; not product scope |
| Merge before the retrospective, contrary to D031's order | user's explicit request (orchestrator brief for this round); recorded in `CURRENT_STATE.md` |

No unrecorded material deviation.

### Cross-task consistency

- One error family: every ingestion refusal is an `IngestionError` subclass (`errors.py`), mapped to exit 2 by the CLI; repository errors join it at the CLI. Messages carry document IDs, field names and file names only.
- One derivation each: collection name (`settings.collection_name`), point ID (`identity.point_id`), payload (`payload.build_payload`), settings (`settings.build_index_settings`), floating-revision refusal (duplicated as a small constant in `config.py` and `bge_m3.py`; both refuse the same set, acceptable).
- The settings comparison covers every recorded field but `hash_contract`, so a chunker cap or fake/real change is refused (D028), which is what keeps `chunk_text`/`section_id` changes visible without a hash change (design "Payload").
- Tests share in-memory Qdrant and the fake embedder; Docker tests use unique bases and clean up (confirmed: no stray collections).

### Scope-drift review

- No retrieval, query path, BM25/sparse vectors, reranking, generation, evaluation runs, `embedder_is_fake` enforcement, hash-refresh script, version history, Langfuse, HTTP route or Phase 2 feature.
- No Malayalam-specific code (only a comment in `chunking.py`); `lote_languages` comes from documents.
- Package boundaries: all new code in `packages/rag/.../ingestion/`; depends on `way2australia_core` models, `DocumentRepository` and `EligibilityPolicy`; nothing under `apps/`.
- Security: authorization enforced by selecting eligible documents before anything is embedded; authorization and language fields stored separately for Spec 005 second-line filtering; API key is a `SecretStr` from the environment and never printed; body text is data only.
- Non-task commits (`cfc365f` workflow/D031, `1248cd9` ROADMAP note) are process and planning docs approved by the user, not product scope.

### Task-review patterns

- Implementer `claude-sonnet-5-5`, reviewer `claude-opus-5-5` throughout; no model mismatch. Task usage ~70–115K tokens per role per round.
- Rounds: T2 needed 3 (slug rule became a design amendment), T8 needed 2 (user changes); all others 1. No BLOCKING or MAJOR implementation finding in any task review; the only MAJOR (T2 r1 F1) was an orchestrator `sed` that overwrote `task-reviews.md`, restored from git.
- Recurring: `make format` reformatted the unrelated `packages/rag/tests/test_content_hash.py` in T1, T4, T5, T6, T7, T8 and T8 r2, and implementers reverted it each time. `make verify` does not run `ruff format --check`, so the drift is invisible to the gate.
- Docs drift collected in T9 (four wording nits), confirming that D031's reconciliation step is useful.

### Remediation required

None. Outcome `PASS`; no RM tasks added; `tasks.md` `Status:` unchanged.

Why no MINOR finding gets an RM task: none breaks a requirement as written or the DoD, and each is cheapest to fix in the spec that next touches the code:
- T7 F1 (chunking outside the per-document try) is the strongest candidate, because R10 says one document's failure must not stop the others. `HeadingChunker` has no raising path today, so it cannot happen yet. The chunking spec (roadmap item 7) adds chunkers that can fail (tokenizer, truncation guard), so it must move chunking inside the per-document handler.
- T6 F4 and T6 F2 (payload indexes) matter for Spec 005 filter performance, not correctness: Qdrant filters work without them. Spec 005 should add the server-side assertion and re-ensure indexes.
- The rest are test-tightness or naming nits.

### Notes for the next spec

- **Retrieval (Spec 005):** filter on `access_scope`, `tenant_id` (and `owner_user_id` is null) as a second line of defence, using the same `GUEST_PUBLIC_POLICY` object on every path, fallbacks included. Use the payload indexes the store creates; add the integration assertion on `payload_schema` and the `dense` vector config (T6 F2) and re-ensure indexes on the "exists, empty, no settings" row (T6 F4). Query embedding must use the same embedder as the index; read the companion `-settings` collection and refuse a mismatch the same way ingestion does. `embed_query` exists on both embedders but is not used by ingestion.
- **Evaluation spec:** enforce `embedder_is_fake` (recorded in the settings collection, not enforced). Evaluation cases still have empty `relevant_section_ids`; every seed section is `main`, so section-level metrics are meaningless until documents gain headings (a human-approved `knowledge/` change).
- **Chunking spec (roadmap item 7):** move `self._chunker.chunk(document)` and point-ID computation inside the per-document try (T7 F1); token-based cap and truncation guard are already in ROADMAP; any chunker change needs a new `index_version` (D028).
- **Device pinning (user observation, 2026-10-17):** the real run used `mps` (Apple GPU). `BgeM3Embedder` lets `sentence-transformers` choose the device, and the device is not in `IndexSettings`. Vectors from different devices can differ slightly, so if cross-machine reproducibility matters, add a configured `device` and decide whether it is an index setting.
- **`UV_HTTP_TIMEOUT` (user observation):** `make setup-bge-m3` needed `UV_HTTP_TIMEOUT=600` on the user's connection (large PyTorch/CUDA wheels in the lock). Consider `UV_HTTP_TIMEOUT ?= 300` in the `setup-bge-m3` target; COMMANDS.md now documents the workaround.
- **Formatting gate:** `packages/rag/tests/test_content_hash.py` is not `ruff format`-clean, so `make format` keeps touching it. Format it once in a small change and consider adding `ruff format --check` to `make lint`/`make verify`.
- **Stale docstring:** `repositories/manifest.py:3` ("one record per document version") should say one record per `document_id` (F1).
- **Small test gaps to close when the code is next touched:** T1 F1 (assert `named == members`), T3 F1 (`pydantic.ValidationError`), T7 F3, T7 F5, T8 r2 F1.
- **Fake-run trap:** always set `QDRANT_COLLECTION_BASE` for `--embedder fake`; a fake run on the default collection marks `way2australia-idx-v1` as fake (D028).
- **`make verify` and a running Qdrant:** `make test` runs all tests, so with a local Qdrant up the integration tests create and remove temporary `w2a-it-*` collections against it. This is harmless, but agents should know it.

### Final handoff

- Outcome `PASS`. Spec 004 can be marked `verified` once the user approves this round. `spec/004` is already merged (`dde5b35`, user's request), so no merge is pending.
- All changes are uncommitted: this file, `design.md` (As-built notes), `DECISIONS.md` (D032), `TECH_STACK.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `CURRENT_STATE.md`. After approval the orchestrator commits them with `Spec-Review: 004/retrospective`, sets the spec status to verified and fills in the Usage line. Nothing was pushed or merged.
