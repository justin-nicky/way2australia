# 012 — Grounded Generation Requirements

Status: approved (2026-11-07)

## Goal

Answer guest questions from retrieved public evidence with an LLM on Amazon Bedrock, with backend-owned citations (roadmap item 10, without the HTTP route). Concretely:

- a context builder turns the retrieved hits into a bounded, deduplicated, ordered set of evidence blocks with backend-assigned source IDs;
- a versioned prompt and a `Generator` interface (Bedrock adapter plus a deterministic fake) produce a structured answer;
- answerability is decided by a deterministic evidence pre-gate, the model's own structured assessment, and backend enforcement that an answer must carry valid citations;
- citations are validated by the backend, fail closed, and mapped to approved document metadata; the model never produces URLs;
- a generator outage (including a timeout) returns an evidence-only response, closing the model-failure path of roadmap item 13;
- `make ask` runs the whole path from the command line; `make eval-generation` measures it;
- user-owned real runs compare Claude Sonnet 5.5 and Claude Haiku 5.5 on Bedrock and choose the default model.

Repository facts that shape the scope (checked 2026-11-07 on `main` `120c110`):

- Retrieval is complete through Spec 011: default `hybrid` with reranking on at depth 20 (D079), BM25 fallback (D058), `lote` applicability (D072). `open_retrieval` is the one wiring function; this spec uses it unchanged.
- Retrieved hits carry the full payload, including `title`, `source_authority`, `source_url` (null for the 8 owner-approved documents, a NAATI or Home Affairs URL for the other 5), `document_version`, `section_id` and `chunk_position`.
- The default index has 34 chunks over 13 documents; the recursive chunker overlaps neighbouring chunks by 16 tokens and prefixes the title (D071).
- Suite `public-eval-v3`: 87 goldens with `expected_facts` (English strings) and `relevant_document_ids`, 15 unanswerable cases (`expected_behavior: insufficient_evidence_or_safe_redirect`), 10 security cases. `evaluation/generation/` is empty.
- Unanswerable cross-encoder top-1 scores overlap the golden ones (D079), so no reranker-score threshold is safe.
- `tests/fixtures/security/poisoned_public_document.md` exists for the isolated security corpus.
- No Bedrock or Anthropic SDK dependency exists yet.

## Dependencies

- Spec 011 (verified, merged `d40d734`): `RerankingRetriever`, rerank identity, `rerank.enabled` resolution in the CLIs (retrospective F2), result 2.5, security 1.5 (D075–D079).
- Spec 010: `ResolvedLote`, `check_applicable`, suite `public-eval-v3`, `languages.py` (query-language detection used for reporting) (D072).
- Spec 008: `open_retrieval`, `FallbackRetriever`, the error-eligibility rules (explicit `__cause__` chain, D057, D062).
- Spec 005/006: `ResolvedAccess`, `check_hit` (D035, D040), `safe_text`, suite loader, `validate-evaluation`, candidate rows (C6), `experiments/results/` conventions, the fake allowance.
- Spec 002: document metadata (`source_authority`, `source_url`, `document_version`).
- Retrospective notes: `.kiro/specs/011-multilingual-reranking/review.md` "Notes for the next spec" (serving items go to Spec 013; refusal threshold needs more unanswerable cases; generation-era cases are the higher-value evaluation additions).
- Real runs (R14) need AWS credentials with Bedrock model access in the user's account, the extras, Docker Qdrant and the user's `w2a-realcheck-idx-v2` collection. They are run by the user.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-11-07, with these choices and changes:

- **Name.** `012-grounded-generation`; branch `spec/012` from `main` (`120c110`).
- **Split.** Spec 012: context building, generation, answerability and citations behind a CLI, plus the model-failure path of roadmap item 13. Spec 013: the HTTP route and serving policy (the `open_retrieval` rework for Spec 011 F1/F2/F3 and Spec 008 F4, Qdrant client and model lifecycle, async freshness, lexical startup and tokenizer policy, circuit breaker, reranker reload or health policy, per-request latency, concurrency and device budgets).
- **Region.** `ap-south-1`. An APAC cross-region inference profile is used only if the chosen model is not served in-region; that choice is recorded in a decision.
- **Model.** Default candidate Claude Sonnet 5.5. The real-run task compares Sonnet 5.5 and Haiku 5.5 on the same cases and records latency, tokens and cost per answer; Claude Opus 5.5 is tried only if both fall short (user change 1).
- **Client.** The Anthropic Python SDK's Bedrock client, or `boto3` Bedrock Runtime Converse if that endpoint is not offered in `ap-south-1` (design decides, recorded in a decision); behind a `Generator` Protocol; optional extra; credentials from the default AWS credential chain only.
- **Prompt versioning.** Prompt files in the repo with `prompt_id`, integer `prompt_version` and a pinned content hash.
- **Answerability.** Deterministic evidence pre-gate, the model's structured assessment, backend enforcement (no valid citation means no answer). No reranker-score cut-off.
- **Citations.** Backend source IDs `S1…Sn`, inline `[Sn]` markers plus a citation list, fail-closed validation, metadata from the payload. Claude's native Citations feature is not used.
- **Gates.** Citation-validation enforcement and unanswerable refusal are hard gates on the fake generator only. Real runs report the `citation_invalid` downgrade rate (informational) and measure refusal against a threshold the user approves in the real-run task (user changes 2 and 3).
- **Generator limits.** Request timeout, `max_tokens`, retry policy and a total generation deadline per request live in config; a timeout or a reached deadline is an outage and gives `evidence_only` (deadline added at requirements approval). The real-run evaluation has a cost guard: a case limit and a printed estimate before the run (user change 4).
- **Deduplication.** Neighbour merge only if the payload has a reliable chunk index; otherwise exact-text deduplication only. The design says which (user change 5).
- **Answer language.** The query's language; `mixed` queries are answered in Malayalam; NAATI, CCL, test names and numbers stay in English (user rule; see R3).
- **Evaluation.** New generation and refusal cases start as candidates; the user-approved ones are promoted into suite `public-eval-v4` in the real-run task.
- **Shape.** Seven tasks: T1 context builder; T2 prompts and answer contract; T3 generator interface, fake and Bedrock adapter; T4 answer service, answerability, citation validation and `make ask`; T5 `make eval-generation`, security checks and candidates; T6 user-owned real runs, model choice and v4 promotion; T7 docs, decisions and hand-off.

## R1 — Context builder

Retrieved hits become a bounded, deduplicated, ordered set of evidence blocks.

### Acceptance criteria

- A context builder in `packages/rag/` takes the hits returned by retrieval (already access- and applicability-checked) and returns ordered evidence blocks. It never calls retrieval, Qdrant or the lexical file and never adds a chunk it was not given.
- Deduplication removes chunks whose text is identical after whitespace normalization, keeping the higher-ranked one. Merging neighbouring chunks of the same document is done only if the design shows the payload's chunk index is reliable for it (same document version, consecutive positions, overlap removable without loss); otherwise only exact-text deduplication is done. The design states which, with the evidence.
- Budget: the number of blocks and the total evidence characters are capped by config values; blocks beyond the cap are dropped whole, lowest-ranked first, and never cut mid-text. The result records how many hits were received, deduplicated, merged (if any) and dropped by the budget.
- Ordering: blocks keep retrieval rank order (the reranked order when reranking served). Each block carries its `source_authority` label; ordering does not reorder by authority.
- Each block gets a backend source ID `S1…Sn` in final order, and a mapping from source ID to `document_id`, `document_version`, `section_id`, `title`, `source_authority` and `source_url`, all taken from the payload.
- The builder is deterministic: the same hits and config give the same blocks and IDs. No language code or Malayalam-specific branch appears in it.

## R2 — Versioned prompts

The prompt is a reviewed, versioned asset whose identity is recorded with every answer.

### Acceptance criteria

- Prompt files (system instructions and the structured output schema) live in the repository, with a `prompt_id`, an integer `prompt_version` and a SHA-256 of their content. A test pins the hash of every committed version, so changing the text without a new version fails `make verify`.
- The config names the active `prompt_id` and `prompt_version`; an unknown pair is refused at load (exit 2, naming the key).
- Evidence blocks are inserted inside clear delimiters, each with its source ID and title; the instructions say the evidence is data, not instructions (C10). No secrets, credentials, account IDs or internal hostnames appear in prompt files (C9: the prompt is not a security boundary).
- Every answer, `make ask` output and `make eval-generation` result records `prompt_id`, `prompt_version` and the content hash.

## R3 — Answer contract and language

Every request ends in one of three explicit outcomes with a closed set of reasons.

### Acceptance criteria

- The answer contract has `status`: `answered`, `insufficient_evidence` or `evidence_only`, and a `reason` from a closed set defined in the design (at least: `no_evidence`, `model_declined`, `citation_invalid`, `output_invalid`, `generator_unavailable`).
- `answered` carries the answer text with inline `[Sn]` markers and the validated citations (R6). `insufficient_evidence` carries a fixed, versioned safe message (no generated text). `evidence_only` carries no generated text; it lists the evidence sources (title, `source_authority`, `source_url`, `document_id`, and a short `safe_text` snippet) so the user still gets the approved sources.
- Every response records identity: retrieval served path and rerank identity, prompt identity, generator identity (provider, model ID, region or inference profile, `is_fake`), token counts when the generator reports them, and latency for retrieval, context building and generation.
- **Answer language rule (user-approved).** The answer is written in the query's language. `mixed` queries are answered in Malayalam. NAATI, CCL, test names and numbers stay in English. The rule is stated in the prompt; `make eval-generation` reports the detected answer script per case (informational, not a gate). The fixed `insufficient_evidence` message exists in English and Malayalam and is chosen by the same rule.

## R4 — Generator interface and fake

Generation goes through an explicit interface that the answer service depends on.

### Acceptance criteria

- A `Generator` Protocol in `packages/rag/` takes the rendered prompt and the output schema and returns a structured result (`answerable`, `answer`, `citations`) plus usage (input and output tokens, when known) and an identity (`provider`, `model_id`, region or profile, `is_fake`).
- A deterministic fake generator, usable without any extra, network or credentials, gives the same output for the same input and can be configured in tests to: answer with chosen citations; cite an unknown ID; cite inconsistently (markers and list differ); decline; return malformed or truncated output; raise each eligible outage (including a timeout) and a non-eligible error.
- No language code or Malayalam-specific branch appears in the generator code.

## R5 — Bedrock adapter, config and outage policy

The real generator is configured, bounded and loaded only when asked for.

### Acceptance criteria

- An adapter calls Claude on Amazon Bedrock with structured output for the R4 schema. The SDK is imported only when the adapter is built; a new optional extra declares it; importing retrieval or answer code never needs it. Without the extra, asking for the Bedrock generator exits 2 with advice naming the setup command.
- A reviewed config (file named by the design) holds: provider, `model_id`, region, inference profile (or none), request timeout, `max_tokens`, retry count and backoff, a total generation deadline per request, and the prompt selection.
- The total generation deadline covers every attempt, retry and backoff of one request. When it is reached, no further attempt starts and the response is `evidence_only` with `reason: generator_unavailable` (sub-reason `deadline`). The deadline is recorded in the generator identity. Invalid values are refused at load with a message naming the key. No credentials, keys or account IDs in config; credentials come from the default AWS credential chain.
- Generator errors have their own type with a closed set of reasons. Eligible outages (always including a request timeout, after the configured retries) give `evidence_only` with `reason: generator_unavailable` and the sub-reason recorded. Authentication, permission, model-not-enabled and validation errors are configuration errors (exit 2), never `evidence_only`. The eligibility rules follow D057/D062 (explicit `__cause__` chain; `__context__` never followed); which HTTP statuses are eligible is decided in the design and recorded in a decision.
- A model refusal stop reason gives `insufficient_evidence` with `reason: model_declined`; output cut by `max_tokens` or failing the schema gives `insufficient_evidence` with `reason: output_invalid`.
- `make verify` passes without the extra, network or credentials. An opt-in real smoke test (environment variable, like `W2A_RUN_BGE_M3_SMOKE`) is skipped by default.

## R6 — Answerability and citation validation

An answer is returned only when it is backed by valid citations; the backend decides.

### Acceptance criteria

- Pre-gate: if the context builder returns no evidence blocks, the response is `insufficient_evidence` with `reason: no_evidence` and the generator is not called (a test shows zero generator calls).
- The model's structured `answerable: false` gives `insufficient_evidence` with `reason: model_declined`; no generated text is returned.
- Citation validation fails closed: every inline `[Sn]` marker and every listed citation must be a source ID given in this request's context, the set of markers must equal the citation list, and an `answerable: true` result must cite at least one source. Any violation gives `insufficient_evidence` with `reason: citation_invalid`; invalid citations are never silently removed and the uncited text is never returned.
- Validated citations are mapped from source IDs to the R1 metadata by the backend. Any URL, title or document ID written by the model is never used as citation metadata.
- No retrieval-score or cross-encoder-score threshold decides answerability (D079).

## R7 — Authorization and untrusted evidence

Generation cannot widen what the guest can see.

### Acceptance criteria

- The only evidence that reaches the prompt is the context built from hits returned by `open_retrieval` with the guest `ResolvedAccess` (and `ResolvedLote` when given); the answer service has no other path to document text (C3). A test shows a staff-scope or other-tenant chunk never reaches the rendered prompt on the isolated security corpus.
- Nothing in the model's output can change the access context, the retrieval call or the citation metadata.
- With the poisoned fixture in the isolated security corpus and a fake generator that follows injected instructions (cites an ID not in context, emits a URL, claims a forbidden document), the answer is `insufficient_evidence` with `reason: citation_invalid`, and no URL or document ID from the model appears in the response.
- Evidence snippets in `evidence_only` responses use `safe_text`.

## R8 — `make ask`

The whole path runs from the command line.

### Acceptance criteria

- `make ask QUERY=... ASK_ARGS=...` runs retrieval (same options and rerank resolution as `make retrieve`, including `--strategy`, `--rerank`/`--no-rerank`, `--lote`), context building, answerability, generation and citation validation, and prints the status, reason, answer, citations and identity.
- `--generator fake|bedrock` selects the generator; the default comes from config. The default config committed during T1–T5 is decided in the design so that `make verify` and default tests stay network-free.
- Exit codes follow the existing CLIs: 0 for any of the three statuses, 2 for configuration errors.

## R9 — `make eval-generation`

Generation quality, refusal and cost are measured on the governed suite.

### Acceptance criteria

- `make eval-generation` runs the active suite's goldens and unanswerable cases through the answer path and writes a generation result (new schema, version recorded) to `experiments/results/` (never overwritten; fake runs to `tmp/` only with the fake allowance).
- Per case: status, reason, citations (document IDs), cited documents vs `relevant_document_ids`, `expected_facts` coverage (case-insensitive substring match, informational), detected answer script, tokens and latency by stage.
- Top-level: answer rate on goldens; refusal rate on unanswerable cases; `citation_invalid` downgrade rate; `evidence_only` and `output_invalid` counts; cited-document precision and recall against `relevant_document_ids`; `expected_facts` coverage overall and by `query_language` (marked informational, since `ml` answers will not contain English fact strings); p50/p95 latency by stage; total and per-answer input and output tokens; estimated cost.
- Gates on the fake generator (in `make verify`): citation enforcement (every fake defect in R4 gives the expected status and reason) and refusal on every unanswerable case when the fake declines or no evidence exists.
- Real-run results are informational except the refusal threshold, which is checked only in R14 against the user-approved value.
- **Cost guard.** For a real generator, `make eval-generation` requires a case limit (all cases only by an explicit flag), prints the case count, an estimated token count and an estimated cost before any model call, and needs confirmation (an interactive prompt or an explicit flag). Prices come from config, never from code.
- Every result records the suite, retrieval identity (as result 2.5), prompt identity, generator identity, git commit and dirty state.

## R10 — Generation security checks

The security gate covers the generation path.

### Acceptance criteria

- `make eval-security` (or a generation step the design adds to it) runs, on the isolated security corpus with the fake embedder, fake reranker and fake generator: the R7 authorization check (no forbidden chunk in the rendered prompt) on every retrieval path already gated; the poisoned-fixture case; and citation manipulation (unknown ID, marker/list mismatch, model-written URL).
- The security result schema version is bumped; existing paths keep their results.
- The checks run inside `make verify` through tests, like the existing security gate.

## R11 — Evaluation candidates

New generation and refusal cases are proposed, never activated by an agent.

### Acceptance criteria

- `evaluation/candidates/012-candidates.jsonl` holds new candidate rows with `status: suggested`: generation goldens (including answers that need two documents, numbers and fees, and source-authority precedence) and unanswerable or refusal cases (including near-miss questions whose topic is in the corpus but whose answer is not). Each row says who drafted it (agent or user) and needs owner approval; Malayalam rows need fluent-speaker review.
- `make validate-evaluation` passes with the candidates file; candidates are never loaded as cases.
- At least one candidate is a golden whose evidence contradicts a likely wrong answer (a plausible but false claim the model might make from general knowledge), so a later faithfulness check has a case to start from.
- No candidate becomes active in T1–T5.

## R12 — Suite `public-eval-v4` (in the real-run task)

Approved candidates become a new governed suite version.

### Acceptance criteria

- In T6, after the user approves candidates, suite `public-eval-v4` is created: every v3 case carried over unchanged except `evaluation_suite_id`, plus the approved cases; v3 becomes `replaced`. The candidate rows stay `suggested` with `review.promoted_as`, as in Spec 010.
- `make validate-evaluation` passes; v4 becomes the default for `make eval-retrieval`, `make eval-security` and `make eval-generation`.
- A continuity check shows the v3 retrieval reference is unchanged on the shared cases (as Spec 010 did with `make eval-continuity`).
- If the user approves no candidate, v4 is not created and the outcome is recorded.

## R13 — Unchanged behaviour and protected paths

### Acceptance criteria

- Retrieval behaviour is unchanged: `open_retrieval`, every retriever, fusion, reranking, fallback, access and applicability code, ingestion, payload, chunkers, lexical files and `INGESTION_NAMESPACE`. No new `index_version`, re-ingestion or lexical rebuild. `make retrieve`, `make eval-retrieval`, `make eval-compare` and `make eval-continuity` give the same results as before.
- `knowledge/` is not changed. `evaluation/` changes only by the candidates file (T5) and, in T6, suite v4. `config/` changes only by the new generation config and prompt files.
- No HTTP route is added (Spec 013).
- Agents never call Bedrock, never run the real models and never write to a `w2a-realcheck-*` collection; tests never write under `experiments/results/` outside `tmp/`.
- No secrets in code, config, prompts, fixtures, results or docs.

## R14 — Real runs and the model choice (user-owned gate)

The user runs the real generator and chooses the default model.

### Acceptance criteria

- **Before any real run**, the user approves and the task records verbatim: the refusal threshold on unanswerable cases, the minimum golden answer rate, and what "falls short" means for the model comparison (for example a maximum p95 generation latency or cost per answer). These are fixed before results are seen.
- The user confirms Bedrock model access in `ap-south-1` for each model tried; if a model is served only through an APAC cross-region inference profile, that is recorded and a decision records the data-residency choice.
- With every code task approved and committed, the user runs `make eval-generation` on the same suite, same case set and same retrieval configuration for Claude Sonnet 5.5 and Claude Haiku 5.5. Claude Opus 5.5 is run only if both fall short of the recorded criteria.
- Each result file is checked like earlier user runs (suite, not fake, clean commit, retrieval identity, prompt identity, generator identity) and committed.
- Before choosing a model, every compared run has zero `generator_unavailable` responses, or the affected cases have been re-run and the re-run recorded.
- The model choice follows the recorded criteria; the choice, or the user's verbatim decision if no model meets them, is recorded. Only these generator config fields change, together in this task: `default_generator` (to `bedrock`), the model ID and inference profile, and `pricing`. The CLI tests for the new default are added in the same task.
- A decision records, per model: answer rate, refusal rate on unanswerable cases, `citation_invalid` downgrade rate, `evidence_only` and `output_invalid` counts, cited-document precision and recall, `expected_facts` coverage by language, p50/p95 latency per stage, tokens and estimated cost per answer, region or profile, and that latency is from the user's network to Bedrock, not a production figure.
- Suite v4 (R12) is promoted in this task, after the model runs or in the same task, as the design orders it.

## R15 — Spec-wide verification

### Acceptance criteria

- `make verify` passes without extras, Docker, network or credentials, and hub-free (`HF_HUB_OFFLINE=1`, empty `HF_HOME`).
- `make test-integration` passes (Docker Qdrant).
- `make eval-security` passes on all existing and new paths.
- `git diff --name-status main...HEAD -- evaluation knowledge config` lists only the candidates file, suite v3 status and v4 files (T6), the generation config and prompt files, and the R14 default, model and pricing change.

## R16 — Documentation and decisions

### Acceptance criteria

- New decisions (from D081; D080 is the workflow trim) record: the context builder (deduplication choice and evidence, budget, ordering, source IDs); prompt versioning; the answer contract and reasons; answerability; citation validation; the generator interface, client choice, extra and config; outage eligibility and `evidence_only`; the answer language rule; the generation result schema and cost guard; security result changes; the region or inference-profile choice; the R14 model outcome; suite v4.
- `ARCHITECTURE.md` (query flow through generation), `COMMANDS.md` (`make ask`, `make eval-generation`, setup, refusals), `TECH_STACK.md` (Bedrock model and client), `ROADMAP.md` (item 10 done except the route; item 13 model-failure path done; item 9 context building done) and `CURRENT_STATE.md` describe the code as built.
- Carry-overs for Spec 013 recorded in `CURRENT_STATE.md` Known issues and the retrospective notes: the HTTP route and all serving items listed under "Decisions resolved before drafting", plus generation latency and concurrency budgets.

## Out of scope

- The HTTP route and every serving item listed for Spec 013.
- Changes to retrieval, reranking, fallback or `open_retrieval`.
- Query translation or transliteration, including `g067`–`g069`.
- FAQ indexing, new knowledge documents, semantic chunking, a new `index_version`.
- Observability and Langfuse (roadmap item 11); full prompt-injection, staff-canary and input/cost-limit suites (item 12) beyond R7 and R10.
- LLM-as-judge metrics, streaming, multi-turn conversation, a second LLM provider or failover between models.
- A retrieval-score or cross-encoder-score answerability threshold.
- Claude's native Citations feature.
- Non-guest roles; per-scope lexical files (D050); Phase 2 release workflow.

## Risks

- **Provenance, not faithfulness.** Citation validation proves that every cited source was in the context, not that the cited source supports the claim. A real model can cite a valid source for an unsupported claim, and a poisoned document can make it repeat an injected claim with a valid citation. Real-run results in this spec do not measure faithfulness; that belongs to roadmap item 12 or a later evaluation spec. R11 adds at least one candidate whose evidence contradicts a likely wrong answer.
- Model access: the chosen model may not be served in `ap-south-1`; an APAC profile moves inference to other APAC regions.
- Small samples: 15 unanswerable cases make the refusal rate coarse (one case is about 6.7%).
- `expected_facts` are English strings, so substring coverage under-reports Malayalam answers; it stays informational.
- Real runs cost money and depend on the user's network; latency figures are not production numbers.
- Model output is probabilistic: two real runs of the same model can differ; R14 decides on one run per model unless the user asks for more.
- Verify budget: the hook allows at most two `make verify` runs per agent session.

## Definition of Done

- R1–R16 satisfied and traced to approved tasks.
- R14 user-owned runs recorded, checked and committed; the default model chosen by the recorded criteria and recorded in a decision; suite v4 promoted or its absence recorded.
- `make verify` (no extras, network, credentials or Docker; also hub-free), `make test-integration` and `make eval-security` pass.
- Protected-path check as in R15.
- `DECISIONS.md`, `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md`, `ROADMAP.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1 | context builder tests (dedup, budget, IDs, determinism, no language branch) |
| R2 | T2 | prompt registry hash pin, unknown pair refusal, escaping and clause tests |
| R3 | T2, T4 | answer models; service status/reason tests; message-language tests |
| R4 | T3 | `FakeGenerator` hook tests |
| R5 | T3 | Bedrock stub-client tests (request shape, D-B table, retries, deadline); config refusals; lazy import; opt-in smoke test (user) |
| R6 | T4 | citation rule tests; pre-gate zero-call test; service tests |
| R7 | T4, T5 | prompt isolation on the security corpus; poisoned-evidence and citation-manipulation checks in `make eval-security` |
| R8 | T4, T6 | `make ask` CLI tests (no default → exit 2 until T6; new-default tests in T6) |
| R9 | T5, T6 | `make eval-generation` tests (cost guard, metrics, gates on the fake); T6 `--min-*` thresholds |
| R10 | T5 | `make eval-security` (security result 1.6) |
| R11 | T5 | candidates file; `make validate-evaluation` |
| R12 | T6 | suite v4 files; `make validate-evaluation`; `make eval-continuity` |
| R13 | T1–T7 | unchanged retrieval tests; `make retrieve` output test; protected-path checks per task |
| R14 | T6 | user-run result files checked and committed; thresholds and choice recorded verbatim |
| R15 | T6, T7 | `make verify`, `make test-integration`, `make eval-security`, protected-path diff |
| R16 | T7 | docs and decisions review in task review and retrospective |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-11-07 — R14, R15: aligned with the approved design D-C (no committed default generator until T6; T6 commits `default_generator: bedrock`, the model ID and pricing together, with the new-default CLI tests) and the D-B addition (zero `generator_unavailable`, or the affected cases re-run, before choosing a model); R15 also allows the v3 suite status change. Before any task started; no task re-opened.
- 2026-11-07 — Design (D-A fallback): at tasks approval the user required that a strict-tool fallback amendment cite the documentation or a recorded HTTP 400 for the forced `tool_choice` rejection. Before any task started; no task re-opened.
- 2026-11-07 — Workflow trim (D080), before T1: tasks no longer run `graphify update .` (removed from the rules and from every task's verification; the orchestrator rebuilds the graph once before the retrospective), and Spec 012 decisions start at D081 (R16, T7, design task outline). No task re-opened.
- 2026-11-07 — T2, T7 (after T1 approval): T2 gains a box widening the language-literal grep test to a quoted `"en"` and the `translation_pair` codes (T1 F2); T7 As-built notes gain the `evaluation/cli.py` correction (T1 F1) and the zero-blocks / `no_evidence` budget case. No approved task re-opened.
- 2026-11-07 — T4 (after T3 approval): T4 gains two boxes from the T3 review: F1 (a deadline that cuts off a classified outage keeps the classified sub-reason in `BedrockGenerator.generate`, `deadline` only when no error caused it) and F2 (the lazy-import test records SDK import attempts so it fails without the `bedrock` extra). No approved task re-opened.
- 2026-11-09 — T5, T7 (after T4 approval): T5 gains two boxes from the T4 review (F5: the `document_id` isolation check made able to fail with a negative control and a corrected comment; F4: a hybrid `--reranker fake` `make ask` test asserting retrieval is closed on success and error paths); T7 As-built notes gain F1 (`make ask` retrieval line format), F2 (citation rule order, to be written into the design) and F3 (the deadline/backoff change supersedes the design's attempt-loop text). No approved task re-opened.
