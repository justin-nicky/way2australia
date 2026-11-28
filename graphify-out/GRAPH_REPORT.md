# Graph Report - way2australia  (2026-11-27)

## Corpus Check
- 415 files · ~513,391 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 40 file(s) not represented in the graph (top: (none) 20, .jsonl 17, .mdc 1)

## Summary
- 7177 nodes · 22578 edges · 304 communities (228 shown, 76 thin omitted)
- Extraction: 76% EXTRACTED · 24% INFERRED · 0% AMBIGUOUS · INFERRED: 5340 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d042ce54`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- test_deadline.py
- test_fallback.py
- DenseIndex
- test_validate.py
- RerankingRetriever
- test_applicability.py
- test_index.py
- test_cli_without_a_rerank_flag_reranks_on_the_committed_default
- Factory
- IngestionConfigurationError
- FakeTokenizer
- test_retrieval_eval.py
- compare.py
- test_lexical_cli.py
- test_suite_v2.py
- D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)
- generation_eval.py
- QdrantIndexStore
- DenseRetriever
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- retrieval/test_access.py
- BGE-M3 Adapter
- day1_baseline.yaml
- Spec 004 ingestion baseline
- GeneratorOutput
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- test_ask_cli.py
- Settings
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- test_lexical_standalone.py
- 009 — Chunking Experiments Requirements
- Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)
- KnowledgeDocument
- ingestion/test_service.py
- test_legacy_baseline_snapshot.py
- Spec 006 evaluation framework
- EvaluationConfigurationError
- Workflow Reviewer
- LocalDocumentRepository
- 008 — Retrieval Fallback Requirements
- LexicalIndex
- tokenizer.py
- Ingestion (Phase 1 baseline, Spec 004)
- Stable command surface (target interface; implemented targets listed)
- re
- HeadingChunker
- typing
- test_generation_eval.py
- ingestion/store.py
- OptionalDependencyError
- DECISIONS.md architecture decision log
- lexical/build.py
- MonkeyPatch
- ingestion.yaml
- Evaluation Phase 1 framework (Spec 006)
- rendered_prompt
- FakeReranker
- Review
- hub_offline_empty_cache
- transcript_metrics.py
- make eval-retrieval
- evaluation/validate.py
- test_manifest_validation.py
- open_retrieval
- embedder
- Phase 1 RAG query pipeline
- build_lexical_index
- IndexSettings
- PromptConfigurationError
- Evaluation Suite (public-eval-v1)
- test_rerank_eval.py
- test_baseline.py
- embedder
- repositories/__init__.py
- pytest
- test_verify_budget_hook.py
- retrieval.yaml
- test_breaker.py
- json
- FallbackReason
- rerank
- Backend stack
- embedder
- roles
- SQLite FTS5
- slices.py
- Roadmap 13 - Graceful degradation
- Repository Structure
- Spec 003 task-gated agent workflow
- list_eligible_documents
- test_rerank_bge.py
- Phase 2 - Knowledge Operations
- CURRENT_STATE.md current state document
- healthcheck
- Constitution
- AnswerService
- test_anthropic_api.py
- test_serving_startup.py
- Task-gated agent workflow loop
- SpyIndex
- Engineering Conventions
- answer.py
- Development Workflow
- subprocess
- read_result
- Mock assessments, scoring, feedback and review windows
- 012 — Grounded Generation Requirements
- AGENTS.md Project Rules
- generation.yaml
- test_repository_contract.py
- Roadmap 7 - Chunking experiments
- AWS target
- open_retrieval / OpenedRetrieval
- test_strategy.py
- check_hit (fail-closed re-check)
- Knowledge Schema and Metadata
- retrieval_identity
- graphify_guard.py
- QdrantIndexStore
- Baseline runner and result JSON
- 006 Evaluation Framework Tasks
- NAATI CCL booking, fees, cancellation, results and credential validity
- eval-security
- precedence
- Phase 1 - Production-oriented RAG
- NAATI CCL candidate rules and test-day setup
- sys
- EligibilityPolicy / GUEST_PUBLIC_POLICY
- Product Context
- asyncio
- verify_budget.py
- Any
- NAATI CCL test format, scoring and results
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
- Roadmap 10 - Grounded generation + citations
- Evaluation Package (evaluation/)
- eval-retrieval
- Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)
- Phase 0 - Project bootstrap
- Vocabulary, flashcards and free access
- make retrieve
- Evaluation Framework Goal
- Versioning and Releases
- test_cli_config.py
- pathlib
- Ingestion pipeline (target vs current state diff)
- eval-compare
- Payments, account access and support boundaries
- Home Affairs credentialled community language points
- ResolvedAccess
- T6 — real runs recorded (round 1, stage 2)
- test_context.py
- Mission
- Way2Australia public offering and assistant scope
- Materials and dialogue practice
- test_schemas.py
- policy
- policy
- policy
- policy
- Phase 2 Analytics Event Contract
- Frontend stack
- StackHolder
- test_graphify_guard.py
- Canonical document metadata
- Orchestrator State Machine
- Project Context README
- Developer tooling
- R13 Unchanged behavior and protected paths
- Retrospective verdict PASS
- way2australia-rag
- Phase 1 analytics event contract
- Spec-driven development workflow
- D025 persona_scope informational
- T9 deviation: git_dirty true in BM25 and hybrid result files
- way2australia
- test_answer_route.py
- way2australia-observability
- write
- security_eval.py
- generation/config.py
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- test_content_hash.py
- test_stack.py
- make ingest
- FakeGenerator
- policy
- T3 — round 2
- check_target_allowed
- test_opening_lifecycle.py
- test_failed_write_removes_partial_file
- 013 — HTTP Route and Serving Policy Requirements
- DocumentRepository
- Retrieval fallback (Spec 008, D056-D062)
- build_security_index
- Spec 005 dense retrieval baseline
- BgeRerankerV2M3
- D055 Default strategy is hybrid (Spec 007)
- test_suite_v4.py
- Round 1 — 2026-11-04
- Readiness
- test_concurrency.py
- serving/config.py
- 007 — Hybrid Retrieval Tasks
- test_bm25_path_imports_neither_the_model_adapter_nor_the_model_stack
- T6 — suite v4 (round 1, stage 4)
- run_phase_one
- ._open
- versions
- D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)
- test_bound_path_refuses_lexical_v1_under_lexical_v2
- Spec 002 document model and repository
- 011 — Multilingual Reranking Requirements
- generation_poisoned_evidence
- rrf_fuse
- httpx
- Spec 009 — Task reviews
- test_goldens.py
- test_route_security.py
- serving.yaml
- message_language
- Scripted
- BodySizeMiddleware
- TestRunsBudgetedMake
- ingest
- test_rerank_config.py
- ClientFactory
- test_store_integration.py
- lexical/ package (Spec 007)
- test_failed_write_removes_partial_file
- generators
- ServingInputs
- TestMain
- FallbackRetriever
- Spec 011 — task reviews
- T6 — preparation (round 1)
- .embed_documents
- T6 — Security gate over the fallback paths
- Spec 012 — task reviews
- CountingStore
- _TracingLock
- Components / boundaries
- Evaluation result format 2.2
- R8 — Evaluation results for degraded runs
- R12 — Real runs (user-owned gate)
- T6 — model choice, default config and v4 candidates (round 1, stage 3)
- _RealStubReranker
- DeviceStub
- TestAgentAndBudget
- Way2Australia AI Platform Master Implementation Plan
- CountingEmbedder
- lexical_closes
- task-reviews.md per-spec log format
- Roadmap 3 - Ingestion baseline
- R5 — `bm25` without Qdrant or the `bge-m3` extra
- T7 — round 2
- test_open_retrieval_passes_the_breaker_to_every_fallback
- stalled_port
- .__init__
- .close
- bge_tokenizer_fixture
- exit_process
- _shape

## God Nodes (most connected - your core abstractions)
1. `open_retrieval()` - 133 edges
2. `LocalDocumentRepository` - 129 edges
3. `DenseIndex` - 111 edges
4. `ResolvedAccess` - 105 edges
5. `RetrievalConfigurationError` - 94 edges
6. `FallbackRetriever` - 93 edges
7. `FakeGenerator` - 91 edges
8. `FakeTokenizer` - 83 edges
9. `DenseRetriever` - 83 edges
10. `RetrievalResult` - 82 edges

## Surprising Connections (you probably didn't know these)
- `T1 — Reranker contract, adapters, errors and config` --references--> `prefer()`  [INFERRED]
  .kiro/specs/011-multilingual-reranking/tasks.md → packages/rag/src/way2australia_rag/evaluation/security_eval.py
- `Acceptance criteria` --references--> `Generator`  [INFERRED]
  .kiro/specs/012-grounded-generation/requirements.md → packages/rag/src/way2australia_rag/generation/base.py
- `Deviations from the approved plan` --references--> `ClaudeMessagesAdapter`  [INFERRED]
  .kiro/specs/012-grounded-generation/review.md → packages/rag/src/way2australia_rag/generation/claude.py
- `Traceability` --references--> `FakeGenerator`  [INFERRED]
  .kiro/specs/012-grounded-generation/requirements.md → packages/rag/src/way2australia_rag/generation/fake.py
- `Acceptance criteria` --references--> `AnswerService`  [INFERRED]
  .kiro/specs/013-http-serving/requirements.md → packages/rag/src/way2australia_rag/generation/service.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Failure classification to fallback serving flow** — kiro_specs_008_retrieval_fallback_design_classify_qdrant_error, kiro_specs_008_retrieval_fallback_design_classify_model_error, kiro_specs_008_retrieval_fallback_design_retrievalunavailableerror, kiro_specs_008_retrieval_fallback_design_fallbackretriever, kiro_specs_008_retrieval_fallback_design_bm25retriever [EXTRACTED 0.85]
- **Standalone lexical open (identity then freshness, no Qdrant)** — kiro_specs_008_retrieval_fallback_design_indexidentity, kiro_specs_008_retrieval_fallback_design_open_standalone_lexical, kiro_specs_008_retrieval_fallback_design_verify_fresh, kiro_specs_008_retrieval_fallback_design_bm25retriever [EXTRACTED 0.85]
- **Authorization applied inside every retrieval leg before fusion** — docs_project_decisions_d035, docs_project_decisions_d040, kiro_specs_007_hybrid_retrieval_design_bm25_retriever, kiro_specs_007_hybrid_retrieval_design_hybrid_retriever [EXTRACTED 0.95]
- **Default strategy decision: R13 rule, T9 runs, D055** — kiro_specs_007_hybrid_retrieval_requirements_r13_default_strategy_decision, kiro_specs_007_hybrid_retrieval_tasks_t9_comparison_gate, docs_project_decisions_d055 [EXTRACTED 0.95]
- **Spec 008 task sequence T1-T8 delivering R1-R14** — kiro_specs_008_retrieval_fallback_tasks_t1_failure_classification_and_qdrant_timeouts, kiro_specs_008_retrieval_fallback_tasks_t2_index_identity_standalone_lexical_open_and_freshness_check, kiro_specs_008_retrieval_fallback_tasks_t3, kiro_specs_008_retrieval_fallback_tasks_t4_fallback_policy_for_hybrid_and_result_marking, kiro_specs_008_retrieval_fallback_tasks_t5, kiro_specs_008_retrieval_fallback_tasks_t6_security_gate_over_the_fallback_paths, kiro_specs_008_retrieval_fallback_tasks_t7_real_runs_user_owned_gate, kiro_specs_008_retrieval_fallback_tasks_t8_documentation_decisions_and_final_verification [EXTRACTED 0.95]
- **Spec 008 deliverable** — docs_project_current_state_spec008, docs_project_current_state_cap_errors, docs_project_current_state_cap_standalone, docs_project_current_state_cap_fallback, docs_project_current_state_cap_result22, docs_project_current_state_cap_security5 [EXTRACTED 1.00]
- **Authorization enforcement chain** — docs_project_decisions_d006, docs_project_decisions_d035, docs_project_decisions_d040, docs_project_decisions_d045, docs_project_decisions_build_access_filter, docs_project_decisions_check_hit [EXTRACTED 1.00]
- **Retrieval fallback stack** — docs_project_decisions_d057, docs_project_decisions_d058, docs_project_decisions_d059, docs_project_decisions_d060, docs_project_decisions_d061, docs_project_decisions_d062 [EXTRACTED 1.00]
- **Graceful degradation paths** — docs_project_roadmap_dense_to_bm25, docs_project_roadmap_reranker_failure, docs_project_roadmap_qdrant_to_fts5, docs_project_roadmap_model_failure [EXTRACTED 1.00]
- **Intentionally avoided technology choices** — docs_project_tech_stack_langgraph, docs_project_tech_stack_bedrock_knowledge_bases, docs_project_tech_stack_bedrock_agents, docs_project_tech_stack_kubernetes, docs_project_tech_stack_multiple_vector_dbs, docs_project_tech_stack_agent_orchestration, docs_project_tech_stack_fine_tuning, docs_project_tech_stack_microservices, docs_project_tech_stack_heavy_frameworks [EXTRACTED 1.00]
- **Hybrid retrieval pipeline** — docs_project_tech_stack_qdrant, way2australia_ai_platform_implementation_plan_bge_m3, docs_project_tech_stack_sqlite_fts5, docs_project_tech_stack_bm25_fts5, docs_project_tech_stack_rrf [EXTRACTED 1.00]
- **Evaluation make targets sharing the suite loader** — _kiro_specs_006_evaluation_framework_design_validate_evaluation, _kiro_specs_006_evaluation_framework_design_eval_retrieval, _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_eval_compare, _kiro_specs_006_evaluation_framework_design_suite_loader [EXTRACTED 1.00]
- **Guest authorization path (resolve, filter, re-check)** — _kiro_specs_005_dense_retrieval_baseline_design_accesscontext, _kiro_specs_005_dense_retrieval_baseline_design_resolve_access, _kiro_specs_005_dense_retrieval_baseline_design_build_access_filter, _kiro_specs_005_dense_retrieval_baseline_design_check_hit [EXTRACTED 1.00]
- **Ingestion pipeline components** — _kiro_specs_004_ingestion_baseline_design_ingestionservice, _kiro_specs_004_ingestion_baseline_design_headingchunker, _kiro_specs_004_ingestion_baseline_design_embedder_protocol, _kiro_specs_004_ingestion_baseline_design_qdrantindexstore [EXTRACTED 1.00]
- **Authorization hard gate construction** — _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_security_index, _kiro_specs_006_evaluation_framework_design_forbidden_variants, _kiro_specs_006_evaluation_framework_design_one_access_path, _kiro_specs_006_evaluation_framework_design_security_gate [EXTRACTED 1.00]
- **Task-gated spec workflow roles** — agent_skills_spec_planner_skill_spec_planner_skill, agent_skills_spec_implementer_skill_spec_implementer_skill, agent_skills_task_reviewer_skill_task_reviewer_skill, agent_skills_spec_reviewer_skill_spec_reviewer_skill [EXTRACTED 1.00]
- **Task-gated workflow roles** — _kiro_specs_003_task_gated_workflow_design_spec_orchestrator, _kiro_specs_003_task_gated_workflow_design_spec_implementer, _kiro_specs_003_task_gated_workflow_design_task_reviewer, _kiro_specs_003_task_gated_workflow_design_spec_planner, _kiro_specs_003_task_gated_workflow_design_spec_reviewer [EXTRACTED 1.00]
- **Language, access and source authority separation** — docs_knowledge_schema_and_metadata_access_scope, docs_knowledge_schema_and_metadata_lote_languages, docs_knowledge_schema_and_metadata_authorization_vs_language_independence, docs_knowledge_source_of_truth_source_precedence [INFERRED 0.75]
- **Knowledge Release composition** — way2australia_ai_platform_implementation_plan_knowledge_release, way2australia_ai_platform_implementation_plan_evaluation_suite, way2australia_ai_platform_implementation_plan_release_manifest, way2australia_ai_platform_implementation_plan_document_manifest [INFERRED 0.75]
- **Security regression controls** — way2australia_ai_platform_implementation_plan_staff_only_canary, way2australia_ai_platform_implementation_plan_poisoned_public_document, way2australia_ai_platform_implementation_plan_graceful_degradation, way2australia_ai_platform_implementation_plan_authorization_before_generation [INFERRED 0.75]
- **Retrieval fallback mechanism** — docs_project_architecture_fallback_retriever, docs_project_architecture_unavailable_error, docs_project_architecture_open_retrieval, docs_project_architecture_open_standalone_lexical [INFERRED 0.85]
- **Hybrid retrieval pipeline** — docs_project_architecture_hybrid_retriever, docs_project_architecture_bm25_retriever, docs_project_architecture_dense_retriever, docs_project_architecture_rrf_fuse [INFERRED 0.85]
- **Evaluation command suite** — docs_project_commands_validate_eval, docs_project_commands_eval_retrieval, docs_project_commands_eval_security, docs_project_commands_eval_compare [INFERRED 0.85]
- **Hybrid retrieval pipeline (dense, BM25, RRF, reranker)** — way2australia_ai_platform_implementation_plan_bge_m3, way2australia_ai_platform_implementation_plan_hybrid_rrf, way2australia_ai_platform_implementation_plan_reranker, way2australia_ai_platform_implementation_plan_qdrant [INFERRED 0.85]
- **Lexical stack: tokenizer, FTS5 store and index-lexical command** — kiro_specs_007_hybrid_retrieval_design_lexical_v1_tokenizer, kiro_specs_007_hybrid_retrieval_design_sqlite_fts5_lexical_store [INFERRED 0.85]
- **Task-gated spec workflow** — docs_project_decisions_d023, docs_project_decisions_d031, docs_project_workflow_task_gated_loop, docs_project_workflow_retrospective [INFERRED 0.85]

## Communities (304 total, 76 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.12
Nodes (57): case(), doc(), doc21(), doc22(), ranked(), refusal(), run(), run_cross() (+49 more)

### Community 1 - "test_deadline.py"
Cohesion: 0.05
Nodes (28): Hard generation cap and budget (R6), Implementation, Review, T4 — round 1, User decision, T4 — Hard generation cap and per-request budget, Verification, AbandonedWork (+20 more)

### Community 2 - "test_fallback.py"
Cohesion: 0.15
Nodes (24): Review, access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary, run_cli() (+16 more)

### Community 3 - "DenseIndex"
Cohesion: 0.10
Nodes (35): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Decisions resolved before drafting, LexicalRow, DenseIndex, build(), DroppedClauseIndex, guest(), pub() (+27 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "RerankingRetriever"
Cohesion: 0.09
Nodes (33): Components / boundaries, Acceptance criteria, Decisions resolved before drafting, R4 — Reranking stage on `hybrid`, Implementation, Review, T2 — round 1, User decision (2026-11-05) (+25 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.10
Nodes (40): Implementation, Implementation, Implementation, Review, Spec 010 — task reviews, T2 — round 1, T3 — round 1, T6 — round 1 (+32 more)

### Community 7 - "test_index.py"
Cohesion: 0.14
Nodes (41): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+33 more)

### Community 8 - "test_cli_without_a_rerank_flag_reranks_on_the_committed_default"
Cohesion: 0.19
Nodes (14): Implementation, factory(), run(), test_cli_dense_or_bm25_without_no_rerank_exits_2_on_the_committed_default(), test_cli_no_rerank_builds_nothing(), test_cli_prints_rerank_off_with_no_rerank(), test_cli_rerank_line_with_the_fake_reranker(), test_cli_rerank_with_dense_or_bm25_exits_2() (+6 more)

### Community 9 - "Factory"
Cohesion: 0.18
Nodes (23): _advice_ok(), clean_env(), Factory, indexed(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client(), test_empty_tenant_exits_2_for_both_clis() (+15 more)

### Community 10 - "IngestionConfigurationError"
Cohesion: 0.03
Nodes (92): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior, Interfaces / models (+84 more)

### Community 11 - "FakeTokenizer"
Cohesion: 0.03
Nodes (98): _check_lexical(), fake_lexical(), As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Security gate (R9), Truncation guard (R2), 009 — Chunking Experiments: Retrospective Review (+90 more)

### Community 12 - "test_retrieval_eval.py"
Cohesion: 0.10
Nodes (46): equivalence_suite(), test_a_reranker_without_the_flag_or_depth_is_refused(), test_reranking_off_has_null_identity_and_no_rerank_unanswerable_keys(), test_unanswerable_rerank_distributions_are_informational(), basic_suite(), build(), chunks_per_document_dense(), default_eval_extras() (+38 more)

### Community 13 - "compare.py"
Cohesion: 0.10
Nodes (42): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+34 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.20
Nodes (20): lexical_dir(), _no_qdrant(), run(), test_bad_config_exits_2(), test_cased_name_cannot_write_into_the_real_repository(), test_env_dir_into_tracked_directory_is_refused(), test_file_holds_the_identity_and_no_chunk_text_is_printed(), test_lexical_location_is_git_ignored() (+12 more)

### Community 15 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)"
Cohesion: 0.21
Nodes (14): make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Known issue: verify_fresh asyncio.run in event loop, Known issue: freshness check rereads every document, Malayalam BM25 limit: exact tokens only, no stemming, D010 Qdrant primary, SQLite FTS5 fallback, D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007) (+6 more)

### Community 17 - "generation_eval.py"
Cohesion: 0.04
Nodes (67): Acceptance criteria, Acceptance criteria, R7 — Marking degraded results, Requirements traceability, Implementation, Review, T1 — round 1, User decision (+59 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.16
Nodes (22): IndexSettingsMismatchError, QdrantIndexStore, client(), test_replace_and_delete_flows(), make_points(), make_settings(), snapshot(), store() (+14 more)

### Community 19 - "DenseRetriever"
Cohesion: 0.07
Nodes (26): User decision, Implementation, T2 — round 2, User decision, DenseRetriever, deterministic_clock(), run_equivalence(), _doc_sets() (+18 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (38): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+30 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "retrieval/test_access.py"
Cohesion: 0.11
Nodes (17): Role, clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload() (+9 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "day1_baseline.yaml"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.14
Nodes (18): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+10 more)

### Community 26 - "GeneratorOutput"
Cohesion: 0.04
Nodes (57): 012 — Grounded Generation Design, Alternatives / deferred decisions, As-built notes, Bedrock adapter, Components / boundaries, Data flow, Direct Anthropic API generator (2026-11-10 amendment, T5b), Interfaces / models (+49 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.10
Nodes (30): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), edit_jsonl(), errors() (+22 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.08
Nodes (40): run(), User decision, T10 — Documentation, decisions and hand-off, Verification, Review, build_lexical(), eval_world(), leg_order() (+32 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "test_ask_cli.py"
Cohesion: 0.14
Nodes (22): ask(), clean_env(), config_copy(), Factory, indexed(), test_anthropic_without_a_model_id_exits_two(), test_bedrock_without_a_model_id_exits_two(), test_configuration_errors_exit_two() (+14 more)

### Community 31 - "Settings"
Cohesion: 0.12
Nodes (10): get_request_settings(), get_settings(), Settings, isolate_settings_environment(), test_create_app_wires_settings(), test_settings_defaults_without_env_file(), test_settings_load_from_env_file(), test_settings_reject_invalid_port() (+2 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.17
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (27): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+19 more)

### Community 35 - "test_lexical_standalone.py"
Cohesion: 0.15
Nodes (20): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+12 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "KnowledgeDocument"
Cohesion: 0.06
Nodes (12): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, DocumentQuery (+4 more)

### Community 39 - "ingestion/test_service.py"
Cohesion: 0.11
Nodes (27): BoomChunker, CountingEmbedder, doc(), Harness, ShortResultEmbedder, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates() (+19 more)

### Community 40 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 41 - "Spec 006 evaluation framework"
Cohesion: 0.10
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+23 more)

### Community 42 - "EvaluationConfigurationError"
Cohesion: 0.08
Nodes (27): Review, EvaluationConfigurationError, EvaluationError, active_unanswerable_cases(), _case_kind(), select_cases(), CaseBase, CaseStatus (+19 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.06
Nodes (65): LocalDocumentRepository, build(), _DefectiveStage, DroppedClauseLexical, guest_access(), new_base(), real_queries(), run_gate() (+57 more)

### Community 45 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.13
Nodes (17): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Change log, Decisions resolved before drafting, Definition of Done (+9 more)

### Community 46 - "LexicalIndex"
Cohesion: 0.03
Nodes (73): Next-step log (done items, as of 2026-11-07), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Acceptance criteria, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R4 — Freshness from the repository (`lexical/freshness.py`), T2: where the shared pieces live (2026-10-31), Acceptance criteria, Acceptance criteria (+65 more)

### Community 47 - "tokenizer.py"
Cohesion: 0.10
Nodes (20): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), Implementation, Review, Review, T3 — round 1, User decision, Review, _inside_git_work_tree() (+12 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.09
Nodes (27): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, Evaluation architecture (Evaluation Suite case types), Evaluation cases have stable IDs and versions; not coupled to chunk IDs, FakeEmbedder (deterministic), HeadingChunker (heading v1, character cap, stable section_id slugs) (+19 more)

### Community 49 - "Stable command surface (target interface; implemented targets listed)"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "re"
Cohesion: 0.09
Nodes (7): test_no_language_literal_in_evaluation_code(), test_generation_source_has_no_language_code_or_name(), test_chillu_pairs_tokenize_the_same_inside_and_at_end(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens(), test_module_has_no_language_code_literal(), test_nfd_equals_nfc()

### Community 51 - "HeadingChunker"
Cohesion: 0.06
Nodes (64): Review, HeadingChunker, assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot() (+56 more)

### Community 52 - "typing"
Cohesion: 0.03
Nodes (79): Closed known issues and findings (moved 2026-11-07), Review, T2 — v2 dense baseline (user-owned gate), Verification, Review, Review, Implementation, Review (+71 more)

### Community 53 - "test_generation_eval.py"
Cohesion: 0.07
Nodes (34): Implementation, Review, T5 — round 3, Test changes (T3/T5b null-default assertions changed; each listed), User decision, _config_copy(), _exact(), _factory() (+26 more)

### Community 54 - "ingestion/store.py"
Cohesion: 0.10
Nodes (17): compare(), mismatch_message(), IndexedDocument, base_settings(), test_build_index_settings_records_embedder_and_chunker(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract(), test_compare_reports_each_other_field() (+9 more)

### Community 55 - "OptionalDependencyError"
Cohesion: 0.09
Nodes (15): BgeM3Embedder, EmbedderInfo, OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+7 more)

### Community 56 - "DECISIONS.md architecture decision log"
Cohesion: 0.09
Nodes (33): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived (+25 more)

### Community 57 - "lexical/build.py"
Cohesion: 0.12
Nodes (16): Requirements traceability, Chunk, check_chunks(), ChunkTooLongError, _effective_limit(), build_payload(), chunk_identity(), _insert() (+8 more)

### Community 58 - "MonkeyPatch"
Cohesion: 0.10
Nodes (23): build_security_repository(), _fixture_files(), security_repository(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper() (+15 more)

### Community 59 - "ingestion.yaml"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "rendered_prompt"
Cohesion: 0.12
Nodes (40): Implementation, GeneratorUnavailableError, UnavailableReason, rendered_prompt(), APIConnectionError, APIStatusError, APITimeoutError, _config() (+32 more)

### Community 62 - "FakeReranker"
Cohesion: 0.08
Nodes (28): T4 — Security gate over the reranked paths, Verification, RerankerInfo, RerankScores, FakeReranker, stable_score(), Strategy, test_vectors_are_l2_normalized() (+20 more)

### Community 63 - "Review"
Cohesion: 0.06
Nodes (41): AnswerContract, AnswerRequest, PublicCitation, PublicEvidence, PublicReason, PublicStatus, to_contract(), _safe_message() (+33 more)

### Community 64 - "hub_offline_empty_cache"
Cohesion: 0.24
Nodes (6): Verification run, apply_hub_offline_empty_cache(), hub_offline_empty_cache(), _clear_opt_outs(), test_each_opt_out_alone_lifts_the_offline_setup(), test_offline_setup_applied_when_no_opt_out_is_set()

### Community 65 - "transcript_metrics.py"
Cohesion: 0.14
Nodes (14): analyse(), category(), command_kinds(), executed_parts(), executed_text(), expand(), main(), parse_time() (+6 more)

### Community 66 - "make eval-retrieval"
Cohesion: 0.13
Nodes (22): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), D036 binding rules, dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval exit 0 or 2 (+14 more)

### Community 67 - "evaluation/validate.py"
Cohesion: 0.11
Nodes (20): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+12 more)

### Community 68 - "test_manifest_validation.py"
Cohesion: 0.19
Nodes (23): load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected() (+15 more)

### Community 69 - "open_retrieval"
Cohesion: 0.02
Nodes (154): Closed by Spec 013 (moved 2026-11-27, T9), Current goal as of 2026-11-07 (before the split), Former "Not yet implemented" entry (done), History, One-off: user-owned pre-merge check for Spec 004 (done 2026-10-17), Spec 002 decisions made before approval, Implementation, Implementation (+146 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 72 - "build_lexical_index"
Cohesion: 0.07
Nodes (45): T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, build_lexical_index(), LexicalIndexError, test_lexical_1_0_fixture_refused(), test_verify_fresh_refuses_added_document(), test_verify_fresh_refuses_chunker_name_mismatch(), build_production() (+37 more)

### Community 73 - "IndexSettings"
Cohesion: 0.14
Nodes (5): IndexSettings, read_index_settings(), test_index_settings_1_0_upgrades_in_memory(), live_client(), test_collection_with_1_0_settings_still_binds()

### Community 74 - "PromptConfigurationError"
Cohesion: 0.12
Nodes (16): Implementation, T2 — round 2, User decision, compute_version_sha256(), _inside(), PromptConfigurationError, _read_json(), _repo_root_from_here() (+8 more)

### Community 75 - "Evaluation Suite (public-eval-v1)"
Cohesion: 0.11
Nodes (17): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+9 more)

### Community 76 - "test_rerank_eval.py"
Cohesion: 0.11
Nodes (34): NotComparableError, doc23(), _FieldSpy, go(), multi_chunk(), Reranked, reranked_run(), test_a_2_4_file_reads_as_not_reranked() (+26 more)

### Community 77 - "test_baseline.py"
Cohesion: 0.15
Nodes (22): client_with_forbidden(), case(), cli_run(), _git(), run(), setup(), test_case_access_context_never_widens_access(), test_cli_release_mismatch_and_bad_args_exit_2() (+14 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (27): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields() (+19 more)

### Community 80 - "pytest"
Cohesion: 0.06
Nodes (66): D-A smoke-test findings so far (user-run, 2026-11-07; results to follow), Implementation, Review, T3 — round 1, User decision, T3 — Generator interface, fake, Bedrock adapter and config, Verification, test_blank_tenant_refused() (+58 more)

### Community 81 - "test_verify_budget_hook.py"
Cohesion: 0.23
Nodes (5): hook_env(), _load_hook_module(), _run_settings_hook(), TestRepoRoot, TestSettingsHookCommand

### Community 82 - "retrieval.yaml"
Cohesion: 0.07
Nodes (28): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+20 more)

### Community 83 - "test_breaker.py"
Cohesion: 0.13
Nodes (36): _trip_breaker(), Circuit breaker (R4), Serving stack and holder (R1, R2, R5), Implementation, Implementation, Review, T3 — round 1, User decision (+28 more)

### Community 84 - "json"
Cohesion: 0.09
Nodes (24): live_suite_rows(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries(), test_virama_and_vowel_sign_add_no_script(), golden_count(), suite_with_statuses() (+16 more)

### Community 85 - "FallbackReason"
Cohesion: 0.08
Nodes (28): As-built notes, T1: Hugging Face error shapes (confirmed 2026-10-29), Review, classify_model_error(), classify_qdrant_error(), _optional_types(), FallbackReason, raise_if_unavailable() (+20 more)

### Community 86 - "rerank"
Cohesion: 0.09
Nodes (22): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+14 more)

### Community 87 - "Backend stack"
Cohesion: 0.12
Nodes (20): Backend stack, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, FastAPI, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, httpx (+12 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "roles"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "SQLite FTS5"
Cohesion: 0.11
Nodes (20): store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, Fusion (+12 more)

### Community 91 - "slices.py"
Cohesion: 0.13
Nodes (13): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), _active_product_support_codes(), row(), test_absent_languages_from_a_temp_registry() (+5 more)

### Community 92 - "Roadmap 13 - Graceful degradation"
Cohesion: 0.32
Nodes (8): Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Deduplication, context budgeting, evidence ordering, Dense to BM25 degradation, Roadmap 9 - Reranking + context building, Roadmap 13 - Graceful degradation, Qdrant failure to SQLite FTS5, Reranker failure to hybrid results, Spec 008 early delivery (D056)

### Community 93 - "Repository Structure"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec 003 task-gated agent workflow"
Cohesion: 0.18
Nodes (13): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, D023 task state lifecycle reference, Spec 003 task-gated agent workflow, Spec 003 status: verified 2026-10-15 bootstrap exception on main, D023 Task-gated agent workflow (+5 more)

### Community 95 - "list_eligible_documents"
Cohesion: 0.11
Nodes (22): _authority_map(), collect(), _document_ids(), collect(), EligibilityPolicy, list_eligible_documents(), eligible_ids(), make_document() (+14 more)

### Community 96 - "test_rerank_bge.py"
Cohesion: 0.14
Nodes (10): extra_installed(), failing(), raised(), test_missing_extra_at_load(), test_missing_extra_is_refused_naming_the_setup_command(), test_network_failure_at_load_becomes_a_skip_with_the_cause_chain(), test_offline_not_cached_is_a_configuration_error_with_advice(), test_refuses_missing_or_floating_revision() (+2 more)

### Community 97 - "Phase 2 - Knowledge Operations"
Cohesion: 0.21
Nodes (13): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+5 more)

### Community 98 - "CURRENT_STATE.md current state document"
Cohesion: 0.08
Nodes (47): build_retriever, CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25 (+39 more)

### Community 99 - "healthcheck"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "AnswerService"
Cohesion: 0.06
Nodes (34): Phase 2 compatibility / migration, Review, Review, T4 — round 1, User decision, Acceptance criteria, R9 — Answer route and request validation, CitationValidationError (+26 more)

### Community 102 - "test_anthropic_api.py"
Cohesion: 0.10
Nodes (28): _config(), _fake_sdk(), factory(), _generator(), _key(), OptionsStub, _reply(), test_auth_token_alone_is_not_a_credential() (+20 more)

### Community 103 - "test_serving_startup.py"
Cohesion: 0.11
Nodes (33): StartupError, create_app(), CountingEmbedder, CountingGenerator, CountingReranker, fake_settings(), indexed_client(), stack_factory() (+25 more)

### Community 104 - "Task-gated agent workflow loop"
Cohesion: 0.17
Nodes (10): graphify skill pointer, Spec 002 task review log (T3-T9), spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop (+2 more)

### Community 106 - "Engineering Conventions"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "answer.py"
Cohesion: 0.08
Nodes (21): _invalid(), post_answer(), get_health(), HealthResponse, error_response(), install_error_handlers(), _internal_handler(), invalid_request() (+13 more)

### Community 108 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 109 - "subprocess"
Cohesion: 0.12
Nodes (14): Implementation, T5b — round 2, User decision, test_importing_the_module_does_not_import_the_sdk(), test_smoke_module_overrides_the_conftest_environment_fixture(), test_importing_generation_modules_does_not_import_the_sdk(), test_the_import_recorder_catches_an_sdk_import_attempt(), test_conforms_to_protocol() (+6 more)

### Community 110 - "read_result"
Cohesion: 0.10
Nodes (18): Implementation, Review, T5 — round 1, User decision, _build_run(), _mixed(), _num(), read_result() (+10 more)

### Community 111 - "Mock assessments, scoring, feedback and review windows"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "012 — Grounded Generation Requirements"
Cohesion: 0.05
Nodes (39): 012 — Grounded Generation Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+31 more)

### Community 113 - "AGENTS.md Project Rules"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "generation.yaml"
Cohesion: 0.05
Nodes (40): anthropic, backoff_s, deadline_s, effort, max_tokens, model_id, request_timeout_s, retries (+32 more)

### Community 115 - "test_repository_contract.py"
Cohesion: 0.17
Nodes (12): test_fusion_module_has_no_authorization_or_io_surface(), InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol() (+4 more)

### Community 116 - "Roadmap 7 - Chunking experiments"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "AWS target"
Cohesion: 0.06
Nodes (39): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Full agent orchestration (avoided), Intentionally avoided choices, AWS target, Bedrock Agents / AgentCore for Phase 1 (avoided), Bedrock Knowledge Bases as core RAG (avoided) (+31 more)

### Community 118 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.17
Nodes (13): BM25Retriever (identity, lexical), Qdrant client lifecycle gap, IndexIdentity, open_retrieval / OpenedRetrieval, open_standalone_lexical, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory (+5 more)

### Community 119 - "test_strategy.py"
Cohesion: 0.20
Nodes (14): Implementation (user-owned runs + agent wrap-up), Review, Review, T5 — round 1, User decision, test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field() (+6 more)

### Community 120 - "check_hit (fail-closed re-check)"
Cohesion: 0.18
Nodes (8): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), PointPayload (17 fields), build_access_filter (single filter builder), check_hit (fail-closed re-check)

### Community 121 - "Knowledge Schema and Metadata"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "retrieval_identity"
Cohesion: 0.18
Nodes (10): Commands as run by the user (2026-11-13, on `a0869a5`, clean tree), Implementation, Recorded elsewhere, Result-file checks (agent, from the JSON), Review, T6 files for the reviewer, T6 — v4 runs recorded (round 1, stage 5), User decision (2026-11-13, T6 approved; verbatim) (+2 more)

### Community 123 - "graphify_guard.py"
Cohesion: 0.18
Nodes (8): is_non_code(), main(), _repo_root(), search_targets(), skip_nudge(), simple_commands(), _strip_wrappers(), _substitutions()

### Community 124 - "QdrantIndexStore"
Cohesion: 0.24
Nodes (10): BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule, IndexSettings and mismatch refusal, IngestionService, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore, Companion -settings collection (+2 more)

### Community 125 - "Baseline runner and result JSON"
Cohesion: 0.40
Nodes (5): Baseline runner and result JSON, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 126 - "006 Evaluation Framework Tasks"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 127 - "NAATI CCL booking, fees, cancellation, results and credential validity"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 128 - "eval-security"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 129 - "precedence"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 130 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.12
Nodes (19): BM25, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases, HitRate@5, Roadmap 1 - Project foundation, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval (+11 more)

### Community 131 - "NAATI CCL candidate rules and test-day setup"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "sys"
Cohesion: 0.29
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 133 - "EligibilityPolicy / GUEST_PUBLIC_POLICY"
Cohesion: 0.25
Nodes (7): Typed runtime Settings (Pydantic Settings), EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - "Product Context"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "asyncio"
Cohesion: 0.21
Nodes (18): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+10 more)

### Community 136 - "verify_budget.py"
Cohesion: 0.17
Nodes (13): agent_key(), _budget(), count_run(), decide(), _dedupe_window_s(), in_repo(), _load_counts(), log() (+5 more)

### Community 138 - "NAATI CCL test format, scoring and results"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.29
Nodes (4): block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 140 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.13
Nodes (15): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline (+7 more)

### Community 141 - "Evaluation Package (evaluation/)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "eval-retrieval"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Target RAG query flow (User -> FastAPI -> validation -> AccessContext -> LanguageContext -> retrieval -> RRF -> reranker -> context builder -> answerability -> prompt -> Bedrock -> citation validation)"
Cohesion: 0.11
Nodes (24): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+16 more)

### Community 144 - "Phase 0 - Project bootstrap"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make retrieve"
Cohesion: 0.06
Nodes (33): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), make retrieve, --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D053 result 2.1 (+25 more)

### Community 147 - "Evaluation Framework Goal"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Versioning and Releases"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_cli_config.py"
Cohesion: 0.12
Nodes (21): manifest_document_count(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+13 more)

### Community 150 - "pathlib"
Cohesion: 0.09
Nodes (5): test_clis_load_recursive_config(), test_schema_1_0_still_loads_heading(), test_schema_1_1_loads_recursive_arm(), test_match_expression_quotes_and_escapes(), live_client()

### Community 151 - "Ingestion pipeline (target vs current state diff)"
Cohesion: 0.22
Nodes (10): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 Document model and repository (verified), Ingestion pipeline (target vs current state diff), Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline) (+2 more)

### Community 152 - "eval-compare"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 153 - "Payments, account access and support boundaries"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 154 - "Home Affairs credentialled community language points"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 155 - "ResolvedAccess"
Cohesion: 0.04
Nodes (106): Implementation detail by spec (as merged), Spec status table (full rows, as of 2026-11-07), 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior (+98 more)

### Community 156 - "T6 — real runs recorded (round 1, stage 2)"
Cohesion: 0.20
Nodes (10): A. Result-file checks (agent, from the files), Approved thresholds and choice rule (user, 2026-11-13, verbatim), B. Refusal breakdown (status, reason, sub_reason), C. Deadline: generation 32 s against `deadline_s: 30`, Commands as run (correction), D. Spot check, Implementation, Not done / waiting (+2 more)

### Community 157 - "test_context.py"
Cohesion: 0.29
Nodes (16): builder(), hit(), test_all_stats_counts(), test_block_larger_than_max_chars_is_dropped_never_cut(), test_deterministic(), test_different_text_is_kept(), test_empty_input(), test_exact_duplicate_keeps_higher_rank() (+8 more)

### Community 158 - "Mission"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "Way2Australia public offering and assistant scope"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Materials and dialogue practice"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 167 - "Frontend stack"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "StackHolder"
Cohesion: 0.08
Nodes (18): As-built notes, Implementation, Review, T5 — round 1, User decision, T5 — Serving package: config, locks, stack holder, re-open, readiness model, T6 — API startup, readiness endpoint, fake mode and `make api`, Verification (+10 more)

### Community 169 - "test_graphify_guard.py"
Cohesion: 0.20
Nodes (3): test_settings_uses_wrapper(), TestSimpleCommands, TestSkipNudge

### Community 170 - "Canonical document metadata"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 179 - "way2australia-rag"
Cohesion: 0.67
Nodes (3): way2australia-api, way2australia-core, way2australia-rag

### Community 189 - "test_answer_route.py"
Cohesion: 0.11
Nodes (26): BlockingGenerator, open_client(), post(), RaisingGenerator, test_422_does_not_echo_a_sentinel_query(), test_a_body_within_the_limit_is_replayed(), test_active_lote_is_accepted(), test_answer_log_line_fields() (+18 more)

### Community 191 - "write"
Cohesion: 0.24
Nodes (13): compare_continuity(), _fmt_key(), _load_raw(), main(), write(), _base(), test_committed_fixtures_equal(), test_differing_hit_exits_one() (+5 more)

### Community 192 - "security_eval.py"
Cohesion: 0.06
Nodes (51): _forbidden_is_nearest(), Implementation, Review, T8 — round 1, User decision, Implementation, Review, T6 — round 1 (+43 more)

### Community 193 - "generation/config.py"
Cohesion: 0.06
Nodes (16): T1 — Context builder, Verification, AnthropicConfig, ContextConfig, _error_fields(), EstimateConfig, EvidenceOnlyConfig, LanguagesConfig (+8 more)

### Community 194 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 196 - "test_content_hash.py"
Cohesion: 0.12
Nodes (22): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), sha256_hex(), _copy_seed(), h() (+14 more)

### Community 197 - "test_stack.py"
Cohesion: 0.16
Nodes (28): open_serving_stack(), ask(), Clock, ClosingReranker, down(), EmbedderFactory, make_inputs(), RerankerFactory (+20 more)

### Community 198 - "make ingest"
Cohesion: 0.12
Nodes (18): docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make index-lexical, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+10 more)

### Community 199 - "FakeGenerator"
Cohesion: 0.08
Nodes (39): FakeGenerator, FakeMode, issued_ids(), build(), test_fake_generator_has_no_deadline_and_accepts_the_argument(), test_chosen_citations_appear_as_markers_and_in_the_list(), test_decline_is_answerable_false(), test_default_answers_citing_the_first_source() (+31 more)

### Community 201 - "T3 — round 2"
Cohesion: 0.67
Nodes (3): Implementation, T3 — round 2, User decision

### Community 202 - "check_target_allowed"
Cohesion: 0.14
Nodes (17): Implementation, Implementation, Review, T3 — round 2, T3 — round 3, User decision, _group_installed(), check_target_allowed() (+9 more)

### Community 203 - "test_opening_lifecycle.py"
Cohesion: 0.11
Nodes (18): CountingClient, CountingReranker, Factory, ingested(), lexical_closes(), open_with(), RerankerFactory, test_bm25_and_the_open_time_fallback_share_one_standalone_helper() (+10 more)

### Community 205 - "013 — HTTP Route and Serving Policy Requirements"
Cohesion: 0.05
Nodes (36): 013 — HTTP Route and Serving Policy Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+28 more)

### Community 206 - "DocumentRepository"
Cohesion: 0.29
Nodes (7): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Document manifest, DocumentRepository, LocalDocumentRepository

### Community 207 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.12
Nodes (19): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+11 more)

### Community 208 - "build_security_index"
Cohesion: 0.08
Nodes (26): test_route_hides_forbidden_documents_on_every_serving_path(), R11 — Security gate (`security_index.py`, `security_eval.py`), Implementation, Review, T5 — round 1, Implementation, Review, T4 — round 1 (+18 more)

### Community 210 - "Spec 005 dense retrieval baseline"
Cohesion: 0.09
Nodes (34): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make eval-retrieval, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5 (+26 more)

### Community 211 - "BgeRerankerV2M3"
Cohesion: 0.09
Nodes (11): Implementation, Review, T1 — round 1, User decision (2026-11-05), BgeRerankerV2M3, is_offline_not_cached(), _cause_chain(), _model_error_text() (+3 more)

### Community 212 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.11
Nodes (22): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed, Next step 4: Spec 007 T9 strategy comparison and hybrid default (+14 more)

### Community 213 - "test_suite_v4.py"
Cohesion: 0.24
Nodes (7): manifest(), rows(), test_candidate_decisions_and_promotions(), test_v3_dataset_files_match_their_committed_hashes(), test_v3_manifest_differs_from_v4_lineage_only_in_status(), test_v3_rows_equal_their_v4_copy_except_suite_id(), test_v4_manifest_counts_and_lineage()

### Community 214 - "Round 1 — 2026-11-04"
Cohesion: 0.17
Nodes (11): 010 — Multilingual Retrieval: Retrospective Review, Deviations from the approved plan, Documentation reconciled, Final handoff, Findings, Patterns in `task-reviews.md`, Protected-data check, Remediation required (+3 more)

### Community 215 - "Readiness"
Cohesion: 0.09
Nodes (9): get_ready(), Readiness, ReadinessSnapshot, GatedEmbedder, RecordingReranker, test_each_degraded_reason_and_the_breaker_states(), test_embedder_and_reranker_locks_are_separate(), test_ready_ok_has_no_reasons() (+1 more)

### Community 216 - "test_concurrency.py"
Cohesion: 0.09
Nodes (16): down_client(), write_serving(), _burst(), _Clock, _comparable(), _ready_app(), _Switch, test_concurrent_requests_match_the_same_request_alone() (+8 more)

### Community 217 - "serving/config.py"
Cohesion: 0.13
Nodes (18): BreakerConfig, BudgetConfig, check_budget(), ConcurrencyConfig, generator_deadline_s(), load_serving_config(), RequestLimits, ServingConfig (+10 more)

### Community 218 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.17
Nodes (11): 007 — Hybrid Retrieval Tasks, Notes for the retrospective, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification (+3 more)

### Community 220 - "T6 — suite v4 (round 1, stage 4)"
Cohesion: 0.22
Nodes (9): Commands for the user (not run by the agent), Implementation, Open items before the T6 task review, Owner and fluent-speaker review, 2026-11-13 (user decisions, verbatim), Suite v4 contents, T6 — suite v4 (round 1, stage 4), Test changes (each listed), User decisions (2026-11-13, after stage 4) (+1 more)

### Community 221 - "run_phase_one"
Cohesion: 0.09
Nodes (16): _close_generator(), _Loader, make_lifespan(), lifespan(), PhaseOne, _refuse_fake_providers(), _resolve(), run_phase_one() (+8 more)

### Community 222 - "._open"
Cohesion: 0.14
Nodes (12): build_index_settings(), IndexPoint, test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), build_client(), docs(), RaisingEmbedder, retriever(), test_a_network_failure_during_model_load_is_unavailable() (+4 more)

### Community 223 - "versions"
Cohesion: 0.29
Nodes (6): schema_version, versions, files, prompt_id, prompt_version, sha256

### Community 224 - "D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)"
Cohesion: 0.29
Nodes (7): D049 Suite public-eval-v2 and the closed v1 reference (Spec 007), suite public-eval-v2, Acceptance criteria, R13 strategy comparison and default-strategy rule, R1 Evaluation Suite public-eval-v2 (91 cases), R2 — v2 dense baseline (user-owned gate), T9 strategy comparison and default-strategy decision

### Community 225 - "test_bound_path_refuses_lexical_v1_under_lexical_v2"
Cohesion: 0.11
Nodes (13): assert_tokenizer_refusal(), CountingClient, _Guard, guard_opens(), wrapping(), guest(), retriever_for(), stable() (+5 more)

### Community 226 - "Spec 002 document model and repository"
Cohesion: 0.09
Nodes (26): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Spec 001 Project Foundation (implemented), Pydantic document models and enums, EligibilityPolicy for guest/public, GET /health endpoint, LocalDocumentRepository with manifest schema validation (+18 more)

### Community 227 - "011 — Multilingual Reranking Requirements"
Cohesion: 0.08
Nodes (25): 011 — Multilingual Reranking Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+17 more)

### Community 228 - "generation_poisoned_evidence"
Cohesion: 0.10
Nodes (19): Security / authorization, Cross-task consistency, Deviations from the approved plan, Documentation reconciled, Final handoff, Findings, Protected-data check, Remediation required (+11 more)

### Community 229 - "rrf_fuse"
Cohesion: 0.06
Nodes (40): R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Testing / evaluation strategy, Implementation, Implementation, Implementation, Implementation, Review, Review (+32 more)

### Community 230 - "httpx"
Cohesion: 0.24
Nodes (12): caused_by(), hub_5xx(), reason(), test_chain_walk_is_bounded(), test_context_is_never_followed(), test_model_classifier_output_is_unchanged_for_local_entry_not_found(), test_network_cause_is_model_unavailable(), test_offline_not_cached_is_excluded_even_with_a_network_error_below() (+4 more)

### Community 231 - "Spec 009 — Task reviews"
Cohesion: 0.12
Nodes (15): Implementation, Implementation, Implementation, Implementation, Review, Spec 009 — Task reviews, T2 — round 2, T3 — round 1 (+7 more)

### Community 236 - "test_goldens.py"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 237 - "test_route_security.py"
Cohesion: 0.17
Nodes (4): _answer_logs(), _assert_clean(), _document_ids(), _SharedClient

### Community 238 - "serving.yaml"
Cohesion: 0.13
Nodes (14): breaker, cooldown_s, failure_threshold, budget, min_generation_s, request_s, concurrency, max_in_flight (+6 more)

### Community 239 - "message_language"
Cohesion: 0.18
Nodes (8): Implementation, T2 — round 1, message_language(), test_digits_only_uses_en(), test_extra_mapping_in_config_without_code_change(), test_latin_query_uses_en(), test_malayalam_query_uses_ml(), test_mixed_query_uses_non_english()

### Community 241 - "BodySizeMiddleware"
Cohesion: 0.20
Nodes (3): BodySizeMiddleware, replay(), chunks()

### Community 246 - "ingest"
Cohesion: 0.15
Nodes (4): KeepOpenClient, client_factory(), ingest(), memory_client()

### Community 247 - "test_rerank_config.py"
Cohesion: 0.40
Nodes (8): test_1_3_loads_all_fields(), test_1_3_requires_the_block(), test_disabled_block_may_omit_the_revision(), test_invalid_values_are_refused_naming_the_key(), test_older_schemas_load_with_reranking_off(), test_older_schemas_refuse_a_rerank_block(), v13(), write()

### Community 252 - "test_store_integration.py"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 253 - "lexical/ package (Spec 007)"
Cohesion: 0.20
Nodes (10): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), tokenizer.py (lexical-v1), make index-lexical (+2 more)

### Community 254 - "test_failed_write_removes_partial_file"
Cohesion: 0.20
Nodes (3): clean_env(), seeded(), test_failed_write_removes_partial_file()

### Community 255 - "generators"
Cohesion: 0.28
Nodes (4): generators(), build(), lexical_handles(), serving_environment()

### Community 256 - "ServingInputs"
Cohesion: 0.25
Nodes (6): factory(), _stack_factory(), factory(), resolve_serving_choices(), ServingChoices, ServingInputs

### Community 258 - "FallbackRetriever"
Cohesion: 0.25
Nodes (8): Fallback authorization invariant (same ResolvedAccess), classify_model_error, classify_qdrant_error, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed), Qdrant 5xx not eligible (D062), RetrievalUnavailableError / FallbackReason

### Community 259 - "Spec 011 — task reviews"
Cohesion: 0.25
Nodes (7): Implementation, Spec 011 — task reviews, T5 — round 1, T6 — round 1, User decision (2026-11-06), User decision (2026-11-06), User decision (2026-11-06, approval)

### Community 260 - "T6 — preparation (round 1)"
Cohesion: 0.25
Nodes (8): Cost estimate (cost guard's own logic, no network), Implementation, Not yet done / waiting, Preconditions (checks that do not touch the Anthropic API), Proposed, awaiting user approval (NOT approved, NOT recorded as approved), Proposed commands (run from the repo root, in your own shell), T6 — preparation (round 1), User-run smoke gate (recorded verbatim, 2026-11-13; no key)

### Community 261 - ".embed_documents"
Cohesion: 0.36
Nodes (4): _cosine_to_query(), _text_with_score_below(), test_declared_vector_size(), test_query_and_document_methods_agree_and_are_separate()

### Community 262 - "T6 — Security gate over the fallback paths"
Cohesion: 0.29
Nodes (7): Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), Acceptance criteria, R10 — Security gate over the fallback paths, T6 security bm25 seed-subset check instead of verify_fresh, T6 — Security gate over the fallback paths, Verification

### Community 263 - "Spec 012 — task reviews"
Cohesion: 0.29
Nodes (6): Implementation, Review, Spec 012 — task reviews, T5 — round 1, T5 — round 2, T7 — round 1

### Community 266 - "Components / boundaries"
Cohesion: 0.33
Nodes (6): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R9 — Result format 2.1

### Community 267 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 268 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 269 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 270 - "T6 — model choice, default config and v4 candidates (round 1, stage 3)"
Cohesion: 0.33
Nodes (6): Implementation, Known issues recorded (verified against the result files and dataset), Safe-redirect proposal (proposal only; nothing changed), Suite v4 candidates for review (PROPOSED; none approved; no dataset edited; `public-eval-v4` not created), T6 — model choice, default config and v4 candidates (round 1, stage 3), User decision (2026-11-13, verbatim)

### Community 274 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 277 - "task-reviews.md per-spec log format"
Cohesion: 0.50
Nodes (4): task-reviewer skill (read-only), task-reviews.md per-spec log format, Spec 004 task review log (T1-T9), Spec 005 task review log (T1-T7)

### Community 278 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 279 - "R5 — `bm25` without Qdrant or the `bge-m3` extra"
Cohesion: 0.50
Nodes (4): R5 — `bm25` without Qdrant or the `bge-m3` extra, bge_m3 import move in ingestion/cli.py (T3 F1), T1 unexplained 14-minute integration hang, T3 bm25 without Qdrant or extra; one open path

### Community 280 - "T7 — round 2"
Cohesion: 0.50
Nodes (4): Implementation, Review, T7 — round 2, User decision (2026-11-13, T7 approved; verbatim)

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **379 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia`, `way2australia-observability`, `Device not pinned, recorded in results (D038)` (+374 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 2148 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **76 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `ResolvedAccess` to `security_eval.py`, `rrf_fuse`, `open_retrieval`, `check_target_allowed`, `LocalDocumentRepository`, `compare.py`, `LexicalIndex`, `DenseRetriever`, `D055 Default strategy is hybrid (Spec 007)`, `007 — Hybrid Retrieval Requirements`, `typing`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `open_retrieval()` (e.g. with `Closed by Spec 013 (moved 2026-11-27, T9)` and `Implementation detail by spec (as merged)`) actually correct?**
  _`open_retrieval()` has 87 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia` to the rest of the system?**
  _379 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12237583205325141 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `CURRENT_STATE.md current state document`, `Spec 006 evaluation framework`, `retrieval.yaml`, `Spec 005 dense retrieval baseline`, `DECISIONS.md architecture decision log`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 49 inferred relationships involving `LocalDocumentRepository` (e.g. with `_check_lexical()` and `fake_lexical()`) actually correct?**
  _`LocalDocumentRepository` has 49 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._