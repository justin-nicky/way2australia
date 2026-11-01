# 009 — Chunking Experiments Design

Status: approved (2026-11-01)

Requirements: `requirements.md` (approved 2026-11-01). Decisions D063 onward are written in T7.

## Design summary

- A `ChunkTokenizer` (BGE-M3 through `tokenizers`, or a deterministic fake) counts tokens exactly as the embedder sees them. It is derived from the embedder configuration, never configured on its own.
- `IngestionService` runs a truncation guard per document, after chunking and before embedding. It refuses a chunk above `min(model max sequence length, chunker token cap)` as a per-document failure. Chunking moves inside the per-document error handling.
- Two new pure chunkers sit next to the unchanged `heading` v1:
  - `structure` v1: heading sections, heading-path `section_id`s, block-boundary packing under a token cap, optional title and heading-path prefix;
  - `recursive` v1: separator hierarchy, token target plus overlap, optional title prefix.
- A `ChunkerIdentity` (name, version, canonical parameters, tokenizer identity) is built from configuration without loading a tokenizer. It replaces `chunker_max_chunk_chars` in:
  - `IndexSettings` (schema 1.1; 1.0 still read);
  - the lexical settings (schema 1.1; 1.0 files refused with rebuild advice);
  - result 2.3.
- Standalone lexical freshness compares per-document `(document_id, document_version, content_hash)` sets plus `ChunkerIdentity`. It does not re-chunk and needs no tokenizer.
- `eval-retrieval` retrieves to the candidate depth, removes duplicate documents and scores at k distinct documents (MRR@k). It refuses a run whose depth cannot guarantee k distinct documents.
- `eval-compare --cross-index` allows collection, `index_version` and chunker differences only.
- `eval-security` runs its five paths for each of the three chunkers.
- An experiment arm is selected with the existing `--config` option (the ingestion config path, already on all four CLIs) and a committed file under `experiments/configs/chunking/`. `config/ingestion.yaml` changes only if R10 promotes the arm.

## Package / file placement

| File | Change |
|---|---|
| `packages/rag/pyproject.toml`, `uv.lock` | base dependencies `tokenizers` and `huggingface_hub` (already transitive through `tokenizers`; declared because it is imported directly, as `referencing` was in Spec 006) |
| `ingestion/tokenization.py` (new) | `ChunkTokenizer` Protocol, `TokenizerIdentity`, `BgeM3Tokenizer`, `FakeTokenizer`, `build_tokenizer(embedder_config)` |
| `ingestion/guard.py` (new) | `check_chunks(chunks, tokenizer, cap)`, `ChunkTooLongError` |
| `ingestion/chunking.py` | `Chunker` Protocol gains `identity: ChunkerIdentity`, and `max_chunk_chars` leaves the Protocol. `ChunkerIdentity` model. `HeadingChunker` is unchanged in behaviour and exposes `identity` (params `{"max_chunk_chars": N}`, tokenizer `None`). |
| `ingestion/structure.py` (new) | `StructureChunker` (`structure` v1), `DuplicateSectionError` |
| `ingestion/recursive.py` (new) | `RecursiveChunker` (`recursive` v1) |
| `ingestion/config.py` | `IngestionConfig` schema 1.1: a discriminated `chunker` union (`heading` / `structure` / `recursive`) and optional `embedder.fake_max_sequence_length` (default 512). Schema 1.0 files are still accepted (they can only name `heading`). `chunker_identity(config)` builds the identity without loading a tokenizer. |
| `ingestion/cli.py` | `build_chunker` dispatches on the name; the existing `--config PATH` option is unchanged |
| `ingestion/service.py` | chunking and the guard move inside the per-document `try`; structured failure details |
| `ingestion/settings.py` | `IndexSettings` 1.1 (`chunker_params`, `chunker_tokenizer`); 1.0 records are upgraded in memory and never rewritten; `compare` ignores `schema_version`; the `max_length` docstring is corrected (Spec 004 T5 F2) |
| `lexical/store.py` | lexical settings 1.1 (`ChunkerIdentity` fields); 1.0 refused by `open` with rebuild advice; `document_versions()` (distinct `(document_id, document_version, content_hash)`); `chunks_per_document()` |
| `lexical/build.py` | `_identity` renamed to public `chunk_identity`; `production_entries` runs the guard |
| `lexical/freshness.py` | per-document comparison; imports only public names |
| `lexical/cli.py` | builds the tokenizer for the guard; existing `--config` unchanged |
| `retrieval/opening.py` | standalone path uses `chunker_identity(config)` (no tokenizer) |
| `retrieval/cli.py`, `evaluation/cli.py` | `compare --cross-index`; existing `--config` unchanged |
| `evaluation/retrieval_eval.py`, `results.py` | depth retrieval, distinct-document metrics, depth check, result 2.3 |
| `evaluation/compare.py` | 2.3 reading, cross-index mode, format-equivalence rule |
| `evaluation/security_eval.py`, `security_index.py` | chunker matrix, security result 1.3 |
| `experiments/configs/chunking/recursive-128.yaml` (new, committed) | the R10 arm (below) |
| `experiments/configs/chunking/heading-idx-v1.yaml` (new, committed) | byte copy of today's `config/ingestion.yaml`, so `idx-v1` stays selectable after a promotion |
| `Makefile` | `COMPARE_ARGS` pass-through for `eval-compare` (`INGEST_ARGS`, `LEXICAL_ARGS`, `EVAL_ARGS` and `RETRIEVE_ARGS` already exist) |

Not changed: `retrieval/fusion.py`, `hybrid.py`, `fallback.py`, `access.py`, `availability.py`, the BM25 query logic, `lexical-v1` (`lexical/tokenizer.py`), `HeadingChunker`'s output, `PointPayload` (17 fields; the heading path appears only in chunk text), `INGESTION_NAMESPACE` and point IDs, `knowledge/`, `evaluation/`, and `config/` (unless R10 promotes).

## Components / boundaries

### Tokenizer (R1)

```text
ChunkTokenizer (Protocol)
  identity: TokenizerIdentity      # name, model_id, revision, max_sequence_length
  count(text) -> int               # includes special tokens (<s>, </s>)
```

- **`BgeM3Tokenizer(model_id, revision)`**
  - Files: `tokenizer.json` and `sentence_bert_config.json` (`max_seq_length`, 8192 at `5617a9f`), fetched with `huggingface_hub.hf_hub_download(repo_id, filename, revision=<pinned SHA>)`.
  - Cache: the cache is tried first (`local_files_only=True`). A download happens only if the file is missing and `HF_HUB_OFFLINE` is not set.
  - Failure: any failure becomes `IngestionConfigurationError` (exit 2). The message names the model, the revision and "network access once, or a populated Hugging Face cache". It never contains a path or URL beyond the model ID.
  - Floating revisions are refused, as in the adapter.
  - It never imports `torch` or `sentence_transformers`; an import-pin test enforces this.
- **`FakeTokenizer(max_sequence_length=512)`**
  - Count: `2 + Σ ceil(len(word) / 4)` over whitespace-separated words, after NFKC.
  - Deterministic, no files.
- **`build_tokenizer(embedder_config)`**
  - Gives `FakeTokenizer` for `provider: fake` and `BgeM3Tokenizer` for `bge_m3`.
  - It is the only constructor, so the tokenizer always matches the embedder (R1).

### Truncation guard (R2)

`check_chunks(document_id, chunks, tokenizer, cap)`:
- The limit is `min(tokenizer.identity.max_sequence_length, cap)`; `cap` is `None` for `heading` v1.
- It counts each `chunk.text`, which is the exact string passed to `embed_documents`.
- The first violation raises `ChunkTooLongError(document_id, section_id, position, tokens, limit)`. Its message carries no text.

`IngestionService.run` per document:
```text
try:
    chunks = chunker.chunk(document)        # moved inside (closes Spec 004 T7 F1)
    check_chunks(...)
    compare/embed/upsert as today
except OptionalDependencyError: re-raise (unchanged)
except Exception: per-document failure (reason, plus structured fields for ChunkTooLongError)
```
- The existing per-document failure semantics are unchanged: other documents continue, nothing is written or deleted for the failed document, and the run's non-zero exit on failures is unchanged.
- `production_entries` (`make index-lexical`) runs the same guard. A violation makes the atomic build refuse (exit 2), so the lexical file never holds a chunk that ingestion refused.

### `structure` v1 (R3)

1. **Sections.** Parse ATX headings outside fences, as `heading` v1 does. Each heading gets its path: the stack of ancestor headings by level. Text before the first heading is section `main`; it is omitted if empty.
2. **`section_id`.** It is `slugify(" / ".join(path_texts))`; the `/` separators become `-` in the slug. For example, `# Fees` then `## Refunds` gives `fees-refunds`, and `# Mocks` then `## Refunds` gives `mocks-refunds`. Two sections with the same `section_id` raise `DuplicateSectionError(document_id, section_id)`; there is no counter suffix. A preamble that collides with a heading slugged `main` is the same error.
3. **Blocks within a section** (the heading line itself is excluded):
   - a fenced block (atomic);
   - a list item (a line starting with `-`, `*`, `+` or `\d+[.)]`, plus its continuation lines);
   - a paragraph (separated by blank lines).
4. **Prefix.**
   - `context_prefix: none`: prefix = the heading line (as in `heading` v1).
   - `context_prefix: title_and_headings`: prefix = `title + "\n" + " › ".join(path_texts)`.
   - The preamble has no heading line, so it gets the title only, or nothing when the setting is `none`.
5. **Packing.**
   - Blocks are packed greedily into `prefix + "\n\n" + body`, with `count(composed) <= max_chunk_tokens`. Tokens are counted on the composed string, never summed.
   - Blocks are joined with `"\n"` between consecutive list items and `"\n\n"` otherwise.
   - A block that alone exceeds the budget is split at line breaks, then at sentence ends, then at whitespace, then at characters (binary search on `count`) as the last resort.
   - **Sentence end** (shared by both chunkers): `.`, `?`, `!` or `।` immediately followed by whitespace or the end of the text; the split falls after the punctuation and the whitespace is dropped. A mark followed by anything else never splits, so `1.5`, `A$20.00`, `naati.com.au` and the inner dot of `e.g.` stay whole. (The final dot of `e.g.` followed by a space does split; accepted, since splitting is only a fallback for oversized blocks.)
   - If the prefix alone leaves less than half the cap, the result is `IngestionConfigurationError` for that document.
6. **Parameters:**
   - `max_chunk_tokens`, an integer from 32 up to the model maximum (checked once the tokenizer is built);
   - `context_prefix`, `none` or `title_and_headings`.

### `recursive` v1 (R4)

- **Prefix.** `context_prefix: none` or `title`; the title prefix is `title + "\n\n"`.
- **Splitting.** Body (frontmatter already removed by the repository) split by the separators `["\n\n", "\n", sentence end (as defined for `structure` v1), " "]`. A unit is split further only while it exceeds the budget; the final fallback is a character split, as in `structure` v1.
- **Packing.** Units are packed greedily into chunks with `count(prefix + chunk) <= target_tokens`. Each new chunk starts with the trailing units of the previous one whose combined count (without special tokens) is at most `overlap_tokens`. A unit is never repeated if that alone would exceed the budget.
- **Parameters.** `target_tokens` is at least 32; `0 <= overlap_tokens < target_tokens / 2`. Violations are a configuration error at load time.
- **IDs.** All chunks use `section_id` `main`, with positions `0..n-1`.

All three chunkers are pure, deterministic and free of language-specific code. Each chunker version has an output snapshot test on the seed corpus and on synthetic fixtures. Any change to the output therefore needs a version bump, and that is what keeps per-document freshness (R6) sound.

### Chunker identity, settings and configuration (R5)

- **Identity.** `ChunkerIdentity`:
  - `name`, `version`;
  - `params` (sorted `dict[str, str | int | bool]`);
  - `tokenizer` (`"<model_id>@<revision>"`, `"fake-tokenizer@1"`, or `None` for `heading`).
  - It is built from configuration by `chunker_identity(config)` and by `Chunker.identity`; a test pins that both give the same result.
- **Index settings.** `IndexSettings` 1.1 replaces `chunker_max_chunk_chars` with `chunker_params` and `chunker_tokenizer`. Reading a 1.0 record maps `chunker_max_chunk_chars=N` to `chunker_params={"max_chunk_chars": N}` and `chunker_tokenizer=None`.
  - `compare` ignores `schema_version` and `hash_contract`, so the `idx-v1` 1.0 record still matches a `heading` v1 configuration: no rewrite, no rebuild.
  - New collections are written as 1.1.
  - `DenseIndex` binding still ignores the chunker (D036).
- **Ingestion config.** `config/ingestion.yaml` stays at schema 1.0 and is untouched. Schema 1.1 files express the new chunkers:

```yaml
schema_version: "1.1"
index_version: "idx-v2"
embedder: {...same as config/ingestion.yaml...}
chunker:
  name: recursive
  version: "1"
  target_tokens: 128
  overlap_tokens: 16
  context_prefix: title
knowledge_release_id: "seed-v1"
evaluation_suite_id: "public-eval-v1"   # copied unchanged; informational in ingestion
```

- **Selecting a config.** The ingestion, lexical, retrieval and `eval-retrieval` CLIs already take `--config PATH` (ingestion config; default `<repo-root>/config/ingestion.yaml`); it is used as is through the existing `*_ARGS` (`make ingest`, `make index-lexical`, `make retrieve`, `make eval-retrieval`). No new option. Result 2.3 records the path and the SHA-256 of the file.

### Lexical identity and per-document freshness (R6)

- **Lexical settings 1.1.** They store `ChunkerIdentity` (name, version, params JSON, tokenizer) in place of `chunker_max_chunk_chars`. `source_chunk_digest` and `dense_identity` are kept.
- **1.0 files.** `LexicalIndex.open` refuses a 1.0 file with `LexicalIndexBindingError`: "lexical index '<label>' was built with lexical settings 1.0; run `make index-lexical` (with the same `QDRANT_COLLECTION_BASE`) to rebuild it". No compatibility reader; one code path (see Alternatives).
- **`check_identity(expected, chunker_identity, hash_contract)`.** Compares `ChunkerIdentity` field by field; refusals name the fields.
- **`verify_fresh(lexical, repository, chunker_identity)`.**
  - `expected` = `{(d.document_id, d.document_version, d.content_hash)}` over the documents `GUEST_PUBLIC_POLICY` makes eligible, loaded through `DocumentRepository`. Loading computes `content_hash`; nothing is chunked or tokenized.
  - `recorded` = `lexical.document_versions()` (`SELECT DISTINCT document_id, document_version, content_hash FROM chunks`).
  - Equal means fresh. Otherwise it refuses with counts (only in the repository, only in the file, changed version or hash) and the rebuild advice.
  - It still uses `asyncio.run`; that limitation stays with the HTTP-route carry-overs.
- **Paths.** The standalone and fallback paths call `check_identity` then `verify_fresh`, with no tokenizer, Qdrant or extra. A test makes `build_tokenizer` raise and shows that `--strategy bm25` and the hybrid fallback still serve. `bind_to(dense)` is unchanged: chunk-digest comparison with the live collection, plus the chunker identity compared with the dense settings' 1.1 view.
- **D060 cost.** Opening no longer parses chunks or hashes chunk text. It still reads and hashes each eligible document once (content hash). D060's caveat is amended accordingly in T7.

### What happens to existing lexical files (user request)

- **Which files.** Every lexical file built before this spec (settings 1.0) is refused once after the merge: `.local/lexical/` files for `way2australia-idx-v1` and `w2a-realcheck-idx-v1`, and any throwaway ones.
- **Fix.** A one-time rebuild: `QDRANT_COLLECTION_BASE=w2a-realcheck make index-lexical` (and the same without the variable for the default collection).
- **What the rebuild needs.** `make index-lexical` creates no Qdrant client and no embedder (`lexical/cli.py`). `idx-v1` uses `heading` v1, whose identity has no tokenizer, so the guard's tokenizer is the only model-related input. The guard there uses `build_tokenizer` of the configured embedder (BGE-M3), which needs only `tokenizer.json` and `sentence_bert_config.json` at the pinned revision, both already in the user's Hugging Face cache. So the rebuild needs no PyTorch, no `bge-m3` extra, no model weights and no Qdrant.
- **Unchanged.** The Qdrant collection `w2a-realcheck-idx-v1` is not touched.
- **How T6 does it.** T6 step 1 runs this rebuild before the baseline run, checks that the new file's `source_chunk_digest` and chunk count (13) equal the old file's (recorded before the rebuild with a read-only SQLite query), and records both in `CURRENT_STATE.md`. Equal digests show that the rebuild changed only the settings format, not the content.
- **Tests.** A 1.0 fixture file is refused with the advice; rebuilding it through `build_lexical_index` gives a 1.1 file with the same digest.

### Distinct-document metrics (R7)

- **Depth.** `D = fusion.candidate_depth` from `config/retrieval.yaml` (50), for every strategy. Each case calls `retriever.retrieve(query, access, D)`. `HybridRetriever` already fuses each leg at `candidate_depth` regardless of `top_k`, so the order is unchanged and the cut is the only difference.
- **Scoring.**
  - `ranked = dedupe_documents(hits)[:k]`; the fields `hit`, `recall` and `reciprocal_rank` are computed on that list.
  - The reciprocal rank is 0 beyond the k-th distinct document (MRR@k), exactly what 2.2 computed on top-5 chunks when each document is one chunk.
  - Leg ranks (Spec 007) stay as they are.
- **Depth check (fail closed).**
  - At open, after binding, the run reads chunks per eligible document from the bound index: lexical `chunks_per_document()` when a lexical file is bound, else the dense `chunk_identities()`.
  - `m` = the largest number of chunks any document has.
  - It requires `(k − 1) · m + 1 <= D`, which guarantees the first k distinct documents lie within any depth-`D` list long enough to hold them. Otherwise the run is refused (exit 2), naming `m`, `k`, `D` and the advice (lower `k`, raise `candidate_depth` up to 50, or use a coarser chunker).
  - BM25 lists shorter than `D` (few matching chunks) are reported as today.
- **Result 2.3 additions (every 2.2 field keeps its meaning):**
  - `metric_unit: "distinct_documents"`, `retrieval_depth: D`;
  - `chunk_stats: {chunk_count, document_count, max_chunks_per_document, required_depth}`;
  - `chunker` (`ChunkerIdentity`, from the bound index settings, or from the lexical file on the standalone and fallback paths);
  - `ingestion_config: {path, sha256}`.

**Recursive arm against depth 50 (user request).** Computed on 2026-11-01 with the cached BGE-M3 tokenizer at `5617a9f`, using a prototype of the `recursive` v1 algorithm above (special tokens counted, title prefix on). The implementation may differ by a chunk here or there; T2 records the real counts and T6 checks them from the result's `chunk_stats`.

| target / overlap | prefix | chunks per document (b001–b008, ml_001, o001–o004) | total | max per doc | largest chunk (tokens) |
|---|---|---|---|---|---|
| 96 / 16 | title | 4 5 3 4 4 6 4 3 4 3 4 4 2 | 50 | 6 | 95 |
| **128 / 16** | **title** | **2 4 2 3 3 4 3 2 2 2 3 3 1** | **34** | **4** | **127** |
| 128 / 16 | none | 2 3 2 3 3 4 3 2 2 2 3 2 1 | 32 | 4 | 125 |
| 192 / 24 | title | 2 2 2 2 2 3 2 1 2 2 2 2 1 | 25 | 3 | 188 |

- **Chosen arm:** `recursive` v1, `target_tokens` 128, `overlap_tokens` 16, `context_prefix: title`, `index_version` `idx-v2`.
  - It gives 34 chunks, at most 4 per document.
  - Required depth `(5 − 1) · 4 + 1 = 17 <= 50`.
  - Total chunks 34 <= 50, so the dense leg at depth 50 returns every chunk and every document appears in the ranking.
  - Headroom: the check holds up to 12 chunks per document at k = 5.
  - The title prefix keeps the document's subject in each small chunk; without it, chunks such as a single bullet about "one repeat per dialogue" lose the "NAATI CCL candidate rules" context.
  - **Confounded by design (user decision 2026-11-01).** The arm changes chunk size and adds the title prefix at once. Its result belongs to "128 tokens + title prefix" together; the two effects are not separated. The T7 decision records this; a later spec may separate them.
- **96 tokens rejected** because it sits exactly at 50 chunks in total (no headroom for corpus growth). **192 tokens rejected** because it splits most documents only in two.

### Cross-index comparison (R8)

`make eval-compare BASE=... CANDIDATE=... COMPARE_ARGS=--cross-index`.

- Without the flag, behaviour is unchanged (D054 refusals).
- With the flag:
  - collection, `index_version`, `chunker` and `ingestion_config` may differ; each difference is printed;
  - still refused: suite or suite version, embedder pair, lexical tokenizer name and version, `top_k`, `metric_unit`, mixed served strategies, and every Spec 006 refusal;
  - the chunk digest is not compared across indexes;
  - the D044 gate is unchanged.
- **Format rule.** Cross-index mode requires 2.3 on both sides. Without the flag, a 2.3 file may be compared with 2.0–2.2 only when the older file shows one chunk per document: it records a `lexical_index` with `chunk_count == document_count`, and the 2.3 side has `max_chunks_per_document == 1`. Anything else is refused with "re-run both with result 2.3". The R10 baseline check (2.3 `idx-v1` against the 2.2 hybrid reference) meets this rule (13 chunks, 13 documents).

### Security gate (R9)

- `eval-security` runs its five paths for three chunkers on the throwaway corpus, all with the fake embedder and `FakeTokenizer`:
  - `heading` v1 (2000 characters);
  - `structure` v1 (`max_chunk_tokens` 64, `title_and_headings`);
  - `recursive` v1 (`target_tokens` 32, `overlap_tokens` 4, `title`).
- The small caps force several chunks per document. The forbidden and canary points are built per chunker, so they stay nearest by construction.
- Security result 1.3: `runs: [{chunker, paths: {...1.2 shape...}}]` and overall `pass`. The gate inside `make verify` (`test_security_eval.py`) is parameterized over the three chunkers.

### Carry-over clean-ups (R11)

- `chunk_identity` is public in `build.py`, and `freshness.py` stops importing `_identity`.
- The `settings.py` docstring is corrected: `max_length` is not used; the model's `max_seq_length` truncates, and the R2 guard now refuses instead.
- A new test covers the embedder returning the wrong number of vectors (the `zip(strict=True)` guard in `_embed`).

## Data flow

```text
make ingest --config F
  config F -> embedder, build_tokenizer(embedder cfg), chunker(name, params, tokenizer)
  settings 1.1 (or 1.0 record read, upgraded in memory) -> compare -> refuse on mismatch (D028)
  per eligible document: try { chunk -> guard -> point IDs -> embed -> upsert } except -> failure

make index-lexical --config F    (no Qdrant, no embedder)
  production_entries(repository, chunker) + guard -> atomic build, lexical settings 1.1

make eval-retrieval --config F [--strategy s]
  open_retrieval: bind (hybrid/dense) or standalone (check_identity + per-document verify_fresh)
  depth check (m, k, D) -> per case retrieve(depth D) -> dedupe -> first k -> metrics -> result 2.3

make eval-compare BASE CANDIDATE [COMPARE_ARGS=--cross-index] -> refusals -> gate
```

## Interfaces / models

```python
class TokenizerIdentity(BaseModel):  # frozen
    name: str                     # "bge-m3" | "fake"
    model_id: str
    revision: str
    max_sequence_length: int

class ChunkTokenizer(Protocol):
    identity: TokenizerIdentity
    def count(self, text: str) -> int: ...

class ChunkerIdentity(BaseModel):  # frozen
    name: str
    version: str
    params: dict[str, str | int | bool]
    tokenizer: str | None

class Chunker(Protocol):
    name: str
    version: str
    identity: ChunkerIdentity
    def chunk(self, document: KnowledgeDocument) -> list[Chunk]: ...

class ChunkTooLongError(IngestionError):
    document_id: str; section_id: str; position: int; tokens: int; limit: int
```

`Chunk` is unchanged (`section_id`, `position`, `text`).

## Error and failure behavior

| Situation | Behaviour |
|---|---|
| Tokenizer files missing or offline, wrong or floating revision | `IngestionConfigurationError`, exit 2, before any write; never a retrieval fallback |
| Chunk above the limit | per-document failure `chunk_too_long` (IDs, counts, limit); other documents continue; non-zero exit; `index-lexical` refuses the build |
| Duplicate section ID (`structure` v1) | per-document failure `duplicate_section` |
| Chunker parameters invalid (cap below 32 or above the model maximum, overlap too large) | configuration error at load or after the tokenizer is built, exit 2 |
| Prefix too long for the cap | per-document failure |
| Index settings mismatch | D028 refusal, listing chunker fields |
| Lexical file 1.0 | refusal with rebuild advice (exit 2) |
| Lexical chunker identity or per-document set differs | refusal with field names or counts (exit 2) |
| Depth check fails | `eval-retrieval` exit 2 with `m`, `k`, `D` and advice |
| `eval-compare` disallowed difference | exit 2, as today |

None of these is fallback-eligible (D057 unchanged).

## Security / authorization

No new authorization code. Chunkers run only on documents `GUEST_PUBLIC_POLICY` made eligible. Payload access fields are copied per chunk as today. Retrieval at depth 50 keeps the filter inside every query and `check_hit` on every hit. The security gate covers each chunker (R9). Reports and refusals carry IDs and counts, never chunk text; tokenizer errors carry no file paths.

## Observability

- The ingestion run report gains structured failure fields.
- Result 2.3 records the chunker, the ingestion config path and hash, `chunk_stats` and the metric semantics.
- No Langfuse (roadmap 11).

## Testing / evaluation strategy

- **Unit tests (no extra, no tokenizer file, no Docker):**
  - `FakeTokenizer` counting;
  - `build_tokenizer` dispatch;
  - `BgeM3Tokenizer` cache-miss offline error (monkeypatched `hf_hub_download`);
  - import pin (no torch);
  - guard: oversized, at the limit, per-document failure, chunker exception inside the `try`;
  - `structure` v1 synthetic fixtures (nested, cousins, duplicate siblings, `main` collision, fences, long lists, a long Malayalam paragraph, an oversized block, prefix modes, reorder and insert stability of IDs);
  - sentence-end rule (both chunkers): splits after `.`, `?`, `!` and `।` followed by a space, a newline or the end of text; no split inside `1.5`, `A$20.00`, `naati.com.au` or the inner dot of `e.g.`; a Malayalam sentence ending in `।` followed by a space splits;
  - `recursive` v1 (no piece over target, overlap, repeatability, configuration validation);
  - snapshot tests per chunker on the seed corpus;
  - `chunker_identity(config)` equals `Chunker.identity`;
  - settings 1.0 read and compare;
  - lexical 1.0 refusal and rebuild equality;
  - per-document freshness (edited, removed, added document; chunker identity mismatch);
  - standalone `bm25` with `build_tokenizer` raising;
  - depth check;
  - 2.3 equals 2.2 on the frozen one-chunk fixture;
  - compare matrix (allowed and refused differences, format rule, gate);
  - security result 1.3;
  - the Spec 004 T7 F3 vector-count test.
- **Opt-in, with the extra:** BGE-M3 tokenizer count and `max_sequence_length` equal the `SentenceTransformer` model's tokenizer and `max_seq_length` (skip without the extra).
- **Integration (Docker Qdrant):** `make test-integration` adds one fake-embedder ingestion with `recursive` v1 (several chunks per document, re-run gives 0 changes) and a 1.0-settings collection that binds unchanged.
- **Gates:** `make verify`, `make test-integration`, `make eval-security`, `make validate-knowledge`, `make validate-evaluation`, `graphify update .` per code task, and the protected-path diff.
- **R10 real runs (T6, user-owned):**
  1. Rebuild the `idx-v1` lexical file (see "What happens to existing lexical files").
  2. Baseline: `QDRANT_COLLECTION_BASE=w2a-realcheck make eval-retrieval` (2.3), then `make eval-compare` against `...20261101T070736Z.json`. It must pass with 68 → 68 hits and MRR 0.9094 → 0.9094, no flips.
  3. Arm: `QDRANT_COLLECTION_BASE=w2a-realcheck`:
     - `make ingest INGEST_ARGS="--config experiments/configs/chunking/recursive-128.yaml"`;
     - `make index-lexical` with the same option in `LEXICAL_ARGS`;
     - `make eval-retrieval` with the same option in `EVAL_ARGS`.
  4. `make eval-compare BASE=<baseline 2.3> CANDIDATE=<arm 2.3> COMPARE_ARGS=--cross-index`.
  5. Promotion rule:
     - the gate passes, neither hits nor MRR drop, at least one improves, and no `ml` or `mixed` case flips from hit to miss;
     - a tie keeps the baseline.
     - If not promoted, `config/ingestion.yaml` is untouched and the default stays `heading` v1 / `idx-v1`.
  6. Promotion steps (only if promoted), in this order:
     1. Real ingestion of `idx-v2` into the default collection base: `make setup-bge-m3`, then `make ingest INGEST_ARGS="--config experiments/configs/chunking/recursive-128.yaml"` (no `QDRANT_COLLECTION_BASE`, so collection `way2australia-idx-v2`). Step 3 already built `w2a-realcheck-idx-v2`; re-running ingestion there reports 0 added, updated and deleted and is optional.
     2. `make index-lexical LEXICAL_ARGS="--config experiments/configs/chunking/recursive-128.yaml"` for the same base.
     3. Only then the config change: `config/ingestion.yaml` takes the content of `experiments/configs/chunking/recursive-128.yaml` (schema 1.1, `idx-v2`).
     4. Check: `make retrieve QUERY=...` and `make eval-retrieval` without `--config` bind to `idx-v2`; `make setup` restores the default environment.
     - `idx-v1` stays readable after promotion: `experiments/configs/chunking/heading-idx-v1.yaml` (created in T3, a byte copy of today's `config/ingestion.yaml`, pinned by a test until promotion) selects it with `--config`. The `idx-v1` collections and their rebuilt lexical files are not deleted.
  7. The agent checks `chunk_stats` (34 ± a few, `max_chunks_per_document` <= 12), identities, `git_dirty` and served strategies, and reports `g061`.

## Phase 2 compatibility / migration

- `ChunkerIdentity` is the unit a Knowledge Release will reference as part of "RAG Config"; preview indexing re-chunks only changed documents, matching per-document freshness.
- `section_id` from heading paths is ready for `relevant_section_ids` once documents gain headings (later spec).
- No migration of stored Qdrant data: 1.0 settings are read in place. Lexical files are rebuilt once (derived artifacts, C1).

## Alternatives / deferred decisions

- **Guard only, keep character boundaries.** Rejected: the roadmap asks for a token cap. The guard alone still protects the `idx-v1` default.
- **Keep re-chunking freshness and load the tokenizer on the standalone path.** Rejected by the brief (Q3): `bm25` would need the tokenizer files, and the D060 cost would remain.
- **Accept lexical 1.0 files through a compatibility reader.** Rejected: the rebuild is one command with no model and no Qdrant, and a second reader would be permanent code for a one-off migration.
- **Count tokens per piece and sum.** Rejected: SentencePiece tokens are not additive across joins; the composed string is counted.
- **Order-dependent suffixes for duplicate headings.** Rejected (roadmap 7 baseline limitation); duplicate siblings are refused.
- **Scoring at k chunks.** Rejected (Q4): it penalizes finer chunking.
- **A separate eval depth option.** Deferred: `candidate_depth` already bounds both legs; one value avoids a second knob.
- **Semantic chunking, FAQ-pair indexing, headed documents and `relevant_section_ids`, per-scope lexical files, Malayalam stemming, a dense query-length guard, and the HTTP-route carry-overs.** Out of scope (requirements).
