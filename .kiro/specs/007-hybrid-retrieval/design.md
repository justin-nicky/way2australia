# 007 — Hybrid Retrieval Design

Status: approved (2026-10-25)

Implements `requirements.md` (approved 2026-10-25). Requirement IDs in brackets.

## Design summary

- Evaluation data first: a new suite `public-eval-v2` (91 cases) with its own dataset files; v1 datasets untouched, v1 manifest `status: replaced` [R1]. The user records the dense v2 baseline before any lexical code exists [R2].
- A new package `way2australia_rag.lexical` holds the `lexical-v1` tokenizer, the SQLite FTS5 lexical store (build, open, bind) and the `make index-lexical` CLI [R3–R5]. It depends on `ingestion/` (chunker, payload, point identity) and `repositories/`, never on `evaluation/`.
- `retrieval/` gains a `Retriever` Protocol, `BM25Retriever`, a pure `rrf_fuse` function, `HybridRetriever`, one SQL access-clause builder next to `build_access_filter`, and a strategy factory driven by `config/retrieval.yaml` [R6–R8]. `DenseRetriever` and `DenseIndex` keep their behavior.
- Evaluation: the runner takes any `Retriever`; result format 2.1 (additive) [R9]; `eval-compare` gets the R10 identity rules; the security gate runs `dense`, `bm25` and `hybrid` over a throwaway Qdrant collection plus a throwaway lexical file built by the same builders [R11, R12].
- Every leg filters inside its own query and calls `check_hit` before fusion (D035, D040). Fusion never sees an unchecked hit, and any leg error fails the whole query.

## Package / file placement

| Path | Change | Req |
|---|---|---|
| `evaluation/suites/public-eval-v2.json` | new manifest | R1 |
| `evaluation/datasets/v2/golden_public.jsonl`, `unanswerable_public.jsonl`, `security_public.jsonl` | new datasets (69, 12, 10 rows) | R1 |
| `evaluation/suites/public-eval-v1.json` | `status` → `replaced` only | R1 |
| `evaluation/candidates/006-candidates.jsonl` | `review.promoted_as` on 6 rows | R1 |
| `packages/rag/.../evaluation/validate.py` | `promoted_as` transcription check | R1 |
| `packages/rag/.../evaluation/cli.py` | default suite v2; `--strategy`; lexical open/bind | R1, R8 |
| `packages/rag/.../evaluation/retrieval_eval.py` | takes a `Retriever`, records strategy, leg ranks, score kind, leg latency; neutral g004/u001 note | R9 |
| `packages/rag/.../evaluation/results.py`, `compare.py` | read 2.1; R10 identity rules | R9, R10 |
| `packages/rag/.../evaluation/security_index.py`, `security_eval.py` | lexical forbidden rows, per-leg sanity, three strategies, result 1.1 | R11 |
| `packages/rag/.../lexical/__init__.py`, `tokenizer.py`, `store.py`, `build.py`, `cli.py` | new package | R3–R5 |
| `packages/rag/.../retrieval/access.py` | `build_sql_access_clause` | R6 |
| `packages/rag/.../retrieval/base.py` | `Retriever` Protocol, `validate_request` (shared query/top_k checks) | R6–R8 |
| `packages/rag/.../retrieval/bm25.py`, `fusion.py`, `hybrid.py`, `strategy.py` | new | R6–R8 |
| `packages/rag/.../retrieval/models.py` | optional fields with defaults (below) | R7, R9 |
| `packages/rag/.../retrieval/cli.py` | `--strategy`, header and leg ranks | R8 |
| `packages/rag/.../ingestion/config.py` | `RuntimeSettings.lexical_index_dir` (`W2A_LEXICAL_INDEX_DIR`) | R4 |
| `config/retrieval.yaml` | new | R8 |
| `Makefile` | `index-lexical` target (`LEXICAL_ARGS`) | R4 |
| `.gitignore` | `/.local/lexical/` | R4, R14 |
| `packages/rag/tests/lexical/`, `tests/retrieval/`, `tests/evaluation/` | tests | all |

Not changed: `retrieval/metrics.py`, `baseline.py`, `baseline_cli.py`, `retrieval/index.py` search/open logic (a read-only `chunk_identities()` helper is added), `ingestion/` index-defining code, `config/ingestion.yaml`, `knowledge/` [R14].

## Components / boundaries

### R1 — Suite v2

- `public-eval-v2.json`: `evaluation_suite_id: public-eval-v2`, `version: 2`, `status: active`, `introduced_in_release: seed-v1`, `case_count: 91`, datasets under `evaluation/datasets/v2/`, `replaces: {"evaluation_suite_id": "public-eval-v1", "version": 1}` (allowed by `additionalProperties`), notes.
- Copied rows keep v1 key order and JSON style (UTF-8, `ensure_ascii=False`, `", "` / `": "` separators as in v1), with only `evaluation_suite_id` changed. New rows `g064`–`g069` are appended to the v2 golden file in mapping order, in the same key order as the v1 goldens.
- The data is produced by the implementer (a scratch script is allowed, not committed); tests are the proof: field-by-field comparison with v1, the mapping, v1 dataset hashes, v1 manifest differs only in `status`, candidates file differs only in `promoted_as`.
- `validate.py` `_candidate_rules`: if `review.promoted_as` is present, its `suite_id` must name a loaded suite, that suite must hold `case_id`, and the case's `query`, `relevant_document_ids`, `expected_facts`, `query_language` must equal `proposed_case`'s, each mismatch one problem line (field names only, never query text).
- `DEFAULT_SUITE` in `evaluation/cli.py` → v2. `baseline_cli.py` keeps v1 (D046).
- The `_notes` overlap text becomes neutral ("g004 overlaps unanswerable u001; both are active cases."), because the owner decided `keep_both`.

### R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`)

```text
TOKENIZER_NAME = "lexical-v1"; TOKENIZER_VERSION = "1"
tokenize(text) -> list[str]:
  1. unicodedata.normalize("NFC", text)
  2. drop every ZWJ (U+200D) and ZWNJ (U+200C)          ← the one ZWJ/ZWNJ rule
  3. lowercase (str.lower)
  4. token chars: category L*, N*, Mn, Mc; everything else separates
  5. return tokens in text order (duplicates kept)
```

- Step 2 matches D026's `slugify` (which drops `Cf`), so ZWJ/ZWNJ never split a token and never survive into one. Consequence, accepted by the user at design approval and pinned by a test: a legacy chillu sequence (for example `ന` + `്` + ZWJ) becomes consonant + virama (`ന്`), which is **not** equal to the atomic chillu `ൻ`. This is a known issue for roadmap 8 (multilingual retrieval), recorded in `CURRENT_STATE.md` by the docs task; the dense leg is unaffected. No Malayalam mapping table is added (R3 allows only Unicode properties). The corpus and all evaluation queries use atomic chillu letters only (checked: zero ZWJ/ZWNJ, 34 atomic chillu letters in `business_008`, the goldens and the candidates).
- `Mn`/`Mc` as token characters keep vowel signs and the virama attached; `M*` marks at a token start (after a separator) also attach to the following run, which never happens in well-formed text.
- Query side: `query_terms(text) -> QueryTerms(terms, truncated)` = `tokenize`, de-duplicated in first-seen order, at most `MAX_QUERY_TERMS = 64`; later terms are dropped and `truncated` is `True`. The truncation is recorded in the retrieval result (`RetrievalResult.query_terms_truncated`), in each evaluation case row (`query_terms_truncated`) and as a count (`truncated_query_count`), and `make retrieve` prints a note. A test runs a query with more than 64 distinct terms and checks the flag, the count and that exactly the first 64 terms reach `MATCH`. Index side: the full token list, joined by single spaces.
- Tests pin exact token lists for: words from `business_008` and the queries of `g064`–`g069` (for example `എടുത്താൽ`, `കോച്ചിംഗ്`, `ഇന്റർപ്രെറ്റ്`), `dialogue-ൽ` → `dialogue`, `ൽ`, English with punctuation and digits (`₹8,499` → `8`, `499`), NFD input equal to NFC input, the legacy-chillu case, and a grep-style test that the module has no language-code literal.

### R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`)

SQLite file, one per Qdrant collection:

```sql
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);   -- one row 'lexical_settings' (JSON)
CREATE TABLE chunks (
  rowid INTEGER PRIMARY KEY,
  point_id TEXT NOT NULL UNIQUE,
  document_id TEXT NOT NULL, document_version INTEGER NOT NULL, content_hash TEXT NOT NULL,
  access_scope TEXT, tenant_id TEXT, owner_user_id TEXT,
  owner_present INTEGER NOT NULL,       -- 1 if the payload has the owner_user_id key
  payload_json TEXT NOT NULL);          -- the full payload as indexed (for check_hit)
CREATE VIRTUAL TABLE chunk_terms USING fts5(terms, tokenize = 'ascii');   -- rowid = chunks.rowid
```

- The `ascii` FTS5 tokenizer treats every non-ASCII character as a token character, so the space-joined `lexical-v1` tokens are stored intact. (`unicode61` splits Malayalam at vowel signs; verified on SQLite 3.51 and 3.53.)
- `lexical_settings` JSON: `schema_version` `"1.0"`, `kind` `"w2a_lexical_index"`, `collection`, `index_version`, `dense_identity` (a copy of the dense identity the file is built for: `collection`, `index_version`, `embedder_model_id`, `embedder_revision`, taken from `config/ingestion.yaml` and the runtime collection base at build time), `tokenizer_name`, `tokenizer_version`, `fts5_tokenizer` `"ascii"`, `bm25` `{k1: 1.2, b: 0.75}` (FTS5's fixed values, recorded), `chunker_name`, `chunker_version`, `chunker_max_chunk_chars`, `hash_contract`, `chunk_count`, `source_chunk_digest`, `created_at`, `sqlite_version` (informational).
- `source_chunk_digest` = SHA-256 of the sorted lines `point_id\tdocument_id\tdocument_version\tcontent_hash\n`.
- `build_lexical_index(entries, target, identity)`: `entries` are `(point_id, payload: Mapping)` pairs with raw mapping payloads (the security builder needs a payload without `owner_user_id`). Writes `target.with_suffix('.tmp-<uuid>')`, `PRAGMA journal_mode=OFF`, one transaction, closes, `os.replace` onto `target`; any exception removes the temp file and leaves the old file.
- `production_entries(repository, chunker)`: `list_eligible_documents(repository, GUEST_PUBLIC_POLICY)` → `chunker.chunk` → `build_payload` → `point_id(document_id, section_id, chunk_position)`: the same chunks, payloads and IDs ingestion writes to Qdrant. `LocalDocumentRepository(repo_root)` reads only the production manifest, so security fixtures cannot appear.
- Default path: `<lexical_index_dir>/<collection>.sqlite`, where `lexical_index_dir` comes from `W2A_LEXICAL_INDEX_DIR` (default `<repo-root>/.local/lexical`, git-ignored) and `collection = collection_name(QDRANT_COLLECTION_BASE, index_version)`. Printed relative to the repository root when inside it, else as the file name.
- `LexicalIndex.open(path, collection, index_version)`: read-only (`file:...?mode=ro` URI). Refuses missing file, missing/malformed settings, unknown `schema_version` or `kind`, tokenizer name/version ≠ code, `collection` or `index_version` ≠ expected. `LexicalIndexBindingError` (subclass of `IndexBindingError`), messages with field names and values of identity fields only, advice "rebuild the lexical index with `make index-lexical` for this collection and index_version".
- The `dense_identity` copy makes the file self-describing: a later fallback spec can open it and report what it belongs to without Qdrant or the `bge-m3` extra (user decision at design approval; recorded in a D049+ decision by the docs task). In this spec every strategy still binds the dense index (below).
- `LexicalIndex.bind_to(dense: DenseIndex)`: compares `dense_identity` with the bound dense index (collection, `index_version`, embedder model ID and revision from `dense.settings`), chunker fields and `hash_contract` with `dense.settings`, and `source_chunk_digest` with the digest of `dense.chunk_identities()` (a new read-only `scroll` over all points, payload include `document_id`, `document_version`, `content_hash`, no filter, no text). On mismatch: counts of points only in Qdrant, only in the lexical index, and with differing version/hash.
- `LexicalIndex.search(match_expression, where_sql, params, limit)` is the only query method (R6).

### R4 — `make index-lexical` (`lexical/cli.py`)

`python -m way2australia_rag.lexical.cli --repo-root . [--config] [--output]`. Loads `config/ingestion.yaml` and runtime settings, builds `production_entries`, writes the file, prints `lexical index: <shown path> (collection <c>, index_version <v>; lexical-v1; chunks N; digest <first 12 hex>)`. No Qdrant client, no embedder. Exit 0 / 2 (`ERROR <ClassName>: <message>` via `safe_text`; other exceptions class name only).

### R6 — `BM25Retriever` (`retrieval/bm25.py`)

```text
retrieve(query, access, top_k):
  validate_request(query, top_k)                 # same rules and messages as DenseRetriever
  terms = query_terms(query)
  if not terms: return empty result               # MATCH never runs
  match = " OR ".join('"' + t.replace('"', '""') + '"' for t in terms)
  where, params = build_sql_access_clause(access)
  rows = lexical.search(match, where, params, top_k)
  hits = [check_hit(json.loads(row.payload_json), access) ...]   # fail closed
```

- `build_sql_access_clause(access)` in `retrieval/access.py` returns the constant fragment `c.access_scope IN (?, …) AND c.tenant_id = ? AND c.owner_present = 1 AND c.owner_user_id IS NULL` (one `?` per allowed scope, scopes sorted) and the parameters from `access.policy.allowed_access_scopes` and `access.tenant_id`. It and `build_access_filter` are the only authorization builders. `owner_present = 1` makes a payload without `owner_user_id` excluded, like Qdrant's `is_null` (SQL cannot tell a missing value from `NULL` otherwise).
- SQL (constant for a policy):
  `SELECT c.point_id, c.payload_json, bm25(chunk_terms) AS s FROM chunk_terms JOIN chunks c ON c.rowid = chunk_terms.rowid WHERE chunk_terms MATCH ? AND <where> ORDER BY s ASC, c.point_id ASC LIMIT ?`
  The `WHERE` runs before `ORDER BY`/`LIMIT`, so forbidden rows never leave SQLite. Score reported as `-s` (higher is better), `score_kind: "bm25"`.
- Hits are `RetrievedChunk`s built like dense hits; `RetrievalResult` carries the dense index identity it was bound with (collection, index_version, embedder fields) so results stay comparable, `device: None`.

### R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`)

- `rrf_fuse(legs: Mapping[str, Sequence[RetrievedChunk]], k: int, weights: Mapping[str, float]) -> list[FusedHit]`: pure, no I/O. `fused = Σ weights[leg] / (k + rank)`; order by `(-fused, best_rank, point_id)`. `FusedHit` keeps the first-seen chunk (dense leg preferred for the payload copy; both are the same point), fused score and `leg_ranks: dict[str, int | None]`.
- `HybridRetriever(dense: DenseRetriever, bm25: BM25Retriever, fusion: FusionConfig)`: `validate_request`, then dense leg at `depth = fusion.candidate_depth` (50), then BM25 leg at the same depth, sequentially; any exception from either leg propagates (no catch, no single-leg fallback). Fuse, cut to `top_k`, re-rank 1..n, `score_kind: "rrf"`, per-leg latency recorded.
- Empty BM25 leg: `fused = 1/(k + dense_rank)` is strictly decreasing in the dense rank, so the dense order is kept; tested on a pure-`ml` query with zero matching terms and on a query with zero terms.

### R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`)

```yaml
# Retrieval strategy and fusion (Spec 007). Reviewed like other config.
schema_version: "1.0"
default_strategy: dense          # dense | bm25 | hybrid
fusion:
  method: rrf
  k: 60
  weights: {dense: 1.0, bm25: 1.0}
  candidate_depth: 50            # 1..50 (MAX_TOP_K)
```

- `RetrievalConfig` (Pydantic, `extra="forbid"`, `k >= 1`, weights `> 0` with exactly the keys `dense` and `bm25`, `candidate_depth` 1–50, `method` only `rrf`).
- `build_retriever(strategy, dense_index, embedder, lexical, config) -> Retriever` is the only place a strategy name becomes a retriever. `Strategy` is a `StrEnum` (`dense`, `bm25`, `hybrid`); CLI `--strategy` choices come from it.
- `make retrieve` / `eval-retrieval`: all strategies build the configured embedder and open the dense index (so identity, `document_count` and binding are the same for every strategy); `bm25` never calls `embed_query`. Strategies `bm25` and `hybrid` open the lexical index and `bind_to` the dense index.
- `make retrieve` header adds `strategy=<name>`; hybrid hit lines append `dense=<rank|->  bm25=<rank|->`.

### R9 — Result format 2.1

`retrieval_evaluation` `schema_version` `"2.1"` = 2.0 plus:
- `retrieval_strategy` (`dense` | `bm25` | `hybrid`), `score_kind` (`dense_cosine` | `bm25` | `rrf`);
- `fusion`: `{method, k, weights, candidate_depth}` for hybrid, else `null`;
- `lexical_index`: `{label (file name), tokenizer_name, tokenizer_version, source_chunk_digest, chunk_count}` for `bm25`/`hybrid`, else `null`;
- per case `query_terms_truncated` (`null` for `dense`) and overall `truncated_query_count`;
- per case `leg_ranks`: `{"dense": {doc_id: rank|null}, "bm25": {...}}` over the relevant documents (document-level rank after dedupe within each leg), only the legs used; `null` for `dense` runs;
- `latency_ms.legs`: `{leg: {p50, p95}}` for hybrid;
- `unanswerable.score_kind`.

`results.py` supports `(retrieval_baseline, 1.0)`, `(retrieval_evaluation, 2.0)`, `(retrieval_evaluation, 2.1)`; a 1.0/2.0 file reads as strategy `dense`, lexical identity `None`. `source_authority` is compared when both files are ≥ 2.0.

### R10 — `eval-compare` identity rules (`compare.py`)

`ComparableRun.info` gains `retrieval_strategy`, `embedder_model_id`, `embedder_revision`, `lexical` (or `None`). `_refusals` adds, after the existing checks:

| Check | Rule | Message part |
|---|---|---|
| collection | both recorded and different → refuse | `collection changed <base> -> <candidate>` |
| collection | either missing/`null` → not compared; info line `collection not recorded in <file>; compared by index_version only` | — |
| index_version | different → refuse | `index_version changed a -> b` |
| embedder | model ID or revision different → refuse | `embedder changed m@r -> m@r` |
| lexical | both non-`None` and tokenizer name/version or digest different → refuse | `lexical index changed ... -> ...` |
| lexical | one or both `None` → identity line only | — |
| strategy | different → identity line `retrieval_strategy: dense -> hybrid` | — |

New next-step text: "compare runs on the same collection, index_version, embedder and lexical index." Device, `git_commit` and latency stay informational. The committed 1.0 vs 2.0 pair (both `w2a-realcheck-idx-v1`, `idx-v1`, BGE-M3 @ `5617a9f`) passes; a test reads both committed files.

### R11 — Security gate (`security_index.py`, `security_eval.py`)

- `build_security_index` also builds a lexical file `<work_dir>/<collection>.sqlite` via `build_lexical_index`, with entries for exactly the same point IDs as the Qdrant collection:
  - seed chunks: `production_entries(seed_repository, chunker)`;
  - canary chunk and canary probe points: canary payload, terms = the canary text, probe terms = the query's terms;
  - forbidden points per variant per query: the D045 payloads with `chunk_text` = the query's terms repeated 3 times (so BM25 ranks them first; `missing_owner` has no `owner_user_id` key → `owner_present = 0`).
  Then `LexicalIndex.open` + `bind_to(dense)`, exercising the production binding. The file lives in the CLI's `TemporaryDirectory`, removed with it.
- Per query and leg, unfiltered sanity checks: dense as today; lexical `SELECT ... WHERE chunk_terms MATCH ? ORDER BY bm25 LIMIT 1` (harness-only SQL, in `security_eval.py`) must return a forbidden document; otherwise `EvaluationHarnessError` (exit 2). A query with zero `lexical-v1` terms skips the lexical sanity check (the BM25 leg cannot run `MATCH`) and is counted in `bm25_no_term_queries`.
- The gate runs each query through `build_retriever` for `dense`, `bm25`, `hybrid` at `top_k` 50. Violations carry `strategy`.
- Security result `schema_version` `"1.1"`: 1.0 plus `strategies`, `violations[].strategy`, `bm25_no_term_queries`, `index.lexical_rows_per_variant`.

### R12 — Docker test

`test_security_integration.py` gains a parametrized test over the three strategies on a unique `w2a-sectest-<8 hex>` base on Docker Qdrant with the lexical file in `tmp_path`; cleanup in `finally`; skip when Qdrant is unreachable.

## Data flow

```text
make index-lexical:
  ingestion.yaml + env → LocalDocumentRepository → eligible (GUEST_PUBLIC_POLICY)
  → HeadingChunker → build_payload, point_id → tokenize → temp SQLite → os.replace

make eval-retrieval --strategy hybrid:
  args/config/settings → suite (active) → release, authorities, registry → output free
  → embedder (real) → Qdrant client → DenseIndex.open (read-only, real)
  → LexicalIndex.open(path, collection, index_version) → bind_to(dense)
  → resolve_access(guest_access(settings))
  → per case: dense leg  [build_access_filter in query → check_hit]
              bm25 leg   [quoted terms MATCH + build_sql_access_clause in WHERE → check_hit]
              → rrf_fuse (authorized hits only) → top_k → metrics
  → result 2.1 (exclusive write)
```

## Interfaces / models

```python
class Retriever(Protocol):
    strategy: Strategy
    def retrieve(self, query_text: str, access: ResolvedAccess, top_k: int = 5) -> RetrievalResult: ...

# retrieval/models.py, additive fields with defaults (dense output unchanged):
RetrievedChunk.leg_ranks: dict[str, int | None] | None = None
RetrievalResult.strategy: str = "dense"
RetrievalResult.score_kind: str = "dense_cosine"
RetrievalResult.leg_latency_ms: dict[str, float] | None = None
RetrievalResult.lexical: LexicalIdentity | None = None
RetrievalResult.query_terms_truncated: bool | None = None

def build_sql_access_clause(access: ResolvedAccess) -> tuple[str, tuple[str, ...]]: ...
def rrf_fuse(legs, k, weights) -> list[FusedHit]: ...
def tokenize(text: str) -> list[str]: ...
def query_terms(text: str) -> list[str]: ...
def build_lexical_index(entries, target: Path, identity: LexicalIdentityInput) -> LexicalSettings: ...
class LexicalIndex: open(...), bind_to(dense), search(...), settings, label
```

## Error and failure behavior

| Situation | Behavior | Exit (CLIs) |
|---|---|---|
| unknown `--strategy` | argparse error | 2 |
| bad `config/retrieval.yaml` | `RetrievalConfigurationError` naming the field | 2 |
| lexical file missing, malformed, other tokenizer, other collection/index_version | `LexicalIndexBindingError` with rebuild advice, before any query | 2 |
| chunk set or chunker fields differ from Qdrant | `LexicalIndexBindingError` with counts | 2 |
| BM25 or dense hit fails `check_hit` | `RetrievalAuthorizationError`, whole query fails | 2 (retrieve, eval-retrieval); violation exit 1 (eval-security) |
| SQLite error during a query | propagates; class name only printed; no fallback | 2 |
| query with no terms | BM25 leg returns 0 hits; hybrid = dense order | 0 |
| `index-lexical` build failure | temp file removed, old file intact | 2 |
| eval-compare identity mismatch (R10) | `not comparable:` message | 2 |
| `--suite public-eval-v1.json` on eval-retrieval / eval-security | suite not active | 2 |

## Security / authorization

- One policy source: `resolve_access` → `ResolvedAccess`. Two filter renderings from it, side by side in `retrieval/access.py`: `build_access_filter` (Qdrant) and `build_sql_access_clause` (SQLite). A test asserts both cover the same three conditions for the same `ResolvedAccess` (scopes, tenant, owner null and present) and that changing the policy's scopes changes both.
- Every leg filters inside its query and calls `check_hit`; fusion only receives checked hits; any leg error fails the query (D040).
- Query text reaches SQLite only as the bound `MATCH` parameter made of quoted `lexical-v1` terms, never as SQL text and never raw. Injection tests (R6) spy on `LexicalIndex.search` and on `sqlite3` `set_trace_callback` to show the SQL text is constant and the `MATCH` argument is the quoted terms.
- The lexical file is opened read-only for queries. It holds only eligible public chunks (production builder); ineligible content exists only in the security gate's temporary file.
- BM25 statistics (IDF, average length) are computed over all rows of a file, including rows the filter excludes. Today the production file holds only eligible public chunks, so this reveals nothing; a roles spec must use per-scope files or accept the statistic leak (recorded in a decision).
- No secrets: the lexical file holds payloads only; paths printed relative or as file names; `safe_text` for payload text (D041).

## Observability

Results record strategy, fusion parameters, lexical identity, leg ranks for relevant documents, per-leg latency (p50/p95, warm-up excluded) and score kind. `make retrieve` prints strategy and leg ranks. No Langfuse (roadmap 11).

## Testing / evaluation strategy

- Unit (in `make verify`, no Docker, no model): tokenizer pins; build/open/bind refusals on `tmp_path` files, atomic replace and failure cleanup; BM25 ranking on a small synthetic corpus (expected order from FTS5), access clause, `owner_present`, injection; `rrf_fuse` hand-computed values, ties, empty leg; hybrid fail-closed with a stub leg returning a forbidden payload; strategy config validation; CLI exit codes for `index-lexical`, `retrieve --strategy`, `eval-retrieval --strategy` (fake embedder, in-memory Qdrant, `tmp_path` lexical file; quality run refusals unchanged); result 2.1 keys and absence of text; compare rules including the two committed files; security gate over three strategies, sanity-check failure as harness error, result 1.1.
- R1 tests: v2 counts from the manifest vs rows, field-by-field v1/v2 equality, mapping, v1 dataset hashes, v1 manifest diff = `status`, candidates diff = `promoted_as`, transcription check fails on a temp copy with a changed query.
- Dense unchanged (user rule at design approval): existing dense tests may be updated only to add the new default model fields (`leg_ranks`, `strategy`, `score_kind`, `leg_latency_ms`, `lexical`, `query_terms_truncated`); dense ranks, scores, document IDs and ordering stay identical. The legacy snapshot test passes untouched. A deterministic equivalence test runs the dense evaluation (fake embedder, in-memory Qdrant) and checks that every per-case 2.0 field of the 2.1 result equals the 2.0 result produced before the change (fixture captured before the T6 code change).
- Real dense equivalence (user-owned, first step of the BM25/hybrid gate): a real dense `make eval-retrieval` on v2 in result 2.1 must pass `make eval-compare` against the R2 dense baseline with no flipped cases.
- Integration: R12 test; existing integration tests.
- Real (user-owned): R2 dense v2; R13 bm25 and hybrid, compare against R2.

## Phase 2 compatibility / migration

- The builder takes a `DocumentRepository`, so `S3DocumentRepository` works unchanged; preview indexing can build one lexical file per candidate `index_version`.
- `LexicalIndex.open` works without Qdrant (only `bind_to` needs it), so roadmap 13 can use `BM25Retriever` as the dense-failure or Qdrant-down fallback with the same `ResolvedAccess` and `check_hit`.
- Result 2.1 and security 1.1 are additive; older files stay readable.
- Suite versions as separate manifests + datasets is the pattern Phase 2 release candidates can extend; the closed v1 reference stays comparable with other v1 files.

## Alternatives / deferred decisions

- Qdrant sparse vectors (single store, `build_access_filter` reused) — rejected: new `index_version`, real re-ingest, client-side BM25 length normalization that goes stale, and FTS5 is still needed for the fallback (D010).
- BGE-M3 learned sparse weights, SPLADE — not BM25; deferred.
- Server-side Qdrant RRF (`prefetch` + `FusionQuery`) — rejected: no per-leg `check_hit` before fusion.
- FTS5 `unicode61` or `trigram` tokenizers — rejected: `unicode61` breaks Malayalam words; `trigram` changes BM25 semantics.
- Mapping legacy chillu sequences to atomic chillu — rejected for now (needs a script-specific table; data has none).
- Concurrent legs — deferred (sequential is deterministic and the corpus is tiny).
- A `bm25` strategy that runs without the `bge-m3` extra or without Qdrant — deferred; every strategy binds the dense index for identical identity (user decision at design approval). Note for the next spec: BM25 must be able to run without Qdrant before it can serve as the FTS5 fallback (roadmap 13); the `dense_identity` copy in the lexical settings is the starting point.
- Incremental lexical updates, lexical index built inside `make ingest` — deferred; full atomic rebuild.
- Stemming, stopwords, per-language analyzers — roadmap 8.

## As-built notes

Recorded by the 2026-10-25 amendment from the T3 task review (round 1, user decision: "Decisions accepted"). Each note describes code as built in T3.

- **`make index-lexical` options (T3).** Besides the design's CLI signature, the command takes `--embedder {bge_m3,fake}` (like `make ingest`), `--output` and `--config`. The `fake` option exists so a throwaway collection ingested with the fake embedder gets a matching `dense_identity` in the lexical file. The default reads the BGE-M3 identity from `config/ingestion.yaml` without loading the model.
- **`LexicalIndex.bind_to` compares `hash_contract` (T3).** The lexical binding compares `hash_contract` with the dense index settings, although dense binding records `IndexSettings.hash_contract` and never compares it.
- **Relative paths (T3).** A relative `W2A_LEXICAL_INDEX_DIR` or `--output` resolves against `--repo-root`.

Recorded by the 2026-10-27 amendment from the T4 task review (round 1, user decision: "Decisions accepted").

- **`LexicalIdentity` location (T4).** The model lives in `retrieval/models.py`, next to `RetrievalResult`.
- **BM25 score (T4).** The reported score is `-bm25() + 0.0`: higher is better, and `+ 0.0` turns a `-0.0` into `0.0`.
- **Non-object `payload_json` (T4).** A row whose `payload_json` is not valid JSON or not a JSON object is passed to `check_hit` as an empty payload and fails closed.
- **Latency rule (T6, from T4 review F2).** Every leg and strategy is timed by one span that starts just after `validate_request` and ends after the last `check_hit`, so dense and BM25 latency measure the same work. As built in T4, `BM25Retriever` follows this rule and `DenseRetriever` stops its clock before `check_hit`; T6 moves the dense stop to match. Hybrid per-leg latency (`latency_ms.legs`) is each leg's own span.
