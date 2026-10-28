# Project Commands

This file defines the intended stable command surface for humans and coding agents.

The commands below are the target interface. Implemented today: `setup`, `format`, `lint`, `typecheck`, `test`, `test-unit`, `test-integration`, `verify`, `skills-sync`, `skills-check`, `validate-knowledge`, `setup-bge-m3`, `ingest`, `index-lexical`, `retrieve`, `retrieval-baseline` (legacy), `validate-evaluation`, `eval-retrieval`, `eval-security`, `eval-compare`. The other targets are created by the spec that needs them.

## Environment

```bash
make setup
make setup-bge-m3
```

`make setup` installs the dev environment without the optional `bge-m3` extra, and removes the extra if it was installed. `make setup-bge-m3` adds it (`uv sync ... --extra bge-m3`: `sentence-transformers`, which brings PyTorch) for real BGE-M3 embeddings. `make verify` never needs it. The download is large; on a slow connection uv may time out, so the `Makefile` defaults `UV_HTTP_TIMEOUT` to 300 seconds for this target; raise it per run if needed, for example `UV_HTTP_TIMEOUT=600 make setup-bge-m3`.

## Quality

```bash
make format
make lint
make typecheck
make verify
```

`make lint` runs `ruff check` and `ruff format --check`, so format drift fails `make verify`; `make format` fixes it.

`make verify` should run the fast deterministic verification set. It runs `make test`, which includes the `integration`-marked tests: they skip when Qdrant is unreachable, and when a local Qdrant is running they create and remove temporary collections against it.

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

- `skills-sync` regenerates `.claude/skills/`, `.agents/skills/` and `.kiro/skills/` from `agent-skills/`.
- `skills-check` fails if any mirror differs; it is part of `make verify`.

Run a role (each in a fresh session; the orchestrator is the usual entry point):

| Host | Commands |
|---|---|
| Claude Code | `/spec-orchestrator [NNN]`, `/spec-planner`, `/spec-implementer <NNN> [task]`, `/task-reviewer <NNN> <task>`, `/spec-reviewer <NNN>` |
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
- options (through `INGEST_ARGS`): `--embedder {bge_m3,fake}` (default `embedder.provider` from the config), `--config` (default `<repo-root>/config/ingestion.yaml`); `make ingest` passes `--repo-root` itself;
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

`make index-lexical` (Spec 007; no Qdrant client, no embedder, no model; writes one local file):
- builds the BM25 index (`lexical-v1` tokens in an SQLite FTS5 file) from the same eligible chunks, payloads and point IDs that `make ingest` writes, for the collection `QDRANT_COLLECTION_BASE` plus `index_version` from `config/ingestion.yaml`. Only guest/public eligible chunks go in, so the file's corpus-wide BM25 statistics (IDF, average length) reveal nothing about other scopes; when roles are added, each access scope needs its own lexical file;
- options (through `LEXICAL_ARGS`): `--embedder {bge_m3,fake}` (the dense identity the file is built for; default from the config, the model is never loaded), `--output`, `--config`; `make index-lexical` passes `--repo-root` itself. A relative `--output` or `W2A_LEXICAL_INDEX_DIR` resolves against the repository root;
- the file is `<W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite`; the default directory is `.local/lexical` (git-ignored). The target is refused (exit 2, nothing written) inside `knowledge/`, `evaluation/` or `config/`, and, inside a git work tree, anywhere git does not report as ignored; a target outside any git work tree is allowed. It is written to a temporary name and renamed, so a failure leaves the old file;
- prints `lexical index: <path> (collection <c>, index_version <v>; lexical-v1; chunks N; digest <12 hex>)`; errors print `ERROR <ClassName>: <message>`, exit `0` or `2`;
- run it again after every `make ingest` that changes content: a stale file is refused by the strategies below (identity, chunker or chunk-digest mismatch), and the refusal names `make index-lexical`.

Strategies: `make retrieve` and `make eval-retrieval` take `--strategy {dense,bm25,hybrid}` (through `RETRIEVE_ARGS` and `EVAL_ARGS`); `--retrieval-config` (default `config/retrieval.yaml`) holds `default_strategy`, now `hybrid`, and the RRF settings. Every strategy still builds the embedder and needs the dense index in Qdrant (BM25 does not embed the query, but binds to the dense index; it needs Qdrant and the `bge-m3` extra). **Because the default is `hybrid`, a command without `--strategy` needs the local lexical file and exits 2 without it** (`LexicalIndexBindingError`, naming `make index-lexical`); the setup order is `make ingest`, then `make index-lexical`. `--strategy dense` needs no lexical file.

## Retrieval

```bash
make retrieve QUERY="Is coaching compulsory?"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--strategy dense"
make retrieve QUERY="Is coaching compulsory?" RETRIEVE_ARGS="--embedder fake --top-k 3"
make retrieval-baseline
make retrieval-baseline BASELINE_ARGS="--embedder fake --allow-fake --output /tmp/baseline.json"
```

`make retrieve` behavior:
- options (through `RETRIEVE_ARGS`): `--embedder {bge_m3,fake}`, `--top-k` (1 to 50, default 5), `--config`, `--strategy {dense,bm25,hybrid}` and `--retrieval-config` (see "Lexical index and retrieval strategies"; the default strategy is `hybrid` and needs the lexical file); `make retrieve` passes `--repo-root` itself. There is no option for role, scope or tenant: access is always guest/public for the tenant in `W2A_TENANT_ID`;
- prints a header (`index: <collection> (index_version ...; embedder <model> @ <revision>, fake=<bool>)`, `device=`, `strategy=<name>`), the hit count (hybrid hit lines also show the per-leg ranks `dense=<rank|->  bm25=<rank|->`; a query with more than 64 distinct terms prints a truncation note), and one line per hit: rank, `document_id`, `section_id`, score, title. It prints no document bodies, absolute paths or API keys; payload text is passed through `safe_text` (control characters, ANSI and bidi override characters removed);
- needs Qdrant with an index built by `make ingest` for the same `QDRANT_COLLECTION_BASE` and `index_version`; with `--embedder fake` use the throwaway base the fake ingest used;
- exit codes: `0` success (including zero hits), `2` refusal or configuration error (empty query, bad `--top-k`, empty `W2A_TENANT_ID`, missing `bge-m3` extra, missing or mismatched index, a missing, stale or mismatched lexical file for `bm25`/`hybrid`, unreachable Qdrant, a hit that fails the access re-check). Retrieval and ingestion errors print `ERROR <ClassName>: <message>`; any other exception prints its class name only;
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
make eval-retrieval EVAL_ARGS="--strategy dense"
make eval-security
make eval-compare BASE=<result.json> CANDIDATE=<result.json>
```

All four run one module, `python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}`. Extra options for `eval-retrieval` and `eval-security` go in `EVAL_ARGS`; the `make` targets pass `--repo-root` themselves. `make eval-generation` does not exist yet (generation evaluation is a later roadmap item). Error lines are `ERROR <ClassName>: <message>` with payload-derived text passed through `safe_text`; an unexpected exception prints its class name only. Exception: an `eval-compare` refusal prints its message without that prefix, starting with `not comparable:`.

`make validate-evaluation` (part of `make verify`, no Qdrant, no model):
- validates the suite manifest (`evaluation/schemas/evaluation_suite.schema.json`; suite `status` is one of `draft`, `active`, `deprecated`, `replaced`) and every dataset line (`evaluation_case_types.schema.json`, which reuses the existing `evaluation_case.schema.json`);
- cross-checks: unique `case_id` across the suite, each case's `evaluation_suite_id`, `case_count`, no dataset path listed twice, and that every relevant document is in the corpus (otherwise "unknown document") and eligible for guest/public (otherwise "not eligible"), through the document repository;
- validates the candidate files in `evaluation/candidates/` (status `suggested`, proposed case valid, eligible documents, a non-`en` proposed query needs `needs_fluent_speaker_review: true` and `owner_review` in `requires_review`) and refuses a suite that lists a candidates file as a dataset;
- prints one line per problem (`ERROR <file>:<line> <case_id> <field>: <reason>`; the line number and case ID are left out when they do not apply) and a closing count line (`validate-evaluation: OK, 0 problems` or `validate-evaluation: FAILED with <n> problem(s)`); exit `0` valid, `1` problems, `2` configuration error (missing schema, unreadable suite, invalid corpus, a dataset path outside the repository).

`make eval-retrieval` (quality measurement; needs the real BGE-M3 index, see `make setup-bge-m3` and `make ingest`):
- options: `--top-k` (1 to 50, default 5), `--strategy {dense,bm25,hybrid}` (default `default_strategy` in `config/retrieval.yaml`, now `hybrid`: it needs the lexical file from `make index-lexical` and exits 2 without it, naming that command), `--retrieval-config`, `--suite` (default `evaluation/suites/public-eval-v2.json`), `--release` (default `seed-v1`, must match `knowledge/releases/<id>.json`), `--output`, `--repo-root` (default: the current directory), `--config` (default `<repo-root>/config/ingestion.yaml`). There is no `--embedder` or `--allow-fake` option;
- runs the active golden cases, then the active unanswerable cases (top-1 score only; their latency is not in p50/p95), through the chosen strategy with the one server-resolved guest access;
- refuses with exit 2, before any Qdrant contact, a suite whose `status` is not `active`, a missing or mismatched declared release, an existing output file, and a configured fake embedder; a recorded fake index is refused after the read-only binding; the D036 binding rules apply;
- the result is `experiments/results/retrieval-evaluation-<index_version>-<UTC YYYYMMDDTHHMMSSZ>.json` unless `--output` is given: `kind: retrieval_evaluation`, `schema_version` 2.1 (2.0 plus `retrieval_strategy`, `score_kind`, `fusion`, `lexical_index`, per-case `leg_ranks` and `query_terms_truncated`, `truncated_query_count`, per-leg latency; D053), a superset of the 1.0 baseline keys (overall, per `query_language`, per `category` and per `source_authority` metrics with a `small_sample` flag below 10 cases, absent query languages, section-level metrics, the unanswerable top-1 score distribution marked informational, latency, per-case rows, notes). It holds no query text, chunk text, absolute paths or secrets, is never overwritten, and nothing is written on error. Tests and throwaway checks should use `--output` in a temporary directory; do not commit a throwaway result;
- `git_dirty` in the result ignores untracked files under `experiments/results/` (earlier result files of the same session); any other change, including a tracked change there, marks the run dirty;
- exit codes: `0` success, `2` refusal or error.

`make eval-security` (authorization hard gate; fake embedder on a throwaway in-memory Qdrant plus a throwaway lexical file in a temporary directory, no Docker, no model; not part of the `make verify` target itself, but its logic is covered by the unit tests that `make verify` runs):
- options: `--repo-root`, `--config`, `--suite`, `--fixture-root` (default `<repo-root>/tests/fixtures/security`; that default lives only in the CLI, library code never names it) and `--output` (default `experiments/results/tmp/security-evaluation-<UTC>.json`, git-ignored);
- builds a collection `w2a-sectest-<8 hex>` holding the eligible seed corpus plus forbidden points (staff scope, other tenant, owned, missing owner, and the staff-only canary fixture) that are the nearest neighbour of every query, checks without a filter that a forbidden point really is nearest, then, for each of `dense`, `bm25` and `hybrid` (each leg also checked without a filter; a query with no `lexical-v1` terms skips the lexical check and is counted), retrieves through the production path at `top_k` 50 for the active retrieval-side security cases and every active golden query. Other attack types are listed as deferred with an owner;
- the fixture folder must hold exactly `poisoned_public_document.md` and `staff_only_canary.md` (hidden dot-files are ignored); any other visible entry or a missing file is refused before anything is copied;
- the throwaway collection is deleted in the CLI's `finally`, so a failed run removes it too;
- the result is `kind: security_evaluation`, `schema_version` 1.1: `passed`, `access`, `index`, `strategies`, `bm25_no_term_queries`, query and case counts, `violations` (`case_id`, `strategy`, `document_id`, `variant`), `deferred`, `excluded_fixtures`, `duration_ms`; IDs, counts and verdicts only, never query or chunk text;
- exit codes: `0` pass, `1` violation (a forbidden document returned, or the access re-check raised; printed as `VIOLATION case <id> document <id> variant <name>`), `2` harness or configuration error (`EvaluationHarnessError`, for example the sanity check not finding a forbidden point nearest; or a configuration error such as an existing output file, which is `RetrievalConfigurationError`, or a refused fixture folder, which is `EvaluationConfigurationError`).

`make eval-compare BASE=<file> CANDIDATE=<file>` (both required; exit 2 with a usage line otherwise):
- reads a Spec 005 1.0 baseline file or a 2.0 or 2.1 evaluation file (a 1.0 or 2.0 file counts as a dense run); the `source_authority` slice is compared only when both are 2.0 or later;
- gate rule (constants in code; changing them needs a spec amendment): fail when the candidate has more than 1 fewer hit cases than the base, or when the mean reciprocal rank drops by more than `1/n` for `n` compared cases. Both are computed from the per-case rows, not from the rounded aggregates. Cases that flip hit to miss or miss to hit are printed as `WARNING flipped ...` lines; slice deltas and latency changes are printed too; none of these fails the gate;
- refuses (exit 2) files that are not comparable: different suite ID or version, different case sets, different `top_k` or document count, either side from a fake-embedder index, a different collection (when both record one), `index_version`, embedder (model ID and revision) or lexical index (tokenizer and chunk digest; a different strategy is allowed and printed as an identity line), a 2.1 `bm25` or `hybrid` file without a `lexical_index` object, an unreadable or unknown file, or a file that repeats a `case_id`. The refusal is one message on stderr that starts with `not comparable:`, names every difference (old -> new, up to 10 case keys per list, then `and N more`) and ends with the next step (for example a new baseline with `make eval-retrieval`);
- flip warnings print the case key as `<case_id> v<case_version>`, sorted, for example `WARNING flipped hit->miss: g002 v1`;
- exit codes: `0` pass (warnings allowed), `1` gate failure, `2` refusal.

Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, at document level (section level where a case has `relevant_section_ids`).

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

Refresh the graph after code changes (local, no model cost).

```text
/graphify . --update
```

In Claude Code: refresh after documentation changes (re-extracts changed docs; uses the model). Run by the user once per spec, after the merge to `main`; `spec-orchestrator` reminds you.

```bash
graphify query "<question>"
```

Query the graph; `graphify path "<A>" "<B>"` and `graphify explain "<concept>"` for relationships and concepts. Install once with `uv tool install graphifyy` and make sure `~/.local/bin` is on `PATH` (`uv tool update-shell`).

## Rule

Do not invent alternative project command surfaces unless this file is intentionally updated.
