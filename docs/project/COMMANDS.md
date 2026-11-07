# Project Commands

This file defines the intended stable command surface for humans and coding agents.

The commands below are the target interface. Implemented today: `setup`, `format`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `verify`, `skills-sync`, `skills-check`, `validate-knowledge`, `setup-bge-m3`, `ingest`, `index-lexical`, `retrieve`, `retrieval-baseline` (legacy), `validate-evaluation`, `eval-retrieval`, `eval-security`, `eval-compare`, `eval-continuity`. The other targets are created by the spec that needs them.

## Environment

```bash
make setup
make setup-bge-m3
```

`make setup` installs the dev environment without the optional `bge-m3` and `reranker` extras, and removes them if they were installed. `make setup-bge-m3` adds it (`uv sync ... --extra bge-m3`: `sentence-transformers`, which brings PyTorch) for real BGE-M3 embeddings, and the optional `reranker` extra (same dependency; the pinned `BAAI/bge-reranker-v2-m3` cross-encoder, Spec 011). **After `make setup`, default runs (hybrid, reranking on since Spec 011 T5) need `make setup-bge-m3` and a cached reranker; the first reranked run downloads the pinned model.** `make verify` never needs either extra or any model. Opt-in real-model tests: `W2A_RUN_BGE_M3_SMOKE=1` (embedder) and `W2A_RUN_RERANKER_SMOKE=1` (reranker); either variable lifts the hub-offline test fixture. The download is large; on a slow connection uv may time out, so the `Makefile` defaults `UV_HTTP_TIMEOUT` to 300 seconds for this target; raise it per run if needed, for example `UV_HTTP_TIMEOUT=600 make setup-bge-m3`.

## Quality

```bash
make format
make lint
make typecheck
make verify
```

`make lint` runs `ruff check` and `ruff format --check`, so format drift fails `make verify`; `make format` fixes it.

`make verify` should run the fast deterministic verification set. It runs `make test`, which includes the `integration`-marked tests: they skip when Qdrant is unreachable, and when a local Qdrant is running they create and remove temporary collections against it.

### Verify budget (agent hooks)

Coding agents should run **`make verify` at most twice per session** (typically once normally and once hub-free). A PreToolUse hook in `.claude/settings.json` runs `python3 "$CLAUDE_PROJECT_DIR/tools/hooks/verify_budget.py" claude || true` on Bash commands (project-root path; **`|| true`** so a missing script never blocks every Bash call). Cursor and Claude Code set **`CLAUDE_PROJECT_DIR`** (Cursor also sets **`CURSOR_PROJECT_DIR`**) to the workspace root regardless of the agent's current directory. The hook also counts **`make test`** toward the same budget. **`make test-unit`**, **`make test-integration`**, and targeted **`pytest …`** are not limited.

While iterating, run focused tests, for example `uv run pytest packages/rag/tests/<area>/test_x.py -q`. Disable the hook: `touch ~/.cache/verify-budget/off`. Reset counters: `rm ~/.cache/verify-budget/counts.json`. Override state dir for tests: `VERIFY_BUDGET_STATE=…`.

## Tests

```bash
make test
make test-unit
make test-integration
```

## Agent skills

```bash
make skills-sync
make skills-check
```

- `skills-sync` regenerates `.claude/skills/`, `.agents/skills/` and `.kiro/skills/` from `agent-skills/`. Cursor already loads `.claude/skills/` and `.agents/skills/`; there is no `.cursor/skills/` mirror (D063).
- `skills-check` fails if any mirror differs; it is part of `make verify`.

Run a role (each in a fresh session; the orchestrator is the usual entry point):

| Host | Commands |
|---|---|
| Claude Code | `/spec-orchestrator [NNN]`, `/spec-planner`, `/spec-implementer <NNN> [task]`, `/task-reviewer <NNN> <task>`, `/spec-reviewer <NNN>` |
| Cursor | `/spec-orchestrator`, `/spec-planner`, `/spec-implementer`, `/task-reviewer`, `/spec-reviewer` (same mirrors as Claude Code / Codex) |
| Codex | `$spec-orchestrator`, `$spec-planner`, `$spec-implementer <NNN> [task]`, `$task-reviewer <NNN> <task>`, `$spec-reviewer <NNN>` |
| Kiro | `/spec-orchestrator`, `/spec-planner`, `/spec-implementer`, `/task-reviewer`, `/spec-reviewer` |

Find an approved task's commit: `git log --grep='^Spec-Task: <NNN>/<task>$' spec/<NNN>`.

## Knowledge

```bash
make validate-knowledge
```

Expected:
- validate document metadata/frontmatter;
- validate IDs/version fields;
- validate manifests;
- ensure production corpus excludes test-only fixtures.

Behavior:
- lists every problem as `ERROR <document_id>: <field>: <reason>` and ends with a summary count;
- also reports manifest entries outside the approved production roots and markdown files under those roots that the manifest does not list;
- fails if a retrievable (active, retrieval-enabled) document in the public corpus is synthetic, not approved or not public;
- exits `0` when valid, `1` on any problem; runs inside `make verify`.

## Ingestion

```bash
make ingest
make ingest INGEST_ARGS="--embedder fake"
```

Behavior:
- options (through `INGEST_ARGS`): `--embedder {bge_m3,fake}` (default `embedder.provider` from the config), `--config` (default `<repo-root>/config/ingestion.yaml`, schema 1.1 with a discriminated chunker; experiment arms under `experiments/configs/chunking/*.yaml`, for example `heading-idx-v1.yaml` for legacy `idx-v1` / `heading` v1); `make ingest` passes `--repo-root` itself;
- reads eligible documents through `DocumentRepository` (guest/public policy);
- chunks, embeds and upserts only added or changed documents, deletes documents that are no longer eligible;
- prints `index: <collection> (index_version <label>; embedder <model> @ <revision>, fake=<bool>)`, then `added: N  updated: N  unchanged: N  deleted: N`, the `document_id`s per category and `ERROR <document_id>: <reason>` lines; refusals go to stderr as `ERROR <ClassName>[: message]`;
- a second run on unchanged content reports `added: 0  updated: 0  unchanged: <all>  deleted: 0`;
- needs Qdrant (`docker compose up -d qdrant`); `QDRANT_URL`, `QDRANT_API_KEY` and `QDRANT_COLLECTION_BASE` come from the environment, index-defining settings from `config/ingestion.yaml`;
- real embeddings need `make setup-bge-m3`; without the extra the command exits 2 before contacting Qdrant;
- for `--embedder fake` always set a throwaway `QDRANT_COLLECTION_BASE`; a fake run on the default collection marks it fake and later real runs are refused until `index_version` changes;
- exit codes: `0` success, `1` any document failed, `2` refusal (settings mismatch, missing group, bad configuration, unreachable Qdrant).

## Lexical index and retrieval strategies

```bash
make index-lexical
make index-lexical LEXICAL_ARGS="--embedder fake"
```

`make index-lexical` (Spec 007; settings 1.2 since Spec 010; no Qdrant client, no embedder, no PyTorch; writes one local file). Token-based chunkers (`recursive` / `structure`, including default `idx-v2`) still need the BGE-M3 tokenizer files at the pinned revision (cached or downloadable) for packing and the truncation guard; `heading` v1 / `idx-v1` uses them only for the guard. Standalone `bm25` open does not load the Hugging Face tokenizer files (D067) but BM25 **queries** use the tokenizer recorded in the lexical file:
- builds the BM25 index (registered tokenizer, default from `config/retrieval.yaml` → **`lexical-v2`**) in an SQLite FTS5 file from the same eligible chunks, payloads and point IDs that `make ingest` writes, including a `lote_languages` column (settings 1.2). Only guest/public eligible chunks go in;
- options (through `LEXICAL_ARGS`): `--embedder {bge_m3,fake}`, `--tokenizer {lexical-v1,lexical-v2}` (default: config value), `--output`, `--config`; `make index-lexical` passes `--repo-root` itself. A relative `--output` or `W2A_LEXICAL_INDEX_DIR` resolves against the repository root;
- the file is `<W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite`; the default directory is `.local/lexical` (git-ignored under `/.local/`). A **second file** for the same collection (for example tokenizer experiments) uses a different directory: `W2A_LEXICAL_INDEX_DIR=.local/lexical-v2 make index-lexical LEXICAL_ARGS="--tokenizer lexical-v2"`. The target is refused (exit 2) inside protected paths or anywhere not git-ignored;
- prints `lexical index: <path> (collection <c>, index_version <v>; <tokenizer name> v<version>; settings 1.2; chunks N; digest <12 hex>)`; errors print `ERROR <ClassName>: <message>`, exit `0` or `2`;
- run it again after every `make ingest` that changes content or chunker, and **once after upgrading to settings 1.2** so `--lote` works on BM25/hybrid (1.1 files serve without `--lote` only). A stale file is refused by identity, chunker or freshness checks.

Strategies: `make retrieve` and `make eval-retrieval` take `--strategy {dense,bm25,hybrid}` and optional `--lote <code>` (through `RETRIEVE_ARGS` and `EVAL_ARGS`); `--retrieval-config` (default `config/retrieval.yaml`) holds `default_strategy` (`hybrid`), RRF settings, and `lexical.tokenizer`. `config/retrieval.yaml` is schema **1.3** (1.0 refused; 1.1 reads as `lexical-v1`; 1.1 and 1.2 read as reranking off): 1.2 added `qdrant` timeouts and the default lexical tokenizer, 1.3 adds the `rerank` block (`enabled` true, `provider`, `model_id`, `revision`, `depth` 20, `max_length`, `batch_size` 16 (range 1..256)). **`--lote`** names the non-English CCL side (active registry codes, not `en` or `*`); omitted means no applicability filter. Invalid codes are refused before opening (exit 2). **`bm25` needs neither Qdrant nor the `bge-m3` extra** (Spec 008), but while `rerank.enabled: true` it also needs **`--no-rerank`** (reranking applies to `hybrid` only; `--strategy dense` and `--strategy bm25` without `--no-rerank` exit 2 with that configuration error). Default (hybrid, rerank on) runs need the `reranker` extra and a cached model. **Reranking** (Spec 011; `RETRIEVE_ARGS` / `EVAL_ARGS`): `--rerank` / `--no-rerank` (mutually exclusive; default is `rerank.enabled` in the config), `--reranker {bge,fake}` on `make retrieve` only (default: `rerank.provider`; `eval-retrieval` refuses a fake reranker with exit 2 before any Qdrant contact). Reranking off never builds or loads a reranker. **Default `hybrid` needs the local lexical file**; setup order is `make ingest`, then `make index-lexical`. `--strategy dense` needs no lexical file.

Fallback (`hybrid` only, the default or `--strategy hybrid`): when Qdrant is unreachable or times out, or the embedding model cannot be loaded because of a network or timeout cause, BM25 serves the query instead, with the same access and `top_k`, and the result says so. It never applies to an explicit `dense` or `bm25`, and nothing else falls back: a missing `bge-m3` extra (a configuration error, exit 2), a model load failure without a network cause, a Qdrant HTTP error status, a missing collection or settings mismatch, a missing or stale lexical file (also when Qdrant is down), or an authorization error all exit 2. After a successful open, every query tries Qdrant again; there is no circuit breaker, so with Qdrant hanging each query waits about `query_timeout_s` (default 3 s) before BM25 serves. When Qdrant is already unavailable at open time, the whole run is served by BM25 with that reason and Qdrant is not tried again during the run.

## Retrieval

```bash
make retrieve QUERY="Is coaching compulsory?"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--strategy dense --no-rerank"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --reranker fake --top-k 3"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--no-rerank"
make retrieval-baseline
make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake --output /tmp/baseline.json"
```

`make retrieve` behavior:
- options (through `RETRIEVE_ARGS`): `--embedder {bge_m3,fake}`, `--top-k` (1 to 50, default 5), `--config`, `--strategy {dense,bm25,hybrid}`, `--lote <code>` (optional applicability filter; validated against `config/language_registry.json`), `--retrieval-config` (see "Lexical index and retrieval strategies"), and `--rerank` / `--no-rerank` / `--reranker {bge,fake}` (Spec 011); `make retrieve` passes `--repo-root` itself. There is no option for role, scope or tenant: access is always guest/public for the tenant in `W2A_TENANT_ID`;
- prints a header (`index: ...`, `device=`, `strategy=<name>`, `lote: <code|none>`); when the fallback served the query it also prints `strategy: bm25 (requested: hybrid; fallback: <reason>)` and a stderr warning; then hit count and lines per hit. The last line is `rerank: <model>@<revision 7 chars> depth <n>` when the stage ran, `rerank: off`, or `rerank: skipped (<reason>, <stage>)` plus a stderr warning when an eligible reranker outage served the plain hybrid hits (a reranker outage never becomes a BM25 fallback). When reranking was requested but a dense outage made BM25 serve the query, no `rerank:` line is printed (the fallback line says what served). It does not print the lexical tokenizer name (check `make index-lexical` output or the file settings). Payload text uses `safe_text`;
- `dense` and `hybrid` need Qdrant with an index built by `make ingest` for the same `QDRANT_COLLECTION_BASE` and `index_version` (`hybrid` falls back to BM25 when Qdrant is unreachable); `bm25` needs only the lexical file built for that collection; with `--embedder fake` use the throwaway base the fake ingest used;
- exit codes: `0` success (including zero hits), `2` refusal or configuration error (empty query, bad `--top-k`, empty `W2A_TENANT_ID`, missing `bge-m3` or `reranker` extra, reranking with `dense`/`bm25` (reranking applies to the hybrid strategy only), `--top-k` above `rerank.depth`, a reranker whose weights are offline and not cached (`HF_HUB_OFFLINE=1`; advice: `make setup-bge-m3` and cache the pinned revision), missing or mismatched index, a missing, stale or mismatched lexical file for `bm25`/`hybrid`, unreachable Qdrant for `dense` (`RetrievalUnavailableError`), an invalid `qdrant` timeout block or schema in `config/retrieval.yaml`, a hit that fails the access re-check). Retrieval and ingestion errors print `ERROR <ClassName>: <message>`; any other exception prints its class name only;
- quoting caveat: `QUERY` is expanded by the shell inside `"$(QUERY)"`, so a query containing `"`, `$` or a backtick needs care. To avoid it, run the module directly: `uv run python -m way2australia_rag.retrieval.cli --repo-root . "your query"` (or `python3 -m uv run python -m ...`), with the same options.

`make retrieval-baseline` behavior (**legacy**: the Spec 005 producer, kept frozen and byte-for-byte compatible, with its own `--allow-fake` and output location `experiments/results/retrieval-baseline-*.json`; use `make eval-retrieval` for the quality measurement, see "Evaluation"):
- options (through `BASELINE_ARGS`): `--embedder {bge_m3,fake}`, `--allow-fake`, `--top-k` (default 5), `--suite` (default `evaluation/suites/public-eval-v1.json`), `--release` (default `seed-v1`, must match `knowledge/releases/<id>.json`), `--output`, `--config`;
- runs the active, answerable golden cases that have `relevant_document_ids` (63 in `public-eval-v1`) through dense retrieval and prints overall HitRate@5 next to the random expectation `min(1, 5/N)`, Recall@5, MRR, p50/p95 latency (after an unmeasured warm-up), the result file name relative to the repository root, and notes;
- an index built with the fake embedder is refused (exit 2) unless `--allow-fake`; the result then carries the note "not a quality measurement". `--allow-fake` is for plumbing checks, never for a recorded baseline;
- the result is `experiments/results/retrieval-baseline-<index_version>-<UTC YYYYMMDDTHHMMSSZ>.json` unless `--output` is given. It is never overwritten and nothing is written on error. It holds no query text, chunk text, absolute paths or secrets. Tests and throwaway checks should use `--output` in a temporary directory. Do not commit a fake or throwaway result;
- the committed real BGE-M3 result is produced by the user after merge (`make setup-bge-m3`, a real `make ingest`, `make retrieval-baseline`, `make setup`);
- since Spec 006 the suite is read through the governed evaluation loader, so the command now refuses, with exit 2, malformed suites it used to ignore: an unknown dataset type; a non-golden dataset path that is missing, not a string, or outside the repository; a non-string golden path; `null` in the newly typed optional fields (`status`, `introduced_in_release`, a non-integer `case_count` on the manifest; `evaluation_suite_id`, `relevant_section_ids` on golden rows). The real `public-eval-v1` suite and the frozen fixture suite are unaffected;
- exit codes as `make retrieve`.

Environment (retrieval and ingestion): `QDRANT_URL`, `QDRANT_API_KEY`, `QDRANT_COLLECTION_BASE`, and `W2A_TENANT_ID` (default `way2australia`; empty or whitespace-only is refused with exit 2). The tenant is a server setting stored on every indexed point, so changing it changes which points `make retrieve` can see, and it also applies to `make ingest`. `W2A_LEXICAL_INDEX_DIR` (optional; default `<repo-root>/.local/lexical`; empty is treated as unset) is the directory of the lexical files for `make index-lexical`, `make retrieve` and `make eval-retrieval`.

## Evaluation

```bash
make validate-evaluation
make eval-retrieval
make eval-retrieval EVAL_ARGS="--strategy dense --no-rerank"
make eval-security
make eval-compare BASE=<result.json> CANDIDATE=<result.json>
make eval-compare BASE=<result.json> CANDIDATE=<result.json> COMPARE_ARGS=--cross-index
make eval-compare BASE=<result.json> CANDIDATE=<result.json> COMPARE_ARGS=--cross-tokenizer
make eval-continuity BASE=<result.json> CANDIDATE=<result.json>
```

`validate-evaluation`, `eval-retrieval`, `eval-security` and `eval-compare` run one module, `python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}`. `make eval-continuity` runs `python -m way2australia_rag.evaluation.continuity`. Extra options for `eval-retrieval` and `eval-security` go in `EVAL_ARGS`; the `make` targets pass `--repo-root` themselves. `make eval-generation` does not exist yet (generation evaluation is a later roadmap item). Error lines are `ERROR <ClassName>: <message>` with payload-derived text passed through `safe_text`; an unexpected exception prints its class name only. Exception: an `eval-compare` refusal prints its message without that prefix, starting with `not comparable:`.

`make validate-evaluation` (part of `make verify`, no Qdrant, no model):
- validates the suite manifest (`evaluation/schemas/evaluation_suite.schema.json`; suite `status` is one of `draft`, `active`, `deprecated`, `replaced`) and every dataset line (`evaluation_case_types.schema.json`, which reuses the existing `evaluation_case.schema.json`);
- cross-checks: unique `case_id` across the suite, each case's `evaluation_suite_id`, `case_count`, no dataset path listed twice, and that every relevant document is in the corpus (otherwise "unknown document") and eligible for guest/public (otherwise "not eligible"), through the document repository;
- validates the candidate files in `evaluation/candidates/` (status `suggested`, proposed case valid, eligible documents, a non-`en` proposed query needs `needs_fluent_speaker_review: true` and `owner_review` in `requires_review`) and refuses a suite that lists a candidates file as a dataset;
- prints one line per problem (`ERROR <file>:<line> <case_id> <field>: <reason>`; the line number and case ID are left out when they do not apply) and a closing count line (`validate-evaluation: OK, 0 problems` or `validate-evaluation: FAILED with <n> problem(s)`); exit `0` valid, `1` problems, `2` configuration error (missing schema, unreadable suite, invalid corpus, a dataset path outside the repository).

`make eval-retrieval` (quality measurement; needs the real BGE-M3 index, see `make setup-bge-m3` and `make ingest`):
- options: `--top-k` (1 to 50, default 5), `--strategy {dense,bm25,hybrid}`, `--lote <code>` (optional; recorded in the result), `--rerank` / `--no-rerank` (default `rerank.enabled`; `--strategy dense|bm25` needs `--no-rerank` while it is true), `--retrieval-config`, `--suite` (default `evaluation/suites/public-eval-v3.json`; suite v2 is refused), `--release` (default `seed-v1`), `--output`, `--repo-root`, `--config`. No `--embedder` or `--allow-fake`;
- runs the active golden cases, then the active unanswerable cases (top-1 score only; their latency is not in p50/p95), through the chosen strategy with the one server-resolved guest access;
- refuses with exit 2, before any Qdrant contact, a suite whose `status` is not `active`, a missing or mismatched declared release, an existing output file, and a configured fake embedder; a recorded fake index is refused after the read-only binding; the D036 binding rules apply;
- the result is `experiments/results/retrieval-evaluation-<index_version>-<UTC YYYYMMDDTHHMMSSZ>.json` unless `--output` is given: `kind: retrieval_evaluation`, `schema_version` **2.5** (**2.5** adds reranking: top-level `rerank_requested`, `rerank` identity, `rerank_skip_counts` (`<reason>:<stage>`), `rerank_truncation` and `warmup_rerank_skip`; per case `served_path`, `rerank_top1_score`, `rerank_truncated_pairs`, `relevant_fused_ranks`; latency by served path with a `legs.rerank` entry and `warmup_rerank_load_ms`; informational cross-encoder top-1 distributions for the unanswerable cases. Skip counts, truncation and those distributions count **measured queries (goldens plus unanswerable)**; per-case rows exist for goldens only. A reranked run's `retrieval_depth` is `rerank.depth` while each leg still fetches 50, and `warmup_ms` includes the open-time reranker load (p50/p95 do not); 2.3 adds distinct-document metrics, D068; **2.4** adds top-level `lote`, per-case `script_mix`, and `metrics.by_script_mix` — script keys from Unicode letter-name prefixes; **romanized Malayalam in Latin script counts as `latin`**, D072), plus the 2.0–2.3 fields documented above. Slices include `query_language`, `category`, `source_authority`, and `by_script_mix`. It holds no query text, chunk text, absolute paths or secrets;
- `git_dirty` in the result ignores untracked files under `experiments/results/` (earlier result files of the same session); any other change, including a tracked change there, marks the run dirty;
- fallback: with the default `hybrid` and Qdrant unreachable, the run is served by `bm25` for every case and says so in the result (`served_strategies`, `fallback_counts`); a file served by one strategy compares like any other run of that strategy; the model is not loaded when Qdrant is unreachable at open time. With reranking requested, the reranker is built (a missing extra still exits 2) but not loaded, the summary prints `rerank: requested but not loaded (served without the reranker)`, the result has `rerank: null`, and BM25 is asked for `rerank.depth` (20) chunks instead of 50 (`retrieval_depth` 20; top-5 distinct-document metrics are unaffected while `required_depth` is at most 20);
- exit codes: `0` success, `2` refusal or error.

`make eval-security` (authorization hard gate; fake embedder on a throwaway in-memory Qdrant plus a throwaway lexical file in a temporary directory, no Docker, no model; not part of the `make verify` target itself, but its logic is covered by the unit tests that `make verify` runs):
- options: `--repo-root`, `--config`, `--suite`, `--fixture-root` (default `<repo-root>/tests/fixtures/security`; that default lives only in the CLI, library code never names it) and `--output` (default `experiments/results/tmp/security-evaluation-<UTC>.json`, git-ignored);
- builds a collection `w2a-sectest-<8 hex>` holding the eligible seed corpus plus forbidden points (staff scope, other tenant, owned, missing owner, and the staff-only canary fixture) that are the nearest neighbour of every query, checks without a filter that a forbidden point really is nearest, then, for each of eight paths (Spec 011 adds `hybrid_rerank`, `hybrid_rerank_skip_open` and `hybrid_rerank_skip_query`, built with a fake reranker at rerank depth 50 and `top_k` 50 so the whole fused pool is re-checked; the committed depth-20 cut is not exercised; security result **1.5**), `dense`, standalone `bm25` (no dense index, no embedder), `hybrid`, `hybrid_fallback_open` (BM25 serving after an open-time outage) and `hybrid_fallback_query` (hybrid whose dense leg is the harness-only `_UnavailableDense`) (each leg also checked without a filter; a query with no lexical terms skips the lexical check and is counted), retrieves through the production path at `top_k` 50 for the active retrieval-side security cases and every active golden query. Other attack types are listed as deferred with an owner;
- the fixture folder must hold exactly `poisoned_public_document.md` and `staff_only_canary.md` (hidden dot-files are ignored); any other visible entry or a missing file is refused before anything is copied;
- the throwaway collection is deleted in the CLI's `finally`, so a failed run removes it too;
- the result is `kind: security_evaluation`, `schema_version` **1.5** (**1.5** adds `path_details` per path: fake reranker identity, depth, skip reason and stage, and the `injection` forbidden variant; 1.3 adds per-chunker `runs`; 1.4 adds `lote_modes`, split `authorization_violations` / `applicability_violations` per run, and `non_applicable_rows_per_variant`; legacy readers accept 1.3): each path runs with `lote: null` and with the active registry code; non-applicable public rows use synthetic code `zz` (harness error if `zz` is active). Summary prints `lote modes: none, <code>` and AUTH/APPLIC counts;
- exit codes: `0` pass, `1` violation (a forbidden document returned, or the access re-check raised; printed as `VIOLATION case <id> document <id> variant <name>`), `2` harness or configuration error (`EvaluationHarnessError`, for example the sanity check not finding a forbidden point nearest, a fallback path that did not fall back, or the plain `hybrid` path in which a query fell back; or a configuration error such as an existing output file, which is `RetrievalConfigurationError`, or a refused fixture folder, which is `EvaluationConfigurationError`).

`make eval-compare BASE=<file> CANDIDATE=<file>` (both required; exit 2 with a usage line otherwise). Extra options pass through `COMPARE_ARGS`:
- `COMPARE_ARGS=--cross-index` (D069): collection, `index_version`, chunker and ingestion config may differ; chunk digest and chunk count are not compared;
- `COMPARE_ARGS=--cross-rerank` (D078): rerank identity (enabled, model, revision, depth, `max_length`) may differ and is printed as `cross-rerank:` lines; the gate still applies; combinable with `--cross-index` and `--cross-tokenizer`. Without the flag a rerank identity difference is refused; **a reranked file with any skipped query is always refused**;
- `COMPARE_ARGS=--cross-tokenizer` (D072): lexical tokenizer name and version may differ when digest and chunk count match; combinable with `--cross-index`;
- reads 1.0 through **2.5** evaluation files; 2.3 and later compare as one distinct-document family; **`lote` must match** (refused as `lote changed none -> ml` etc.); 2.3+ chunker rules as before;
- gate rule (constants in code; changing them needs a spec amendment): fail when the candidate has more than 1 fewer hit cases than the base, or when the mean reciprocal rank drops by more than `1/n` for `n` compared cases. Both are computed from the per-case rows, not from the rounded aggregates. Cases that flip hit to miss or miss to hit are printed as `WARNING flipped ...` lines; slice deltas and latency changes are printed too; none of these fails the gate;
- refuses (exit 2) files that are not comparable: different suite ID or version, different case sets, different `top_k` or document count, either side from a fake-embedder index, a different collection (when both record one), `index_version`, embedder (model ID and revision) or lexical index (tokenizer and chunk digest; a different strategy is allowed and printed as an identity line), a `bm25` or `hybrid` file (2.1, or 2.2 by served strategy) without a `lexical_index` object, a 2.2 file that mixes served strategies (`not comparable: ... mixes served strategies (golden cases bm25: 3, hybrid: 66; served_strategies: bm25, hybrid); re-run when the system is stable.`), an unreadable or unknown file, or a file that repeats a `case_id`. The refusal is one message on stderr that starts with `not comparable:`, names every difference (old -> new, up to 10 case keys per list, then `and N more`) and ends with the next step (for example a new baseline with `make eval-retrieval`);
- the embedder pair comes from `index_settings`, or from `dense_identity` when the run never reached Qdrant, so a fallback-only 2.2 file compares against a Spec 007 `bm25` file; identity lines add `requested <x> and was served by <y>` only when they differ; a fallback path's latency is marked `includes failed dense attempt: <reason>` and stays informational (after an open-time fallback there is no per-query dense attempt, so that share is about 0 ms; the 2.2 file does not say whether a fallback happened at open time or per query);
- flip warnings print the case key as `<case_id> v<case_version>`, sorted, for example `WARNING flipped hit->miss: g002 v1`;
- exit codes: `0` pass (warnings allowed), `1` gate failure, `2` refusal.

`make eval-continuity BASE=<file> CANDIDATE=<file>` (both required; extra options through `CONTINUITY_ARGS`):
- compares hit, reciprocal rank and ranked document IDs for every golden shared by `case_id` and `case_version`; prints suite, suite version, `lote`, `git_commit` and case-set differences as informational lines without refusing them;
- refuses (exit 2) when collection, `index_version`, chunker, embedder pair, lexical identity, rerank identity, served strategy or `top_k` differ, or either side is a reranked run with skipped queries (D-C), or a file is unreadable;
- exit codes: **`0`** no shared-case differences, **`1`** at least one shared case differs, **`2`** refusal. **GNU make** maps recipe exit 1 to make exit 2; when cases differ, stderr shows `eval-continuity: exit 1`. For R10-style gates that need module exit 1, run `uv run python -m way2australia_rag.evaluation.continuity BASE CANDIDATE` directly (Spec 010 T5 continuity check).

Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority/**script-mix** slices, at document level (section level where a case has `relevant_section_ids`).

## Experiments

```bash
make experiment CONFIG=experiments/configs/day1_baseline.yaml
```

Experiment results should record:
- Git commit;
- Knowledge Release ID;
- Evaluation Suite ID;
- chunker config/version;
- embedding model/version;
- retrieval strategy;
- reranker config;
- prompt version;
- metrics;
- stage latency;
- token/cost data where available.

## Docker

```bash
docker compose up -d
docker compose down
```

Expected local dependency: Qdrant.

## Infrastructure

Terraform remains explicit:

```bash
terraform fmt
terraform validate
terraform plan
terraform apply
```

Do not automate destructive infrastructure commands.

## Knowledge graph (graphify, developer tooling, D048)

```bash
graphify update .
```

Refresh the graph after code changes (local, no model cost). In the spec workflow `spec-orchestrator` runs it once per spec, after the last task approval and before the retrospective; implementers do not run it per task (D080).

```text
/graphify . --update
```

In Claude Code: refresh after documentation changes (re-extracts changed docs; uses the model). Run by the user once per spec, after the merge to `main`; `spec-orchestrator` reminds you.

```bash
graphify query "<question>"
```

Query the graph; `graphify path "<A>" "<B>"` and `graphify explain "<concept>"` for relationships and concepts. The extraction cache `graphify-out/cache/` is local and git-ignored (D080). Install once with `uv tool install graphifyy` (upgrade with `uv tool upgrade graphifyy`; 0.9.103 at D080) and make sure `~/.local/bin` is on `PATH` (`uv tool update-shell`).

## Rule

Do not invent alternative project command surfaces unless this file is intentionally updated.
