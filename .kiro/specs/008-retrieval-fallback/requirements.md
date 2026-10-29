# 008 — Retrieval Fallback Requirements

Status: approved (2026-10-29)

## Goal

Keep guest/public retrieval answering, with unchanged authorization, when Qdrant or the dense embedding model fails at runtime. This spec covers the two retrieval paths of roadmap 13 (graceful degradation):
- Qdrant unavailable → SQLite FTS5 BM25;
- dense or embedding failure → BM25.

Concretely:
- the lexical file opens and is checked without Qdrant and without the `bge-m3` extra, and the `bm25` strategy runs with neither;
- runtime failures are classified: only availability failures may fall back; everything else still fails closed;
- the `hybrid` strategy (whether it is the default or `--strategy hybrid`) falls back to BM25 through an explicit, tested policy outside fusion, at open time and per query;
- Qdrant connect and query timeouts make a hanging Qdrant a fallback trigger rather than a stall;
- every result records the strategy requested and the strategy that served it; evaluation records the served strategy per case, and `eval-compare` compares by the served strategy;
- the security gate covers the fallback paths;
- user-owned real runs show that a run with Qdrant unreachable reproduces the Spec 007 BM25 reference, and that hybrid is unchanged with Qdrant up.

This spec is taken ahead of roadmap 7 (chunking experiments). Reason: on the current corpus (13 documents, no headings, one chunk each, `relevant_section_ids` empty) chunking gives little measurable signal (C11), while D055 made the default strategy depend on Qdrant, the `bge-m3` extra and the lexical file at once. The reordering is recorded in `DECISIONS.md` and `ROADMAP.md` by this spec (R14). The reranker and model-failure paths of roadmap 13 stay with roadmap 13; they need a reranker and generation first.

## Dependencies

- Spec 007: hybrid retrieval (verified, merged `3cf70eb`). Provides `lexical-v1` (D051), the SQLite FTS5 lexical store with its `dense_identity` copy and `source_chunk_digest` (D050), `production_entries`, `LexicalIndex.open`/`bind_to`, `BM25Retriever`, `build_sql_access_clause`, `rrf_fuse` and `HybridRetriever` (fail closed, D052), `Strategy`, `build_retriever`, `config/retrieval.yaml` (`default_strategy: hybrid`, D055), result 2.1 and security result 1.1 (D053), the `eval-compare` identity rules (D054).
- Spec 006: evaluation framework (governed suite loader, `make eval-retrieval`, `make eval-security`, `make eval-compare` with the D044 gate).
- Spec 005: `AccessContext`, `resolve_access`, `ResolvedAccess`, `build_access_filter`, `check_hit` (D035, D040), `DenseIndex`, `DenseRetriever`, `safe_text`, `load_runtime_settings`.
- Spec 004: `HeadingChunker`, `PointPayload`, point IDs, `config/ingestion.yaml` (`idx-v1`, embedder identity), `build_embedder`.
- Spec 002: `LocalDocumentRepository`, `GUEST_PUBLIC_POLICY`.
- Reference results (suite `public-eval-v2` v2, `w2a-realcheck-idx-v1`, BAAI/bge-m3 @ `5617a9f`): BM25 `experiments/results/retrieval-evaluation-idx-v1-20261028T123109Z.json` (64 of 69 hits, MRR 0.7082) and hybrid `experiments/results/retrieval-evaluation-idx-v1-20261028T123121Z.json` (68 of 69, MRR 0.9094).
- Retrospective notes: `.kiro/specs/007-hybrid-retrieval/review.md`, "Notes for the next spec".
- The real runs (R12) need `make setup-bge-m3`, the user's `w2a-realcheck-idx-v1` collection (read-only) and its lexical file. They are run by the user.
- No new runtime dependency is expected.

## Decisions resolved before drafting

Decision Brief approved by the user on 2026-10-29, with all five recommendations and these additions:

- **Spec choice (Q1).** Retrieval graceful degradation is Spec 008, ahead of roadmap 7; the reordering is recorded in `DECISIONS.md` and `ROADMAP.md` as a task/DoD item of this spec.
- **When the fallback applies (Q2).** On for `hybrid`, whether from `default_strategy` or from `--strategy hybrid`. Off for an explicit `--strategy dense` or `--strategy bm25`.
- **What triggers it (Q2).** Only runtime availability failures: Qdrant unreachable (connection refused or failed), Qdrant connect or query timeout, and dense model load or download failure. Authorization errors, binding or identity mismatches, a stale lexical file and configuration errors never fall back; they fail closed as today.
- **Missing `bge-m3` extra.** A configuration error for `dense` and `hybrid`: fails closed, never falls back. `bm25` does not need the extra.
- **Timeouts.** Qdrant connect and query timeouts live in `config/retrieval.yaml`, so a hanging Qdrant triggers the fallback. A unit test uses a stalled fake; the closed-port real run covers only "connection refused".
- **Freshness without Qdrant (Q3).** Recompute the source chunk digest from the repository and chunker, and refuse when it differs from the file. The design notes that this needs revisiting for a large corpus.
- **Fault injection (Q4).** Real runs simulate an outage by pointing `QDRANT_URL` at a closed port. Unit tests use a test-only injection seam; there is no production debug flag.
- **Partial degradation.** Each evaluation case records the strategy that served it. `eval-compare` refuses a file with mixed served strategies and compares by the served strategy, not the requested one.
- **Out of this spec (Q5).** Malayalam stemming and `g061` go to a later multilingual or reranking spec; per-scope lexical files wait for a roles spec.

## R1 — Failure classification

Retrieval failures are classified so that only availability failures can trigger the fallback.

### Acceptance criteria

- One named classification (exception type or category) marks a failure as fallback-eligible. Eligible failures are exactly: Qdrant connection refused or failed, Qdrant connect timeout, Qdrant query timeout, and a dense model load or download failure whose explicit cause chain contains a network or timeout error (connection refused or failed, DNS failure, timeout). A model load failure without such a cause (missing model ID, missing or wrong revision, gated repository, corrupt cache, permissions, offline mode with a missing cache) is a configuration error and is not eligible.
- Never eligible, and still raised as today: `RetrievalAuthorizationError` (including a `check_hit` violation in any leg), `IndexBindingError` and lexical binding errors, a stale or foreign lexical file (R4), `RetrievalConfigurationError`, a missing `bge-m3` extra (`OptionalDependencyError` or equivalent), invalid requests (empty query, `top_k` out of range), and any unexpected exception that is not mapped to an eligible failure.
- Mapping from client or model exceptions to the eligible classification happens in one place per source (Qdrant, embedder), so unknown exceptions stay non-eligible by default. Qdrant errors are unwrapped only through the client's known wrapper; an unrelated error raised while handling a network error is never classified as an outage.
- A test covers every eligible and every listed non-eligible case, including: a missing model revision and a missing model ID fail closed; a connection error during model load gives the model-unavailable classification.

## R2 — Qdrant timeouts

A hanging Qdrant becomes a bounded, eligible failure.

### Acceptance criteria

- `config/retrieval.yaml` gains a Qdrant connect timeout and a Qdrant query timeout (seconds), validated by `RetrievalConfig` (positive, with an upper bound set in the design); an invalid or missing value is a configuration error naming the field.
- Every retrieval-side Qdrant client (`make retrieve`, `make eval-retrieval`) is created with these timeouts. Ingestion and `make index-lexical` are not changed.
- A unit test with a stalled fake (a connection that never answers, or a fake client that blocks beyond the timeout) shows that the dense leg fails with an eligible timeout within the configured bound plus a small tolerance, and that `hybrid` then serves BM25.
- If the Qdrant client cannot separate connect and query timeouts, the design records how both bounds are still enforced.

## R3 — Lexical index without Qdrant

The lexical file can be opened and identified without a Qdrant client or the embedder.

### Acceptance criteria

- A standalone open path checks the file against the run's expected identity read from configuration only: collection, `index_version`, embedder model ID and revision (from `config/ingestion.yaml`, without building the embedder), tokenizer name and version, chunker fields and `hash_contract`. Any difference is refused (exit 2 in the CLIs) with the existing rebuild advice (`make index-lexical`), naming fields, never chunk text.
- The standalone path is read-only and creates no Qdrant client.
- When Qdrant is reachable and the run binds the dense index (`hybrid`), the existing `bind_to` check against Qdrant still runs unchanged (D050).

## R4 — Freshness check from the repository

Without Qdrant, a stale lexical file is detected from source documents.

### Acceptance criteria

- On every standalone open (R3), the source chunk digest is recomputed from `LocalDocumentRepository` and the configured chunker, using the same eligible-document rules and identity tuple as `make index-lexical` (`production_entries`, `source_chunk_digest`), with no embedder and no Qdrant.
- A digest different from the file's recorded digest refuses the run (not eligible for fallback), naming the differing chunk count and advising `make index-lexical`; no chunk text is printed.
- A test changes a seed document's content (temporary repository) and shows the refusal; a test shows an unchanged repository passes.
- The design records the cost of this check and that it needs revisiting for a large corpus.

## R5 — `bm25` without Qdrant or the `bge-m3` extra

The explicit `bm25` strategy depends only on the lexical file and the repository.

### Acceptance criteria

- `--strategy bm25` (in `make retrieve` and `make eval-retrieval`) builds no embedder, creates no Qdrant client and opens the lexical file through R3 and R4.
- `BM25Retriever` no longer requires a `DenseIndex`; it keeps the same `ResolvedAccess`, `build_sql_access_clause`, `check_hit`, query validation, `MATCH` quoting and truncation behavior (Spec 007 R6).
- A test shows `bm25` runs with the embedder factory and Qdrant client factory set to fail if called, and with the `bge-m3` modules unavailable.
- On the same lexical file, the ranked hits of `bm25` equal those of the Spec 007 `bm25` path (characterization test on a fixture).
- The fallback is off for an explicit `bm25`; it has no dense leg to fall back from.

## R6 — Fallback policy for `hybrid`

`hybrid` falls back to BM25 on eligible failures through an explicit policy.

### Acceptance criteria

- The policy applies when the resolved strategy is `hybrid`, from `default_strategy` or from `--strategy hybrid`. It never applies to an explicit `dense` or `bm25`; there an eligible failure is raised as today (no silent switch).
- **At open time:** if creating or binding the dense side fails with an eligible failure (Qdrant unreachable or timing out), the run opens the lexical file through R3 and R4 and serves BM25. A missing `bge-m3` extra or any non-eligible failure is raised.
- **Per query:** if the dense leg of a query fails with an eligible failure (Qdrant timeout or connection failure, model load or download failure with a network cause), that query is served by the BM25 retriever. Each query attempts the dense leg again; there is no circuit breaker.
- A BM25 failure, or any non-eligible failure in either leg, is raised; the policy never falls back from BM25 to anything.
- The served fallback result equals what `bm25` returns for the same query, `access` and `top_k` (same retriever, same lexical file).
- The policy is a separate wrapper (or equivalent explicit component) built by `build_retriever`; `rrf_fuse` and `HybridRetriever` keep failing closed (D052) and contain no fallback catch.
- Authorization is unchanged on every path: the BM25 fallback uses the same server-resolved `ResolvedAccess`, the SQL access clause inside its query and `check_hit` on every hit (C3, D035, D040).
- Tests cover: Qdrant down at open, dense-leg failure on one query of several (other queries stay hybrid), model load failure, a non-eligible dense error (raised), a BM25 error during fallback (raised), and an explicit `dense` with Qdrant down (raised).

## R7 — Marking degraded results

A degraded result is never mistaken for a normal one.

### Acceptance criteria

- `RetrievalResult` records the requested strategy, the served strategy and, when they differ, a fallback reason from a fixed vocabulary (for example `qdrant_unavailable`, `qdrant_timeout`, `model_unavailable`); the reason never contains exception text, URLs, keys or chunk text.
- A fallback-served result carries the BM25 `score_kind` and no fusion fields.
- `make retrieve` prints the served strategy and the reason when it differs from the requested one; exit code 0 for a served fallback.
- Payload text is still printed only through `safe_text` (D041).

## R8 — Evaluation results for degraded runs

`make eval-retrieval` records, per case, the strategy that served it.

### Acceptance criteria

- `retrieval_evaluation` format 2.2: the 2.1 keys plus, per case, `served_strategy` and `fallback_reason` (null when not degraded); top level, the requested strategy, the set of served strategies, a count of fallback-served cases per reason, and the Qdrant timeouts used.
- Metrics, slices and latency are computed as today over all cases. When every case was served by one strategy, the top-level `retrieval_strategy` and `score_kind` describe that served strategy; the requested strategy is recorded separately.
- Runs with no fallback produce the same metrics and per-case ranks as 2.1 for the same strategy (equivalence test on a fixture).
- 1.0, 2.0 and 2.1 files still read; their served strategy is their recorded strategy (dense for 1.0 and 2.0).
- The lexical identity block is written for any run that used the lexical file, including a fallback-only run.

## R9 — `eval-compare` by served strategy

Comparison never mixes strategies silently.

### Acceptance criteria

- `eval-compare` refuses (exit 2) a file whose cases were served by more than one strategy, naming the file and the per-strategy case counts.
- Otherwise each file's strategy for comparison is its served strategy; the identity lines show requested and served strategy. A different served strategy is not refused (D054 stays: strategies of the same system compare under the unchanged D044 gate).
- The D054 identity refusals still apply. For a fallback-only file, the collection, `index_version` and embedder pair come from configuration and the lexical file's `dense_identity`, so it compares against the Spec 007 BM25 reference.
- Tests cover: mixed file refused, fallback-only file compared as `bm25`, 2.1 and 2.2 files compared, older formats still read.

## R10 — Security gate over the fallback paths

The authorization hard gate covers every way a hybrid query can be served.

### Acceptance criteria

- `make eval-security` additionally gates: `bm25` opened without Qdrant (R3–R5) and `hybrid` with an injected eligible dense failure at open time and per query, against the same throwaway forbidden rows as Spec 007 (including the missing-owner row). Any forbidden hit fails the gate.
- Security result format 1.2 records the gated paths and names the path in each violation; `access.role` stays `guest` (D047).
- The per-leg unfiltered sanity checks still run; a sanity failure is a harness error (exit 2).
- `make eval-security` passes on `public-eval-v2`.

## R11 — Fault-injection tests and isolation

Failures are tested without a production debug switch.

### Acceptance criteria

- Unit tests inject failures through a test-only seam (constructor-injected client, embedder or factory); no CLI flag, environment variable or config key exists to force a fallback.
- A Docker-free test points the Qdrant client at a closed local port and shows `hybrid` serves BM25 with reason `qdrant_unavailable`, and `dense` exits with the existing Qdrant error.
- `make verify` runs all of R1–R11's tests without Docker, the `bge-m3` extra or a model download.
- `make test-integration` still passes against Docker Qdrant.

## R12 — Real runs (user-owned gate)

The user shows the fallback on the real system.

### Acceptance criteria

- With `QDRANT_URL` pointing at a closed port, the user runs `make eval-retrieval` (default strategy) on suite `public-eval-v2` v2 with the `w2a-realcheck-idx-v1` lexical file. Every case is served by `bm25` with reason `qdrant_unavailable`, and `make eval-compare` against the BM25 reference (`…20261028T123109Z.json`) passes with hits 64 → 64, MRR 0.7082 → 0.7082 and no flip.
- With Qdrant up, the user runs `make eval-retrieval` (default strategy). No case falls back, and `make eval-compare` against the hybrid reference (`…20261028T123121Z.json`) passes with hits 68 → 68, MRR 0.9094 → 0.9094 and no flip.
- The user runs `make retrieve --strategy bm25` once without the `bge-m3` extra (after `make setup`) and with Qdrant unreachable, and it returns hits.
- The result files are committed and their numbers recorded in `CURRENT_STATE.md`. Agents never run the real model and never write to a `w2a-realcheck-*` collection.

## R13 — Unchanged behavior, protected paths and spec-wide verification

### Acceptance criteria

- With Qdrant and the model available, `dense` and `hybrid` rankings are unchanged; ingestion, the payload, `config/ingestion.yaml`, `lexical-v1`, the lexical file format and `make index-lexical` are unchanged (no new `index_version`, no rebuild needed). The legacy `make retrieval-baseline` stays as pinned (D046).
- `config/` changes only by adding the Qdrant timeouts to `config/retrieval.yaml`. Nothing under `evaluation/` or `knowledge/` changes.
- `make verify` passes without the `bge-m3` extra, Docker or a model download; `make test-integration` and `make eval-security` pass.
- Tests never write under `experiments/results/` except `experiments/results/tmp/` or a temporary directory.
- No secrets in code, config, fixtures, results or docs; fallback reasons and refusals never print the Qdrant URL's credentials or API key.

## R14 — Documentation and decisions

### Acceptance criteria

- New decisions (from D056) record: Spec 008 taken ahead of roadmap 7 and why; the failure classification and the fail-closed list; the fallback policy (hybrid only, per query, no circuit breaker, outside fusion); the Qdrant timeouts; the standalone lexical open and the repository-based freshness check (with its large-corpus caveat); result 2.2 and security result 1.2; the `eval-compare` served-strategy rules.
- `ROADMAP.md` records that retrieval graceful degradation (part of item 13) was done before item 7, and that the reranker and model-failure paths remain in item 13.
- `ARCHITECTURE.md` ("Retrieval" and "Retrieval fallback"), `COMMANDS.md`, `TECH_STACK.md` and `CURRENT_STATE.md` describe the code as built, including that `bm25` needs neither Qdrant nor the `bge-m3` extra.

## Out of scope

- Reranker failure fallback and model (generation) failure fallback (roadmap 13; no reranker or generation exists).
- Retries, circuit breakers, health probes, caching of failures, or any fallback from BM25 to another path.
- Falling back for an explicit `dense` or `bm25`, or for a missing `bge-m3` extra.
- An HTTP retrieval route and its startup behavior; Langfuse, metrics or alerting.
- Automatic `make index-lexical` on ingest or a freshness check inside ingestion.
- Per-scope lexical files and non-guest roles (roles spec; D050).
- Malayalam stemming, any tokenizer change, query transformation (roadmap 8); `g061` (reranking or multilingual spec).
- Chunking changes, a new `index_version`, re-ingestion, `relevant_section_ids` (roadmap 7).
- New or changed evaluation cases; the Phase 2 "compare shared cases" mode; Knowledge Releases; any Phase 2 work.
- Device pinning (D038); the open Spec 004 nits and Spec 006 retrospective F1, unless a task touches the same code.

## Definition of Done

- R1–R14 satisfied and traced to approved tasks.
- R12 user-owned runs recorded, checked and committed.
- `make verify` (no extra, Docker or model), `make test-integration` and `make eval-security` pass.
- Protected-path check: under `config/` only the `retrieval.yaml` timeouts; nothing under `evaluation/` or `knowledge/`.
- `DECISIONS.md` and `ROADMAP.md` record the move ahead of roadmap 7; `ARCHITECTURE.md`, `COMMANDS.md`, `TECH_STACK.md` and `CURRENT_STATE.md` match the code.
- The required `spec-reviewer` retrospective passes and the user approves the merge.

## Traceability

| Requirement | Task(s) | Verification |
|---|---|---|
| R1 | T1, T4 | `test_availability.py` (Qdrant wrapper-only unwrapping, unrelated-error case, model cause-chain cases incl. missing revision/model ID); `test_index.py`, `test_retriever.py`; `test_fallback.py`; `make verify` |
| R2 | T1, T4 | config 1.1 validation in `test_strategy.py`; stalled-fake tests (DenseIndex and through `open_retrieval`); factory test; `make verify` |
| R3 | T2 | `test_lexical_standalone.py` (identity refusals, no client or embedder) |
| R4 | T2 | `test_lexical_standalone.py` (fresh passes; edited or removed document refused); design large-corpus note |
| R5 | T3 | `test_bm25.py` characterization; no-extra/no-Qdrant `open_retrieval` and CLI tests; import pin; manual closed-port `make retrieve --strategy bm25` (throwaway) |
| R6 | T4 | `test_fallback.py` (open-time, per-query, retry, same access, equal to bm25, non-eligible raised); `git diff` of `fusion.py`/`hybrid.py` empty |
| R7 | T4 | result-model and `make retrieve` CLI tests; manual throwaway run |
| R8 | T5 | `test_retrieval_eval.py` (2.2 keys, no-fallback equivalence, fully-fallback and mixed fixtures) |
| R9 | T5 | `test_compare.py` (mixed refused, served-strategy comparison, `dense_identity` embedder pair, older formats) |
| R10 | T6 | `test_security_eval.py`; `test_security_integration.py`; `make eval-security` (five paths) |
| R11 | T1, T4 | test-only injection; closed-port and stalled-fake tests; `make verify` without Docker/extra/model; `make test-integration` |
| R12 | T7 | user runs; `make eval-compare` vs the Spec 007 BM25 and hybrid references; field checks recorded in `CURRENT_STATE.md` |
| R13 | T1, T2, T3, T6, T8 | `make verify`, `make test-integration`, `make eval-security`; per-task protected-path checks; `git diff --name-status main...HEAD -- evaluation knowledge config` |
| R14 | T8 | doc review against code; D056–D062; ROADMAP note |
| Definition of Done | T8 | spec-wide commands; protected-path output; retrospective |

## Change log

<!-- Approved amendments only, one dated line each:
- YYYY-MM-DD — <R#/T#>: <what changed and why>. Re-opened <T#>. -->
- 2026-10-29 — R1, R6 (design review, user): a model load failure is eligible only when its explicit cause chain contains a network or timeout error; configuration-type load failures (missing model ID or revision, gated repository, corrupt cache, permissions, offline mode) fail closed. Qdrant errors are unwrapped only through the known client wrapper. Tests added to R1. No task re-opened (no tasks yet).
