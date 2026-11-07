# 012 — Grounded Generation Tasks

Status: implementing (branch spec/012, base 416fc3a)

Implement the tasks in order; each depends on the ones before it. Requirements: `requirements.md` (approved 2026-11-07). Design: `design.md` (approved 2026-11-07; D-A and D-B as recommended, D-C no committed default until T6, D-D generic wording with the English-terms clause).

Rules for every task:
- **Protected paths.** `knowledge/` never changes. `config/` and `evaluation/` change only as each task's "Allowed protected-path changes" line says. Every task checks `git status --porcelain -- evaluation knowledge config`, and the reviewer compares the output with the allowed list.
- **Retrieval unchanged.** These are not edited: everything under `retrieval/` except the argument helper extracted from `retrieval/cli.py` (T4), and `rerank/`, `lexical/`, `ingestion/`, `repositories/`, `config/retrieval.yaml`, `config/ingestion.yaml`, `apps/api/`. Existing retrieval, compare, continuity and security tests pass with their assertions unchanged (only import paths may change for the `script_mix` move). `make retrieve` output is byte-identical for the same inputs.
- **No HTTP route** (Spec 013).
- **No committed default generator until T6 (D-C).** `default_generator`, `bedrock.model_id` and `pricing` stay `null` in T3–T5. Tests never rely on a default generator; they pass `--generator fake` or construct `FakeGenerator`.
- **`make verify` needs no Docker, PyTorch, extras, network, AWS credentials or model files**, and passes with an empty `HF_HOME` and `HF_HUB_OFFLINE=1`. Importing any module under `generation/` must not import the Anthropic SDK or `boto3`/`botocore`. Tests unset `AWS_*` variables they could read (autouse fixture) so no test can reach AWS by accident.
- **Agents never call Bedrock**, never run the real embedder, reranker or generator, and never write to a `w2a-realcheck-*` or `way2australia-*` collection. Real runs and smoke tests are user-owned.
- **Verify budget.** At most two `make verify` runs per agent session: iterate with targeted `uv run pytest <paths>` and `make lint typecheck`, then run `make verify` once at the end of the task.
- **No language literal or Malayalam-specific branch** in `generation/` code (grep test). Script → language mapping comes from `config/generation.yaml`; active codes from `config/language_registry.json`.
- **No secrets** in code, config, prompts, fixtures, results or docs. No AWS account IDs or ARNs with account IDs.
- **SDK usage.** Class names, constructor arguments and request fields of the Anthropic SDK come from its current documentation (record the URL and SDK version in the T3 hand-off), not from memory.
- **Results.** Tests never write under `experiments/results/` (use `tmp_path`). Throwaway CLI output goes to `experiments/results/tmp/`. Committed result files are never modified.
- **Messages.** Refusals and errors name fields, codes, model IDs and document IDs only, never chunk text, paths, URLs or credentials.
- **`lote` stays outside `AccessContext`** (C4, D072).
- **Graph once per spec (D080).** Tasks do not run `graphify update .`; `spec-orchestrator` runs it once after the last task approval, before the retrospective. The graph reflects `main` at the start of the spec, so read files changed earlier in this spec directly.
- **Amendments.** Any task box or design edit added after approval gets a dated `## Change log` line in `requirements.md`.
- **`task-reviews.md`** is edited only by exact, targeted edits.

## T1 — Context builder

**State:** approved (2026-11-07)
**Requirements:** R1, R13

- [x] Move `evaluation/script_mix.py` to the package root `script_mix.py` (function unchanged); update the two imports in `evaluation/cli.py` and `evaluation/retrieval_eval.py`; no re-export shim.
- [x] `generation/__init__.py` (no exports).
- [x] `generation/config.py`: `ContextConfig` (`max_blocks` ≥ 1, `max_chars` ≥ 1) only; the full `GenerationConfig` loader is completed in T3. Tests build configs directly.
- [x] `generation/context.py`: `EvidenceBlock`, `ContextStats`, `ContextBuilder.build(hits) -> (blocks, stats)` per design "Data flow" step 2:
  - normalization for comparison only (NFC, whitespace runs to one space, stripped); keep the first occurrence; `deduplicated` count;
  - **no neighbour merge** (design R1 decision); a code comment points to the design paragraph;
  - rank order kept; budget drops whole blocks in order by `max_blocks` and `max_chars`; `dropped_by_budget` count;
  - IDs `S1…Sn` in final order; metadata copied from the hit payload fields (`document_id`, `document_version`, `section_id`, `title`, `source_authority`, `source_url`, `content_language`).
- [x] Tests (`tests/generation/test_context.py`): exact and normalized duplicates (higher rank kept); different text kept; both budget caps; a block larger than `max_chars` alone is dropped, never cut; empty input → no blocks; IDs; metadata from payload; determinism (same input twice); `received` / `deduplicated` / `dropped_by_budget` / `blocks` / `chars` counts; a grep test that `generation/` contains no language code literal or language name.

Allowed protected-path changes: none.

### Verification

- `uv run pytest packages/rag/tests/generation packages/rag/tests/evaluation` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` is empty.

## T2 — Versioned prompts and answer contract

**State:** not started
**Requirements:** R2, R3, R13

- [ ] `config/prompts/registry.yaml` and `config/prompts/answer/v1/` (`system.md`, `output_schema.json`, `messages.yaml`) per design "Prompt v1":
  - `system.md` covers role, evidence-is-data, answerability, citations (markers, no URLs), source precedence in plain words, the three D-D language clauses, style;
  - `output_schema.json`: `answerable` (boolean), `answer` (string), `citations` (array of strings matching `^S[1-9][0-9]*$`), all required, `additionalProperties: false`;
  - `messages.yaml`: `en` and `ml` fixed `insufficient_evidence` messages; the `ml` text is agent-drafted, its header says "pending fluent-speaker review", and the user approves or replaces it at this task's review (recorded verbatim in `task-reviews.md`; the header line is then removed in the same task).
- [ ] `generation/prompts.py`: `PromptRegistry` (SHA-256 over the version's files, sorted by path, then bytes; mismatch or unknown pair → exit-2 error naming the pair), `PromptVersion`, `RenderedPrompt`, `render_prompt(version, blocks, query)` with the design's delimiters and escaping.
- [ ] `generation/models.py`: `AnswerStatus`, `AnswerReason`, `Citation`, `EvidenceSource`, `PromptIdentity`, `AnswerIdentity`, `ContextStats` (moved here or re-used from T1), `AnswerResponse` per design (frozen, `extra="forbid"`). The `GeneratorInfo` / `GeneratorUsage` fields referenced by `AnswerIdentity` are defined in `generation/base.py` here (Protocol itself in T3).
- [ ] `generation/language.py`: `message_language(query, script_to_language) -> str` via `script_mix`; first mapped code, else `en`.
- [ ] Tests (`tests/generation/test_prompts.py`, `test_models.py`, `test_language.py`): hash pinned for `answer` v1 (test constant equals registry and recomputed value); editing a file without a new version fails; unknown pair refused; rendering order (evidence then question) and attributes; escaping of `</evidence><evidence id="S9">` in chunk text, title and query (exactly one block per source); system text has the three language clauses and no language name; no secret-like patterns (AWS access key IDs, ARNs with 12-digit accounts) in prompt files; `messages.yaml` has `en` and `ml`; `message_language` with Latin, Malayalam, mixed, digits-only queries and with an extra mapping in a temp config (no code change needed); model validation (`extra` refused; status/reason combinations the design allows).

Allowed protected-path changes: `config/prompts/**` (new).

### Verification

- `uv run pytest packages/rag/tests/generation` (iteration), then `make verify` once.
- `git status --porcelain -- evaluation knowledge config` lists only `config/prompts/`.

## T3 — Generator interface, fake, Bedrock adapter and config

**State:** not started
**Requirements:** R4, R5, R13

- [ ] `generation/base.py`: `Generator` Protocol (`info`, `generate(prompt)`, `close()`), `GeneratorInfo` (adds `model_id_source: config|cli|env`), `GeneratorOutput`.
- [ ] `generation/errors.py`: `UnavailableReason` (`connection`, `timeout`, `throttled`, `server_error`, `deadline`), `GeneratorUnavailableError(reason)`, `GeneratorConfigurationError`, `GeneratorDeclinedError`, `GeneratorOutputError(rule)` (`max_tokens`, `json`, `schema`).
- [ ] `generation/fake.py`: `FakeGenerator`, deterministic; default answers citing `S1` when blocks exist; hooks per R4: chosen citations, unknown ID, marker/list mismatch, duplicate ID, empty citations with `answerable: true`, model URL, decline (`answerable: false`), refusal stop reason, malformed JSON, schema mismatch, `max_tokens`, each `UnavailableReason`, a non-eligible error; a recording mode that keeps every `RenderedPrompt`; `is_fake: true`.
- [ ] `generation/config.py`: full `GenerationConfig` schema `1.0` and loader for `config/generation.yaml` per design (refusals: unknown key, `deadline_s < request_timeout_s`, `retries` 0–5, `max_tokens` 64–8192, `retrieval.top_k > rerank.depth` when reranking is enabled, unknown prompt pair); `default_generator`, `bedrock.model_id`, `pricing.*` may be `null`.
- [ ] `config/generation.yaml` committed with `default_generator: null`, `bedrock.model_id: null`, `pricing` nulls (D-C), `endpoint: runtime`, `region: ap-south-1`, `inference_profile: null`, `effort: low`, `max_tokens: 1024`, `request_timeout_s: 20`, `retries: 2`, `backoff_s: 1.0`, `deadline_s: 30`, the context, retrieval, evidence-only, languages and estimate values from the design.
- [ ] `generation/bedrock.py`: `BedrockGenerator` per design "Bedrock adapter":
  - lazy SDK import in `__init__`; missing extra → `OptionalDependencyError` naming `make setup-bedrock`;
  - client by `endpoint` (`runtime` / `mantle`) with `max_retries=0`, region; credentials from the default chain only; credential failure → `GeneratorConfigurationError`;
  - request: model (`inference_profile` or `model_id`), `max_tokens`, `system`, one user message, `output_config` with `format` (schema) and `effort`; no sampling fields, no `thinking`, no tools, no streaming;
  - attempt loop with per-attempt timeout `min(request_timeout_s, remaining)`, exponential backoff capped by the deadline, `retry-after` honoured only within the deadline, stop with `DEADLINE` when ≤ 1 s remains; `usage.attempts`;
  - D-B classification table by SDK exception type and HTTP status; explicit `__cause__` chain only;
  - output: `refusal` → `GeneratorDeclinedError`; `max_tokens` → `GeneratorOutputError("max_tokens")`; first text block parsed and validated with `jsonschema`;
  - a client-construction seam so tests inject a stub client; `close()`.
- [ ] `generation/build.py`: `build_generator(config, provider, model_id_override)`; `bedrock` without a model ID → exit-2 error with advice (`--model-id` or T6 config).
- [ ] `packages/rag/pyproject.toml`: `bedrock = ["anthropic[bedrock]>=<version>"]` (version checked against the SDK docs; hand-off records version and docs URL); `uv.lock`; `Makefile` `setup-bedrock` (`--extra bge-m3 --extra reranker --extra bedrock`); `make setup` still removes optional extras.
- [ ] Opt-in smoke test `W2A_RUN_BEDROCK_SMOKE=1` with model from `W2A_BEDROCK_MODEL_ID` (skipped by default; never run by agents): one fixed two-block prompt through the configured endpoint and region; passes only if the output is schema-constrained structured output that validates against the v1 schema, cites only issued IDs, and records model, endpoint, region or profile and usage. Prints a one-line summary with no credentials.
- [ ] Tests (`tests/generation/test_fake.py`, `test_bedrock.py`, `test_generation_config.py`): every fake hook; lazy import (`anthropic`, `boto3`, `botocore` absent from `sys.modules` after importing every `generation/` module); missing extra exit 2; stub-client request shape (no `temperature`/`top_p`/`top_k`/`thinking`/`tools`; `output_config.format` and `effort` present; `max_retries=0`); D-B table (connection, timeout, 408, 429, 500, 502, 503, 504, 529 eligible; 400, 401, 403, 404, credentials → configuration error; other errors propagate; `__context__` ignored); retries and backoff with a fake clock; deadline stops further attempts and raises `DEADLINE` even mid-retry; `retry-after` beyond the deadline not honoured; output parsing branches; config refusals; the committed file has `default_generator: null`, `model_id: null`, null pricing (read from the file); `bedrock` without a model ID refused.

Allowed protected-path changes: `config/generation.yaml` (new).

User-owned check after this task is approved (gate before T6's runs; recommended before T4 starts): the D-A smoke test for Sonnet 5.5 and Haiku 5.5 in the user's account and region, recorded verbatim in `task-reviews.md` (pass or fail, model ID, endpoint, region or profile; no credentials). If structured output is not accepted, `spec-planner` amends the spec for the named strict-tool fallback before T6.

### Verification

- `uv run pytest packages/rag/tests/generation` (iteration), then `make verify` once (also with `HF_HUB_OFFLINE=1 HF_HOME=$(mktemp -d)` as the single run if budget allows only one).
- `git status --porcelain -- evaluation knowledge config` lists only `config/prompts/` (T2, committed) and `config/generation.yaml`.

## T4 — Answer service, citation validation and `make ask`

**State:** not started
**Requirements:** R3, R6, R7, R8, R13

- [ ] `generation/citations.py`: `validate_citations(output, blocks)` per design step 6 (rules `unknown_id`, `marker_mismatch`, `no_citation`, `duplicate_id`, `model_url`); validated `Citation`s in first-marker order with metadata from the blocks.
- [ ] `generation/service.py`: `AnswerService(retriever, builder, prompt_version, generator, config)` and `answer(query, access, top_k, lote) -> AnswerResponse` per design "Data flow" and the error table; pre-gate makes zero generator calls; catches only `GeneratorUnavailableError`, `GeneratorDeclinedError`, `GeneratorOutputError`; `evidence_only` sources with `safe_text` snippets cut to `snippet_chars`; `insufficient_evidence` message by `message_language`; identity (retrieval fields as result 2.5, prompt, generator or `None` when not called), usage, per-stage latency, context stats.
- [ ] `retrieval/cli.py`: extract the retrieval argument definitions and rerank resolution into a helper reused by `generation/cli.py`; `make retrieve` behaviour and output unchanged (existing CLI tests untouched).
- [ ] `generation/cli.py` and `Makefile` target `ask` (`make ask QUERY=... ASK_ARGS=...`) per design "`make ask`": shared retrieval arguments plus `--generator fake|bedrock` and `--model-id`; `open_retrieval` called as `retrieval/cli.py` calls it; without `--generator` and with `default_generator: null` → exit 2 with advice; output lines per design (answer through `safe_text`); fake generator prints `generator: fake` and a stderr warning; exit 0 for the three statuses, 2 for configuration errors; generator and retrieval closed on exit.
- [ ] Tests (`tests/generation/test_citations.py`, `test_service.py`, `test_ask_cli.py`):
  - citations: every rule; `[S01]`, `[s1]`, markers inside words, no markers, URLs in `http` and `https` forms; metadata never taken from the model;
  - service: pre-gate zero calls; every status, reason and sub-reason end to end with a fake retriever and `FakeGenerator`; `RetrievalAuthorizationError` and `LanguageApplicabilityError` propagate; identity complete; message language;
  - R7: on the security corpus (fake embedder, fake reranker), a recording fake generator shows no staff-scope or other-tenant chunk text or `document_id` in any rendered prompt; the model output cannot change access or citation metadata;
  - CLI: with `--embedder fake --reranker fake --generator fake` on the in-memory fixtures used by the retrieval CLI tests; no `--generator` → exit 2 (reads `default_generator` from the file, never a literal); `--generator bedrock` without model ID → exit 2; fake warning; exit codes; `make retrieve` output unchanged for a fixed query.

Allowed protected-path changes: none.

### Verification

- `uv run pytest packages/rag/tests/generation packages/rag/tests/retrieval` (iteration), then `make verify` once.
- `make ask QUERY="Is coaching compulsory?" ASK_ARGS="--embedder fake --reranker fake --generator fake"` against a throwaway fake index base (`QDRANT_COLLECTION_BASE=w2a-t012-<8 hex>`, deleted afterwards), or the in-memory fixture path the CLI tests use if Docker is not running; output recorded in the hand-off.
- `git status --porcelain -- evaluation knowledge config` is empty for this task.

## T5 — `make eval-generation`, generation security checks and candidates

**State:** not started
**Requirements:** R9, R10, R11, R13

- [ ] `evaluation/generation_eval.py` and the `generation` subcommand in `evaluation/cli.py`; `Makefile` target `eval-generation` (`EVAL_ARGS`), per design "`make eval-generation`":
  - `--generator` required while `default_generator` is null; `--model-id`, `--price-input`, `--price-output` overrides recorded;
  - real generator: exactly one of `--limit N` / `--all`; phase 1 (retrieval, context, rendering, estimate printed; zero generator calls) then confirmation (`y` on a TTY, or `--yes`; no TTY and no `--yes` → exit 2); null pricing without overrides → exit 2 naming the key;
  - fake generator: `--allow-fake` required, output to `experiments/results/tmp/`;
  - result `generation_evaluation` schema `1.0` with every top-level and per-case field in the design, including `generator_unavailable` counts by sub-reason with affected `case_id`s (also printed in the summary);
  - `--min-refusal-rate`, `--min-answer-rate`: exit 1 when not met.
- [ ] `evaluation/security_eval.py`: `generation_prompt_isolation` over all eight retrieval paths, `generation_poisoned_evidence`, `generation_citation_manipulation` per design "Security"; security result `1.6`; the eight retrieval paths and their records unchanged.
- [ ] `evaluation/candidates/012-candidates.jsonl`: `status: suggested` rows in the existing candidate format (no new case fields), each with drafter (`agent`) and the required reviews (`owner_review`; `fluent_speaker_review` for `ml`/`mixed`):
  - generation goldens: answers needing two documents; fees and numbers; source-authority precedence; at least one whose evidence contradicts a likely wrong answer (the plausible false claim stated in the row's review notes, the true fact in `expected_facts`);
  - unanswerable / refusal cases, including near-miss questions whose topic is in the corpus but whose answer is not;
  - English, Malayalam and mixed rows.
- [ ] Tests (`tests/evaluation/test_generation_eval.py`, `test_security_eval.py` additions, `test_validate.py` if needed):
  - hard gates on the fake (R9): every fake defect gives the expected status and reason; every unanswerable case refuses when the fake declines or no evidence exists;
  - cost guard: estimate printed before any generator call (recording fake shows zero calls before confirmation); `--limit` proportional selection (at least one unanswerable case when N ≥ 2); `--all`; `--yes`; no-TTY exit 2; null pricing refused for a real generator (stub `bedrock` provider, no SDK); overrides recorded;
  - metrics on a crafted case set (answer rate, refusal rate with `evidence_only` excluded, `citation_invalid` by sub-reason, `generator_unavailable` by sub-reason, precision/recall, `expected_facts` coverage by language marked informational, script mix, latency, tokens, cost); `--min-*` exit 1; result written only under `tmp_path`;
  - security 1.6 checks pass and a deliberately broken validator (monkeypatched) makes `generation_citation_manipulation` fail;
  - `make validate-evaluation` passes with the candidates file; candidates are never loaded as cases.

Allowed protected-path changes: `evaluation/candidates/012-candidates.jsonl` (new).

### Verification

- `uv run pytest packages/rag/tests/evaluation packages/rag/tests/generation` (iteration), then `make verify` once.
- `make eval-security` passes (all retrieval paths and the three generation checks).
- `make eval-generation EVAL_ARGS="--generator fake --allow-fake --embedder fake --reranker fake"` on a throwaway fake index, or the in-memory path if Docker is not running; output under `experiments/results/tmp/`, summary in the hand-off.
- `make validate-evaluation`.
- `git status --porcelain -- evaluation knowledge config` lists only the candidates file for this task.

## T6 — Real runs, model choice and suite v4 (user-owned gate)

**State:** not started
**Requirements:** R12, R14, R8 (default), R13

User-owned steps (the agent prepares commands and checks files; it never calls Bedrock):

- [ ] Smoke gate passed for each model to compare (T3 check, recorded in `task-reviews.md`); if not, stop for a spec amendment.
- [ ] **Before any real run**, the user approves and this task records verbatim in `task-reviews.md`: the refusal threshold on unanswerable cases, the minimum golden answer rate, and the "falls short" criteria (for example maximum p95 generation latency, maximum cost per answer).
- [ ] Model access: the user confirms each model in `ap-south-1`; if a model is served only through an APAC inference profile, record it (the decision is written in T7).
- [ ] Runs: `make setup-bedrock`; on `w2a-realcheck-idx-v2` with suite v3, `lote` as in the v3 references, same case selection for each model: `make eval-generation EVAL_ARGS="--generator bedrock --model-id <id> --price-input <p> --price-output <p> --all --yes --min-refusal-rate <t> --min-answer-rate <t>"` for Claude Sonnet 5.5 and Claude Haiku 5.5 (Opus 5.5 only if both fall short).
- [ ] Each compared run has zero `generator_unavailable`, or the affected cases are re-run (`--limit`/case selection as the design allows) and the re-run recorded.
- [ ] The agent checks each result file (suite, not fake, clean commit, retrieval identity equal across runs, prompt identity, generator identity, thresholds given) and the user commits them.
- [ ] Model choice by the recorded criteria, or the user's verbatim decision.

Agent steps after the choice:

- [ ] `config/generation.yaml`: `default_generator: bedrock`, the chosen `bedrock.model_id` (and `inference_profile` if needed), `pricing` — changed together in one commit.
- [ ] CLI tests for the new default, in this task: replace the T4/T5 "no `--generator` → exit 2" tests with tests that read `default_generator` from the file (never a literal) and show `make ask` / `make eval-generation` without `--generator` build the configured provider (stub, no SDK call).
- [ ] Suite v4 (R12), with the user: the user approves candidates (owner, and fluent speaker for `ml`/`mixed`), verbatim in `task-reviews.md`; create `evaluation/suites/public-eval-v4.json` and `evaluation/datasets/v4/` (v3 cases carried over unchanged except `evaluation_suite_id`, plus approved cases with new `case_id`s); v3 suite `status: replaced`; candidate rows keep `status: suggested` with `review.promoted_as`; `DEFAULT_SUITE` in `evaluation/cli.py` → v4. If none is approved, record that and skip v4.
- [ ] Continuity: the user runs `make eval-retrieval` on v4 with the settings of the current v3 retrieval reference (Spec 011 depth 20, rerank on, `lote ml`: `experiments/results/retrieval-evaluation-idx-v2-20261106T072428Z.json`) and `make eval-continuity` against that file: no shared-case differences.
- [ ] One reference run of the chosen model on v4 (`make eval-generation`, case limit at the user's choice), committed.

Allowed protected-path changes: `config/generation.yaml` (`default_generator`, `bedrock.model_id`, `bedrock.inference_profile`, `pricing` only); `evaluation/suites/public-eval-v3.json` (`status` only); `evaluation/suites/public-eval-v4.json`, `evaluation/datasets/v4/**` (new); `evaluation/candidates/012-candidates.jsonl` (`review` fields only).

### Verification

- Result files checked and committed; thresholds and choice recorded verbatim.
- `make validate-evaluation`; `make verify` once; `make eval-security` on v4.
- `git diff --name-status main...HEAD -- evaluation knowledge config` matches R15.

## T7 — Docs, decisions and hand-off

**State:** not started
**Requirements:** R15, R16, Definition of Done

- [ ] `DECISIONS.md` from D081 (D080 is the workflow trim): context builder (exact-text dedup only, the payload evidence, budget, ordering, source IDs); prompt versioning and registry hash; answer contract and reasons; answerability (pre-gate, model assessment, backend enforcement, no score threshold); citation validation rules; generator interface, client choice (D-A), extra, config and deadline; outage eligibility (D-B) **as its own decision recording the departure from D062**; no committed default until T6 (D-C) and the T6 default; answer-language rule and generic wording (D-D); generation result 1.0 and cost guard; security result 1.6; region / inference-profile choice; the T6 model outcome with the numbers listed in R14; suite v4 (or its absence).
- [ ] `ARCHITECTURE.md` (query flow through generation; `generation/` module table), `COMMANDS.md` (`make ask`, `make eval-generation`, `make setup-bedrock`, overrides, refusals and exit codes), `TECH_STACK.md` (Bedrock model, client, region), `ROADMAP.md` (item 10 done except the route; item 9 context building done; item 13 model-failure path done), `CURRENT_STATE.md` (implemented reality; Spec 012 row; Known issues).
- [ ] Carry-overs in `CURRENT_STATE.md` Known issues and for the retrospective's notes: Spec 013 serving items (HTTP route, `open_retrieval` rework for 011 F1/F2/F3 and 008 F4, Qdrant client and model lifecycle, async freshness, lexical startup and tokenizer policy, circuit breaker, reranker reload/health, latency/concurrency/device budgets including generation); provenance-not-faithfulness (item 12 or an evaluation spec); neighbour merge needing overlap boundaries in the payload; streaming.
- [ ] Design As-built notes for any deviation found during T1–T6.
- [ ] Spec-wide checks (R15): `make verify` (no extras, network, credentials or Docker; hub-free), `make test-integration` (Docker Qdrant), `make eval-security`, protected-path diff.

Allowed protected-path changes: none.

### Verification

- All commands above pass; results recorded in the implementer hand-off.
- `grep` of the docs for stale schema versions (security `1.5`, "no generation") and path counts before hand-off (Spec 011 process note).
