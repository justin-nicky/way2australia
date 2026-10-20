# 005 — Dense Retrieval Baseline Design

Status: approved (2026-10-20)

Implements `requirements.md` (approved 2026-10-19). Requirement IDs in brackets.

## Design summary

- A new `retrieval/` package in `packages/rag` holds:
  - a read-only `DenseIndex` over the Spec 004 collection;
  - an access resolver and filter builder;
  - a `DenseRetriever`;
  - document-level metric functions;
  - a baseline runner;
  - two CLIs.
- `packages/core` gains `Role` and `AccessContext`.
- Spec 004 code changes in four small, behavior-preserving places:
  - `RuntimeSettings` gains `tenant_id`;
  - embedders expose the device they ran on;
  - the recorded-settings read becomes a public function;
  - `ensure_collection` re-creates payload indexes on one more row [R9].
- Payload, point identity, `IndexSettings` fields, `INGESTION_NAMESPACE` and `index_version` are unchanged, so the existing index stays valid.

Query path (sequence):

```text
server settings (W2A_TENANT_ID) ──► guest_access() ──► AccessContext(guest, tenant)
                                                         │
                                         resolve_access() ──► ResolvedAccess(policy=GUEST_PUBLIC_POLICY, tenant)
                                                         │
config/ingestion.yaml + QDRANT_* ─► DenseIndex.open(embedder.info, index_version)   (read-only binding, R4)
                                                         │
query_text ─► embedder.embed_query ─► DenseIndex.search(vector, build_access_filter(resolved), top_k)
                                                         │
                                  check_hit(payload, resolved) for every hit (fail closed, R3)
                                                         │
                                                  RetrievalResult
```

## Package / file placement

| Path | Content | Req |
|---|---|---|
| `packages/core/src/way2australia_core/access.py` | `Role` StrEnum (`guest`, `staff`, `subscriber`, `registered_user`, `admin`, matching `config/access_policy.yaml` roles), `AccessContext` | R1 |
| `packages/core/src/way2australia_core/__init__.py` | re-export | R1 |
| `packages/rag/src/way2australia_rag/retrieval/__init__.py` | public exports | R5 |
| `retrieval/errors.py` | `RetrievalError` family | all |
| `retrieval/access.py` | `guest_access`, `ResolvedAccess`, `resolve_access`, `build_access_filter`, `check_hit` | R1–R3 |
| `retrieval/index.py` | `DenseIndex` (read-only open, `search`, `document_count`) | R4, R7 |
| `retrieval/models.py` | `RetrievedChunk`, `RetrievalResult` | R5 |
| `retrieval/retriever.py` | `DenseRetriever` | R5 |
| `retrieval/metrics.py` | `dedupe_documents`, `hit_rate_at_k`, `recall_at_k`, `reciprocal_rank`, `random_hit_rate`, `percentile` | R7 |
| `retrieval/goldens.py` | read-only suite + golden-case loader (minimal models) | R8 |
| `retrieval/baseline.py` | `run_baseline()` → `BaselineResult`, JSON writer | R8 |
| `retrieval/cli.py` | `python -m way2australia_rag.retrieval.cli` (one query) | R6 |
| `retrieval/baseline_cli.py` | `python -m way2australia_rag.retrieval.baseline_cli` | R8 |
| `ingestion/config.py` | `RuntimeSettings.tenant_id` (`W2A_TENANT_ID`) | R1 |
| `ingestion/embedding.py`, `ingestion/bge_m3.py` | `device` attribute | R6, R8 |
| `ingestion/store.py` | public `read_index_settings()`; `_ensure_payload_indexes()` | R4, R9 |
| `Makefile` | `retrieve`, `retrieval-baseline`; `lint` adds `ruff format --check`; `UV_HTTP_TIMEOUT ?= 300` | R6, R8, R10 |
| `packages/rag/tests/retrieval/` | unit and integration tests | R11 |
| `packages/core/tests/test_access.py` | `AccessContext` tests | R1 |
| `packages/rag/tests/test_date_and_policy.py` | `named == members` | R10 |
| `packages/rag/tests/test_content_hash.py` | `ruff format` only | R10 |
| `experiments/results/` | baseline JSON results (real one committed by the user's run) | R8 |

Retrieval imports these from `ingestion/` as they are: `Embedder`, `FakeEmbedder`, `BgeM3Embedder`, `IndexSettings`, `collection_name`, `DENSE_VECTOR_NAME`, `SETTINGS_COLLECTION_SUFFIX`, `PointPayload`, `load_ingestion_config`, `RuntimeSettings` and `build_embedder` (from `ingestion/cli.py`). Moving shared index code into its own package is deferred (see Alternatives).

## Components / boundaries

- **`AccessContext` (core):** a frozen Pydantic model with `role: Role` and `tenant_id: str` (stripped, non-blank: empty or whitespace-only is rejected by the model itself). It has no language fields and no scopes: scopes are a rag-side policy decision.
- **`guest_access(settings: RuntimeSettings) -> AccessContext`:** the only constructor used by the CLIs and the baseline. The tenant comes from `settings.tenant_id`.
- **`resolve_access(ctx) -> ResolvedAccess`:**
  - `Role.GUEST` returns `ResolvedAccess(policy=GUEST_PUBLIC_POLICY, tenant_id=ctx.tenant_id)`, with the identical object.
  - Any other role raises `RetrievalConfigurationError("role '<r>' is not implemented")`.
  - This is the only mapping from role to policy.
- **`build_access_filter(resolved) -> models.Filter`:** `must` conditions:
  - `FieldCondition(access_scope, MatchAny(sorted(policy.allowed_access_scopes)))`;
  - `FieldCondition(tenant_id, MatchValue(tenant))`;
  - `IsNullCondition(owner_user_id)`.

  This is the only place an authorization filter is built. A point that lacks `owner_user_id` does not match `is_null`, so it is excluded (fails safe).
- **`check_hit(payload, resolved) -> PointPayload`:**
  - Validates the raw payload as `PointPayload` (`extra="forbid"`).
  - Then requires `AccessScope(payload.access_scope) in resolved.policy.allowed_access_scopes`, `payload.tenant_id == resolved.tenant_id` and `payload.owner_user_id is None`.
  - Any failure raises `RetrievalAuthorizationError` naming `document_id` (when readable) and the failed field names only.
- **`DenseIndex`:** read-only by construction; it calls only `collection_exists`, `get_collection`, `retrieve` (read-only; already used by `read_index_settings`), `query_points` and `scroll`.
  - `DenseIndex.open(client, collection_base, index_version, embedder_info)` performs the R4 checks and returns a bound index holding the recorded `IndexSettings`.
  - `search(vector, query_filter, limit)` runs `query_points(collection, query=vector, using="dense", query_filter=..., limit=..., with_payload=True, with_vectors=False)`.
  - `document_count(query_filter)` scrolls `document_id` only, under the same filter, and returns the distinct count. That count is N for R7, so N counts only documents the caller may see.
- **`DenseRetriever(index, embedder)`:**
  - `retrieve(query_text, access: ResolvedAccess, top_k=5) -> RetrievalResult`.
  - It validates arguments, embeds, searches with `build_access_filter(access)`, applies `check_hit` to every hit, and times embed + search with `time.perf_counter`.
  - It takes a `ResolvedAccess`, never a raw scope list, so callers cannot pass their own scopes.
- **Metrics:** pure functions over `list[str]` ranked document IDs and a `set[str]` of relevant IDs. No I/O.
- **Golden loader:** see Data flow.
- **Baseline runner:** `run_baseline(retriever, access, cases, suite, release_id, top_k, allow_fake, clock)` returns a `BaselineResult`. The CLI writes it.

## Data flow

**Retrieve CLI [R6]:**
1. Parse args.
2. `load_ingestion_config`.
3. `RuntimeSettings()`, which refuses an empty tenant.
4. `build_embedder(config, provider)`, which detects a missing extra before any Qdrant call.
5. Create the client.
6. `DenseIndex.open`.
7. `resolve_access(guest_access(settings))`.
8. `retrieve`.
9. Print the header (collection, `index_version`, embedder @ revision, `fake=`, `device=`) and one line per hit: `rank  document_id  section_id  score  title`.

**Golden loading (read-only) [R8]:**
- `goldens.load_suite(repo_root, suite_path)` reads `evaluation/suites/public-eval-v1.json` into `SuiteRef(evaluation_suite_id, version, datasets)`.
- Each dataset path is resolved under `repo_root` and must stay inside it; a path that escapes `repo_root` is a configuration error.
- Only the dataset with `type == "golden_answerable"` is read, line by line, into a minimal `GoldenCase` with these fields: `case_id`, `case_version`, `query`, `query_language`, `category`, `relevant_document_ids`, `answerable`, `status`, `access_context`. It uses `extra="ignore"`, so new case fields never break the loader.
- Kept: `status == "active"`, `answerable is True`, non-empty `relevant_document_ids`. The count of excluded cases is reported.
- Files are opened read-only and nothing is written under `evaluation/`. `access_context` is loaded only to be ignored: retrieval always uses the server-resolved guest access.
- This loader is a stand-in until Spec 006's suite loader replaces it.

**Declared release [R8]:**
- `--release` defaults to `seed-v1`. The runner reads `knowledge/releases/<id>.json` read-only and requires its `knowledge_release_id` to equal the argument.
- It records `declared_knowledge_release_id`. It does **not** compare the release's document snapshot with the index; the result carries `release_snapshot_verified: false` and a note saying so.

**Baseline run [R8]:**
1. Same setup as the retrieve CLI.
2. If `index.settings.embedder_is_fake` and not `--allow-fake`, refuse with exit 2.
3. N = `index.document_count(build_access_filter(access))`.
4. Warm-up: `retrieve(cases[0].query, …)`. The result is discarded and the wall time is recorded as `warmup_ms`, which includes the model load.
5. For each case: `retrieve`, then `dedupe_documents`, then metrics. Record `latency_ms` from `RetrievalResult` (embed + search only).
6. Aggregate overall and per `query_language` and per `category` (counts and the means of each metric).
7. Latency p50/p95 by nearest-rank over the measured cases only.
8. `random_hit_rate = min(1, top_k / N)`.
9. Write JSON to `--output` (default `experiments/results/retrieval-baseline-<index_version>-<YYYYMMDDTHHMMSSZ>.json`, UTC), creating the directory if needed. An existing file is never overwritten; that is an error.
10. Print a summary: overall HitRate@5 next to the random expectation, Recall@5, MRR, p50/p95, the output file name (relative to `repo_root`) and the notes.

Any exception during the run aborts it with exit 2 and no file is written (all or nothing).

**Device [R6, R8]:**
- `Embedder` gains `device: str | None`.
- `FakeEmbedder.device` is `None`.
- `BgeM3Embedder.device` is `None` until the model loads, then `str(model.device)` (for example `mps`, `cpu`, `cuda:0`).
- It is recorded after the warm-up. It is not configured, not passed to `SentenceTransformer`, and not part of `IndexSettings`.

**`W2A_TENANT_ID` [R1]:**
- `RuntimeSettings.tenant_id: str` has `validation_alias="W2A_TENANT_ID"`, default `"way2australia"`, and a validator that strips it and refuses an empty value.
- `RuntimeSettings()` is built at CLI startup before the client, through one shared settings loader used by the ingestion and retrieval CLIs. It turns a `ValidationError` into a configuration error (`RetrievalConfigurationError` or `IngestionConfigurationError`) naming the environment variables only, never values.
- Ingestion also constructs `RuntimeSettings`, so `make ingest` likewise exits 2 on an empty `W2A_TENANT_ID`. That is acceptable: misconfiguration fails everywhere. Ingestion does not use the tenant.

**Index-store fixes [R9]:**
- `_create_collection`'s index loop moves into `_ensure_payload_indexes()`. It is called on creation and on the "exists, empty, no settings" row before `_write_settings`.
- `create_payload_index` with the same keyword schema is idempotent in Qdrant 1.19; a test confirms that a second call on an existing index does not fail.
- The recorded-match and refusal rows are unchanged. Payload, identity, settings fields and `index_version` are untouched, so `idx-v1` stays valid.
- `_read_settings` becomes the module function `read_index_settings(client, collection) -> IndexSettings | None`, keeping its validation and field-names-only error. The store method delegates to it, and `DenseIndex.open` uses it.

## Interfaces / models

```python
# packages/core/src/way2australia_core/access.py
class Role(StrEnum):
    GUEST = "guest"; STAFF = "staff"; SUBSCRIBER = "subscriber"
    REGISTERED_USER = "registered_user"; ADMIN = "admin"

class AccessContext(BaseModel):          # frozen, extra="forbid"
    role: Role
    tenant_id: str  # stripped, non-blank (validator rejects empty/whitespace)

# retrieval/access.py
@dataclass(frozen=True, slots=True)
class ResolvedAccess:
    policy: EligibilityPolicy
    tenant_id: str

def guest_access(settings: RuntimeSettings) -> AccessContext: ...
def resolve_access(context: AccessContext) -> ResolvedAccess: ...
def build_access_filter(access: ResolvedAccess) -> models.Filter: ...
def check_hit(payload: Mapping[str, object], access: ResolvedAccess) -> PointPayload: ...

# retrieval/models.py  (frozen, extra="forbid")
class RetrievedChunk(BaseModel):
    rank: int; point_id: str; score: float
    document_id: str; document_version: int; section_id: str; chunk_position: int
    title: str; chunk_text: str
    knowledge_domain: str; source_authority: str; source_type: str; source_url: str | None
    content_language: str; lote_languages: list[str]

class RetrievalResult(BaseModel):
    hits: list[RetrievedChunk]
    collection: str; index_version: str
    embedder_model_id: str; embedder_revision: str; embedder_is_fake: bool
    device: str | None; top_k: int; latency_ms: float

# retrieval/retriever.py
MIN_TOP_K, MAX_TOP_K, DEFAULT_TOP_K = 1, 50, 5
class DenseRetriever:
    def __init__(self, index: DenseIndex, embedder: Embedder) -> None: ...
    def retrieve(self, query_text: str, access: ResolvedAccess,
                 top_k: int = DEFAULT_TOP_K) -> RetrievalResult: ...

# retrieval/metrics.py
def dedupe_documents(hits: Sequence[RetrievedChunk]) -> list[str]: ...
def hit_rate_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float: ...
def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float: ...
def reciprocal_rank(ranked: Sequence[str], relevant: set[str]) -> float: ...
def random_hit_rate(k: int, n_documents: int) -> float: ...   # min(1, k/N); N>=1
def percentile(values: Sequence[float], q: float) -> float: ... # nearest-rank
```

`DenseIndex` also exposes `collection`, `index_version` and `settings: IndexSettings`.

`top_k` caps chunk hits. Document metrics use the deduplicated documents within those `top_k` chunks. With one chunk per document today, k chunks are k documents.

Baseline JSON (`schema_version "1.0"`):

```json
{
  "schema_version": "1.0",
  "kind": "retrieval_baseline",
  "created_at": "<UTC ISO-8601>",
  "git_commit": "<sha or null>", "git_dirty": false,
  "evaluation_suite_id": "public-eval-v1", "evaluation_suite_version": 1,
  "declared_knowledge_release_id": "seed-v1", "release_snapshot_verified": false,
  "collection": "way2australia-idx-v1", "index_version": "idx-v1",
  "index_settings": { "...": "full recorded IndexSettings" },
  "retrieval_strategy": "dense", "top_k": 5, "device": "mps",
  "embedder_is_fake": false,
  "case_count": 63, "excluded_case_count": 0, "document_count": 13,
  "random_hit_rate_at_k": 0.3846, "random_hit_rate_formula": "min(1, k/N) = 5/13",
  "metrics": {"overall": {"hit_rate_at_5": 0.0, "recall_at_5": 0.0, "mrr": 0.0, "n": 63},
              "by_query_language": {"en": {}, "mixed": {}},
              "by_category": {"official": {}}},
  "latency_ms": {"p50": 0.0, "p95": 0.0, "warmup_ms": 0.0, "measured_cases": 63},
  "cases": [{"case_id": "g001", "case_version": 1, "query_language": "en", "category": "business",
             "ranked_document_ids": ["..."], "relevant_document_ids": ["..."],
             "hit": true, "recall": 1.0, "reciprocal_rank": 1.0, "latency_ms": 0.0}],
  "notes": ["Top-5 over 13 indexed documents is optimistic; compare HitRate@5 with the random expectation 5/13.",
            "The index was not verified against the declared release's document snapshot.",
            "Model load and the warm-up query are excluded from p50/p95."]
}
```

A fake run adds `"not a quality measurement"` to `notes`. The JSON has no query text, no chunk text, no absolute paths and no secrets.

Query text is left out to keep the result small. Case IDs identify the queries, since `evaluation/` is versioned.

`git_commit` comes from `git rev-parse HEAD` and `git_dirty` from `git status --porcelain` (a subprocess run in `repo_root`). Both are `null` if git is unavailable.

## Error and failure behavior

Error family (`retrieval/errors.py`):
- `RetrievalError`
  - `RetrievalConfigurationError`: bad args, config, environment, unimplemented role, fake index without `--allow-fake`, suite or release problems, output file exists;
  - `IndexBindingError`: R4 refusals;
  - `RetrievalAuthorizationError`: R3.

Reused from ingestion: `IngestionConfigurationError` and `OptionalDependencyError`.

| Condition | Error | Exit (both CLIs) | Qdrant contacted? |
|---|---|---|---|
| bad `--top-k`, empty query | `RetrievalConfigurationError` | 2 | no |
| unreadable/invalid `config/ingestion.yaml` | `IngestionConfigurationError` | 2 | no |
| empty `W2A_TENANT_ID` | `RetrievalConfigurationError` | 2 | no |
| `bge-m3` extra missing | `OptionalDependencyError` | 2 | no |
| non-guest role | `RetrievalConfigurationError` | 2 | no |
| Qdrant unreachable | any client exception → class name only | 2 | attempted |
| collection or settings collection missing | `IndexBindingError` | 2 | yes, read only |
| settings missing/malformed/foreign | `IndexBindingError` (field names only) | 2 | read only |
| `index_version` or embedder field mismatch | `IndexBindingError` naming each field, recorded vs wanted | 2 | read only |
| `dense` vector missing or wrong size | `IndexBindingError` | 2 | read only |
| hit fails re-check | `RetrievalAuthorizationError` (`document_id`, field names) | 2 | read only |
| fake index, baseline without `--allow-fake` | `RetrievalConfigurationError` | 2 | read only |
| suite/dataset/release file missing, invalid, or escaping `repo_root` | `RetrievalConfigurationError` (file name only) | 2 | no |
| output file exists | `RetrievalConfigurationError` | 2 | before writing |
| success, including zero hits | — | 0 | — |

Messages for `RetrievalError` and `IngestionError` are printed: they never contain paths or secrets by contract. Any other exception prints its class name only, as ingestion does.

## Security / authorization

- **Single source of authorization:** authorization comes only from `resolve_access`, which uses the server role and the `W2A_TENANT_ID` setting. Neither CLI has a flag for role, scope or tenant. The golden case's `access_context` is never used.
- **Filter in the query:** the filter is inside the Qdrant query, so unauthorized points never leave Qdrant [R2].
- **Re-check:** `check_hit` independently re-checks every payload against the same policy instance. The ingestion `EligibilityPolicy` decides what is indexed; this is the second line of defense [R3].
- **Shared-policy contract for fallbacks:** `build_access_filter` and `check_hit` take `ResolvedAccess`. A later BM25 or FTS5 fallback receives the same `ResolvedAccess` and must call `check_hit`; recorded in a decision.
- **Language:** language never takes part in authorization. There is no language-specific code.
- **Untrusted data:** `chunk_text` is untrusted data. It is returned, never interpreted, and never printed by either CLI or written to the baseline JSON.
- **Secrets:** the API key remains a `SecretStr`. `httpx` logging stays at WARNING.
- **Read-only:** retrieval is read-only on Qdrant. The baseline is read-only on `evaluation/` and `knowledge/`, and its file writes go only to `experiments/results/` or `--output`.

## Observability

- The CLIs log INFO lines to stderr: collection, `index_version`, case count, N and timings. No query or chunk text appears in logs, except that `make retrieve` echoes nothing beyond the hit lines.
- `RetrievalResult.latency_ms` (embed + search) and the baseline `latency_ms` block, with warm-up excluded.
- The device is recorded per run.
- No Langfuse (roadmap item 11). The result fields (collection, `index_version`, settings, release, suite, commit) are the C14 reproducibility record.

## Testing / evaluation strategy

All unit tests use `FakeEmbedder` and `QdrantClient(":memory:")`, with no Docker and no PyTorch [R11].

| Test file | Covers |
|---|---|
| `packages/core/tests/test_access.py` | `AccessContext` rejects empty tenant; no language fields |
| `retrieval/test_access.py` | guest resolves to the identical `GUEST_PUBLIC_POLICY`; other roles refused; filter derived from policy (a test policy with `{public, staff}` changes the `MatchAny`); `check_hit` passes valid payloads and raises on wrong scope, tenant, non-null owner, malformed payload, with no chunk text in the message |
| `retrieval/test_index.py` | each R4 refusal row (missing collection, missing settings collection, malformed settings, `index_version`, each embedder field incl. fake flag, missing/wrong-size `dense`); `DenseIndex` makes no write calls (spy client); `document_count` under filter |
| `retrieval/test_retriever.py` | ranking order, `top_k` bounds (0, 51, non-int refused; 1 and 50 accepted), empty query refused, result fields, filter always passed (spy), latency recorded |
| `retrieval/test_authorization_isolation.py` | isolated collection with seeded synthetic points: `staff` scope, other tenant, non-null `owner_user_id`, each with the query text as its own chunk text so it is nearest with the fake embedder; never returned. A store that drops the filter makes `retrieve` raise `RetrievalAuthorizationError` |
| `retrieval/test_metrics.py` | hand-built rankings: duplicates, no hits, several relevant documents, MRR 0, `random_hit_rate` cap and `N >= 1`, nearest-rank percentiles |
| `retrieval/test_goldens.py` | loads the real `public-eval-v1` (63 active answerable cases); filtering of inactive/unanswerable/empty-relevant cases in a temporary suite; path escaping `repo_root` refused; file contents unchanged (hash before/after) |
| `retrieval/test_baseline.py` | fake index: refused without `--allow-fake`; with it, JSON in `tmp_path` has every required field, the random expectation, the three notes plus "not a quality measurement", no chunk or query text, no absolute path; warm-up excluded from `measured_cases`; existing output not overwritten |
| `retrieval/test_cli.py` | exit codes per the error table, missing extra exits 2 with no client created, empty `W2A_TENANT_ID` exits 2, no role/scope/tenant flag, output has no API key/paths/bodies |
| `ingestion/test_store.py` (extended) | "exists, empty, no settings" row calls `create_payload_index` for every `KEYWORD_INDEX_FIELDS` entry (spy); `read_index_settings` behaves as before |
| `ingestion/test_store_integration.py` (extended, `integration`) | Docker: `payload_schema` has each keyword index; `dense` size and Cosine; F4 row re-creates indexes; second `create_payload_index` harmless |
| `retrieval/test_retrieval_integration.py` (`integration`) | Docker: fake ingest into a throwaway base, then `retrieve` returns seed `document_id`s; cleanup |
| `test_date_and_policy.py` | `named == members` |

- Gate: `make verify`, now with `ruff format --check`.
- Measurement: the user-owned `make retrieval-baseline` against a real BGE-M3 index, not a gate. Its JSON is committed and summarized in `CURRENT_STATE.md`.

## Phase 2 compatibility / migration

- **New roles:** they extend `resolve_access` with their policies (from `config/access_policy.yaml`-derived server code). The filter builder already handles any scope set. `user_private` will need the owner condition to become `owner_user_id == user`, decided in that spec.
- **Releases:** the declared release ID and `release_snapshot_verified: false` leave room for Phase 2 release verification and atomic index switching without changing the result format (bump `schema_version` if fields change).
- **Spec 006:** reuses `metrics.py` and replaces `goldens.py` with the governed suite loader. The baseline JSON is the comparison point.
- **Spec 007 and later fallbacks:** they take `ResolvedAccess` and call `check_hit`.
- No data migration: the existing `idx-v1` collection is used as is.

## Alternatives / deferred decisions

Resolved at design approval (user, 2026-10-20):
- Because ingestion also builds `RuntimeSettings`, an empty `W2A_TENANT_ID` makes `make ingest` exit 2 as well. Accepted: misconfiguration fails everywhere.
- The random expectation stays `min(1, k/N)`, as R7 specifies. The exact multi-relevant formula is not added, and R7 is not amended.
- Query text is left out of the baseline JSON. Case IDs and the versioned datasets identify the queries.
- `build_embedder` is imported from `ingestion/cli.py` and not moved to a factory module in this spec.

Other alternatives:

- **Shared `index/` package** for embedder, settings and collection naming: deferred. Moving it now would churn Spec 004 imports and tests; revisit when hybrid retrieval adds sparse vectors.
- **Full `IndexSettings` comparison at query time:** rejected, because queries are not chunked and it would couple retrieval to the chunker config.
- **Drop-and-log on re-check failure:** rejected in favor of fail closed, since a failure means an index or filter bug.
- **Async retriever:** deferred to the API spec, which can wrap the synchronous call in a thread pool.
- **Pinning the device or making it an index setting:** deferred; the device is recorded only.
- **Exact random expectation for cases with several relevant documents** (`1 − C(N−r,k)/C(N,k)`): not included. R7 specifies k/N, which understates the random rate for those cases. It could be added later as an extra field.
- **Including query text in the baseline JSON:** left out. Case IDs plus versioned datasets are enough.
- **Importing `build_embedder` from `ingestion/cli.py`:** accepted for now. Moving it to a factory module is a cleanup for the shared-package change.
