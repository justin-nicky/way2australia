# 004 — Ingestion Baseline Design

Status: approved (2026-10-15)

## Design summary

A batch pipeline computes the **target state** (the eligible documents), reads the **current state** from Qdrant payloads, and applies the difference.

```text
config/ingestion.yaml + env settings
        │
        ▼
list_eligible_documents(repo, GUEST_PUBLIC_POLICY)  ──► target documents
        │                                                   │
        │             Chunker (pure)  ──► expected chunks + point IDs
        │                                                   │
QdrantIndexStore.read_state()  ──► {document_id: version, hash, point IDs}
        │                                                   │
        └──────────────► plan: added / updated / unchanged / deleted
                                         │
          Embedder (embed first) ──► delete document points ──► upsert new points
                                         │
                                  run summary + exit code
```

- The index is derived. Documents stay the source of truth; Qdrant records what was indexed (R10). There is no separate state store.
- Everything index-defining (embedder, revision, chunker, size cap, index version) lives in a versioned config file. Everything environment-specific (Qdrant URL, collection base name, API key) lives in environment settings.
- Chunker and embedder are Protocols. The service depends on the Protocols, `DocumentRepository`, and a thin `QdrantIndexStore`, never on concrete classes or file paths.
- No HTTP route, no retrieval, no sparse vectors, no evaluation.

## Package / file placement

New code is reusable RAG capability, so it lives under `packages/rag/` (AGENTS.md: application vs RAG). It contains no business knowledge and no Malayalam-specific behavior.

```text
packages/rag/src/way2australia_rag/ingestion/
├── __init__.py
├── config.py        # IngestionConfig (file) + RuntimeSettings (env), loaders
├── chunking.py      # Chunk, Chunker Protocol, HeadingChunker, slugging
├── embedding.py     # EmbedderInfo, Embedder Protocol, FakeEmbedder
├── bge_m3.py        # BgeM3Embedder (lazy heavy imports; optional group)
├── identity.py      # UUID namespace constant, point_id()
├── payload.py       # PointPayload model, build_payload(), IDENTITY_FIELDS
├── settings.py      # IndexSettings model, compare(), refusal text
├── store.py         # QdrantIndexStore (collection, settings, state, upsert, delete)
├── service.py       # IngestionService.run() -> RunReport
├── errors.py        # IngestionError hierarchy
└── cli.py           # python -m way2australia_rag.ingestion.cli

config/ingestion.yaml                      # index-defining configuration (new)
packages/rag/tests/ingestion/              # unit + integration tests
```

- `Makefile` gains `ingest` and `setup-bge-m3`.
- `packages/rag/pyproject.toml` gains `qdrant-client` and `pydantic-settings` as dependencies and a `bge-m3` optional group.
- Repository changes (R2, R3): date validation in `repositories/local.py`/`manifest.py`; the policy-vs-config test in `packages/rag/tests/`.

## Components / boundaries

### Hardening (R2, R3)

- **Dates:** the loader parses every date field (`last_reviewed_at`, `effective_from`, `effective_to`, any other date field the metadata schema defines) with a strict `YYYY-MM-DD` check, sharing one helper with `validate.py` so the two cannot diverge. Errors name document and field and carry no absolute path.
- **Policy vs configuration:** a test loads `config/access_policy.yaml`, asserts `roles.guest.allowed_scopes == ["public"]`, equals the scopes in `GUEST_PUBLIC_POLICY`, and that every scope named anywhere in the file is a member of the `AccessScope` enum.

### Chunker (R4)

```python
class Chunk(BaseModel):  # frozen
    section_id: str
    position: int      # 0-based piece index within the section
    text: str

class Chunker(Protocol):
    name: str
    version: str
    max_chunk_chars: int
    def chunk(self, document: KnowledgeDocument) -> list[Chunk]: ...
```

`HeadingChunker` (name `heading`, version `1`):

1. Parse ATX headings (`#` to `######`) outside fenced code blocks.
2. Text before the first heading, or the whole body when there are no headings, is the section `main`.
3. `section_id` is the slug of the full heading text (never of the possibly truncated chunk text, see 6). Slug rule (`slugify`):
   1. Unicode NFKC, then lower-case. NFKC includes canonical composition, so NFC and NFD forms of the same heading give the same slug.
   2. Drop every character of Unicode category `Cf` (format: ZWJ, ZWNJ, zero-width space, BOM, …) before the word pass, so they never split a word.
   3. Word characters are those where `str.isalnum()` is true or whose Unicode category is `M*` (combining marks). Regex `\w` is not used: it splits Indic words at vowel signs.
   4. Each run of other characters becomes one `-`; leading and trailing `-` are trimmed.
   5. An empty slug falls back to `section`.
   Non-Latin headings keep their letters and marks; there is no script-specific code.
4. Heading level and nesting are not part of the ID (leaf heading text only).
5. If two headings in one document produce the same slug, the later ones get `-2`, `-3`, … in document order. This is the only positional element in an ID and exists solely to keep IDs unique. A suffix already taken by an earlier ID (including a heading whose literal slug is e.g. `foo-2`) is skipped, so the next free number is used; a later heading whose own slug is already taken gets a suffix the same way. When the document has a non-empty preamble, `main` is reserved, so a heading slugging to `main` becomes `main-2`. Documents without duplicate headings, including all seed documents, are unaffected.
6. A section longer than `max_chunk_chars` is split on paragraph boundaries, then on whitespace (a single word longer than the budget is hard-split), so no piece exceeds the cap. Every piece keeps the section's `section_id`; `position` is the piece index. Each piece's text starts with its heading line for embedding context. `max_chunk_chars` must be at least 16; a smaller cap is rejected with `IngestionConfigurationError`. A heading line longer than half the cap is truncated to `max_chunk_chars // 2` characters in the chunk text only, never in `section_id`, so the body budget stays at least 1.
7. Output is deterministic and pure: no I/O, no clock, no randomness.

The size cap is measured in characters because token counting would couple the chunker to a tokenizer. It is part of the recorded chunker settings.

**Seed reality:** none of the 13 seed documents has headings and all are 83–248 words, so today the baseline yields one chunk per document with `section_id` `main` and `position` 0. Heading behavior is therefore tested on synthetic documents, and the baseline is not evidence that heading chunking works. No headings are added to `knowledge/`.

### Embedder (R5, R6)

```python
class EmbedderInfo(BaseModel):  # frozen
    model_id: str
    revision: str
    vector_size: int
    normalize: bool
    is_fake: bool
    settings: dict[str, str | int | float | bool]   # e.g. batch_size, max_length

class Embedder(Protocol):
    info: EmbedderInfo
    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...
    def embed_query(self, text: str) -> list[float]: ...
```

- **`FakeEmbedder`:** model ID `fake-hash-embedder`, revision `1`, configurable vector size (default 64), `is_fake = True`. Vectors derive from SHA-256 of the text expanded to the vector size and L2-normalized, so equal text gives equal vectors with no model.
- **`BgeM3Embedder`:** model ID `BAAI/bge-m3`, vector size 1024, dense-only, normalized. Built on `sentence-transformers`.
  - **Revision pin:** the revision is a full commit SHA in `config/ingestion.yaml`, passed to the loader as `revision=`. The adapter refuses a missing revision, `main` or `latest`. Task T4 resolves the SHA from the model hub and records it; this design does not invent one.
  - **Load once:** the model is created lazily on the first call and cached on the instance. Batch size comes from the config and `embed_documents` encodes in batches.
  - **Optional dependency and Pyright:** `sentence-transformers` (which brings PyTorch) is imported only inside the loader method, with a targeted `# pyright: ignore[reportMissingImports]` on that import. The module imports cleanly without the group, so `make verify` passes without it. Selecting the adapter without the group raises `OptionalDependencyError` naming `make setup-bge-m3`.
  - **Install:** `make setup-bge-m3` runs the same `uv sync` as `make setup` plus the `bge-m3` extra. Because `uv sync` removes packages not requested, `make setup` removes the group again; the Makefile target and `COMMANDS.md` say to use `make setup-bge-m3` when working with real embeddings.
  - **Smoke test:** runs only when `W2A_RUN_BGE_M3_SMOKE=1` and the group is installed; otherwise pytest reports "skipped" with that reason.

### Index settings (R7)

```python
class IndexSettings(BaseModel):  # frozen, schema_version "1.0"
    index_version: str
    embedder_model_id: str
    embedder_revision: str
    embedder_vector_size: int
    embedder_normalize: bool
    embedder_is_fake: bool
    chunker_name: str
    chunker_version: str
    chunker_max_chunk_chars: int
    hash_contract: str       # recorded, never compared
```

`compare(recorded, wanted)` returns the list of differing fields, ignoring `hash_contract`. Any difference means refusal.

**Storage (works in both in-memory mode and Docker Qdrant):** a companion collection `<collection>-settings` holds exactly one point (fixed ID, a 1-dimensional dummy vector, the settings as payload). Reasons for this choice:

- Collection-level metadata depends on the Qdrant and client versions and on in-memory mode; the companion collection depends on neither.
- A reserved point inside the main collection would be returned by dense search unless every retrieval filtered it out; a separate collection can never appear in retrieval results.
- It is created and removed together with the main collection by the same code path.

**Collection name:** `<collection_base>-<index_version>`, derived in one place from `RuntimeSettings.collection_base` and `IngestionConfig.index_version`. The recorded `index_version` is therefore always consistent with the name.

**Startup check (`ensure_collection`):**

| Collection | Settings point | Action |
|---|---|---|
| absent | absent | create both, write settings |
| exists | present, equal | proceed |
| exists | present, differs | refuse (`IndexSettingsMismatchError`) listing each differing field |
| exists, non-empty | absent | refuse (unknown provenance) |
| exists, empty | absent | write settings, proceed |

The refusal message says: build a new index by setting `index_version` to a new label in `config/ingestion.yaml`; the existing collection is left untouched and is never deleted by ingestion.

A change of `hash_contract` is not a mismatch. It makes every document's `content_hash` differ, so ordinary change detection re-indexes everything (R10).

### Payload (R8)

Every point carries these fields and nothing else:

| Field | Class | Source |
|---|---|---|
| `tenant_id` | hash-covered | document |
| `access_scope` | hash-covered | document |
| `owner_user_id` | hash-covered | document |
| `language_scope` | hash-covered | document |
| `lote_languages` | hash-covered | document |
| `content_language` | hash-covered | document |
| `title` | hash-covered | document |
| `knowledge_domain` | hash-covered | document |
| `source_authority` | hash-covered | document |
| `source_type` | hash-covered | document |
| `source_url` | hash-covered | document (needed for citations) |
| `chunk_text` | derived from body, which the hash covers | chunker |
| `content_hash` | the hash itself | document |
| `document_id` | identity, compared directly | document |
| `document_version` | identity, compared directly | document |
| `section_id` | identity, compared directly | chunker |
| `chunk_position` | identity, compared directly | chunker |

Rules:

- **Rule:** every non-identity payload field is covered by `content_hash`; identity fields are compared directly. A unit test asserts that the non-identity payload field set is a subset of `CONTENT_HASH_METADATA_FIELDS` plus the body-derived `chunk_text` and `content_hash`, so a field added to the payload without hash coverage fails the build.
- **Left out on purpose:** `persona_scope` (decision D-log; not loaded, not hashed) and `last_reviewed_at` (the hash excludes it, so a review-date change must not require a re-index). Also left out: `introduced_in_release`, `approval_status`, `lifecycle_status`, `retrieval_enabled`, `synthetic` and the effective dates, because only documents that pass eligibility are indexed and the eligibility policy, not payload filtering, owns those checks.
- **Authorization data is present even though only guest-eligible documents are indexed.** Retrieval (Spec 005) filters on `access_scope`, `tenant_id` and `owner_user_id` as a second line of defence, so staff or subscriber scopes need no schema change. `lote_languages` and `content_language` are the fields the multilingual spec (item 8) filters on. Authorization and language fields remain separate (AGENTS.md).
- **Changes that cannot be seen by change detection:** `chunk_text` and `section_id` can change without a `content_hash` change only if the chunker changes, and a chunker name, version or size-cap change is refused by the settings check (R7), so the rebuild path is explicit.
- **Payload indexes:** the store creates keyword payload indexes on `access_scope`, `tenant_id`, `document_id`, `content_language` and `lote_languages` so Spec 005 filters are efficient. This is a no-op in in-memory mode.

### Point identity (R9)

```python
INGESTION_NAMESPACE = uuid.UUID("…")   # fixed, generated once, documented in identity.py and DECISIONS.md

def point_id(document_id: str, section_id: str, position: int) -> str:
    return str(uuid.uuid5(INGESTION_NAMESPACE, f"{document_id}\x1f{section_id}\x1f{position}"))
```

The namespace value is generated once during T5 and then never changes. The unit-separator joins fields unambiguously.

### Store (R7, R9, R10)

`QdrantIndexStore` wraps `qdrant_client.QdrantClient` (sync; the batch job gains nothing from the async client) and exposes only:

- `ensure_collection(settings) -> None`
- `read_state() -> dict[str, IndexedDocument]`, where `IndexedDocument` holds `document_version`, `content_hash` and the set of point IDs. It scrolls payloads only (no vectors), restricted to the identity fields and `content_hash`.
- `replace_document(document_id, points)`: delete all points whose `document_id` matches (payload filter), then upsert `points` in one call.
- `delete_documents(document_ids)`.

The named vector is `dense`, so a sparse vector can be added later without recreating points.

### Service (R1, R10, R11)

`IngestionService(repository, policy, chunker, embedder, store, batch_size)` is async because `DocumentRepository` is.

1. `settings = build_index_settings(config, embedder.info, chunker)`; `store.ensure_collection(settings)`.
2. `target = await list_eligible_documents(repository, policy)`.
3. `state = store.read_state()`.
4. **Deletions:** every `document_id` in `state` that is not in `target` is deleted. This one rule covers deprecated, retrieval-disabled and removed documents.
5. **Classification** per target document: chunk it (pure and cheap), compute the expected point IDs, then:
   - not in `state` → **added**;
   - `content_hash` or `document_version` differs, or the set of indexed point IDs differs from the expected set → **updated**;
   - otherwise **unchanged**.
   The point-ID-set comparison is what lets a half-restored document (R10) be detected and repaired even when its hash and version still match.
6. **Execution** per added/updated document, in its own try/except:
   1. embed all its chunks (`embed_documents`, in config batch size);
   2. `store.replace_document(...)`: delete the document's points, then upsert the new ones in a single call.
   If embedding fails, nothing in the index changes for that document. If delete or upsert fails, the document may be absent; the next run sees it as added and restores it. The failure is recorded, other documents continue.
7. Return `RunReport(index_version, collection, embedder_model_id, embedder_is_fake, added, updated, unchanged, deleted, failures)` where the first four are lists of `document_id`s.

**Replacement gap (accepted for Phase 1):** between the delete and the upsert, a document has no points. This is acceptable for an offline batch run. Atomic switching of an entire index belongs to the Phase 2 release workflow.

### Entry point (R11, R12)

`python -m way2australia_rag.ingestion.cli` (run through `make ingest`):

- Options: `--repo-root`, `--config` (default `config/ingestion.yaml`), `--embedder {bge_m3,fake}` (default from config).
- Prints the summary, for example:
  ```text
  index: way2australia-idx-v1 (embedder BAAI/bge-m3 @ <revision>, fake=false)
  added: 13  updated: 0  unchanged: 0  deleted: 0
  ```
  with the `document_id`s listed per category, and `ERROR <document_id>: <reason>` lines for failures. No absolute paths, no document text.
- Exit codes: `0` success; `1` one or more document failures; `2` refusal or configuration error (settings mismatch, missing optional group, Qdrant unreachable, bad config).

## Data flow

1. CLI loads `RuntimeSettings` (environment) and `IngestionConfig` (file) and builds repository, chunker, embedder, store.
2. `ensure_collection` creates the collection or validates recorded settings.
3. Eligible documents come from `list_eligible_documents`. Nothing else reaches the index.
4. Current state is read back from Qdrant payloads.
5. The plan is computed from `content_hash`, `document_version` and point-ID sets.
6. Changed documents are embedded, then replaced; non-eligible documents are deleted.
7. The summary is printed; the exit code reflects failures.

## Interfaces / models

Public contracts are those in "Components" above: `Chunker`/`Chunk`, `Embedder`/`EmbedderInfo`, `IndexSettings`, `PointPayload`, `point_id`, `QdrantIndexStore`, `IngestionService`, `RunReport`. All models are frozen Pydantic models; behavior contracts are `Protocol`s (AGENTS.md: plain Python, Pydantic and `Protocol`).

### Configuration (R12)

`config/ingestion.yaml` (versioned, reviewed like other config):

```yaml
schema_version: "1.0"
index_version: "idx-v1"
embedder:
  provider: bge_m3              # bge_m3 | fake
  model_id: BAAI/bge-m3
  revision: "<full commit SHA, resolved in T4>"
  batch_size: 16
  normalize: true
  fake_vector_size: 64
chunker:
  name: heading
  version: "1"
  max_chunk_chars: 2000
```

`RuntimeSettings` (Pydantic Settings, environment and `.env`, never committed):

| Setting | Env var | Default |
|---|---|---|
| Qdrant URL | `QDRANT_URL` | `http://localhost:6333` (`:memory:` allowed for tests) |
| Qdrant API key | `QDRANT_API_KEY` | none (secret, environment only) |
| Collection base name | `QDRANT_COLLECTION_BASE` | `way2australia` |

Collection name = `<QDRANT_COLLECTION_BASE>-<index_version>` (single derivation, R7).

**Reconciliation with `experiments/configs/day1_baseline.yaml`:**

| Value | `day1_baseline.yaml` | `config/ingestion.yaml` | Handling |
|---|---|---|---|
| Embedding model | `BAAI/bge-m3` | `BAAI/bge-m3` | must agree; a test enforces it |
| Corpus manifest | `knowledge/manifest/document_manifest.jsonl` | the local repository's manifest | a test checks the path is the repository's manifest path |
| Required access scope | `public` | `GUEST_PUBLIC_POLICY` | a test checks agreement |
| Chunking | recursive, 600/60 tokens | heading, 2000 characters | **diverges deliberately**: that file is roadmap item 7's recursive experiment, so it is left unchanged and the divergence is recorded here and in `DECISIONS.md` |

## Error and failure behavior

| Situation | Behavior |
|---|---|
| Settings differ from the recorded ones | refuse before any write; exit 2; message lists fields and the rebuild path |
| Non-empty collection without settings | refuse; exit 2 |
| Optional embedder group missing | `OptionalDependencyError` naming `make setup-bge-m3`; exit 2 |
| Revision missing, `main` or `latest` | configuration error; exit 2 |
| Qdrant unreachable | error without credentials in the message; exit 2 |
| Embedding fails for a document | old points kept; failure reported; others continue; exit 1 |
| Delete or upsert fails for a document | document may be absent; next run restores it; failure reported; exit 1 |
| Bad date or invalid document | the repository raises while loading; nothing is written; exit 2 |
| Run interrupted | safe to re-run; point-ID-set comparison repairs any half-written document |

Error messages and the summary never contain absolute paths, document text, or the API key.

## Security / authorization

- Ingestion selects documents only through `list_eligible_documents` with `GUEST_PUBLIC_POLICY`. The policy is code-owned; the LLM never creates or modifies it, and no model is involved in ingestion at all.
- Security fixtures, synthetic, non-public and ineligible documents never reach the index; ingestion also deletes any indexed point not in the eligible set.
- The policy is tested against `config/access_policy.yaml` (R3). Fallback retrieval in later specs must use the same policy object.
- Retrieved text is untrusted data. Ingestion treats document bodies as data: no body text is executed, interpolated into commands, or logged.
- Authorization and language metadata are written as separate payload fields.
- The Qdrant API key comes from the environment only and is never logged. No secrets in code, config or fixtures.
- `owner_user_id` is carried in the payload but is `null` for every Phase 1 document; no private-user knowledge is indexed.

## Observability

- Stdout summary (R11) and standard-library logging at INFO for stage boundaries and WARNING/ERROR for failures. Logs use document IDs, never text or paths.
- No Langfuse and no metrics in this spec. The index version label and embedder identity in the summary are the lightweight release identifiers Phase 1 needs.

## Testing / evaluation strategy

Default (`make verify`, no Docker, no PyTorch, no model download):

- **Chunker:** no headings gives `main` and position 0; heading slugs are stable under reordering; duplicate headings get unique IDs; Malayalam and other non-Latin headings slug without special-casing; a long section splits into pieces with the same `section_id` and increasing positions, each within the cap; determinism; headings inside code fences ignored.
- **Fake embedder:** determinism, declared size, normalization, query vs document methods, `is_fake`.
- **Identity:** `point_id` is stable and distinct across section and position; namespace constant pinned by a test.
- **Payload:** field set equals the table; the hash-coverage subset test; `persona_scope` and `last_reviewed_at` absent.
- **Settings:** `compare` ignores `hash_contract`; each other field difference is reported.
- **Store and service** on `QdrantClient(":memory:")` with the fake embedder and temporary repositories:
  - first run adds all eligible documents; second run reports zero added/updated/deleted and makes no embedding calls and no writes (counting wrappers);
  - changed body, changed metadata field and bumped `document_version` each cause an update;
  - a review-date change causes no update;
  - shrinking a document from 3 chunks to 2 leaves no orphan;
  - a document that becomes deprecated, retrieval-disabled or removed from the manifest is deleted;
  - security fixtures and non-public documents never reach the index;
  - embedding failure keeps old points, reports, continues with other documents, and exits non-zero;
  - a document with missing points but a matching hash and version is repaired;
  - settings mismatch (model, revision, vector size, normalization, chunker version, size cap, fake vs real) refuses with no writes; a hash-contract change re-indexes instead of refusing;
  - the settings-storage mechanism works in in-memory mode.
- **Hardening:** bad dates in every date field fail loading; the policy-vs-config test; the day1-baseline embedding-model agreement test.
- **CLI:** exit codes `0`, `1`, `2`; summary contains no absolute paths.

Opt-in, honestly reported as skipped:

- **Docker Qdrant integration** (marker `integration`): the same settings-storage, replace and delete flows against `http://localhost:6333` with a unique temporary collection base that the test removes afterwards. A fixture probes Qdrant and skips with a clear reason when it is unreachable.
- **Real-model smoke test:** `W2A_RUN_BGE_M3_SMOKE=1` only; embeds a Malayalam and an English sentence, checks size 1024 and normalization.

Ingestion of the seed corpus with the fake embedder into in-memory Qdrant is part of the default suite, which makes "13 documents, one chunk each, second run idempotent" a verified fact.

## Phase 2 compatibility / migration

- The service depends on `DocumentRepository`, so `S3DocumentRepository` plugs in unchanged.
- `index_version` is the lightweight Index Version a Knowledge Release will reference; Phase 2 candidate indexes become new collections named after new labels, which is the same rebuild path R7 already defines.
- Atomic publishing and rollback (switching the active collection) are not implemented; the delete-then-insert gap is accepted until then.
- Adding a persona or per-user dimension later means adding the field, its purpose and `content-hash-v2` together; v2 triggers a full re-index through ordinary change detection.
- Staff/subscriber indexing needs no payload schema change because `access_scope`, `tenant_id` and `owner_user_id` are already present.

## Alternatives / deferred decisions

- **Collection-level metadata for settings:** rejected as the primary mechanism because it depends on the Qdrant and client versions and on in-memory mode. The companion collection works everywhere.
- **Reserved settings point in the main collection:** rejected because dense search would return it unless every query filtered it out.
- **Separate state file or database for indexed documents:** rejected; the index is a derived artifact and Qdrant already records what was indexed.
- **`FlagEmbedding` instead of `sentence-transformers`:** deferred. `FlagEmbedding` also exposes BGE-M3 sparse and multi-vector output, but sparse retrieval is planned as BM25 (roadmap item 6) and this spec is dense-only.
- **Token-based size cap:** deferred; it would couple the chunker to a tokenizer. Characters are enough for a baseline.
- **Async Qdrant client:** not needed for a batch job.
- **Recursive, semantic and FAQ-aware chunking, sparse vectors, retrieval, evaluation, fake-index enforcement (flag recorded now, enforced by the evaluation spec), hash-refresh script, version history:** out of scope (see requirements).
