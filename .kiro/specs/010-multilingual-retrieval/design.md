# 010 — Multilingual Retrieval Design

Status: approved (2026-11-04)

## Design summary

Four independent additions, each kept out of the code it sits next to:

1. **Applicability, beside access (R2–R4).** A validated `ResolvedLote` value travels next to `ResolvedAccess` as a new keyword argument of `Retriever.retrieve`. A new module `retrieval/applicability.py` owns the three applicability pieces (Qdrant condition, SQL condition, hit re-check), mirroring `retrieval/access.py`, which does not change. Each retriever appends the applicability condition to the access filter it already builds, inside the same query.
2. **Tokenizer `lexical-v2` (R5, R6).** `lexical/tokenizer.py` becomes a small registry of versioned tokenizers. `lexical-v2` runs one generic step, "replace listed sequences", over a data table cited to the Unicode Standard, before the `lexical-v1` steps. A lexical file records its tokenizer, and queries always use the file's tokenizer. The lexical schema moves to settings 1.2, which adds a `lote_languages` column; the schema version is independent of the tokenizer version.
3. **Reporting (R7, R8).** Result 2.4 adds `lote` and a `by_script_mix` slice computed from `unicodedata` letter names. `eval-compare` gains `--cross-tokenizer` and refuses a `lote` difference. A new `make eval-continuity` command does the R10 case-by-case check.
4. **Gate and suite (R1, R9).** Security result 1.4 runs each chunker and path twice (no `lote`, and the active code) against new public but non-applicable rows. Suite v3 follows the Spec 007 T1 promotion pattern.

With no `lote`, no code path changes behaviour (R11): the new keyword defaults to `None`, and the applicability builders are never called.

## Package / file placement

New:

| File | Content |
|---|---|
| `packages/rag/src/way2australia_rag/languages.py` | `active_lote_codes(repo_root)`: the registry's active `product_support` codes (no `en`). It shares the registry parsing with `evaluation/slices.active_registry_languages`, which keeps adding `en` for query-language slices. |
| `packages/rag/src/way2australia_rag/retrieval/applicability.py` | `ResolvedLote`, `resolve_lote`, `build_lote_condition` (Qdrant), `build_sql_lote_clause`, `check_applicable`, `LOTE_COLUMN_SEPARATOR` |
| `packages/rag/src/way2australia_rag/lexical/equivalents.py` | `SEQUENCE_EQUIVALENTS` data table with the Unicode citation and version |
| `packages/rag/src/way2australia_rag/evaluation/script_mix.py` | `script_mix(text) -> str` |
| `packages/rag/src/way2australia_rag/evaluation/continuity.py` | per-case continuity comparison for `make eval-continuity` |
| `evaluation/candidates/010-candidates.jsonl`, `evaluation/suites/public-eval-v3.json`, `evaluation/datasets/v3/*.jsonl` | R1 |
| tests beside each module (`tests/retrieval/test_applicability.py`, `tests/lexical/test_tokenizer_v2.py`, `tests/evaluation/test_script_mix.py`, `tests/evaluation/test_continuity.py`, `tests/evaluation/test_suite_v3.py`, and additions to the existing bm25, dense, hybrid, fallback, opening, store, build, compare, results and security tests) | |

Changed: `retrieval/base.py` (protocol keyword), `retrieval/retriever.py`, `bm25.py`, `hybrid.py`, `fallback.py`, `opening.py` (`document_count` takes `lote`), `retrieval/errors.py` (`LanguageApplicabilityError`), `retrieval/cli.py` (`--lote`), `retrieval/strategy.py` (`RetrievalConfig` 1.2 `lexical.tokenizer`), `lexical/tokenizer.py`, `lexical/store.py`, `lexical/build.py`, `lexical/cli.py` (`--tokenizer`), `evaluation/retrieval_eval.py`, `results.py`, `compare.py`, `cli.py`, `security_index.py`, `security_eval.py`, `security_corpus.py` (if the rows live there), `validate.py` (v3 promotion checks), `Makefile` (`eval-continuity`, `CONTINUITY_ARGS`), `config/retrieval.yaml` (schema 1.2, `lexical.tokenizer: lexical-v1`).

**Not changed** (R11): `retrieval/access.py` (`build_access_filter`, `build_sql_access_clause` and `check_hit` keep their output), `fusion.py`, `availability.py`, `index.py` (`DenseIndex.search` already takes a `models.Filter`), ingestion (chunkers, payload, `IndexSettings`, `INGESTION_NAMESPACE`), `config/ingestion.yaml`, `knowledge/`, the legacy `make retrieval-baseline`, and `lexical-v1` tokenization output.

## Components / boundaries

### `ResolvedLote` and validation (R2)

```python
@dataclass(frozen=True, slots=True)
class ResolvedLote:
    code: str            # an active registry code, never "*" and never "en"

def resolve_lote(code: str | None, active_codes: Sequence[str]) -> ResolvedLote | None:
    """None -> None (no filter). Otherwise refuse (RetrievalConfigurationError)
    unless `code` is in `active_codes`; message names the value and the codes."""
```

- `active_codes` comes from `languages.active_lote_codes(repo_root)`. Today that is `["ml"]`. Generic code never contains the literal `ml`; tests read it from the registry or use a temporary registry.
- `en` is not a LOTE (English is the other side of every CCL pair), so it is refused like any code that isn't active. Its message explains why, for example: "'en' is not a LOTE: `lote` names the non-English side of the CCL pair (active codes: ml)". The `*` marker and empty strings are refused before the registry lookup.
- Only the CLIs, the evaluation runner and the security gate call `resolve_lote`. Retrievers receive a `ResolvedLote` only, so an unvalidated string cannot reach a filter, just as `ResolvedAccess` comes only from `resolve_access`.

### Applicability builders (R3)

- **One shape rule, enforced everywhere it can enter.** `lote_languages` is either exactly `["*"]` or a non-empty list of distinct language codes without `*`. `["*", "ml"]` is invalid. The rule already holds for documents (core `KnowledgeDocument._validate_lote_languages`, so manifests and `make validate-knowledge` refuse it). `applicability.valid_lote_languages(value) -> bool` restates it for raw payloads. The lexical builder refuses a payload that breaks it (`LexicalIndexError`, temporary file removed), and `check_applicable` raises `LanguageApplicabilityError` on such a hit. Under this rule "is `["*"]`" (SQL equality on `|*|`) and "contains `*`" (Qdrant `MatchAny`) select the same chunks. A Qdrant point written around the model, such as a raw upsert, that carries `["*", "ml"]` and passes the Qdrant condition for another code is stopped by `check_applicable`. Both stores therefore fail closed on the same rows, and no path returns it.
- **Qdrant:** `build_lote_condition(lote)` returns `FieldCondition(key="lote_languages", match=MatchAny(any=["*", lote.code]))`. The retriever builds `Filter(must=[*build_access_filter(access).must, condition])`. The access filter object itself is not modified. `lote_languages` already has a keyword payload index.
- **SQL:** `build_sql_lote_clause(lote)` returns `("(c.lote_languages = ? OR instr(c.lote_languages, ?) > 0)", ("|*|", f"|{code}|"))`. The BM25 retriever joins it to the access clause with ` AND `. The column stores the sorted codes wrapped in separators (`|*|`, `|ml|`, `|ml|ta|`). Codes are lowercase ISO 639 (core `_check_language_code`), so they can never contain `|`, and the builder refuses a value that would. `instr` avoids `LIKE` wildcards, and the parameters are bound, never formatted into the SQL.
- **Re-check:** `check_applicable(payload: PointPayload, lote)` runs after `check_hit` on every hit when `lote` is not `None`. A `lote_languages` that fails `valid_lote_languages` (missing, empty, non-list, duplicates, or `*` combined with a code), or a valid list that is neither `["*"]` nor contains the code, raises `LanguageApplicabilityError(document_id=...)`. The message names the document ID and field only.

### Retriever protocol (R3)

```python
class Retriever(Protocol):
    strategy: Strategy
    def retrieve(self, query_text: str, access: ResolvedAccess,
                 top_k: int = DEFAULT_TOP_K, *, lote: ResolvedLote | None = None
                 ) -> RetrievalResult: ...
```

- `DenseRetriever`: applies the combined filter and runs `check_applicable` after `check_hit`.
- `BM25Retriever`: with a `lote` on a file without the column (settings 1.1), it raises `LexicalIndexBindingError` before any SQL ("lexical index '<label>' has no lote_languages column (lexical settings 1.1); run `make index-lexical` …"). This is a configuration error, so it is not fallback-eligible and exits 2.
- `HybridRetriever`: passes `lote` to both legs, with no other change.
- `FallbackRetriever`: passes the same `lote` object to the primary and to the fallback, on both the open-time and the per-query path.
- `RetrievalResult` gains `lote: str | None` (default `None`), set by every retriever. Fusion is untouched.

### Tokenizers (R5, R6)

```python
class LexicalTokenizer(Protocol):
    name: str; version: str
    def tokenize(self, text: str) -> list[str]: ...
    def query_terms(self, text: str) -> QueryTerms: ...

TOKENIZERS: Mapping[str, LexicalTokenizer]   # "lexical-v1", "lexical-v2"
def tokenizer_named(name: str, version: str) -> LexicalTokenizer   # unknown -> LexicalIndexBindingError
```

- **`lexical-v1`:** today's functions, unchanged. The module-level `tokenize` and `query_terms` stay as `lexical-v1` aliases, so existing imports and the D051 pin test keep working.
- **`lexical-v2`:** NFC, then `replace_sequences(text, SEQUENCE_EQUIVALENTS)` (a longest-match scan over a tuple of `(sequence, replacement)` strings), then the `lexical-v1` steps (drop ZWJ/ZWNJ, lowercase, split). The replacement must run before ZWJ is dropped, because the legacy sequence is defined by its ZWJ.
- **`SEQUENCE_EQUIVALENTS`** (`lexical/equivalents.py`) holds code points only. Its header comment cites the Unicode Standard Malayalam section on chillu characters, which lists each atomic chillu with its earlier representation (base consonant + U+0D4D VIRAMA + U+200D ZWJ), and records the Unicode version checked. The six pairs:

  | Atomic chillu | Legacy sequence |
  |---|---|
  | U+0D7A | U+0D23 U+0D4D U+200D |
  | U+0D7B | U+0D28 U+0D4D U+200D |
  | U+0D7C | U+0D30 U+0D4D U+200D |
  | U+0D7D | U+0D32 U+0D4D U+200D |
  | U+0D7E | U+0D33 U+0D4D U+200D |
  | U+0D7F | U+0D15 U+0D4D U+200D |

  - T3 checks every row against the cited text before it is committed, and records the check in the task review.
  - The newer chillus (U+0D54–U+0D56) are left out unless the standard defines a legacy sequence for them.
  - These pairs are not canonically equivalent (NFC leaves them apart), which is why a table is needed.
- **Tokenizer settings:** the tokenizer name and version identify the tokenizer only. Lexical settings `schema_version` identifies the file layout (R3).
- **`LexicalIndex`:**
  - `_check` accepts any tokenizer in `TOKENIZERS` and refuses an unknown one with rebuild advice.
  - It exposes `self.tokenizer` (from the file's settings) and `has_lote_column` (`schema_version == "1.2"`).
  - `BM25Retriever` calls `self._lexical.tokenizer.query_terms`, so a file is always queried with its own tokenizer.
  - `LexicalSettings.schema_version` accepts `"1.1"` and `"1.2"`. The builder writes `"1.2"` only; 1.0 is still refused as today.
- **Builder:** `build_lexical_index(entries, target, identity, tokenizer)` writes the tokenizer's name and version, its `tokenize` output into `chunk_terms`, and the `lote_languages` column.
- **Builder CLI:** `make index-lexical` takes `--tokenizer lexical-v1|lexical-v2` (`LEXICAL_ARGS`). Without the option it uses `lexical.tokenizer` from `config/retrieval.yaml` (new key, schema 1.2, value `lexical-v1` until R10).
- **Retrieval config:** `RetrievalConfig` reads 1.1 files as `lexical.tokenizer: lexical-v1`, so older config copies in tests still load. Retrieval does not consult the config key; a file's recorded tokenizer is what queries use.
- **Two files side by side (R6, R10):** the file path stays `<W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite`. The second arm uses another directory, for example `W2A_LEXICAL_INDEX_DIR=.local/lexical-v2`, which is already git-ignored under `.local/`. No new path option is added.
- `verify_fresh`, `check_identity` and `bind_to` do not compare tokenizers, so either file passes them.

### Script mix (R7)

```python
def script_mix(text: str) -> str:
    scripts = {unicodedata.name(ch, "").split(" ", 1)[0].lower()
               for ch in text if unicodedata.category(ch).startswith("L")}
    scripts.discard("")
    return "+".join(sorted(scripts)) or "none"
```

- **Letters only.** Digits (`N*`), punctuation (`P*`), symbols (`S*`, for example `₹`), whitespace (`Z*`), format characters (`Cf`, ZWJ/ZWNJ) and combining marks (`Mn`/`Mc`: virama, vowel signs) are skipped, so they add no script.
- **First word of the character name.** Examples: `LATIN SMALL LETTER A` → `latin`; `MALAYALAM LETTER CHILLU L` → `malayalam`; `DEVANAGARI LETTER KA` → `devanagari`.
- **Known approximation, documented and tested:** a few letter names do not start with a script name (for example `MODIFIER LETTER …` → `modifier`, `CJK UNIFIED IDEOGRAPH-…` → `cjk`). For the current suite (Latin and Malayalam) the result equals the Unicode `Script` property; a test asserts this for every letter in every v3 query.
- **No new dependency.** The alternative, a range table generated from `Scripts.txt`, is recorded under Alternatives.
- Romanized Malayalam (`g062`) gives `latin`. `COMMANDS.md` and the decision say so.

### Continuity command (R10)

- **Invocation:** `make eval-continuity BASE=<file> CANDIDATE=<file>` runs `evaluation/continuity.py`.
- **Inputs:** two result files, 2.3 or 2.4.
- **Identity must match:** collection, `index_version`, chunker, embedder pair, lexical identity, served strategy and `top_k`. A mismatch refuses with exit 2.
- **Allowed to differ, printed as lines:** suite ID and version, `lote`, case set and `git_commit`.
- **Compared:** for every golden `case_id` present in both files with the same `case_version`, it compares `hit`, `reciprocal_rank` and `ranked_document_ids`. It prints the shared count, the cases only in each file, and every differing case with old -> new values.
- **Exit codes:** 0 when no shared case differs, 1 when any does, 2 when a file is unreadable or not comparable.
- **Tests:** fixture result files under `packages/rag/tests/evaluation/fixtures/`.

## Data flow

Sequence for `make eval-retrieval --lote ml --strategy hybrid`:

1. `resolve_lote("ml", active_lote_codes(repo_root))` returns `ResolvedLote("ml")`. An invalid code exits 2 here, before Qdrant is opened.
2. `open_retrieval(...)` runs unchanged. `OpenedRetrieval.document_count(access, lote)` counts applicable eligible documents for the random expectation:
   - dense: Qdrant count with the combined filter;
   - lexical: `COUNT(DISTINCT document_id)` with both clauses, which needs the column when a `lote` is given.
3. Per case, `retriever.retrieve(query, access, depth, lote=lote)`:
   - `FallbackRetriever` (open-time or per-query, same `lote`) or `HybridRetriever` runs both legs with `lote`;
   - dense: `Filter(must=[access…, lote_condition])`, then `check_hit`, then `check_applicable`;
   - BM25: `WHERE MATCH ? AND <access> AND <lote>`, then `check_hit`, then `check_applicable`;
   - RRF fusion runs on hits that are already checked, then `dedupe_documents`.
4. Each row gets `script_mix(case.query)`. Results add `lote` and `by_script_mix` and are written as 2.4.

With no `lote`, step 1 yields `None`, no condition is added and no re-check runs. The SQL and the Qdrant filter are byte-identical to today; a test asserts this.

## Interfaces / models

- **`RetrievalResult.lote: str | None = None`.**
- **Result 2.4 (`retrieval_evaluation`):**
  - top level gains `lote` (string or `null`) and `metrics.by_script_mix`, with the same shape as `by_query_language`: `hit_rate_at_5`, `recall_at_5`, `mrr`, `n`, `small_sample`;
  - each case row gains `script_mix`.
  - `results.read_result` reads 2.0–2.4. For files older than 2.4, `lote` reads as `None` and `by_script_mix` is absent.
- **`eval-compare`:**
  - `COMPARE_ARGS=--cross-tokenizer` relaxes only the tokenizer name and version in `_identity_problems`. `source_chunk_digest` and `chunk_count` still must match; they don't depend on the tokenizer, because the digest covers point ID, document ID, version and hash.
  - It can be combined with `--cross-index`; each option relaxes only its own fields.
  - A `lote` difference is refused in every mode as `lote changed <old> -> <new>`, with `null` printed as `none`.
  - Without the option, a tokenizer difference gets the advice line `use COMPARE_ARGS=--cross-tokenizer only when …`.
- **Security result 1.4 (`security_evaluation`):** the 1.3 keys, plus:
  - `lote_modes`: `[null, "<code>"]`;
  - per run: `authorization_violations` and `applicability_violations` (counts and IDs);
  - `non_applicable_rows_per_variant`;
  - `passed`, which requires zero of both.
- **Lexical settings 1.2:** the 1.1 fields; `chunks` gains `lote_languages TEXT NOT NULL`. A payload without a list of strings raises `LexicalIndexError` at build time, and the temporary file is removed.
- **`config/retrieval.yaml` 1.2:** adds `lexical: {tokenizer: lexical-v1}`. `RetrievalConfig` validates the name against `TOKENIZERS`.
- **Errors:**
  - `LanguageApplicabilityError(RetrievalError)` has a `document_id`. It is a sibling of `RetrievalAuthorizationError`, not a subclass, and it is not a `RetrievalUnavailableError`.
  - The CLIs already map every `RetrievalError` to exit 2 with a path-free message. That is unchanged, so the error refuses the run the same way an authorization error does.

## Error and failure behavior

| Situation | Behaviour |
|---|---|
| `--lote` unknown, inactive, `en`, `*` or empty | `RetrievalConfigurationError`, exit 2, before any Qdrant or lexical access; message lists active codes |
| `--lote` given, lexical file is settings 1.1 (no column) | `LexicalIndexBindingError` from `BM25Retriever` (also from the lexical `document_count`), exit 2, advice `make index-lexical`; not fallback-eligible |
| No `lote`, lexical file 1.1 | served exactly as today |
| A hit violates access | `RetrievalAuthorizationError` (unchanged, checked first) |
| A hit passes access but is not applicable / malformed `lote_languages` | `LanguageApplicabilityError`, exit 2; never caught by `FallbackRetriever`; in the security gate an applicability violation |
| Lexical file records an unknown tokenizer | `LexicalIndexBindingError` at open, rebuild advice |
| `make index-lexical --tokenizer` unknown | exit 2, names known tokenizers |
| `eval-compare` tokenizer differs without option / `lote` differs | exit 2 with the named difference |
| `eval-continuity` identity mismatch / unreadable | exit 2; shared case differs: exit 1 |
| Security sanity check: non-applicable row not ranked first under the access filter alone | harness error, exit 2 (never a pass) |

## Security / authorization

- **Authorization comes first and doesn't change.** The access builders and `check_hit` keep their output and order. Applicability only adds conditions, so with a `lote` the candidate set is a subset of what access alone allows. This is tested: on every path, `set(hits with lote) ⊆ set(hits without lote)` on the security corpus.
- **Separate error.** `LanguageApplicabilityError` and its own security counter keep the two concerns apart (C4). An access violation is never reported as an applicability violation. When a hit fails both checks, `check_hit` runs first and authorization wins.
- **Fixed gate inputs.** The security gate's `lote` comes from the registry, never from a case or query. Cases keep `access_context` only.
- **Rows in the security gate (R9):** non-applicable rows are public, belong to the server tenant and have a null owner, with `lote_languages: ["zz"]`.
  - `zz` is a well-formed code that is not assigned. The harness refuses to run if it ever becomes active.
  - Each row carries every query's tokens, so it is nearest in both legs. There is one row per gated query, like the forbidden rows.
  - A new access-forbidden variant `staff_scope_lote` (staff scope, `lote_languages: [<active code>]`) joins the existing forbidden rows, which use `["*"]`. So "forbidden even though applicable" covers both `["*"]` and the explicit code.
- **Sanity checks per leg:** with the access filter alone (no `lote`), a non-applicable row ranks first. That shows the applicability filter is what removes it. The existing unfiltered check for access-forbidden rows is unchanged.
- **Both modes are gated** for each chunker and path:
  - `lote: null`: access-forbidden rows are a violation; non-applicable rows are allowed.
  - `lote: <code>`: both kinds are violations.
- **Docker isolation test** (`test_security_integration.py`): adds non-applicable points and asserts they are excluded with a `lote` on the real Qdrant server.
- **Corpus statistics:** the lexical file holds only eligible public chunks for every language. Filtering by language at query time doesn't change IDF, and a `lote` can't reveal anything access forbids. D050's per-scope note is unchanged.

## Observability

- `make retrieve` prints `lote: <code|none>` and the lexical tokenizer of the file it used.
- Result 2.4 records `lote`, the tokenizer (already in `lexical_index`) and the script-mix slice.
- `make index-lexical` prints the tokenizer and the lexical settings version.
- No Langfuse yet (roadmap 11).

## Testing / evaluation strategy

- **Unit tests (`make verify`, no extra, Docker or model; also with `HF_HOME` empty and `HF_HUB_OFFLINE=1`):**
  - `resolve_lote` with a temporary registry: an active code passes; unknown, inactive, `en`, `*`, empty and `None` behave as specified.
  - The SQL and Qdrant builders: exact output, bound parameters, no change to the access builders' output.
  - **Store parity.** One set of tagged rows is loaded into an in-memory Qdrant collection and a temporary lexical file, then queried with each `lote` (the active code, a second code, none) through the Qdrant condition and the SQL clause. The two stores return identical document sets. The rows are `["*"]`, `[code]`, `[code, other]` and `[other]`. A row tagged `["*", code]` is refused by the lexical builder, and on the Qdrant side, written by a raw upsert, it raises `LanguageApplicabilityError` from `check_applicable` for every `lote`. So neither store returns it on any path.
  - `valid_lote_languages`: `["*"]`, single and multiple codes, duplicates, empty, `["*", code]`, non-list.
  - Per path (dense, standalone bm25, hybrid, fallback open, fallback query): a non-applicable chunk that ranks first is excluded with a `lote` and returned without one. A store with the filter dropped by injection makes `check_applicable` raise. Malformed `lote_languages` raises. `LanguageApplicabilityError` is not caught by `FallbackRetriever`.
  - Seed corpus with the fake embedder: `lote` set to the active code returns the same hits as no `lote`, on every strategy (R3).
  - Lexical:
    - every table pair, inside a word and at word end;
    - `lexical-v2` equals `lexical-v1` on every seed chunk and every v3 query that contains no listed sequence;
    - the D051 `lexical-v1` pin still holds;
    - a file is queried with its own tokenizer;
    - a 1.1 file serves without a `lote`, and is refused with one;
    - 1.2 files are built with each tokenizer;
    - `--tokenizer` and the config default.
  - BM25 authorization and applicability tests are parametrized over both tokenizers.
  - `script_mix`: each character class that adds no script; `₹1,300 mock-ൽ`; a virama and vowel signs inside a word; `g062` → `latin`; the name-prefix result equals the Unicode `Script` property for every letter in the v3 queries (asserted with a small fixture of known scripts, no new dependency).
  - Result 2.4 keys; readers for 2.0–2.4.
  - `eval-compare`: tokenizer refused without the option, accepted with it, another identity difference still refused with it, `lote` refused.
  - `eval-continuity`: equal, differing, only-in-one-file, identity mismatch, unreadable.
  - Security 1.4: both modes, the sanity checks, the new variant, the `zz` guard; the existing 1.3 tests adapted.
  - Suite v3: rows carried from v2 equal field by field, the v2 dataset hash, promotion checks in `make validate-evaluation`, slice minimums (at least 12 `ml`, at least 12 `mixed`, at least 3 unanswerable `ml`).
- **Integration tests (`make test-integration`):** the Docker applicability isolation test.
- **Real runs (T5, user-owned):**
  1. Build `lexical-v1` into `.local/lexical`.
  2. Build `lexical-v2` with `W2A_LEXICAL_INDEX_DIR=.local/lexical-v2 make index-lexical LEXICAL_ARGS="--tokenizer lexical-v2"`. Both builds are for `w2a-realcheck-idx-v2`.
  3. Run four `make eval-retrieval --lote ml` arms (hybrid and bm25, each tokenizer).
  4. Run `make eval-continuity BASE=…idx-v2-20261103T104934Z.json CANDIDATE=<hybrid v1 v3 run>`. It must exit 0 over the 69 shared goldens.
  5. Run two `make eval-compare COMPARE_ARGS=--cross-tokenizer` comparisons, with `lexical-v1` as base.
  6. Apply the R10 rule. Record every output in `task-reviews.md`.

## Phase 2 compatibility / migration

- **Lexical files:** existing 1.1 files keep working without a `lote`. A one-time `make index-lexical` gives each collection settings 1.2. The default index needs no Qdrant change, no re-ingestion and no new `index_version`.
- **New languages:** adding an active LOTE (for example `ta`) is a registry entry plus documents with `lote_languages` that include it. `resolve_lote` and both filters need no code change. A non-Latin script gets its script-mix key automatically. A script with its own legacy-sequence equivalences is a new tokenizer version with more table rows, not a code branch.
- **Roles:** `ResolvedLote` is orthogonal to roles. A future staff or subscriber policy changes `ResolvedAccess` only.
- **Phase 2 releases:** suite v3 is a normal versioned suite. The Knowledge Release `seed-v1` still names v1 (D049, known issue).

## Alternatives / deferred decisions

- **`json_extract` on `payload_json` for the SQL condition:** rejected at requirements approval. It is less explicit than the access clause, and the rebuild happens anyway.
- **A child table `chunk_lote_languages(chunk_rowid, code)` with `EXISTS`:** more relational, but the user asked for a column on `chunks`. Separated codes plus `instr` keep a single explicit column with bound parameters.
- **Putting `lote` inside `AccessContext`:** rejected by C4. Language must never be able to affect authorization.
- **A Scripts.txt range table for script mix:** exact `Script` property values, but a committed generated file and a version to maintain. The name prefix is exact for the suite's scripts and needs no file; switch if a future script's letter names don't start with the script name.
- **Character n-grams or Malayalam stemming:** declined (expected to show nothing on an English corpus). **Per-script fusion weighting:** declined; roadmap 9.
- **Query translation or transliteration:** the fix for `g067`–`g069` on the BM25 fallback; carry-over.
- **Default `lote` from config (always on):** declined at the Decision Brief (Q1). No value means no filter.

## As-built notes

- **T5 tokenizer promotion.** Default `config/retrieval.yaml` → `lexical.tokenizer: lexical-v2` (tie on cross-tokenizer compares; zero measured gain on seed because no legacy chillu ZWJ sequences in corpus or v3 queries). v3 hybrid reference: `experiments/results/retrieval-evaluation-idx-v2-20261104T105300Z.json`; bm25: `…20261104T105321Z.json`. BM25-only `ml` MRR 0.2396 (n=16) on realcheck.

- **R10 continuity.** Spec 009 hybrid reference `…idx-v2-20261103T104934Z.json` vs hybrid lexical-v1 v3 arm: module exit 0, 69 shared goldens identical; suite/lote/git lines printed only. Invoked as `uv run python -m way2australia_rag.evaluation.continuity` (not `make eval-continuity`) so exit 1 means case differences.

- **`make eval-continuity` and GNU make.** Recipe exit 1 (shared cases differ) becomes make exit 2; stderr prints `eval-continuity: exit 1` (T3 round 2). Operators read that line or call the module directly for 0/1/2 semantics (documented in `COMMANDS.md`).

- **`eval-compare --cross-index`.** T3 round 2: lexical `source_chunk_digest` and `chunk_count` are skipped when `--cross-index` is set (D069 behaviour restored vs round-1 regression); still enforced for `--cross-tokenizer` without `--cross-index`.

- **`make retrieve` smoke.** Does not print lexical tokenizer name; promotion evidence is `make index-lexical` output (settings 1.2, tokenizer name/version) — user-accepted T5 deviation.

- **`open_retrieval`.** Does not verify that the opened lexical file's recorded tokenizer matches `config/retrieval.yaml`; a stale `lexical-v1` file would serve silently after v2 promotion. Carry-over to roadmap item 10 startup policy (`CURRENT_STATE.md`).

- **Script mix.** Uses the first word of each letter's Unicode name (not Scripts.txt); romanized Malayalam queries (for example `g062`) report `latin`. Tests pin name prefixes against a small fixture; unmapped letters in v3 queries fail tests.

- **Candidate schema (T1 amendment).** `candidate_row.proposed_case` is a `oneOf` golden or unanswerable shape; unanswerable candidates require `query_language`.

- **Registry parsing.** `languages.py` (package root) owns `_active_product_support_codes`; `evaluation/slices.active_registry_languages` reuses it and adds `en`. Approved design already placed `languages.py` at the package root; T6 `ARCHITECTURE.md` had listed it under `retrieval/` (retrospective F1).
