# 006 — Evaluation Framework Design

Status: approved (2026-10-24)

## Design summary

A new package `packages/rag/src/way2australia_rag/evaluation/` holds the governed suite loader, the evaluation runners, the result format and the comparison tool. It sits on top of `retrieval/` and does not change it, with one minimal exception added by the 2026-10-24 amendment (T8a, T5 review F1): `RetrievalAuthorizationError` (`retrieval/errors.py`) gains a `document_id` attribute, set at both raise sites in `retrieval/access.py`. Its message text is unchanged, and no other `retrieval/` behavior changes:

- `DenseIndex`, `DenseRetriever`, `resolve_access`/`guest_access`, `build_access_filter`, `check_hit`, `safe_text` and `retrieval/metrics.py` are imported unchanged. There is one access policy path (D035, D040).
- `retrieval/metrics.py` stays where it is, byte-for-byte. Section-level metrics are a thin layer in `evaluation/` that calls the same functions with section keys.
- `retrieval/baseline.py` and `retrieval/baseline_cli.py` (legacy `make retrieval-baseline`) are not edited. Only `retrieval/goldens.py` becomes a thin compatibility wrapper over the new loader. A characterization test, written before the change, pins its output byte-for-byte.
- One CLI module with four subcommands sits behind four make targets: `validate-evaluation`, `eval-retrieval`, `eval-security`, `eval-compare`.
- The security gate builds a throwaway in-memory Qdrant collection with the fake embedder. Forbidden points get exactly the query's vector, so they are the nearest by construction. The unfiltered nearest neighbour is checked to be forbidden, so the gate cannot pass vacuously. The same builder runs against Docker Qdrant in an integration test (R9).
- Under `evaluation/`, exactly three files are added: two schema files and one candidates file. Nothing existing is edited.

## Package / file placement

```text
packages/rag/src/way2australia_rag/evaluation/
├── __init__.py            # docstring only (same convention as retrieval/)
├── errors.py              # EvaluationError, EvaluationConfigurationError
├── models.py              # SuiteManifest, DatasetRef, case models, CandidateRow, LoadedSuite
├── schemas.py             # loads the three case/suite schemas into a local referencing Registry
├── suite.py               # read_manifest, read_dataset, load_suite, declared_release_id
├── validate.py            # validation checks behind `make validate-evaluation`
├── slices.py              # query_language / category / source_authority slices, small_sample, absent languages
├── sections.py            # section-level metrics over (document_id, section_id) keys
├── retrieval_eval.py      # run_retrieval_evaluation -> result document 2.0
├── results.py             # result constants, default paths, read_result (1.0 and 2.0) -> ComparableRun
├── compare.py             # compare(base, candidate) -> Comparison; gate rule constants
├── security_corpus.py     # build_security_repository(fixture_root, work_dir): isolated repository (moved from tests/conftest.py)
├── security_index.py      # build_security_index (throwaway, fake embedder, w2a-sectest-* only)
├── security_eval.py       # run_security_evaluation -> gate result
└── cli.py                 # `python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}`

packages/rag/src/way2australia_rag/retrieval/goldens.py   # becomes a compatibility wrapper (R1, R12)
packages/rag/src/way2australia_rag/retrieval/errors.py    # T8a: RetrievalAuthorizationError.document_id (message unchanged)
packages/rag/src/way2australia_rag/retrieval/access.py    # T8a: both check_hit raise sites pass document_id
packages/rag/pyproject.toml                               # T8a: `referencing` declared directly (imported by schemas.py; already locked)

evaluation/schemas/evaluation_suite.schema.json           # NEW (R2)
evaluation/schemas/evaluation_case_types.schema.json      # NEW (R2)
evaluation/candidates/006-candidates.jsonl                # NEW (R14)

packages/rag/tests/evaluation/                            # new test package (see Testing)
packages/rag/tests/retrieval/fixtures/legacy_baseline_snapshot.json  # characterization snapshot (R12)

Makefile        # validate-evaluation (added to verify), eval-retrieval, eval-security, eval-compare
.gitignore      # experiments/results/tmp/
```

Nothing else changes under `evaluation/`. `knowledge/`, `config/`, `experiments/configs/` and the committed result file are not touched. `tests/conftest.py` keeps its `security_repository` fixture, but now calls `security_corpus.build_security_repository(fixture_root=REPO_ROOT / "tests/fixtures/security", work_dir=tmp_path)`, so the copying logic lives in one place. Library code never names `tests/fixtures/security`. Only the CLI (`--fixture-root`, default `<repo-root>/tests/fixtures/security`) and the tests supply that path.

## Components / boundaries

| Component | Responsibility | Reads | Writes |
|---|---|---|---|
| `suite.py` | Parse the suite manifest and datasets into typed models. Tolerate extra fields. Ignore `access_context`. Refuse unknown dataset types and escaping paths. | `evaluation/suites/*.json`, the listed datasets, `knowledge/releases/<id>.json` | nothing |
| `schemas.py` | Load `evaluation_case.schema.json` (existing) and the two new schema files into one `referencing.Registry` keyed by `$id`. No network resolution. | `evaluation/schemas/` | nothing |
| `validate.py` | All R2 checks. Collects every problem, then exits 0, 1 or 2. | suite, datasets, schemas, candidates, document repository | nothing |
| `retrieval_eval.py` | Run active goldens and unanswerable cases through `DenseRetriever`. Compute metrics, slices, section block and unanswerable report. Build the 2.0 document. | index (read-only), repository (for `source_authority`), `config/language_registry.json` | nothing (the CLI writes) |
| `results.py` / `compare.py` | Read 1.0 or 2.0 into one comparable form. Refuse unlike runs. Compute deltas, flips and the gate. | two result files | nothing |
| `security_index.py` | Build a throwaway fake-embedder collection with seed points and forbidden points. | seed repository, isolated security repository | only a `w2a-sectest-*` collection on the client it is given (in-memory by default) |
| `security_eval.py` | Run the retrieval-side security cases and all active golden queries. Run the unfiltered sanity check, then the authorized retrieval, and report violations. | the security index | nothing (the CLI writes JSON to `experiments/results/tmp/` or `--output`) |
| `goldens.py` (wrapper) | Keep the Spec 005 names, selection rule, messages and error class for legacy `retrieval-baseline`. | as before | nothing |

Boundaries:
- `evaluation/` depends on `retrieval/`, `ingestion/` and `repositories/`. Nothing in those packages imports `evaluation/`, except `retrieval/goldens.py`, the compatibility wrapper.
- There is no evaluation-specific access code. Every retrieval goes through `DenseRetriever.retrieve(query, access, top_k)` with `access = resolve_access(guest_access(settings))`.

## Data flow

### `make validate-evaluation` (R2, runs in `make verify`)

1. `schemas.py` builds the registry. A missing or invalid schema is exit 2.
2. Read and validate the suite manifest against `evaluation_suite.schema.json`.
3. For every dataset, check each line against `evaluation_case_types.schema.json#/$defs/<dataset type>`. That definition is `allOf` the existing `evaluation_case.schema.json` plus the type's required fields, so the existing schema is reused, not edited.
4. Run the cross-checks:
   - `case_id` unique across the suite;
   - every case's `evaluation_suite_id` equals the suite's;
   - `case_count` equals the number of case lines;
   - no dataset path appears twice.
5. Check relevant documents through the repository, never file paths. `LocalDocumentRepository(LocalRepositoryConfig(repo_root))` lists all documents, and `list_eligible_documents(repo, GUEST_PUBLIC_POLICY)` gives the eligible ones. An ID that is not in the corpus gives "unknown document". An ID that is in the corpus but not in the eligible set gives "document not eligible for guest/public".
   - A repository error (invalid corpus) is exit 2, with advice to run `make validate-knowledge`.
6. Validate each candidate row in `evaluation/candidates/*.jsonl` against `evaluation_case_types.schema.json#/$defs/candidate_row`:
   - `status` must be `suggested`;
   - a `proposed_case` must validate against the golden definition, with its status `suggested`;
   - its relevant documents must be eligible (same check as step 5);
   - no suite's `datasets[].path` may point under `evaluation/candidates/`.
7. Print one line per problem (`<file>:<line> <case_id> <field>: <reason>`, through `safe_text`) and a count. Exit 0 if there are no problems, 1 if there are problems, 2 on configuration errors.

### `make eval-retrieval` (R4–R7, R10)

Startup order. Every file check runs before any Qdrant contact, as in Spec 005:

1. Check `--top-k`.
2. Load config (`config/ingestion.yaml`) and runtime settings (`load_runtime_settings`).
3. `load_suite` and `declared_release_id`. A suite whose manifest `status` is not `active` is refused with exit 2: "suite '<id>' has status '<status>'; only an active suite is evaluated". This is a design-level rule approved at design approval; R4 does not state it. `validate-evaluation` still validates and reports any suite, whatever its status.
4. Load the repository and build a `source_authority` map: `document_id` to `source_authority` over the eligible documents.
5. Read the language registry: `product_support.*.internal_code` where `status == active`, plus `en`. This is data, not code, so there is no `ml` literal in code.
6. Resolve and check the output path. The default is `experiments/results/retrieval-evaluation-<index_version>-<UTC>.json`.
7. Build the embedder from `config.embedder.provider`. If the embedder is fake, refuse with exit 2 here, before any Qdrant contact. There is no `--embedder` or `--allow-fake` flag.
8. Create the client and call `DenseIndex.open(client, settings.collection_base, config.index_version, embedder.info)`. This is read-only, and the D036 binding rules apply.
9. If `index.settings.embedder_is_fake`, refuse with exit 2. This is a second refusal: a fake index can only bind a fake embedder, which step 7 already refused, but the check stays explicit.
10. `access = resolve_access(guest_access(settings))`.
11. Run the evaluation:
    - one unmeasured warm-up query (the first active golden);
    - `document_count = index.document_count(build_access_filter(access))`;
    - each active golden case, in dataset order;
    - each active unanswerable case, recording only its top-1 score. Its latency is not in p50/p95, so p50/p95 stays comparable with 1.0.
12. Build the 2.0 document and write it with `retrieval.baseline.write_result`, imported unchanged: exclusive create, partial-file cleanup, never overwritten.
13. Print the summary through `safe_text`.

The collection comes from `QDRANT_COLLECTION_BASE` and `index_version`, exactly as for `make retrieve`. There is no new configuration file (`config/` is protected) and no refusal of the default collection. The collection name is recorded and printed.

### `make eval-security` (R8)

1. Load the suite. Select the active security cases whose `attack_type` is in `RETRIEVAL_SIDE_ATTACK_TYPES`, plus all active golden cases. List the rest as deferred.
2. Create `QdrantClient(location=":memory:")`, a `FakeEmbedder(vector_size=FAKE_VECTOR_SIZE)` and a collection base `w2a-sectest-<8 hex>` (`uuid4`).
3. `build_security_index(client, base, queries, embedder, chunker)`:
   - Create the collection and its settings record with `QdrantIndexStore.ensure_collection`, using fake-identity `IndexSettings` (`index_version = "sec-v1"`).
   - Seed points: the eligible seed corpus (`list_eligible_documents`), chunked with the configured `HeadingChunker` and written with `build_payload` and `point_id` through `QdrantIndexStore.replace_document`. This is the production path.
   - The isolated security repository (`security_corpus.build_security_repository`) copies an explicit list of fixture file names, the constant `SECURITY_FIXTURE_FILES = ("poisoned_public_document.md", "staff_only_canary.md")`, never a glob (2026-10-24 amendment, T5 review F4). It refuses, with `EvaluationConfigurationError` (exit 2) before copying anything, a fixture root that holds any other visible entry (for example a stray `README.md`) or lacks a listed file. Hidden (dot-prefixed) entries such as `.DS_Store` (macOS Finder noise) are ignored, never copied and never refused. The message names the file name only, never an absolute path.
   - Canary points: `fixture_staff_canary` from the isolated security repository (`security_corpus.py`, the same copy-to-temp approach as `tests/conftest.py`), as real `build_payload` points. One point keeps the canary's own text vector. One more point per query reuses the canary payload, with `chunk_position` set to the query's index and the vector `embedder.embed_query(query)`.
   - Synthetic forbidden points, one per query and per variant, written with a raw `client.upsert`, because one variant breaks the `PointPayload` model on purpose. Each starts from a valid public payload with document ID `forbidden_<variant>`. The four variants:
     - `staff_scope`: `access_scope: staff`;
     - `other_tenant`: `tenant_id: "<server tenant>-other"`;
     - `owned`: `owner_user_id: "eval-user"`;
     - `missing_owner`: the `owner_user_id` key is removed.

     `chunk_position` is the query index, `chunk_text` is the fixed sentinel `"forbidden fixture"` (never the query), and the vector is `embedder.embed_query(query)`. Point IDs use `point_id("forbidden_<variant>", "main", query_index)`.
4. For each query:
   - Sanity check: an unfiltered `client.query_points` with `limit = 5` must have a forbidden or canary point at rank 1. A forbidden point's vector equals the query vector, so its cosine is 1.0, and no seed point can score higher. Otherwise this is a harness error (exit 2), never a pass.
   - Authorized retrieval: `DenseRetriever(DenseIndex.open(client, base, "sec-v1", embedder.info), embedder).retrieve(query, access, top_k=MAX_TOP_K)`.
   - A returned `document_id` in the forbidden set (`fixture_staff_canary`, `forbidden_*`) is a violation. A `RetrievalAuthorizationError` from `check_hit` is also a violation (the store returned an unauthorized point). The violation's `document_id` is read from the error's `document_id` attribute, never parsed from its message (2026-10-24 amendment, T5 review F1).
5. Check that the filter is identical for every query: `build_access_filter(access)` is built once and compared with the filter passed to `search`, through a spy index in tests. A second test asserts that the filter is unchanged after running the injection-style queries (`s003`).
6. Report. Exit 0 if there are no violations. Exit 1 on any violation, naming the `case_id`, `document_id` and variant, never text. Exit 2 on a harness or configuration error. The collection is deleted at the end; the in-memory client is discarded.
7. JSON is written only to `experiments/results/tmp/security-evaluation-<UTC>.json` (git-ignored) or to `--output`, again with the exclusive writer.

`poisoned_public_document.md` is not part of the authorization gate. Its scope is `public`, so the access filter correctly allows it. What keeps it out of production is ingestion eligibility (synthetic), not retrieval authorization (D026). It belongs to the prompt-injection tests (roadmap 12). The result lists it under `excluded_fixtures` with that reason.

### `make eval-compare BASE=... CANDIDATE=...` (R11)

1. `read_result(path)` accepts exactly two forms. Anything else is exit 2.
   - `kind: retrieval_baseline` with `schema_version: "1.0"`: Spec 005's format, read as-is.
   - `kind: retrieval_evaluation` with `schema_version: "2.0"`.

   A file whose per-case rows repeat a `case_id` (with the same or a different `case_version`) is refused with exit 2, naming the file name and the `case_id` (2026-10-24 amendment, T6 review F5). One suite never holds two versions of one case, so a repeated `case_id` means a broken or hand-edited file.

   It produces a `ComparableRun`:
   - identity: suite ID and version, `top_k`, `document_count`, `embedder_is_fake`;
   - per-case map `(case_id, case_version)` to `(hit, recall, reciprocal_rank)`;
   - per-case slice keys: `query_language` and `category` (both formats) and `source_authority` (2.0 only);
   - informational fields: collection, `index_version`, `index_settings`, device, git commit, latency.
2. Refuse (exit 2) on any of these:
   - suite ID or version differ;
   - the case key sets differ;
   - `top_k` differ;
   - `document_count` differ;
   - either run is fake.
3. Compute from the per-case rows, not the rounded aggregates:
   - `hits_base`, `hits_cand`;
   - mean reciprocal rank for each side, unrounded;
   - n = the number of compared cases.
4. Gate:
   - fail if `hits_cand < hits_base - HIT_TOLERANCE_CASES` (constant 1);
   - fail if `mrr_base - mrr_cand > 1/n + 1e-9`. The epsilon only absorbs float error.
   - Otherwise pass.
5. Print, through `safe_text`:
   - overall and per-slice deltas. The `source_authority` slice is shown only when both runs are 2.0, otherwise a note says it was not compared;
   - latency deltas;
   - identity differences;
   - `WARNING flipped hit->miss: g026 (v1)` and `WARNING flipped miss->hit: ...` lines, sorted by `case_id`;
   - the verdict.
6. Exit 0 on pass (warnings allowed), 1 on gate failure, 2 on refusal.

## Interfaces / models

```python
# evaluation/models.py — all pydantic, extra fields tolerated on cases
class DatasetType(StrEnum): GOLDEN_ANSWERABLE, UNANSWERABLE_REFUSAL, SECURITY
class CaseStatus(StrEnum):  # mirrors evaluation_case.schema.json
    ACTIVE, REVIEW_REQUIRED, POTENTIALLY_OBSOLETE, DEPRECATED, REPLACED, SUGGESTED

class DatasetRef(BaseModel): type: DatasetType; path: str
class SuiteManifest(BaseModel):     # extra="ignore"
    evaluation_suite_id: str; version: int; datasets: list[DatasetRef]
    status: str = ""; introduced_in_release: str = ""; case_count: int | None = None

class CaseBase(BaseModel):            # extra="ignore"
    case_id: str; case_version: int
    status: str                        # plain string; CaseStatus is checked by validate-evaluation
    evaluation_suite_id: str = ""; query: str
    access_context: dict[str, Any] | None = None   # loaded, never used
class GoldenCase(CaseBase):
    answerable: bool; relevant_document_ids: list[str]
    relevant_section_ids: list[str] = []; query_language: str; category: str
class UnanswerableCase(CaseBase): answerable: bool; expected_behavior: str
class SecurityCase(CaseBase): attack_type: str; expected_behavior: str

class LoadedSuite(BaseModel):
    manifest: SuiteManifest
    goldens: list[GoldenCase]; unanswerable: list[UnanswerableCase]; security: list[SecurityCase]
    def active(self, dataset_type) -> list[...]          # status == active only
    def excluded_by_status(self, dataset_type) -> dict[str, int]

# evaluation/suite.py
def read_manifest(repo_root: Path, suite_path: str | Path) -> SuiteManifest
def read_dataset(repo_root: Path, ref: DatasetRef) -> list[CaseBase]   # typed by ref.type
def load_suite(repo_root: Path, suite_path: str | Path) -> LoadedSuite
def declared_release_id(repo_root: Path, release_id: str) -> str       # moved from goldens.py

# evaluation/security_eval.py
RETRIEVAL_SIDE_ATTACK_TYPES = frozenset({"authorization_bypass", "filter_injection",
    "paid_content_exfiltration", "context_exfiltration", "privacy_exfiltration"})
DEFERRED_OWNERS = {"system_prompt_extraction": "roadmap-12", "ungrounded_generation": "roadmap-10",
    "citation_manipulation": "roadmap-10", "indirect_prompt_injection": "roadmap-12",
    "denial_of_wallet": "roadmap-12"}            # anything else -> "unclassified"
FORBIDDEN_VARIANTS = ("staff_scope", "other_tenant", "owned", "missing_owner")
SECURITY_COLLECTION_PREFIX = "w2a-sectest-"

SECURITY_COLLECTION_BASE_RE = re.compile(r"^w2a-sectest-[0-9a-f]{8}$")

def build_security_repository(fixture_root: Path, work_dir: Path) -> LocalDocumentRepository
    # explicit fixture root, no default path in library code

def build_security_index(client, collection_base, queries, embedder, chunker, *,
                         seed_repository, security_repository, tenant_id) -> SecurityIndex
    # enforced in code: collection_base must match SECURITY_COLLECTION_BASE_RE,
    # and neither the collection nor its -settings may already exist on the client
    # (it only ever creates a new throwaway collection); otherwise
    # EvaluationConfigurationError before any write
def run_security_evaluation(index: SecurityIndex, access: ResolvedAccess,
                            cases, deferred) -> SecurityReport

# evaluation/compare.py
HIT_TOLERANCE_CASES = 1
def mrr_tolerance(n: int) -> float: return 1.0 / n
def compare(base: ComparableRun, candidate: ComparableRun) -> Comparison   # raises on unlike runs
```

Loader models versus validation (as built in T1, review F1). The loader models are deliberately tolerant:
- `CaseBase.status` is a plain `str`, not `CaseStatus`. The legacy tests use a `retired` status that must still load and be excluded.
- `SuiteManifest.status`, `introduced_in_release` and `case_count`, and `CaseBase.evaluation_suite_id`, have defaults, because the legacy temp suites omit them.

So allowed status values and required suite and case fields are enforced by `validate-evaluation` through `evaluation_suite.schema.json` and `evaluation_case_types.schema.json` (T2), never by the loader models. A status outside `CaseStatus` is simply not `active`, so it never runs.

Allowed suite manifest `status` values (as built in T2, review F4; enforced by the `enum` in `evaluation_suite.schema.json`): `draft`, `active`, `deprecated`, `replaced`. An empty or missing value is rejected. These differ from the case statuses on purpose: a suite has no `review_required`, `potentially_obsolete` or `suggested` state, and a case has no `draft` state. Only `active` is evaluated by `eval-retrieval` and `eval-security`; every other value is refused with exit 2.

`retrieval/goldens.py` after the change keeps its public names:
- `GoldenCase` is re-exported from `evaluation.models` with the same fields plus defaults.
- `SuiteRef` and `load_suite` keep the "exactly one `golden_answerable` dataset" rule and the same messages.
- `load_golden_cases` reads only the golden dataset through `read_dataset` and keeps the same selection (active, answerable, non-empty `relevant_document_ids`) and excluded count.
- `declared_release_id` is re-exported.
- `EvaluationConfigurationError` messages are re-raised as `RetrievalConfigurationError(str(error))`, so legacy callers see the same class and text.
- The legacy path does not read the rows of the unanswerable or security datasets, so a malformed row there cannot change legacy behavior. Manifest-level problems are different (as built in T1, review F2): legacy `retrieval-baseline` now refuses, with exit 2, suites it used to ignore:
  - an unknown dataset type;
  - a non-golden dataset path that is missing, not a string, or escapes the repository root;
  - a non-string golden path;
  - `null` in the newly typed optional fields (`status`, `introduced_in_release`, a non-integer `case_count` on the manifest; `evaluation_suite_id`, `relevant_section_ids` on golden rows).

  The real `public-eval-v1` suite and the frozen fixture suite are unaffected. This is documented in the `COMMANDS.md` legacy entry (T8b).

### Result document 2.0 (`kind: retrieval_evaluation`)

A superset of the D037 1.0 keys. Every 1.0 key keeps its name, type and meaning (`case_count` and `excluded_case_count` still refer to golden cases).

```json
{
  "schema_version": "2.0",
  "kind": "retrieval_evaluation",
  "created_at": "...", "git_commit": "...", "git_dirty": false,
  "evaluation_suite_id": "public-eval-v1", "evaluation_suite_version": 1,
  "evaluation_suite": {
    "status": "active",
    "cases_by_type": {"golden_answerable": 63, "unanswerable_refusal": 12, "security": 10},
    "excluded_by_status": {"golden_answerable": {}, "unanswerable_refusal": {}, "security": {}}
  },
  "declared_knowledge_release_id": "seed-v1", "release_snapshot_verified": false,
  "collection": "...", "index_version": "idx-v1", "index_settings": {"...": "..."},
  "retrieval_strategy": "dense", "top_k": 5, "device": "mps:0", "embedder_is_fake": false,
  "case_count": 63, "excluded_case_count": 0, "document_count": 13,
  "random_hit_rate_at_k": 0.3846, "random_hit_rate_formula": "min(1, 5/13)",
  "metrics": {
    "overall": {"hit_rate_at_5": 0.0, "recall_at_5": 0.0, "mrr": 0.0, "n": 63},
    "by_query_language": {"en": {"...": "...", "n": 54, "small_sample": false}},
    "by_category": {"...": "..."},
    "by_source_authority": {"owner_approved": {"...": "..."}, "naati": {"...": "..."}}
  },
  "absent_query_languages": ["ml"],
  "small_sample_threshold": 10,
  "section_level": {"measurable_cases": 0, "note": "no active golden case has relevant_section_ids"},
  "unanswerable": {
    "status": "not_evaluable_before_generation", "owner": "roadmap-10", "n": 12,
    "top1_score": {"min": 0.0, "p50": 0.0, "p95": 0.0, "max": 0.0},
    "golden_top1_score": {"min": 0.0, "p50": 0.0, "p95": 0.0, "max": 0.0},
    "cases": [{"case_id": "u001", "case_version": 1, "top1_score": 0.0}]
  },
  "latency_ms": {"p50": 0.0, "p95": 0.0, "warmup_ms": 0.0, "measured_cases": 63},
  "cases": [{"case_id": "g001", "case_version": 1, "query_language": "en", "category": "business",
             "source_authority": "owner_approved", "ranked_document_ids": [], "relevant_document_ids": [],
             "hit": true, "recall": 1.0, "reciprocal_rank": 1.0, "top1_score": 0.0, "latency_ms": 0.0}],
  "notes": ["..."]
}
```

- `small_sample` is added to every slice entry, including the 1.0-named slices.
- The `source_authority` slice key is the sorted, `+`-joined set of the relevant documents' `source_authority` values from the repository map.
- Section-level metrics (R6) use the string key `"<document_id>#<section_id>"` for both retrieved hits and a case's `relevant_section_ids` entries, and pass those keys to the unchanged `retrieval/metrics.py` functions (as built in T3, review F3).
- Scores are rounded to 4 decimals and latencies to 3, as in 1.0.
- The fixed notes are the R5 list, including the g004/u001 note. The g004 note is emitted only while both cases are active in the loaded suite, so it disappears by itself after a human resolution.
- No field holds query text, chunk text, absolute paths or secrets.

## Error and failure behavior

All CLI errors print `ERROR <ClassName>: <safe_text(message)>`, or the class name only for unexpected exceptions, as in Spec 005. Nothing is written on error.

| Situation | Command | Exit | Qdrant contacted? |
|---|---|---|---|
| Schema file missing or invalid | validate, retrieval, security | 2 | no |
| Suite or dataset unreadable, unknown dataset type, path escapes repository | all but compare | 2 | no |
| Validation problems (schema, duplicate ID, suite mismatch, `case_count`, unknown or ineligible document, candidate rules) | validate | 1 | no |
| Knowledge corpus invalid (repository error) | validate, retrieval, security | 2 | no |
| Suite `status` not `active` | retrieval | 2 | no |
| Declared release missing or mismatched | retrieval | 2 | no |
| Output file exists | retrieval, security | 2 | no |
| Configured embedder is fake | retrieval | 2 | no |
| Missing `bge-m3` extra | retrieval | 2 | no |
| Index missing or binding mismatch (D036) | retrieval | 2 | read-only |
| Index recorded as fake | retrieval | 2 | read-only |
| No active golden cases, or no visible documents | retrieval | 2 | read-only |
| `check_hit` raises during quality evaluation | retrieval | 2 (fail closed) | read-only |
| Unfiltered sanity check: nearest point not forbidden | security | 2 (harness error) | in-memory |
| Forbidden document returned, or `check_hit` raises | security | **1 (gate failure)** | in-memory |
| Security collection base without the `w2a-sectest-` prefix | security (builder) | 2 | no writes |
| Security fixture root holds an unexpected visible entry or lacks a listed fixture file (hidden entries are ignored) | security | 2 | no |
| Unreadable or unknown result kind/version | compare | 2 | no |
| Result file repeats a `case_id` (any `case_version`) | compare | 2 | no |
| Unlike runs (suite, case set, `top_k`, `document_count`) or a fake run | compare | 2 | no |
| Quality gate failed | compare | **1** | no |
| Unexpected exception | any | 2 | — |

## Security / authorization

- One policy path. Every query, quality and security alike, goes through `DenseRetriever` with `resolve_access(guest_access(settings))`. The filter is built only by `build_access_filter`, and every hit passes `check_hit` (D035, D040). No evaluation code builds a filter or reads role, scope or tenant from a case. `access_context` is loaded and ignored (D033, D034).
- The security index can never be a quality index:
  - its settings record `embedder_is_fake: true`, so `eval-retrieval` and real `make retrieve` refuse to bind it (D036);
  - the builder refuses, in code and before any write, a collection base that does not match `^w2a-sectest-[0-9a-f]{8}$`, and any target collection (or its `-settings`) that already exists. It can therefore only create a fresh throwaway collection, on the in-memory client (CLI and unit tests) or on Docker (integration test with a unique base). `test_security_eval.py` covers each refusal: the default base `way2australia`, a `w2a-sectest-` base without the 8-hex suffix, and an existing collection;
  - by default it lives in an in-memory client.
- The builder writes ineligible (canary) points only into such a collection. It is the only code that writes ineligible content, and its docstring and a test state this.
- Retrieved text is untrusted. Only `document_id`s, scores, ranks and IDs are recorded. Printed payload-derived text goes through `safe_text` (D041).
- C6: no evaluation code opens an evaluation dataset for writing. A test hashes `evaluation/` before and after each runner and requires them to be equal. Candidates are never loaded as cases, and `validate` refuses a suite that references them.
- Protected paths: the two schema files and the candidates file are each created by a named task. Verification is `git status --porcelain -- evaluation knowledge config`, which must list exactly those three added files and nothing modified.
- No new secrets or settings. Qdrant settings come from the existing `RuntimeSettings`.

## Observability

- Logging goes to stderr: one info line per phase (suite loaded with counts; index bound with collection, `index_version` and N; runs with case count; result file name relative to the repository). The `httpx` logger is at WARNING, as in Spec 005.
- The result JSON carries the C14 reproduction metadata: git commit and dirty flag, suite ID and version, declared release, collection, `index_version`, `IndexSettings`, device, `top_k`.
- `eval-security` reports its total duration in milliseconds and the point counts per variant.
- No Langfuse or metrics backend (roadmap 11).

## Testing / evaluation strategy

New tests live under `packages/rag/tests/evaluation/`. None needs PyTorch, a model download or Docker, except the one marked `integration`.

| Test | Covers |
|---|---|
| `test_suite_loader.py` | valid suite; unknown dataset type; escaping path; malformed line (file and line, no text); ignored `access_context`; extra fields; read-only (hash before and after) (R1) |
| `test_schemas.py` | the two new schemas are valid Draft 2020-12; per-type required fields reject temp-copy cases missing each field; the existing schema is referenced, not copied (R2) |
| `test_validate.py` | the current repository validates (exit 0); temp-copy failures for duplicate ID, suite mismatch, `case_count`, unknown document, ineligible document, candidate referenced by a suite, a non-`suggested` candidate (R2, R14) |
| `test_status_handling.py` | inactive statuses excluded and counted; `suggested` never run; deferred and `unclassified` attack types (R3) |
| `test_slices.py` | slice keys incl. `naati+owner_approved`; `small_sample` below 10; absent languages from a temp registry (no literal `ml` in code: a grep-style test over `evaluation/*.py`) (R5) |
| `test_sections.py` | section metrics on synthetic cases; zero-measurable block (R6) |
| `test_retrieval_eval.py` | injected index, retriever and embedder; fake embedder and fake index refused; field set; no query or chunk text in the output (scans the document for every query string); never overwritten; partial cleanup through the reused writer; unanswerable distribution (R4, R7, R10) |
| `test_security_eval.py` | full in-memory gate passes on the seed corpus; sanity check holds for every query; a filter-dropping index makes the gate fail with exit 1 naming `case_id` and `document_id`; filter identical for every query (spy); prefix refusal; **runtime bound: the whole gate under 10 s** (`perf_counter`) (R8) |
| `test_compare.py` | pass at exactly one lost case; fail at two; MRR pass at exactly 1/n and fail just above it; flip warnings both ways; each refusal; reads the committed 1.0 file `experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json` (read-only) and compares it with itself (pass, no warnings) (R11) |
| `test_cli.py` | subcommand exit codes; `safe_text` on output; nothing written on error; tests write only to `tmp_path` (R4, R7, R8, R11) |
| `test_security_integration.py` (`integration`) | same builder on Docker Qdrant with a unique `w2a-sectest-*` base; no forbidden point returned; collection and `-settings` removed in `finally`; skips when Qdrant is unreachable (R9) |
| `retrieval/test_legacy_baseline_snapshot.py` | written **first**, before `goldens.py` changes: a fixed-clock, fixed-git-state, in-memory fake-index `run_baseline` document equals the committed snapshot byte-for-byte; existing `test_goldens.py`, `test_baseline.py` and `test_cli.py` pass unchanged (R12) |

Live-data rule for tests (2026-10-24 amendment, T8a). A unit test that reads live `knowledge/` or `evaluation/` data never asserts today's literal counts (13 documents; 85, 63, 12 or 10 cases; 5 retrieval-side security cases), because those fail on the first approved content or evaluation change and on every Phase 2 release. It asserts consistency with the live source instead:
- documents loaded equal the number of manifest entries;
- suite rows equal the manifest `case_count`;
- per-type counts equal the row counts derived from the datasets (and, for security, the rows whose `attack_type` is in `RETRIEVAL_SIDE_ATTACK_TYPES`);
- a second ingest run reports every loaded document unchanged.

A test that genuinely needs exact numbers reads the frozen fixture copy `packages/rag/tests/retrieval/fixtures/legacy_baseline_repo/`. Tests over the committed 1.0 result file, a frozen artifact, may keep its recorded numbers.

Spec-level checks:
- `make verify`: validate-evaluation, the security gate test and all unit tests, with no extra, no Docker and no model.
- `make test-integration`.
- The protected-path `git status` check.
- User-owned, post-merge, not a gate: a real `make eval-retrieval` on `w2a-realcheck-idx-v1`, then `make eval-compare BASE=experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json CANDIDATE=<new file>`. It is expected to pass, reproducing HitRate@5 0.952 and MRR 0.878. Any flips are listed as warnings.

## Phase 2 compatibility / migration

- `CaseStatus` mirrors the existing schema enum, which already holds the Phase 2 statuses. The loader just counts them, so Phase 2 governance adds transitions, not new loading logic.
- Candidate rows already have the Phase 2 suggestion shape: `candidate_id`, `proposal_type`, `target_suite_id`, `proposed_by`, `drafted_by`, `requires_review`, `rationale`, and `proposed_case` or `target_case_ids` plus `options`. Admin accept, edit or reject can consume them later. Activation stays a human, versioned change (new `case_version`s or cases, and a suite version bump).
- `eval-compare` is the core of Phase 2's "candidate evaluation versus active release". The authorization gate is the "hard-block security regression" Phase 2 needs. Phase 2 release-candidate evaluation will also need a "compare shared cases" mode: only cases present in both runs with the same `case_version` are compared, new, removed and changed cases are reported separately, and security regressions are still a hard fail. It is not built in Spec 006, where `eval-compare` refuses any difference in the case set (recorded in `tasks.md` "Notes for the retrospective").
- Assets are read by repository-relative path through `suite.py` only. A later metadata-database or S3 source can replace `read_manifest` and `read_dataset` behind the same models.
- `retrieval/goldens.py` and legacy `make retrieval-baseline` can be retired by a later spec once nothing needs the 1.0 producer. `read_result` keeps reading 1.0 files.

## Alternatives / deferred decisions

Decisions recorded at design approval (2026-10-23):

- **Eligibility is ingestion's job only.** Ingestion eligibility (`EligibilityPolicy`: approved, active, `retrieval_enabled`, not synthetic, allowed scope) is the **only** guard against synthetic or unapproved documents. Retrieval does not re-check them: the payload does not carry those fields (D026), and the access filter and `check_hit` check scope, tenant and owner only. So `poisoned_public_document.md` (public scope, synthetic) stays out of the authorization gate and belongs to the prompt-injection tests (roadmap 12).
- **Only an active suite is evaluated.** `eval-retrieval` refuses a suite whose `status` is not `active` (exit 2, clear message). `validate-evaluation` validates and reports any suite. This rule is set at design level; R4 does not state it.
- **The agent drafts the Malayalam candidates; a fluent speaker corrects them.** The implementer drafts about 6 pure-`ml` golden queries. Every `ml` row carries:
  - `drafted_by: agent`;
  - `needs_fluent_speaker_review: true`;
  - `requires_review: ["fluent_malayalam_speaker", "owner_review"]`, where the first value is the one R14 names.

  `validate-evaluation` applies a language-neutral rule, with no `ml` literal in code: a candidate whose proposed `query_language` is not `en` must have `needs_fluent_speaker_review: true` and `owner_review` in `requires_review`. No `ml` candidate may be approved before a fluent speaker has corrected it. Approval happens outside this spec in every case.
- **The security gate retrieves at `top_k = 50`** (`MAX_TOP_K`), the widest result set, for every query.
- **The fixture builder lives in the package, under two conditions.** `security_corpus.build_security_repository(fixture_root, work_dir)` takes the fixture root as an explicit parameter; only the CLI and the tests supply `tests/fixtures/security`. `build_security_index` can only create a new `w2a-sectest-<8 hex>` collection, enforced in code and tested (see Security / authorization).

- **Move `metrics.py` into `evaluation/`:** rejected. It would touch the legacy import path for no gain. Section metrics reuse the same functions with `"<document_id>#<section_id>"` keys.
- **Refactor `baseline.py` to share a result builder with 2.0:** rejected for this spec. It risks byte drift in the legacy output. Instead, 2.0 is built separately, and only `write_result`, `check_output_free` and `git_state` are imported unchanged.
- **Separate CLI modules per target:** rejected for one `cli.py` with subcommands, which gives one argument and error-handling path.
- **Default `eval-security` to Docker Qdrant:** rejected. `make verify` must not need Docker. Docker coverage is the integration test (R9).
- **Count a multi-authority case in each authority slice:** rejected. It double-counts. The `+`-joined key keeps slices disjoint.
- **Recompute versus trust the aggregates in compare:** the gate uses per-case rows. The recorded aggregates are rounded to 4 decimals, which matters at a tolerance of about 0.016.
- **Tolerances as CLI flags:** rejected. They are constants, and a change needs a spec amendment (R11).
- **A score threshold for unanswerable cases:** deferred to generation and answerability (roadmap 10). The distribution is informational.
- **Including `poisoned_public_document` in the gate:** not an authorization case (public scope). Deferred to the prompt-injection tests (roadmap 12).
- **Still deferred:** CI workflow (roadmap 15), device pinning (D038), `relevant_section_ids` candidates (chunking spec), the Spec 004 nits.
- **Proposed new decisions**, recorded in `DECISIONS.md` during implementation:
  - D042: suite loader and validator, and the schema files under the protected path;
  - D043: the 2.0 result format, and that compare reads 1.0;
  - D044: the quality gate (more than 1 case, MRR more than 1/n, flips are warnings);
  - D045: the security gate construction and the `w2a-sectest-` prefix;
  - D046: legacy `retrieval-baseline` kept frozen.

  D042 is the next free number in `DECISIONS.md` (D041 is the last, checked 2026-10-24). The suite-status refusal folded into these decisions names the allowed suite status values (`draft`, `active`, `deprecated`, `replaced`).

## As-built notes

Recorded by the 2026-10-24 amendment from the T3 and T5 task reviews. Each note describes code as built in T3–T5; the T8a changes above (`document_id` attribute, explicit fixture list, duplicate `case_id` refusal) are design changes, not notes.

- **`eval-retrieval` options (T3 review F2).** Besides `--top-k`, `--suite`, `--release` and `--output`, the `retrieval` subcommand takes `--repo-root` (default: the current directory) and `--config` (default: `<repo-root>/config/ingestion.yaml`). Neither selects an embedder or allows a fake run.
- **`eval-security` (T5 review F2).**
  - Options: `--repo-root`, `--config`, `--suite`, `--fixture-root` and `--output`. `--fixture-root` defaults to `<repo-root>/tests/fixtures/security`; that default lives only in `cli.py` (`DEFAULT_FIXTURE_ROOT`), never in library code.
  - The throwaway collection is deleted by the CLI in its `finally` block (`delete_security_index`), and the in-memory client is closed there, so a failed run also removes it.
  - `EvaluationHarnessError` (in `evaluation/errors.py`, a subclass of `EvaluationError`) marks a broken harness, for example an unfiltered sanity check that does not find a forbidden point nearest. It is exit 2, never a pass.
  - The result document has `kind: security_evaluation`, `schema_version: "1.0"`, `created_at`, `git_commit`, `git_dirty`, `passed`, `evaluation_suite_id`, `evaluation_suite_version`, `access` (`role`, `tenant_id`, `allowed_access_scopes`), `index` (`collection`, `index_version`, `embedder_is_fake`, `seed_document_count`, `forbidden_points_per_variant`), `query_count`, `security_cases_run`, `golden_queries_run`, `violations` (`case_id`, `document_id`, `variant`), `deferred` (`case_id`, `attack_type`, `owner`), `excluded_fixtures` and `duration_ms`. It holds IDs, counts and verdicts only, never query or chunk text.
- **`security_document` hard-codes `access.role: "guest"` (T5 review F3).** This is correct in Phase 1, where guest is the only role. It must change, to the resolved role, when other roles are added. No code change in this spec.
- **Section keys (T3 review F3)** are `"<document_id>#<section_id>"` (see "Result document 2.0").

Added by the `spec-reviewer` retrospective round 1 (2026-10-24). Each note describes code as built and approved in a task review; none changes the approved design text above.

- **Flip-line format (T6 review F2/F4, closed by user decision, no code change).** Flip warnings print the case key as `<case_id> v<case_version>`, sorted by that string (so by `case_id`), for example `WARNING flipped hit->miss: g002 v1`, not the `g026 (v1)` sketch in "Data flow". In a refusal, the 10-key cap applies per list (`case_version changed`, `only in BASE`, `only in CANDIDATE`), each followed by `and N more` when longer (T6 review F2, user decision).
- **`eval-compare` refusal output (T6 implementation notes, accepted at T6 approval).** A refusal (`NotComparableError`) is printed to stderr as its message only, starting with `not comparable:`, without the `ERROR <ClassName>:` prefix the "Error and failure behavior" section gives for other errors. Unexpected exceptions still print `ERROR <ClassName>` only.
- **`validate-evaluation` output (T2).** Each problem line is printed as `ERROR <file>:<line> <case_id> <field>: <reason>` (line and case ID omitted when they do not apply), followed by `validate-evaluation: OK, 0 problems` or `validate-evaluation: FAILED with <n> problem(s)`.
- **`build_security_repository` signature (T5 implementation notes, confirmed at T5 approval).** It takes a keyword-only `schema_source` (the document metadata schema path, supplied by the CLI and tests), so library code names neither the fixture folder nor the schema location: `build_security_repository(fixture_root, work_dir, *, schema_source)`.
- **Security index seed points (T5 implementation notes, accepted at T5 approval).** The seed corpus is written by running the production `IngestionService` against the throwaway collection (which calls `ensure_collection` and `replace_document`), not by a separate loop. Canary probe points use `point_id(<canary>, "query-probe", <query index>)`, so they cannot collide with the canary's own chunk point.
- **Existing output file in `eval-security` (T8b review F2).** The refusal comes from the reused `retrieval.baseline.check_output_free` and is a `RetrievalConfigurationError` (exit 2), not an `EvaluationHarnessError`.
