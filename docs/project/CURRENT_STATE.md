# Current State

Last updated: 2026-11-13 (Spec 013 approved; implementing on `spec/013`, base `1e27909`; T1 next)

## Current phase

Phase 1 foundation complete.

Architecture, initial public knowledge seed, evaluation seed and Phase 1/Phase 2 boundaries have been designed.

Spec 001 project foundation is complete.

## Current goal

Specs **001–012** are **verified on `main`** (last: Spec 012, merged `467b8c8`, 2026-11-13). Retrieval defaults: index **`idx-v2`** (recursive 128 + title, D071), **`hybrid`** with BM25 fallback (D055, D058), **`lexical-v2`** (D072), reranking on at depth 20 (D079). Setup for a default run: `make ingest`, then `make index-lexical`; reranked runs need `make setup-bge-m3` and a cached reranker. Workflow trim **D080** is in place. **Spec 012** (roadmap item 10 without the HTTP route: context building, generation, answerability, citations) is **verified and merged** (`467b8c8`, 2026-11-13): every task (T1–T7, including T5b) approved 2026-11-13; the required retrospective (`.kiro/specs/012-grounded-generation/review.md`, round 1) **passed** with four MINOR carry-overs. Generation: default generator `anthropic` (direct Anthropic API, development and evaluation) with `claude-sonnet-5-5` (D086, D090); Bedrock stays the production target but is blocked (all quotas 0; its smoke test is open). Default suite `public-eval-v4` (D091). `make ask` and `make eval-generation` exist; real runs call the API and are user-run. The HTTP route and serving policy are **Spec 013** (`.kiro/specs/013-http-serving/`): requirements, design and tasks approved 2026-11-13; implementing on `spec/013` (base `1e27909`), T1–T9 not started. Repository-based shared context keeps Codex, Claude Code, Cursor and Kiro interchangeable (D063). Closed history: `docs/project/HISTORY.md`.

## Finalized high-level decisions

- Python/FastAPI backend.
- Next.js/TypeScript frontend.
- RAG under `packages/rag/`.
- Shared domain concepts under `packages/core/`.
- Public/guest retrieval only in Phase 1.
- English + Malayalam initially; future CCL languages through metadata/config.
- `DocumentRepository` abstraction from the beginning.
- `LocalDocumentRepository` in Phase 1.
- S3-backed repository planned for Phase 2.
- Qdrant primary retrieval.
- SQLite FTS5 fallback.
- BGE-M3 initial embeddings.
- BM25 + RRF hybrid retrieval (Spec 007, merged; default strategy `hybrid`, D055); `hybrid` degrades to BM25 when Qdrant or the embedding model is unreachable (Spec 008, merged).
- multilingual reranking implemented (Spec 011): `BAAI/bge-reranker-v2-m3` cross-encoder over hybrid candidates, default on at depth 20 (D079).
- Amazon Bedrock Runtime for generation.
- Langfuse for RAG tracing.
- CloudWatch for operations.
- Terraform for AWS infrastructure.
- AWS Mumbai (`ap-south-1`) deployment target.
- GitHub Actions for CI/CD.
- Evaluation Suite includes goldens, unanswerable/refusal, multilingual, security and regression cases.
- Phase 2 Knowledge Release workflow/evaluation governance are designed but not implemented.
- Basic product analytics are Phase 2 only.

## Seed data status

Latest seed design includes:
- normalized public business knowledge;
- normalized official knowledge;
- Malayalam-specific official policy;
- structured owner-approved FAQ pairs;
- document manifest/inventory;
- document metadata schema;
- lightweight initial Knowledge Release;
- versioned evaluation datasets;
- Evaluation Suite manifest;
- evaluation schema;
- security fixtures;
- source-precedence/access/language configuration;
- Phase 2 analytics event schema.

## Current implementation status

Implemented (detail per spec: `docs/project/HISTORY.md`, the specs under `.kiro/specs/` and `DECISIONS.md`):
- Spec 001: `uv` workspace, FastAPI skeleton with `GET /health`, typed settings, pytest, Ruff, Pyright, `make verify`, local Qdrant (Docker Compose), package skeletons (`packages/core`, `packages/rag`, `packages/observability`).
- Spec 003 and D080: task-gated spec skills (`agent-skills/`, mirrored by `make skills-sync`, checked by `make skills-check`); task states and `task-reviews.md` (`WORKFLOW.md`, D023); verify-budget and graphify-guard hooks (`tools/hooks/`, D073, D080).
- Spec 002: document models, `DocumentRepository` and `LocalDocumentRepository`, `content-hash-v1`, `EligibilityPolicy`, `make validate-knowledge`.
- Spec 004: ingestion (`IngestionService`, chunkers, BGE-M3 adapter, `QdrantIndexStore`, `make ingest`).
- Spec 005: dense retrieval (`AccessContext`, access filter and fail-closed `check_hit`, `DenseRetriever`, `make retrieve`).
- Spec 006: evaluation framework (suite loader, `make validate-evaluation`, `make eval-retrieval`, `make eval-security`, `make eval-compare`).
- Spec 007: BM25 (SQLite FTS5, `make index-lexical`), RRF hybrid, default `hybrid`.
- Spec 008: retrieval fallback (`hybrid` → BM25 on Qdrant or model outage; `bm25` needs neither).
- Spec 009: `structure` and `recursive` chunkers, default `idx-v2`, `eval-compare --cross-index`.
- Spec 010: `lote` applicability on every path, `lexical-v2`, suite `public-eval-v3`, `make eval-continuity`.
- Spec 011: cross-encoder reranking on `hybrid` (`BAAI/bge-reranker-v2-m3`, depth 20), result 2.5, security 1.5.
- Spec 012: `generation/` (context builder D081, prompt `answer` v1 and registry D082, answerability and citation validation D083, `AnswerService`, shared Claude adapter with `BedrockGenerator` and `AnthropicGenerator` D084/D086, outage eligibility D085), `make ask`, `make eval-generation` (result 1.1, D088), security 1.6 (D089), default `anthropic` / `claude-sonnet-5-5` (D090), suite `public-eval-v4` (D091). Real runs recorded in `task-reviews.md` (T6).

Not yet implemented:
- no HTTP retrieval route (Spec 013); retrieval degradation exists only for `hybrid` (Spec 008); reranking exists on `hybrid` only (Spec 011);
- the Phase 2 "compare shared cases" mode of `eval-compare` (today any difference in the case set is refused);
- the generation HTTP route, streaming, tracing and a hard wall-clock generation deadline;
- observability;
- CI/CD;
- Terraform deployment.

## Spec status

| Spec | Status |
|---|---|
| 001 — project foundation | implemented before the review process existed (no `review.md`) |
| 002 — document model and repository | verified 2026-10-15, merged `dca6cbd` |
| 003 — task-gated agent workflow | verified 2026-10-15 (bootstrap exception, built on `main`) |
| 004 — ingestion baseline | verified 2026-10-17, merged `dde5b35` |
| 005 — dense retrieval baseline | verified 2026-10-23, merged `b33462e` |
| 006 — evaluation framework | verified 2026-10-24, merged `ab28d89` |
| 007 — hybrid retrieval | verified 2026-10-28, merged `3cf70eb` |
| 008 — retrieval fallback | verified 2026-11-01, merged `1107b67` |
| 009 — chunking experiments | verified 2026-11-04, merged `5a6deb7` |
| 010 — multilingual retrieval | verified 2026-11-04, merged `cae06c3` |
| 011 — multilingual reranking | verified 2026-11-06, merged `d40d734` |
| 012 — grounded generation | verified 2026-11-13, merged `467b8c8` (T1–T7 including T5b approved; retrospective round 1 PASS; the branch also carries `7ccfc9a`, Cursor model preferences, with no `Spec-Task` trailer) |
| 013 — HTTP route and serving policy | implementing (branch `spec/013`, base `1e27909`); spec approved 2026-11-13; T1–T9 not started |

## Next step

1. **Spec 013 — HTTP route and serving policy (implementing on `spec/013`; T1 next).** Spec approved 2026-11-13: `.kiro/specs/013-http-serving/` (R1–R18, nine tasks). In scope: the route over `AnswerService` with config-resolved `rerank.enabled` and `default_generator`; the `open_retrieval` rework and resource lifecycle (Spec 011 F1/F3, Spec 008 F4); lexical startup and tokenizer check (CLIs too) and freshness inside an event loop; a minimal circuit breaker (D062 unchanged) with a server start on BM25 when Qdrant is down and a checked dense re-open; a hard wall-clock generation cap with a per-request budget and the `config/generation.yaml` comment fixes (Spec 012 F2); readiness (`/ready`), request limits, a concurrency cap, public contract 1.0, request-ID logging without query text; `make api`. Deferred by the user at planning: streaming; usage on raised outcomes (prompt v2, Spec 012 F1); `fallback_stage` (item 11, Spec 008 F2); reranker reload and device pinning (item 14); per-client rate limiting (item 12); an internal endpoint (item 16). Later specs: **prompt v2** (URL habit: Sonnet's v4 refusal rate is 9/17 without the backend `model_url` discard; marker use; g080 answer language; a deterministic safe-redirect flag with `safe_handling_rate` and result 1.2) and the **Bedrock switch** (its own spec or task, with the smoke test and a latency re-check once AWS grants access). The `deferred s005/s006 … roadmap-10` labels in `make eval-security` come from the `DEFERRED_OWNERS` constant (`evaluation/security_eval.py`) and stay a carry-over. The user runs `/graphify . --update` on `main` and commits `graphify-out/`.
2. **Bedrock smoke test (user-run, open):** the direct-API smoke test passed on 2026-11-13 for `claude-sonnet-5-5` and `claude-haiku-5-5`. The Bedrock smoke test (`W2A_RUN_BEDROCK_SMOKE=1`, `global.` profiles, `ap-south-1`) stays open until AWS grants access (Free plan blocks Marketplace models, all quotas 0, increases go through AWS Sales, `ap-south-1` offers only `global.` profiles for Claude 5.5). Switching `default_generator` to `bedrock` is its own spec or task with a timeout and latency re-check (D086). `aws login` credentials need `eval "$(aws configure export-credentials --format env)"` first (`botocore[crt]` is not in the `bedrock` extra; documented in `COMMANDS.md`).
3. **Follow-up chore (D080):** in `packages/rag/tests/evaluation/test_security_eval.py`, share one CLI gate run across `test_cli_lexical_file_is_removed_after_a_pass`, `test_cli_pass_writes_a_result_and_exits_zero` and `test_cli_clause_less_lexical_store_exits_one_naming_strategies` (about −38 s of `make verify`). Docker tests stay in `make verify` until CI runs `make test-integration`.
4. The trial docs re-extraction of 2026-11-07 was discarded and is not to be retried (D080); the docs part of the graph stays from the earlier extraction.
5. Open since the verify-budget chore: remove user-level verify-budget hook copies; the committed hook is `.claude/settings.json` + `tools/hooks/verify_budget.py`.
6. Open chore: the post-merge `/graphify . --update` docs re-extraction was refused by the shrink guard again on 2026-11-13 (1443 vs 1927 doc nodes; same outcome as the 2026-11-07 trial, D080). Decide whether to drop the post-merge reminder from `spec-orchestrator` or limit it to new docs.

## Ingestion operating notes

- Default production index (after Spec 009 T6 promotion): **`idx-v2`**, **`recursive` v1** (128 tokens, 16 overlap, title prefix) in `config/ingestion.yaml`; collection **`way2australia-idx-v2`**. Legacy **`idx-v1`** / heading: `experiments/configs/chunking/heading-idx-v1.yaml` with `--config`.
- Use `QDRANT_COLLECTION_BASE` for every fake-embedder run. A fake run without it records the default collection for the configured `index_version` as fake, and a later real run is then refused until a new `index_version` is set in `config/ingestion.yaml`.
- After `make setup`, default runs (hybrid with reranking on, Spec 011 T5) need `make setup-bge-m3` plus a cached reranker (the first reranked run downloads the pinned model); `--strategy bm25` (and `dense`) now needs `--no-rerank`.
- `make setup` removes the optional `bge-m3` extra; use `make setup-bge-m3` before a real-embedding run (on a slow connection `UV_HTTP_TIMEOUT=600 make setup-bge-m3`). A missing extra is detected when the embedder is built (exit 2, before any Qdrant call).
- `make verify` runs the Docker integration tests too when a local Qdrant is reachable (they create and remove temporary collections); otherwise they skip.
- `INGESTION_NAMESPACE` (`533d6c5a-5ac2-4dd5-a4e6-5fbb620efba2`) is permanent: changing it changes every point ID.
- Decisions: D025 to D030 and D032 in `DECISIONS.md`.

## Known issues / deferred

Spec 012 carry-overs for Spec 013 and later (T7):
- **Spec 013 serving items:** HTTP route; `open_retrieval` rework (Spec 011 F1/F2/F3 and Spec 008 F4: depth per served path, rerank resolved from config, one helper for the standalone open); Qdrant client and model lifecycle (close on every open failure and in `close()`); async freshness check; lexical startup and tokenizer policy; circuit breaker; reranker reload and health; latency, concurrency and device budgets that include generation (the generation deadline is the generation share of the request budget, D084); a hard wall-clock generation cap.
- Validation proves provenance, not faithfulness: a valid citation can sit under an unsupported claim (roadmap item 12 or an evaluation spec).
- Neighbour merge in the context builder needs overlap boundaries in the chunk payload, which means a new `index_version` (D081). Streaming is deferred to Spec 013.
- Bedrock: the smoke test and the switch of `default_generator` are open (D086). Latency and timeout figures from Spec 012 are direct-API figures from the user's network, not Bedrock or production figures.
- Prompt v2 inputs are listed below (URL habit, marker use, answer language, safe redirect).

Spec 012 retrospective (`.kiro/specs/012-grounded-generation/review.md`, round 1), MINOR, no remediation tasks:
- F1: token counts and `actual_cost_usd` omit billed responses that raise (`output_invalid` from `max_tokens`/`json`/`schema`, and a refusal stop reason): `GeneratorOutputError` and `GeneratorDeclinedError` carry no usage, so the response records `usage: null` and the cost is a lower bound (`cases_with_usage` shows the gap; Haiku's three `max_tokens` cases are not in its $0.027876). Fix with prompt v2 or the next generation-result bump.
- F2: `config/generation.yaml` comments beyond `deadline_s` are stale: `backoff_s` "capped by the deadline" (it is not, since the T3 review F1 change) and `bedrock.model_id` "null until T6 commits the chosen model's Bedrock ID" (it stays null until the Bedrock switch). Fix with the `deadline_s` comment and the hard wall-clock cap.
- F3: the `make eval-security` deferral owners `roadmap-10` for s005/s006 (and `UNANSWERABLE_OWNER` in `retrieval_eval.py`) are code constants (`DEFERRED_OWNERS` in `evaluation/security_eval.py`), not evaluation data; item 10 is done except the route. The cases still do not run through the answer path, so only the owner label is stale. Retarget when item 12 or prompt v2 runs them.
- F4: D083 and D084 headers cite the wrong requirement numbers (answerability is R6; the generator is R4/R5); the bodies are correct.

Spec 012 T6 carry-overs (for a later prompt version or follow-up; the prompt is not changed in this spec):
- The refusal rate includes backend-enforced refusals. In the Sonnet run, 4 of its 13 unanswerable refusals are `citation_invalid/model_url` (the model wrote a URL, the backend discarded the answer) and the same rule cost 2 goldens (g035, g070); Haiku had `marker_mismatch` refusals on 5 goldens. A later prompt version should address URLs in answers and marker use.
- Backend-enforced refusals in the Sonnet runs (counted from the result files, 2026-11-13): the v3 run had 4 unanswerable refusals from `citation_invalid/model_url` (u007, u011, u013, u014) out of 13; the v4 reference run has 6 of 15 (those four plus u016 and u017, the two new v4 unanswerable cases; the result rows record `citation_invalid / model_url`, so the backend found a URL in the model's output, and that Sonnet was trying to answer is an inference, since the files keep no text for a discarded answer). That is 6 distinct unanswerable cases across the two runs; v4 also repeats the 2 golden losses (g035, g070). Without the `model_url` discard the v4 refusal rate would be 9/17 (0.5294), not 0.8824, so the refusal-rate threshold is met through the backend, not the model's own judgement. Input for the prompt-v2 spec (URL habit).
- `deadline_s` is a soft deadline: three cases (Haiku g040 31.9 s, Sonnet g022 32.6 s and g021 32.1 s of generation against 30 s) overshot because `with_options(timeout=)` is a per-phase httpx timeout, not a wall-clock cap (`generation/claude.py`). The comment in `config/generation.yaml` ("total per request") is not strictly true. The comment fix and a hard wall-clock cap are a follow-up (Spec 013 or a chore; D084); no effect on the p95 criterion.
- Haiku 5.5 hit `max_tokens` (1024) on 3 Malayalam or mixed goldens (g065, g076, g086): Malayalam token cost. Input for any later Haiku reconsideration.
- Wrong answer language (g080, Sonnet): the question was romanized Malayalam ("Official test-nu headphone use cheyyamo?"), the answer was romanized Telugu ("Ledu... kaadu... chudandi... kosam"). The facts and citation were correct. Input for a later prompt version, together with the `model_url` habit above.
- Safe redirect is not scored (decision 2026-11-13: option 3 for this spec): u001 and u003 are `insufficient_evidence_or_safe_redirect` cases, and Sonnet's answered "No, cannot guarantee / check Home Affairs" replies are safe redirects but count as known false misses in every run. Carry-over for a later prompt-v2 spec: a deterministic redirect marker in the answer contract, a `safe_handling_rate` and generation result 1.2, together with the g080 answer-language issue and the `model_url` habit above. No scorer or schema change in Spec 012.
- Expected-facts coverage uses English substring matching, so it is always 0 for Malayalam-script answers (g072 was correct but scored 0/2). Informational only for `ml`.

These are evaluation-data gaps, deliberately deferred for now (decision 2026-10-13). Changing them requires human-approved evaluation cases (C6).
- `relevant_section_ids` is empty in every evaluation case, so `eval-retrieval` reports zero section-measurable cases (deferred by Spec 009; headed documents and suite v3 are a later spec).

Spec 009 known issues and carry-overs (documented; no remediation tasks):
- Ignored top-level `knowledge_release_id` / `evaluation_suite_id` in `config/ingestion.yaml` and `experiments/configs/chunking/recursive-128.yaml` (`evaluation_suite_id` still names the replaced `public-eval-v1`). The ingestion loader ignores them. Remove at the next `index_version`; keep this promotion's byte copy so the arm's `ingestion_config` hash stays valid (D071).
- Size vs prefix confounding: the promoted arm is recursive 128 tokens *and* title prefix together (D071). Recorded metrics belong to that pair, not either treatment alone. A later spec may split them.
- `g026` (en, `business_006_mock_assessments`) flipped hit→miss on promotion. Overall HitRate@5 stayed 0.9855 (68/69); English HitRate@5 / Recall@5 1.0 → 0.9815, MRR 0.9352 → 0.9321. R10 allowed the flip (`en`, not `ml`/`mixed`). Revisit with reranking or a size-vs-prefix split.
- FAQ pairs: `knowledge/structured/owner_approved_faq_pairs.jsonl` is not indexed (own spec).
- Semantic chunking: out of scope (roadmap 7 remainder).
- Malayalam stemming: not implemented (declined in Spec 010; roadmap carry-over).
- Spec 008 serving/API items remain open for **Spec 013 (HTTP route and serving policy; split from roadmap item 10 at Spec 012 planning)** (see Spec 008 known issues and 008 retrospective F4/F5): startup and reopen policy for a missing or stale lexical file **and** refusal when the file's recorded tokenizer disagrees with `config/retrieval.yaml` (Spec 010 T5 carry-over: `open_retrieval` does not check today; stale `lexical-v1` would serve silently after a v2 promotion); circuit breaker, Qdrant client lifecycle, async freshness (`verify_fresh` uses `asyncio.run`), freshness cost on a large corpus (D060/D067), fallback-stage observability, Qdrant 5xx eligibility (D062), API surface.
- Per-scope lexical files remain a roles-spec item (D050).
- In a shallow clone (base commit `06b1af9` absent) the Spec 007 T1 v1 byte-identity tests in `test_suite_v2.py` skip, and nothing flags it. Accepted while there is no CI; revisit in the CI spec.

Spec 008 known issues and carry-overs (documented by T8; no remediation tasks):
- Qdrant client lifecycle (T4 review): `open_retrieval` closes the Qdrant client on the fallback path but not on every open failure, and `OpenedRetrieval.close()` does not close the client. A long-running server would leak a connection pool per failed open; the CLIs exit after one run. **Spec 013** (first HTTP surface) must close the client on every open failure and in `close()`, with a test.
- `verify_fresh` uses `asyncio.run`, so it cannot run inside a running event loop; **Spec 013** needs an async freshness check or a check at startup outside the loop (T2 review F3).
- The standalone freshness check rereads every eligible document at each open (milliseconds for 13 documents); revisit for a large corpus (D060).
- No circuit breaker: with Qdrant hanging, each hybrid query waits about `query_timeout_s` (3 s) before BM25 serves (D058). Qdrant 5xx and a Hugging Face hub 5xx are not fallback-eligible (D062).
- The security gate's standalone `bm25` path checks identity plus "every seed chunk present" instead of `verify_fresh`, and that check is one-way (an extra non-forbidden row is not refused); see the design As-built notes (T6).

Spec 008 retrospective (`.kiro/specs/008-retrieval-fallback/review.md`, round 1), MINOR, no remediation tasks:
- F2: result 2.2 and `eval-compare` do not distinguish an open-time from a per-query fallback (same `bm25+fallback:<reason>` path; `dense_attempt` about 0 ms after an open-time fallback, yet labelled "includes failed dense attempt"). Docs corrected; a `fallback_stage`-style field is left to **Spec 013** or observability (item 11).
- F4: `open_retrieval`'s `bm25` branch and `_open_fallback` duplicate the standalone open and lexical `document_count` wiring; fold into one helper when **Spec 013** reworks `open_retrieval` (together with the client lifecycle item).
- F5: no test drives the open-time fallback from a `bind_to` scroll failure (Qdrant fails after `DenseIndex.open`) through `open_retrieval`; covered by composition (`chunk_identities` maps transport errors, T1; the `except` spans `open_bound_lexical`, T4).

Spec 011 known issues and carry-overs (documented by T6; no remediation tasks in this spec):
- **Context building** (deduplication, context budgeting, evidence ordering) was done by Spec 012 (D081).
- **Latency limit and device for Spec 013:** depth 20 costs about 1 s per query at p95 on `mps:0` (+920.6 ms over the hybrid reference, 79 ms under the 1000 ms escalation line); there is no inference timeout (D077) and the device is not pinned. The binding per-request limit, circuit breaker, model and client lifecycle and device choice belong to the HTTP spec. The numbers are a dev-machine figure, not a production one.
- **Unanswerable cross-encoder scores** (D079): top-1 scores for the 15 unanswerable cases (median -4.17, max 1.67) overlap the golden distribution (median 3.08); three unanswerable cases score above 0, so no fixed cut-off is safe. Input to the answerability decision (D083, which uses the retrieval hits' presence, not a score cut-off), not a threshold.
- **Query translation / transliteration** remains the intended fix for `g067`–`g069` on BM25-only and on the hybrid fallback (reranking applies to hybrid only; on the v3 BM25-only run the `ml` misses return no BM25 candidates, so reranking the fallback cannot help).
- **Residual rank losses:** `g038` (en) and `g062` (mixed) drop from rank 1 to 2 under reranking (still hits); `g057` stays at 0.5; `g026` is back to a hit at reciprocal rank 0.333.
- **Gate coverage:** `make eval-security` runs the rerank paths at depth 50 / `top_k` 50, so the committed depth-20 cut is not itself exercised (membership is decided by the legs and re-checked; D078).
- `retrieval/availability.py` private names are imported by `rerank/errors.py` (design As-built notes); `check_applicable` is called on a partial `PointPayload` and must keep reading only `document_id` and `lote_languages` (a test guards this).
- `experiments/configs/rerank/retrieval-depth50.yaml` differs from `config/retrieval.yaml` in `rerank.enabled` and `rerank.depth`.

Spec 011 retrospective (`.kiro/specs/011-multilingual-reranking/review.md`, round 1), MINOR, no remediation tasks:
- F1: with reranking requested and a dense outage, `eval-retrieval` asks BM25 for `rerank.depth` (20) chunks instead of 50 and records `retrieval_depth` 20; top-5 distinct-document metrics are unaffected while `required_depth` (17) is at most 20. Recorded in the design As-built notes and `COMMANDS.md`; fix together with the Spec 013 rework of `open_retrieval` (depth per served path).
- F2: `open_retrieval(rerank=False)` is the library default; only the two CLIs resolve the effective setting from `rerank.enabled`. The Spec 013 HTTP route must resolve it from config too, or it serves un-reranked hybrid silently.
- F3: `top_k > rerank.depth` is refused inside the stage at query time, after the reranker was loaded at open (`make retrieve --top-k 30` loads the model, then exits 2); `eval-retrieval` refuses earlier through the distinct-document depth check, with advice that names `candidate_depth`, not `rerank.depth`. No wrong result is possible.

Spec 010 known issues and carry-overs (documented by T6; no remediation tasks in this spec):
- **Query translation / transliteration** (including Latin-script Malayalam): the intended fix for **`g067`–`g069`** on BM25-only and on the hybrid **fallback** path when dense is unavailable; out of scope for Spec 010. BM25-only `ml` MRR **0.2396** (n=16) on v3 realcheck (`…20261104T105321Z.json`).
- **`g056` / `g057`:** hybrid fusion demotes a dense rank-1 relevant document to reciprocal rank 0.5 (BM25 rank 2); inputs for **roadmap item 9** reranking, not a Spec 010 bug.
- **No Malayalam knowledge content** was added (`knowledge/` unchanged); evaluation grew via v3 cases only.
- **Malayalam stemming** and **per-script fusion weighting** were declined (requirements out of scope).
- **Script mix** uses Unicode **name** prefixes, not Scripts.txt; romanized Malayalam counts as **`latin`** (reporting only).
- **`open_retrieval`** does not compare the lexical file's recorded tokenizer to `config/retrieval.yaml` (stale `lexical-v1` would serve silently); group with the **Spec 013** startup policy (also missing/stale file).
- Spec **009** carry-overs below remain unchanged (ignored yaml keys, `g026`, FAQ, semantic chunking, per-scope lexical files, shallow-clone test skip, etc.).

Spec 007 known issues and carry-overs (documented by T10; no remediation tasks):
- The `seed-v1` Knowledge Release still names suite `public-eval-v1` (replaced); releases are Phase 2 (D049).
- BM25 statistics (IDF, average length) are computed over every row of a lexical file, including rows the access clause excludes. Today only eligible guest/public chunks are indexed, so they reveal nothing; a future roles spec needs one lexical file per access scope (D050).
- Malayalam in BM25 matches only exact tokens (no stemming): `g067`–`g069` are lost by BM25 alone and `g064`/`g065` rank on the Latin `NAATI`/`CCL`; hybrid keeps every `ml` hit but with lower reciprocal ranks (MRR 0.9167 -> 0.7917 on a 6-case sample).
- `git_state` (shared with the legacy `make retrieval-baseline`) ignores every untracked file under `experiments/results/`, not only result JSON; a path git quotes reports dirty (fails safe). Accepted at T10 review (F3).

Spec 006 retrospective (`.kiro/specs/006-evaluation-framework/review.md`, round 1), MINOR, no remediation tasks:
- F1: the byte-identity check of `evaluation/` before and after a run is tested for the loader (`test_suite_loader.py`) and the validator (`test_validate.py`), not around the `eval-retrieval` and `eval-security` runners (the design's "each runner"). Both runners read evaluation data only through `load_suite`, and no evaluation code writes under `evaluation/`.
- Legacy `make retrieval-baseline --allow-fake` without `--output` still writes into `experiments/results/` (Spec 005 location, kept by R12/R13); only the new commands use the git-ignored `experiments/results/tmp/`. Do not commit a fake result.
- `make eval-security` is not a step of the `make verify` target; its gate runs inside `make verify` through `test_security_eval.py`.
- The security result's `access.role` is hard-coded `guest` (correct in Phase 1; change it when other roles are added).

Spec 005 retrospective (`.kiro/specs/005-dense-retrieval-baseline/review.md`, round 1), MINOR, no remediation tasks (F1 and F2 were documentation gaps, reconciled in that round):
- F4: interface sketches in `design.md` differ from the code (`retrieval/__init__.py` has no exports; `SuiteRef.golden_dataset_path`; extra `run_baseline` parameters); recorded in the design's As-built notes.
- F5: the design error table says a non-guest role is refused without Qdrant contact, but resolution runs after the read-only `DenseIndex.open` (as the design data flow and T5 say); unreachable today.

Spec 004 review findings still open (all MINOR, no remediation tasks; see `.kiro/specs/004-ingestion-baseline/task-reviews.md` and `review.md` round 1):
- T3 F1: `test_info_reports_fake_identity` uses `pytest.raises(Exception)` instead of `pydantic.ValidationError`.
- T7 F2: `QdrantIndexStore` holds both `_index_version` and `index_version`.
- T7 F5: `test_security_fixtures_never_reach_the_index` does not assert the fixtures loaded.
- T8 round 2 F1: the late `OptionalDependencyError` re-raise in `service.py` (broken installs) has no test.
- Retro F1: the `repositories/manifest.py` module docstring says "one record per document version"; the loader allows one record per `document_id` (D026, D032).
- The BGE-M3 device is recorded in retrieval results and the baseline JSON but not pinned and not an index setting (D038); the user's real run used `mps`.
- Default production index is `recursive` v1 (Spec 009 T6); `heading` v1 remains via `heading-idx-v1.yaml`. None of the 13 seed documents has headings, so heading behaviour is covered mainly by synthetic tests (D030).

Spec 002 retrospective (`.kiro/specs/002-document-model-and-repository/review.md`, round 1), MINOR, no remediation tasks (F1–F4 handled by Spec 004 as noted):
- F3: partly closed by Spec 004 T1 (`GUEST_PUBLIC_POLICY` and access scopes are tested against `config/access_policy.yaml`); source authorities are still not cross-checked against `source_precedence.yaml`.
- F4: decided by D026 (one version per `document_id`; version history is Phase 2); the `manifest.py` docstring is still stale and the "version increments on change" rule is unenforced.
- F5: `ARCHITECTURE.md` repository sketch uses `list_documents(status=...)`, not `DocumentQuery`.
- F6: loader and `validate-knowledge` validate documents on two separate paths (loader reports only the first Pydantic error, no date check).

## Important constraint

Do not begin implementing Phase 2 S3/admin/release-management functionality during Phase 1.

Only preserve the interfaces/IDs needed to add it cleanly later.
