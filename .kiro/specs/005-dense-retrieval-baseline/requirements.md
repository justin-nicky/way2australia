# 005 — Dense Retrieval Baseline Requirements

Status: approved (2026-10-20)

## Goal

Retrieve the top-k chunks for a query from the Spec 004 Qdrant dense index, with these guarantees:
- the BGE-M3 query embedder is bound to the index's recorded settings, and any mismatch is refused;
- a server-owned guest/public authorization filter is applied inside the Qdrant query, and every result is re-checked against the same policy;
- the first measurable retrieval baseline is recorded: document-level HitRate@5, Recall@5, MRR and latency on the active golden cases, next to the random-retrieval expectation.

This spec is roadmap item 4 (dense retrieval baseline). It gives the evaluation framework (Spec 006) and hybrid retrieval (Spec 007) a retriever and a baseline to measure against. It also closes Spec 004 open findings T6 F2, T6 F4 and T1 F1, and the formatting-drift and `UV_HTTP_TIMEOUT` observations.

## Dependencies

- Spec 004 — ingestion baseline (verified, merged `dde5b35`): `Embedder` Protocol, `FakeEmbedder`, `BgeM3Embedder`, `IndexSettings`, the `<collection>-settings` companion collection, `collection_name`, the named `dense` vector, the 17-field `PointPayload`, keyword payload indexes, `config/ingestion.yaml`, `RuntimeSettings`.
- Spec 002 — document model and repository (verified): `EligibilityPolicy`, `GUEST_PUBLIC_POLICY`, `AccessScope`.
- Spec 001 — local Qdrant (`qdrant/qdrant:v1.19.2`).
- Evaluation assets, read only: `evaluation/suites/public-eval-v1.json`, `evaluation/datasets/golden_public.jsonl`.
- Spec 004 retrospective: `.kiro/specs/004-ingestion-baseline/review.md` ("Notes for the next spec").
- The real baseline needs `make setup-bge-m3` and a real `make ingest`. That run belongs to the user and is not a gate.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-10-19 (option A for Q1–Q8, plus two additions).

- **Baseline meaning (Q1):**
  - A small baseline runner runs the active golden cases of `public-eval-v1` through the dense retriever.
  - It reports document-level HitRate@5, Recall@5 and MRR, overall and sliced by `query_language` and `category`, plus retrieval latency.
  - It also reports the random-retrieval expectation (k/N document hit rate, for example 5/13) next to HitRate@5.
  - It writes one JSON result to `experiments/results/`.
  - It is not a CI gate. The real BGE-M3 run is user-owned, and its result is committed as the recorded baseline.
  - Spec 006 owns suite governance, `make eval-retrieval` and regression gates.
- **Placement and interface (Q2):**
  - A new `packages/rag/src/way2australia_rag/retrieval/` package reuses the Spec 004 embedder, settings and collection-naming code unchanged.
  - The retrieval interface is synchronous.
  - Retrieval has its own error family.
- **Index binding (Q3):**
  - Retrieval opens the index read-only.
  - It refuses a missing collection, missing or malformed settings, an `index_version` or embedder-identity mismatch (model ID, revision, vector size, normalization, fake flag), and a missing or wrong-size `dense` vector.
  - Chunker settings are not compared.
- **Authorization (Q4):**
  - `AccessContext(role, tenant_id)` lives in `packages/core`.
  - One server-side resolver maps `guest` to `GUEST_PUBLIC_POLICY`.
  - One filter builder turns the policy and the server tenant into the Qdrant filter.
  - Every result is re-checked against the same policy object, and a violation fails closed.
- **Language (Q5):** no language filter or query-language detection. Results carry the language fields so the baseline can be sliced.
- **Result shape (Q6):**
  - `top_k` is a parameter, default 5, bounded 1–50. No new `config/` file.
  - No score threshold.
  - Results are chunk hits, and metrics deduplicate them to documents.
- **Entry points (Q7):** a developer query CLI (`make retrieve`) and the baseline command (`make retrieval-baseline`). No FastAPI route.
- **Spec 004 retrospective items (Q8):**
  - Fixed in this spec:
    - T6 F4: re-create payload indexes on the "exists, empty, no settings" path;
    - T6 F2: integration assertion on payload indexes and the `dense` vector config;
    - format `test_content_hash.py` once and add `ruff format --check` to the lint gate;
    - `UV_HTTP_TIMEOUT` default in `setup-bge-m3`;
    - T1 F1 (user addition): the policy-vs-config scope check becomes two-way.
  - The embedding device is recorded, not pinned.
  - T7 F1 (chunking outside the per-document try) stays with the chunking spec.

## R1 — Access context and server-owned authorization policy

A minimal `AccessContext` shall carry the caller's role and tenant. A single server-side resolver shall turn it into the `EligibilityPolicy` used for retrieval.

### Acceptance criteria

- `AccessContext` lives in `packages/core` and has at least `role` and `tenant_id`. Phase 1 implements only the `guest` role.
- The resolver maps `guest` to `GUEST_PUBLIC_POLICY`; the same object is returned, not a copy. Any role that is not implemented is refused with a retrieval error, never mapped to a default.
- The tenant comes from server-side settings, never from a query, a document payload or an LLM. It is the environment setting `W2A_TENANT_ID` on `RuntimeSettings` (default `way2australia`), read once at startup and never set per request.
- An empty or whitespace-only `W2A_TENANT_ID` is refused at startup with a configuration error (exit 2), before any Qdrant call.
- Language fields never feature in the access context or the policy.
- Unit tests cover guest resolution, refusal of unimplemented roles, and that query text cannot change the resolved policy or tenant.

## R2 — Authorization filter applied during retrieval

A single filter builder shall derive the Qdrant filter from the resolved policy and tenant, and the dense query shall always carry it.

### Acceptance criteria

- The filter requires all three conditions:
  - `access_scope` is in `policy.allowed_access_scopes`;
  - `tenant_id` equals the server tenant;
  - `owner_user_id` is null.
- The filter is built only from the policy object and the server tenant. No other code path builds an authorization filter. A test pins that the filter is derived from the policy, so changing the policy's scopes changes the filter.
- Every Qdrant query issued by retrieval carries the filter. There is no unfiltered query path, and nothing filters results after generation.
- The filter builder and the result re-check take the policy object as input, so later fallback paths (BM25, SQLite FTS5) can enforce the same policy. This is stated in the decision record.
- Isolated test collection: points written directly with `access_scope` `staff`, with another `tenant_id`, or with a non-null `owner_user_id` are never returned, even when they are the nearest vectors. These are synthetic test points, never production data.

## R3 — Fail-closed re-check of results

Every result shall be checked again against the same policy object and tenant before it is returned.

### Acceptance criteria

- A result whose payload fails the re-check raises a retrieval authorization error. Nothing from that query is returned; the bad result is never silently dropped.
- The re-check uses the `EligibilityPolicy` instance the resolver returned, not a second definition of the allowed scopes.
- A test feeds a store that ignores the filter and confirms the re-check raises.
- The error message names `document_id` and field names only, never chunk text.

## R4 — Query embedder bound to the index settings

Retrieval shall open the index read-only and refuse to query when the query embedder does not match the settings recorded with the index.

### Acceptance criteria

- The collection is `collection_name(QDRANT_COLLECTION_BASE, index_version)`, with `index_version` from `config/ingestion.yaml`. The derivation is the same function ingestion uses.
- Retrieval is refused with a configuration or refusal error, and no query runs, when any of these holds:
  - the collection or the companion settings collection is missing;
  - the settings record is missing, malformed or foreign;
  - the recorded `index_version` differs from the configured one;
  - any recorded embedder field differs from the query embedder's `EmbedderInfo`: model ID, revision, vector size, normalization or fake flag;
  - the `dense` named vector is missing or its size differs from the embedder's vector size.
- The refusal names each differing field and never prints values from a malformed record.
- Chunker settings and `hash_contract` are not compared at query time.
- A fake query embedder against a real index, or a real embedder against a fake index, is refused by the fake-flag comparison.
- Retrieval never creates, deletes or modifies a collection, payload index or settings record.
- Unit tests cover each refusal row with in-memory Qdrant and the fake embedder.

## R5 — Dense top-k retrieval

The retriever shall embed the query with the bound embedder and return the top-k chunks by dense similarity, under the R2 filter.

### Acceptance criteria

- Interface: `retrieve(query_text, access, top_k)` returns a `RetrievalResult`. It lives in `packages/rag/src/way2australia_rag/retrieval/` and is synchronous.
- `top_k` defaults to 5 and must be an integer from 1 to 50; anything else is refused. An empty or whitespace-only query is refused.
- Results are ranked by descending score. Each hit carries:
  - point ID and score;
  - `document_id`, `document_version`, `section_id`, `chunk_position`;
  - `chunk_text`, `title`;
  - `knowledge_domain`, `source_authority`, `source_type`, `source_url`;
  - `content_language`, `lote_languages`.
- The result also records the collection, `index_version`, embedder model ID and revision, the fake flag, `top_k`, and retrieval latency in milliseconds.
- There is no score threshold and no answerability decision.
- Language and authorization stay separate: no language filter is applied, language fields never widen or narrow access, and there is no language-specific (for example Malayalam-specific) code.
- Retrieved `chunk_text` is untrusted data. Retrieval never interprets or executes it.
- Unit tests with the fake embedder and in-memory Qdrant cover ranking, `top_k` bounds, result fields and the filter being present.

## R6 — Developer query command

A developer CLI shall run one query against the index.

### Acceptance criteria

- `make retrieve QUERY="..."` runs `python -m way2australia_rag.retrieval.cli`. Options: `--top-k`, `--embedder fake`, `--config`.
- Output:
  - the collection, `index_version`, embedder identity, fake flag and the device actually used, when known;
  - per hit: rank, `document_id`, `section_id`, score and title.
- Output never contains absolute paths, the API key or full document bodies.
- Exit codes: `0` success (including zero hits); `2` for refusal or configuration errors, including an index mismatch, a missing `bge-m3` extra, unreachable Qdrant or an invalid argument. A missing extra is detected before any Qdrant call.
- The role is always `guest` and the tenant comes from server settings. The CLI has no flag that changes role, scope or tenant.

## R7 — Document-level retrieval metrics

Metric functions shall compute document-level retrieval quality from ranked hits and the evaluation case's `relevant_document_ids`.

### Acceptance criteria

- Ranked chunk hits are deduplicated to documents, keeping each document's first rank.
- Metrics at k (default 5):
  - HitRate@k: at least one relevant document in the top k;
  - Recall@k: the fraction of relevant documents found in the top k;
  - MRR: reciprocal rank of the first relevant document, 0 if none.
- The random-retrieval expectation for document hit rate is computed from k and N, where N is the number of distinct documents in the index. It is reported as k/N, for example 5/13, capped at 1.
- No metric uses chunk IDs, point IDs or `section_id`. Goldens stay bound to `document_id` (C13).
- Unit tests check each metric against hand-built rankings, including duplicates, no hits and multiple relevant documents.

## R8 — Retrieval baseline command and recorded result

A baseline command shall run the active golden cases through the retriever and write one reproducible JSON result.

### Acceptance criteria

- `make retrieval-baseline` reads `evaluation/suites/public-eval-v1.json` and its golden dataset read-only. It uses only active, answerable golden cases with `relevant_document_ids`. Unanswerable and security datasets are not run.
- Each case is retrieved with the role and tenant resolved by R1. The case's own `access_context` never widens access.
- The JSON result records:
  - the git commit;
  - Evaluation Suite ID and version;
  - the declared Knowledge Release ID (`seed-v1`), next to the actual index identity (collection, `index_version` and the recorded `IndexSettings`);
  - the full recorded `IndexSettings` and the collection name;
  - `top_k`, retrieval strategy `dense`, and the device actually used, when known;
  - case count, document count N and the random expectation k/N;
  - HitRate@5, Recall@5 and MRR overall and sliced by `query_language` and `category`;
  - retrieval latency p50 and p95;
  - per-case ranked `document_id`s.
- The runner does not verify that the index matches the declared release's document snapshot, and the result says so in plain text.
- Before timing, the runner performs one unmeasured warm-up query. Model loading is excluded from the p50/p95 latency. If load or warm-up time is reported, it is a separate field.
- The result states in plain text that top-5 over the indexed N documents (13 in the seed corpus) is optimistic. The random expectation is shown next to HitRate@5.
- The result is written under `experiments/results/`. It contains no absolute paths, no API key and no chunk text.
- A fake index is refused unless `--allow-fake` is passed. With it, the result is labelled `embedder_is_fake: true` and "not a quality measurement".
- Exit codes: `0` success; `2` refusal or configuration error.
- The baseline is not a CI gate. One real BGE-M3 result is produced by the user and committed as the recorded baseline. Until then, `CURRENT_STATE.md` says it is pending.

## R9 — Index store hardening (Spec 004 T6 F2, T6 F4)

Ingestion's index store shall re-create missing payload indexes. Integration tests shall assert the server-side index layout.

### Acceptance criteria

- When a collection exists, is empty and has no recorded settings, `ensure_collection` (re)creates the keyword payload indexes before writing settings. Re-creating an existing index is harmless.
- A Docker integration test asserts that the collection's `payload_schema` contains every `KEYWORD_INDEX_FIELDS` entry as keyword, and that the `dense` vector has the expected size and Cosine distance.
- No change to the 17-field payload, point identity, settings fields or `INGESTION_NAMESPACE`. No new `index_version` is required.

## R10 — Quality-gate and setup fixes

Small fixes carried from the Spec 004 retrospective.

### Acceptance criteria

- `packages/rag/tests/test_content_hash.py` is formatted once with `ruff format`, with no behavior change.
- `make lint` (and therefore `make verify`) runs `ruff format --check` on the same paths `make format` formats, and it passes.
- `make setup-bge-m3` sets `UV_HTTP_TIMEOUT ?= 300`, which can be overridden from the environment.
- The policy-vs-config test asserts that the access scopes named in `config/access_policy.yaml` equal the `AccessScope` members (two-way). A new `AccessScope` member without a configuration entry, or the reverse, fails the test.

## R11 — Test strategy

### Acceptance criteria

- `make verify` passes without PyTorch, Docker or a model download, using the fake embedder and in-memory Qdrant.
- Docker Qdrant tests use the `integration` marker, skip when Qdrant is unreachable, use unique throwaway collection bases, and remove what they create.
- Authorization tests (R2, R3) use an isolated test collection. Security fixtures and synthetic points never enter the production collection.
- Tests never write to `knowledge/`, `evaluation/`, `config/`, or to `experiments/results/` outside a temporary directory.

## R12 — Decisions and documentation

### Acceptance criteria

- New decisions (D033 onward) in `DECISIONS.md` cover:
  - `AccessContext` and the resolver;
  - the single filter builder and fail-closed re-check, and that fallbacks reuse the same policy;
  - the query-embedder binding and refusal rules;
  - the baseline result format and its random expectation;
  - device recorded, not pinned.
- `ARCHITECTURE.md` describes the retrieval query flow as built, `COMMANDS.md` documents `make retrieve` and `make retrieval-baseline`, and `TECH_STACK.md` and `CURRENT_STATE.md` reflect implemented reality.
- `CURRENT_STATE.md` records the recorded baseline, or states it is pending the user-owned run.

## Out of scope

- Spec 006 evaluation framework:
  - suite governance;
  - `make eval-retrieval`, refusal and security evaluation runners;
  - regression or CI gates on metrics;
  - section-level metrics and `relevant_section_ids`.
- Any change to evaluation cases (C6), `knowledge/`, `config/` or `evaluation/`. `experiments/configs/day1_baseline.yaml` stays unchanged.
- BM25, sparse vectors, RRF fusion, hybrid retrieval (Spec 007); reranking; query rewriting.
- Language filtering, query-language detection and multilingual retrieval handling (roadmap item 8).
- Score thresholds, answerability, context building and generation.
- FastAPI retrieval route, request limits, Langfuse tracing.
- SQLite FTS5 or BM25 fallback implementation. Only the shared-policy contract is defined here.
- Roles other than `guest`, and scopes other than `public` at runtime; staff, subscriber and private-user retrieval.
- Pinning or configuring the embedding device, or adding the device to `IndexSettings`.
- Chunking changes, including Spec 004 T7 F1, and any change that needs a new `index_version`.
- Other Spec 004 nits not listed in R9/R10: T3 F1, T5 F2, T7 F2/F3/F5, T8 r2 F1, and the `manifest.py` docstring.
- Phase 2 features (S3 repository, Knowledge Release workflow, analytics).

## Definition of Done

- Every requirement R1–R12 is satisfied and traced to at least one approved task.
- `make verify` passes without the `bge-m3` extra, Docker or a model download, and now includes `ruff format --check`.
- `make test-integration` passes against local Qdrant.
- Retrieval never returns a point outside the guest/public policy and the server tenant; this is proven by the isolated-collection tests and the fail-closed re-check test.
- Mismatched query embedders are refused, as proven by tests.
- `make retrieval-baseline --allow-fake`, run on a throwaway fake index, produces a well-formed result with the random expectation and the optimism note.
- The user-owned real BGE-M3 baseline is either committed under `experiments/results/` or recorded as pending in `CURRENT_STATE.md`.
- No changes under `knowledge/`, `evaluation/` or `config/`.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md` and `CURRENT_STATE.md` match the code as built.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T2 | `make test-unit` (`core/tests/test_access.py`, `retrieval/test_access.py`) |
| R2 | T2, T4 | `retrieval/test_access.py`, `retrieval/test_authorization_isolation.py`, `retrieval/test_retriever.py` |
| R3 | T2, T4 | `retrieval/test_access.py`, `retrieval/test_authorization_isolation.py` (filter-dropping store raises) |
| R4 | T3 | `retrieval/test_index.py` (each refusal row, no writes) |
| R5 | T4, T5 | `retrieval/test_retriever.py`; `make test-integration` (`test_retrieval_integration.py`) |
| R6 | T5 | `retrieval/test_cli.py`; throwaway fake `make retrieve` |
| R7 | T6 | `retrieval/test_metrics.py` |
| R8 | T6 | `retrieval/test_goldens.py`, `retrieval/test_baseline.py`; throwaway fake `make retrieval-baseline --allow-fake` |
| R9 | T1 | `ingestion/test_store.py`; `make test-integration` (`test_store_integration.py`) |
| R10 | T1 | `make lint` (format check), `test_date_and_policy.py`, `make -n setup-bge-m3` |
| R11 | T1–T6 | `make verify` without Docker/PyTorch; `make test-integration` |
| R12 | T7 | doc review against code; `git diff --stat main -- knowledge evaluation config` |
| Definition of Done | T7 | `make verify`, `make test-integration`, fake CLI runs, protected-path diff |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-10-20 — R4/T3: design.md `DenseIndex` may also call the read-only `retrieve` (already used by `read_index_settings`), so the T3 no-writes spy test matches the design. No requirement text changed; no task re-opened.
