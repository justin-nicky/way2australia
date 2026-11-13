# Graph Report - way2australia  (2026-11-13)

## Corpus Check
- 380 files · ~459,116 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 40 file(s) not represented in the graph (top: (none) 20, .jsonl 17, .mdc 1)

## Summary
- 6286 nodes · 19645 edges · 251 communities (202 shown, 49 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 4548 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1730ef99`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- build_security_repository
- FallbackRetriever
- DenseIndex
- test_validate.py
- test_reranking.py
- test_applicability.py
- test_index.py
- test_opening_rerank.py
- Factory
- FakeTokenizer
- build_chunker
- test_retrieval_eval.py
- compare.py
- test_lexical_cli.py
- test_suite_v2.py
- Spec 007 hybrid retrieval
- generation/service.py
- QdrantIndexStore
- DenseRetriever
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- retrieval/test_access.py
- BGE-M3 Adapter
- day1_baseline.yaml
- Spec 004 ingestion baseline
- prompts.py
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- test_ask_cli.py
- way2australia_api/config.py
- evaluation/cli.py
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- test_lexical_standalone.py
- 009 — Chunking Experiments Requirements
- Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)
- KnowledgeDocument
- ingestion/test_service.py
- test_legacy_baseline_snapshot.py
- Spec 006 evaluation framework
- suite.py
- Workflow Reviewer
- LocalDocumentRepository
- 008 — Retrieval Fallback Requirements
- LexicalIndex
- tokenizer.py
- Ingestion (Phase 1 baseline, Spec 004)
- Stable command surface (target interface; implemented targets listed)
- test_lexical_tokenizer.py
- HeadingChunker
- baseline.py
- test_generation_eval.py
- point_id
- BgeM3Embedder
- DECISIONS.md architecture decision log
- test_config_schema_11.py
- MonkeyPatch
- ingestion.yaml
- Evaluation Phase 1 framework (Spec 006)
- rendered_prompt
- FakeReranker
- make eval-retrieval
- tests/conftest.py
- transcript_metrics.py
- make index-lexical
- evaluation/validate.py
- test_manifest_validation.py
- check_hit
- embedder
- Phase 1 RAG query pipeline
- LexicalIndexBindingError
- typing
- generation/config.py
- Evaluation Suite (public-eval-v1)
- test_rerank_eval.py
- test_baseline.py
- embedder
- repositories/validate.py
- pytest
- test_verify_budget_hook.py
- retrieval.yaml
- asyncio
- json
- build_retriever
- rerank
- Backend stack
- embedder
- roles
- SQLite FTS5
- re
- Roadmap 10 - Grounded generation + citations
- Repository Structure
- Spec 001 project foundation
- test_eligibility.py
- OptionalDependencyError
- Phase 2 - Knowledge Operations
- CURRENT_STATE.md current state document
- healthcheck
- Constitution
- read_result
- test_anthropic_api.py
- BGE-M3 embeddings
- Task-gated agent workflow loop
- test_violation_names_the_document_from_the_error_attribute
- Engineering Conventions
- ChunkerIdentity
- Development Workflow
- FakeEmbedder
- safe_text
- Mock assessments, scoring, feedback and review windows
- 012 — Grounded Generation Requirements
- AGENTS.md Project Rules
- generation.yaml
- test_repository_contract.py
- Roadmap 7 - Chunking experiments
- AWS target
- FallbackRetriever
- load_retrieval_config
- IngestionService
- Knowledge Schema and Metadata
- Spec 012 — task reviews
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
- test_local_repository.py
- verify_budget.py
- test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote
- NAATI CCL test format, scoring and results
- test_open_retrieval_bm25_builds_no_embedder_and_no_client
- Roadmap 12 - Security
- Evaluation Package (evaluation/)
- eval-retrieval
- Retrieval fallback (Spec 008, D056-D062)
- Phase 0 - Project bootstrap
- Vocabulary, flashcards and free access
- make eval-compare
- Evaluation Framework Goal
- Versioning and Releases
- test_cli_config.py
- test_security_eval.py
- Spec 004 retrospective round 1 (PASS)
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
- ShortResultEmbedder
- test_graphify_guard.py
- Canonical document metadata
- Orchestrator State Machine
- Project Context README
- Developer tooling
- R13 Unchanged behavior and protected paths
- Retrospective verdict PASS
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- D025 persona_scope informational
- T9 deviation: git_dirty true in BM25 and hybrid result files
- way2australia
- way2australia-api
- way2australia-observability
- write
- security_eval.py
- os
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- open_retrieval
- test_content_hash.py
- documents/models.py
- make retrieve
- FakeGenerator
- policy
- Spec 010 — task reviews
- check_target_allowed
- chunking.py
- test_failed_write_removes_partial_file
- test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it
- DocumentRepository
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- build_security_index
- Spec 005 dense retrieval baseline
- live_suite_rows
- D055 Default strategy is hybrid (Spec 007)
- test_suite_v4.py
- Round 1 — 2026-11-04
- Authorization enforced before generation
- dense_equivalence.py
- Review
- 007 — Hybrid Retrieval Tasks
- subprocess
- T6 — suite v4 (round 1, stage 4)
- EvaluationSchemas
- EmbedderInfo
- versions
- D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)
- RetrievalConfigurationError
- test_both_lote_modes_on_every_path_and_chunker
- T1 — round 1
- DocumentRepository Protocol (async)
- retrieval_eval.py
- Roadmap 11 - Observability
- query_terms
- test_changed_unanswerable_field_is_a_problem_without_text
- CountingEmbedder
- Scripted
- test_a_rerank_path_that_fell_back_is_a_harness_error

## God Nodes (most connected - your core abstractions)
1. `LocalDocumentRepository` - 124 edges
2. `DenseIndex` - 115 edges
3. `open_retrieval()` - 112 edges
4. `ResolvedAccess` - 102 edges
5. `RetrievalConfigurationError` - 95 edges
6. `Strategy` - 86 edges
7. `DenseRetriever` - 84 edges
8. `run_retrieval_evaluation()` - 81 edges
9. `FakeTokenizer` - 80 edges
10. `FakeEmbedder` - 78 edges

## Surprising Connections (you probably didn't know these)
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T1 — Reranker contract, adapters, errors and config` --references--> `prefer()`  [INFERRED]
  .kiro/specs/011-multilingual-reranking/tasks.md → packages/rag/src/way2australia_rag/evaluation/security_eval.py
- `Acceptance criteria` --references--> `Generator`  [INFERRED]
  .kiro/specs/012-grounded-generation/requirements.md → packages/rag/src/way2australia_rag/generation/base.py
- `Traceability` --references--> `FakeGenerator`  [INFERRED]
  .kiro/specs/012-grounded-generation/requirements.md → packages/rag/src/way2australia_rag/generation/fake.py
- `User decision` --references--> `test_each_forbidden_row_type_is_in_the_lexical_file()`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/task-reviews.md → packages/rag/tests/evaluation/test_security_eval.py

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

## Communities (251 total, 49 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.12
Nodes (56): case(), doc(), doc21(), doc22(), ranked(), refusal(), run(), run_cross() (+48 more)

### Community 1 - "build_security_repository"
Cohesion: 0.21
Nodes (7): build_security_repository(), _fixture_files(), security_repository(), copy_fixtures(), test_hidden_entries_are_ignored(), test_missing_fixture_is_refused(), test_stray_fixture_file_is_refused_before_any_copy()

### Community 2 - "FallbackRetriever"
Cohesion: 0.09
Nodes (36): Implementation, Review, T4 — round 1, User decision, Review, Acceptance criteria, Dependencies, R5 — Reranker unavailable: serve un-reranked hybrid (+28 more)

### Community 3 - "DenseIndex"
Cohesion: 0.10
Nodes (35): LexicalRow, DenseIndex, build(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+27 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_reranking.py"
Cohesion: 0.07
Nodes (47): T4 — Distinct-document metrics, result 2.3 and cross-index compare, Verification, 011 — Multilingual Reranking Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+39 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.14
Nodes (31): User decision, Verification, active_lote_codes(), build_lexical(), _doc_sets(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical (+23 more)

### Community 7 - "test_index.py"
Cohesion: 0.12
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "test_opening_rerank.py"
Cohesion: 0.11
Nodes (30): As-built notes, Implementation, Review, T6 — round 1, User decision (2026-11-06), reranker_factory(), factory(), access() (+22 more)

### Community 9 - "Factory"
Cohesion: 0.14
Nodes (25): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+17 more)

### Community 10 - "FakeTokenizer"
Cohesion: 0.04
Nodes (72): Package / file placement, Testing / evaluation strategy, Tokenizer (R1), Requirements traceability, Implementation, Implementation, Implementation, Implementation (+64 more)

### Community 11 - "build_chunker"
Cohesion: 0.07
Nodes (39): As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Security gate (R9), 009 — Chunking Experiments: Retrospective Review, Cross-task consistency, Deviations from the approved plan, Documentation reconciled (+31 more)

### Community 12 - "test_retrieval_eval.py"
Cohesion: 0.11
Nodes (43): test_a_reranker_without_the_flag_or_depth_is_refused(), test_reranking_off_has_null_identity_and_no_rerank_unanswerable_keys(), test_unanswerable_rerank_distributions_are_informational(), basic_suite(), build(), default_eval_extras(), fusion_config(), golden() (+35 more)

### Community 13 - "compare.py"
Cohesion: 0.11
Nodes (37): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+29 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.20
Nodes (20): lexical_dir(), _no_qdrant(), run(), test_bad_config_exits_2(), test_cased_name_cannot_write_into_the_real_repository(), test_env_dir_into_tracked_directory_is_refused(), test_file_holds_the_identity_and_no_chunk_text_is_printed(), test_lexical_location_is_git_ignored() (+12 more)

### Community 15 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "Spec 007 hybrid retrieval"
Cohesion: 0.12
Nodes (24): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+16 more)

### Community 17 - "generation/service.py"
Cohesion: 0.04
Nodes (75): 012 — Grounded Generation Design, Alternatives / deferred decisions, As-built notes, Data flow, Interfaces / models, `make ask`, `make eval-generation`, Observability (+67 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.09
Nodes (33): IndexSettingsMismatchError, IndexedDocument, QdrantIndexStore, read_index_settings(), client_factory(), CountingStore, client(), _keyword_indexed() (+25 more)

### Community 19 - "DenseRetriever"
Cohesion: 0.10
Nodes (33): User decision, IndexPoint, DenseRetriever, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), test_formula_shows_the_cap_when_k_reaches_document_count() (+25 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.05
Nodes (38): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index), 007 — Hybrid Retrieval Requirements (+30 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "retrieval/test_access.py"
Cohesion: 0.13
Nodes (17): Role, clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload() (+9 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "day1_baseline.yaml"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.07
Nodes (40): HeadingChunker heading v1 2000-char cap, Pydantic document models and enums, EligibilityPolicy for guest/public, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, LocalDocumentRepository with manifest schema validation, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs (+32 more)

### Community 26 - "prompts.py"
Cohesion: 0.05
Nodes (39): Bedrock adapter, Components / boundaries, Direct Anthropic API generator (2026-11-10 amendment, T5b), Testing / evaluation strategy, Implementation, Review, Review, Review (+31 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.12
Nodes (25): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), errors(), manifest() (+17 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.09
Nodes (35): User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world(), production_chunker(), retrieve() (+27 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "test_ask_cli.py"
Cohesion: 0.06
Nodes (40): Implementation, Implementation, Review, Review, T7 — round 1, T7 — round 2, User decision (2026-11-13, T7 approved; verbatim), output() (+32 more)

### Community 31 - "way2australia_api/config.py"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 32 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (46): R8 — Result format 2.2 (`retrieval_eval.py`), _authority_map(), _compare(), default_security_output_path(), format_summary(), _generation(), main(), _rerank_lines() (+38 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.15
Nodes (20): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+12 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (28): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 35 - "test_lexical_standalone.py"
Cohesion: 0.16
Nodes (20): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+12 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "KnowledgeDocument"
Cohesion: 0.10
Nodes (5): _check_language_code(), KnowledgeDocument, BoomChunker, ListRepository, IgnoresQueryRepository

### Community 39 - "ingestion/test_service.py"
Cohesion: 0.18
Nodes (24): doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text(), test_chunker_exception_is_per_document_failure() (+16 more)

### Community 40 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 41 - "Spec 006 evaluation framework"
Cohesion: 0.10
Nodes (29): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+21 more)

### Community 42 - "suite.py"
Cohesion: 0.07
Nodes (32): active_unanswerable_cases(), CaseBase, CaseStatus, DatasetRef, DatasetType, GoldenCase, LoadedSuite, SecurityCase (+24 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.11
Nodes (43): LocalDocumentRepository, build(), DroppedClauseLexical, guest_access(), real_queries(), run_gate(), security_result(), spied() (+35 more)

### Community 45 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.05
Nodes (50): Decisions D056-D062, Spec 008 Retrieval Fallback Design, Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria (+42 more)

### Community 46 - "LexicalIndex"
Cohesion: 0.11
Nodes (14): Tokenizers (R5, R6), T3 — `lexical-v2`, tokenizer selection, script mix, `--cross-tokenizer`, continuity command, T5 — User-owned real runs on v3 and the `lexical-v2` decision, Verification, Verification, _chunker_identity_differences(), _differences(), LexicalIndex (+6 more)

### Community 47 - "tokenizer.py"
Cohesion: 0.22
Nodes (10): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), Review, _is_token_char(), replace_sequences(), tokenize(), _tokenize_after_nfc(), _tokenize_v1(), _tokenize_v2() (+2 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.10
Nodes (28): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+20 more)

### Community 49 - "Stable command surface (target interface; implemented targets listed)"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_lexical_tokenizer.py"
Cohesion: 0.10
Nodes (5): test_chillu_pairs_tokenize_the_same_inside_and_at_end(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens(), test_module_has_no_language_code_literal(), test_nfd_equals_nfc()

### Community 51 - "HeadingChunker"
Cohesion: 0.09
Nodes (43): HeadingChunker, _is_word_char(), slugify(), assert_structure_chunks_whitespace_fidelity(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+35 more)

### Community 52 - "baseline.py"
Cohesion: 0.05
Nodes (48): Implementation, Implementation, Implementation, Review, Review, Review, T2 — round 1, T6 — round 1 (+40 more)

### Community 53 - "test_generation_eval.py"
Cohesion: 0.06
Nodes (32): Review, _config_copy(), _exact(), _factory(), _fixed_usage(), generation_run(), _golden(), _QueryRetriever (+24 more)

### Community 54 - "point_id"
Cohesion: 0.05
Nodes (34): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Acceptance criteria, Chunk, format_summary(), main(), _parser(), IngestionError, point_id() (+26 more)

### Community 55 - "BgeM3Embedder"
Cohesion: 0.12
Nodes (12): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+4 more)

### Community 56 - "DECISIONS.md architecture decision log"
Cohesion: 0.11
Nodes (29): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1, D008 Language and authorization are independent (+21 more)

### Community 57 - "test_config_schema_11.py"
Cohesion: 0.05
Nodes (57): Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, Acceptance criteria, Acceptance criteria (+49 more)

### Community 58 - "MonkeyPatch"
Cohesion: 0.19
Nodes (16): spy_lexical_path(), wrapper(), strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error(), test_cli_clause_less_lexical_store_exits_one_naming_strategies(), test_cli_harness_error_exits_two_and_writes_nothing(), test_cli_lexical_file_is_removed_after_a_failed_run(), failing() (+8 more)

### Community 59 - "ingestion.yaml"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "rendered_prompt"
Cohesion: 0.08
Nodes (47): Implementation, T4 — Answer service, citation validation and `make ask`, Verification, GeneratorUnavailableError, UnavailableReason, check_top_k(), resolve_retrieval_args(), ResolvedRetrievalArgs (+39 more)

### Community 62 - "FakeReranker"
Cohesion: 0.06
Nodes (24): Deviations from the approved plan, Implementation, T4 — round 1, User decision (2026-11-05), T2 — `RerankingRetriever`, skip policy and wiring, Verification, _AlwaysFailingScore, RerankerInfo (+16 more)

### Community 63 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 64 - "tests/conftest.py"
Cohesion: 0.14
Nodes (11): Verification run, Verification run, apply_hub_offline_empty_cache(), hub_offline_empty_cache(), _clear_opt_outs(), test_each_opt_out_alone_lifts_the_offline_setup(), test_offline_setup_applied_when_no_opt_out_is_set(), manifest_records() (+3 more)

### Community 65 - "transcript_metrics.py"
Cohesion: 0.14
Nodes (14): analyse(), category(), command_kinds(), executed_parts(), executed_text(), expand(), main(), parse_time() (+6 more)

### Community 66 - "make index-lexical"
Cohesion: 0.08
Nodes (32): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1) (+24 more)

### Community 67 - "evaluation/validate.py"
Cohesion: 0.18
Nodes (15): Review, _candidate_rules(), problem(), _describe(), _document_problems(), EvaluationProblem, _promotion_problems(), _read_rows() (+7 more)

### Community 68 - "test_manifest_validation.py"
Cohesion: 0.16
Nodes (24): ManifestValidationError, load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected() (+16 more)

### Community 69 - "check_hit"
Cohesion: 0.03
Nodes (120): Closed known issues and findings (moved 2026-11-07), Current goal as of 2026-11-07 (before the split), Former "Not yet implemented" entry (done), History, Implementation detail by spec (as merged), One-off: user-owned pre-merge check for Spec 004 (done 2026-10-17), Spec 002 decisions made before approval, Spec status table (full rows, as of 2026-11-07) (+112 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 72 - "LexicalIndexBindingError"
Cohesion: 0.09
Nodes (36): R4 — Freshness from the repository (`lexical/freshness.py`), LexicalIndexBindingError, build_production(), identity(), ingest_dense(), open_lexical(), payload(), repository() (+28 more)

### Community 73 - "typing"
Cohesion: 0.05
Nodes (26): R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), T2: where the shared pieces live (2026-10-31), Implementation, Implementation, Review, Review, T2 — round 1, T3 — round 1 (+18 more)

### Community 74 - "generation/config.py"
Cohesion: 0.06
Nodes (29): Implementation, Implementation, Review, T2 — round 1, T2 — round 2, User decision, AnthropicConfig, _check_cross_files() (+21 more)

### Community 75 - "Evaluation Suite (public-eval-v1)"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "test_rerank_eval.py"
Cohesion: 0.11
Nodes (34): NotComparableError, doc23(), _FieldSpy, go(), multi_chunk(), Reranked, reranked_run(), test_a_2_4_file_reads_as_not_reranked() (+26 more)

### Community 77 - "test_baseline.py"
Cohesion: 0.11
Nodes (22): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+14 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/validate.py"
Cohesion: 0.06
Nodes (27): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields() (+19 more)

### Community 80 - "pytest"
Cohesion: 0.15
Nodes (38): Implementation, Test changes (T3/T5b null-default assertions changed; each listed), build_generator(), load_generation_config(), GeneratorConfigurationError, test_config_requires_positive_values(), _load(), _raw() (+30 more)

### Community 81 - "test_verify_budget_hook.py"
Cohesion: 0.07
Nodes (7): hook_env(), _load_hook_module(), _run_settings_hook(), TestAgentAndBudget, TestRepoRoot, TestRunsBudgetedMake, TestSettingsHookCommand

### Community 82 - "retrieval.yaml"
Cohesion: 0.07
Nodes (32): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+24 more)

### Community 83 - "asyncio"
Cohesion: 0.07
Nodes (32): collect(), _document_ids(), collect(), _eligible_document_versions(), DocumentQuery, DocumentRepository, EligibilityPolicy, list_eligible_documents() (+24 more)

### Community 84 - "json"
Cohesion: 0.12
Nodes (17): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_dataset_types_loaded_by_type(), test_declared_release_id(), test_escaping_path_refused() (+9 more)

### Community 85 - "build_retriever"
Cohesion: 0.03
Nodes (78): Interfaces / models, Package / file placement, R1 — Failure classification (`errors.py`, `availability.py`), R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, 008 — Retrieval Fallback Tasks (+70 more)

### Community 86 - "rerank"
Cohesion: 0.09
Nodes (22): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+14 more)

### Community 87 - "Backend stack"
Cohesion: 0.07
Nodes (38): Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Backend stack, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency) (+30 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "roles"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "SQLite FTS5"
Cohesion: 0.18
Nodes (14): Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Lexical store, lexical-v1 tokens (D051), make index-lexical, One lexical file per access scope (future roles) (+6 more)

### Community 91 - "re"
Cohesion: 0.11
Nodes (16): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), _active_product_support_codes(), row(), test_absent_languages_from_a_temp_registry() (+8 more)

### Community 92 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.20
Nodes (12): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 10 - Grounded generation + citations, Roadmap 13 - Graceful degradation, Roadmap 14 - AWS deployment (+4 more)

### Community 93 - "Repository Structure"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec 001 project foundation"
Cohesion: 0.12
Nodes (19): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+11 more)

### Community 95 - "test_eligibility.py"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 96 - "OptionalDependencyError"
Cohesion: 0.07
Nodes (19): Next-step log (done items, as of 2026-11-07), Acceptance criteria, R2 — `bge-reranker-v2-m3` adapter and optional extra, User decision (2026-11-05), OptionalDependencyError, BgeRerankerV2M3, _extra_installed(), extra_installed() (+11 more)

### Community 97 - "Phase 2 - Knowledge Operations"
Cohesion: 0.15
Nodes (17): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+9 more)

### Community 98 - "CURRENT_STATE.md current state document"
Cohesion: 0.10
Nodes (36): standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open (+28 more)

### Community 99 - "healthcheck"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "read_result"
Cohesion: 0.20
Nodes (8): read_result(), test_2_2_bm25_without_a_lexical_object_is_refused(), test_committed_1_0_versus_2_0_passes_with_identity_rules(), test_committed_baseline_compared_with_itself_passes(), test_cross_tokenizer_still_refuses_digest_mismatch(), test_make_eval_compare_cross_index_prints_chunker(), test_tokenizer_change_accepted_with_cross_tokenizer(), test_unreadable_and_malformed_files()

### Community 102 - "test_anthropic_api.py"
Cohesion: 0.11
Nodes (27): _config(), _fake_sdk(), factory(), _generator(), _key(), OptionsStub, _reply(), test_auth_token_alone_is_not_a_credential() (+19 more)

### Community 103 - "BGE-M3 embeddings"
Cohesion: 0.18
Nodes (11): docker compose up -d / down (local Qdrant), Device not pinned, recorded in results (D038), Embeddings, Deterministic fake embedder, AWS deployment architecture (ap-south-1), BGE-M3 embeddings, CI/CD pipeline, Multilingual design (lote_languages) (+3 more)

### Community 104 - "Task-gated agent workflow loop"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.22
Nodes (3): OddIdStore, SpyIndex, test_violation_names_the_document_from_the_error_attribute()

### Community 106 - "Engineering Conventions"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "ChunkerIdentity"
Cohesion: 0.06
Nodes (33): User decision, 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7) (+25 more)

### Community 108 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.16
Nodes (15): FakeEmbedder, _fake_embedder(), _cosine_to_query(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size() (+7 more)

### Community 110 - "safe_text"
Cohesion: 0.08
Nodes (23): Acceptance criteria, _build_run(), default_output_path(), _mixed(), _num(), _rerank_fields(), _served_strategy(), _unreadable() (+15 more)

### Community 111 - "Mock assessments, scoring, feedback and review windows"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "012 — Grounded Generation Requirements"
Cohesion: 0.05
Nodes (41): 012 — Grounded Generation Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+33 more)

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
Cohesion: 0.13
Nodes (16): AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Derived retrieval index in Qdrant, EBS, EC2, Generation, IAM (+8 more)

### Community 118 - "FallbackRetriever"
Cohesion: 0.07
Nodes (31): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+23 more)

### Community 119 - "load_retrieval_config"
Cohesion: 0.08
Nodes (38): Implementation (user-owned runs + agent wrap-up), Review, Review, T5 — round 1, User decision, Implementation, Review, Spec 011 — task reviews (+30 more)

### Community 120 - "IngestionService"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "Knowledge Schema and Metadata"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "Spec 012 — task reviews"
Cohesion: 0.06
Nodes (28): Commands as run by the user (2026-11-13, on `a0869a5`, clean tree), D-A smoke-test findings so far (user-run, 2026-11-07; results to follow), Implementation, Implementation, Implementation, Known issues recorded (verified against the result files and dataset), Recorded elsewhere, Result-file checks (agent, from the JSON) (+20 more)

### Community 123 - "graphify_guard.py"
Cohesion: 0.18
Nodes (8): is_non_code(), main(), _repo_root(), search_targets(), skip_nudge(), simple_commands(), _strip_wrappers(), _substitutions()

### Community 124 - "QdrantIndexStore"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 125 - "Baseline runner and result JSON"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

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
Cohesion: 0.27
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 133 - "EligibilityPolicy / GUEST_PUBLIC_POLICY"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - "Product Context"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "test_local_repository.py"
Cohesion: 0.30
Nodes (13): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+5 more)

### Community 136 - "verify_budget.py"
Cohesion: 0.17
Nodes (13): agent_key(), _budget(), count_run(), decide(), _dedupe_window_s(), in_repo(), _load_counts(), log() (+5 more)

### Community 137 - "test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote"
Cohesion: 0.14
Nodes (6): _DefectiveStage, DroppedLoteClauseLexical, test_dropped_applicability_filter_reports_applicability_not_authorization(), test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote(), defective(), defective()

### Community 138 - "NAATI CCL test format, scoring and results"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_open_retrieval_bm25_builds_no_embedder_and_no_client"
Cohesion: 0.29
Nodes (4): block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 140 - "Roadmap 12 - Security"
Cohesion: 0.25
Nodes (8): Authorization regression and staff canary, BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline, Roadmap 12 - Security, Prompt injection and poisoned retrieved content tests, Public access filter

### Community 141 - "Evaluation Package (evaluation/)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "eval-retrieval"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.07
Nodes (36): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+28 more)

### Community 144 - "Phase 0 - Project bootstrap"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make eval-compare"
Cohesion: 0.15
Nodes (14): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+6 more)

### Community 147 - "Evaluation Framework Goal"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Versioning and Releases"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_cli_config.py"
Cohesion: 0.15
Nodes (19): clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file(), test_exit_0_then_idempotent_second_run() (+11 more)

### Community 150 - "test_security_eval.py"
Cohesion: 0.09
Nodes (7): clean_env(), _lexical_work_dir(), new_base(), seed_repository(), test_builder_refuses_a_real_embedder_identity(), __init__(), test_the_harness_reranker_failures_use_the_fake_reranker_switches()

### Community 151 - "Spec 004 retrospective round 1 (PASS)"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

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
Cohesion: 0.06
Nodes (49): As-built notes, Package / file placement, Security / authorization, Implementation, Review, T4 — round 1, User decision, T4 — BM25 retriever and SQL access clause (+41 more)

### Community 156 - "T6 — real runs recorded (round 1, stage 2)"
Cohesion: 0.10
Nodes (18): A. Result-file checks (agent, from the files), Approved thresholds and choice rule (user, 2026-11-13, verbatim), B. Refusal breakdown (status, reason, sub_reason), C. Deadline: generation 32 s against `deadline_s: 30`, Commands as run (correction), Cost estimate (cost guard's own logic, no network), D. Spot check, Implementation (+10 more)

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

### Community 169 - "test_graphify_guard.py"
Cohesion: 0.15
Nodes (4): test_settings_uses_wrapper(), TestMain, TestSimpleCommands, TestSkipNudge

### Community 170 - "Canonical document metadata"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "write"
Cohesion: 0.18
Nodes (18): _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _identity_refusals(), _info_lines(), _load_raw(), _lote_label() (+10 more)

### Community 192 - "security_eval.py"
Cohesion: 0.05
Nodes (56): Change log, Implementation, Implementation, Review, Review, T8 — round 1, T9 — round 1, User decision (+48 more)

### Community 193 - "os"
Cohesion: 0.12
Nodes (3): _no_aws_environment(), _no_aws_environment(), _no_aws_environment()

### Community 194 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 195 - "open_retrieval"
Cohesion: 0.07
Nodes (22): Implementation, T1 — round 1, User decision, Notes for the retrospective, T3 — `bm25` without Qdrant or the `bge-m3` extra; one open path, Verification, Notes for the next spec, Final handoff (+14 more)

### Community 196 - "test_content_hash.py"
Cohesion: 0.11
Nodes (23): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), sha256_hex(), manifest_document_count(), _copy_seed() (+15 more)

### Community 197 - "documents/models.py"
Cohesion: 0.20
Nodes (6): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, test_guest_policy_agrees_with_access_policy_config()

### Community 198 - "make retrieve"
Cohesion: 0.14
Nodes (15): make retrieve, resolve_access (only role-to-policy mapping), ResolvedAccess(policy, tenant_id), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Hybrid hit lines show per-leg ranks dense=<rank|-> bm25=<rank|->; truncation note above 64 distinct terms, Lexical file <W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite (default .local/lexical, git-ignored), No option for role, scope or tenant; access is always guest/public for W2A_TENANT_ID, QUERY variable (+7 more)

### Community 199 - "FakeGenerator"
Cohesion: 0.06
Nodes (58): Alternatives / deferred decisions, Implementation, Review, Review, T5 — round 3, User decision, AccessContext, test_blank_tenant_refused() (+50 more)

### Community 201 - "Spec 010 — task reviews"
Cohesion: 0.12
Nodes (16): Implementation, Implementation, Implementation, Implementation, Implementation, Spec 010 — task reviews, T2 — round 1, T2 — round 2 (+8 more)

### Community 202 - "check_target_allowed"
Cohesion: 0.21
Nodes (12): Implementation, T3 — round 3, User decision, check_target_allowed(), LexicalTargetRefusedError, _git_repo(), test_default_location_is_allowed(), test_differently_cased_protected_name_is_refused() (+4 more)

### Community 203 - "chunking.py"
Cohesion: 0.09
Nodes (28): Implementation, _char_split(), _merge_pieces(), _merge_word_pieces(), _parse_sections(), _Section, split_at_sentence_ends(), _split_body() (+20 more)

### Community 205 - "test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it"
Cohesion: 0.25
Nodes (3): test_a_forbidden_hit_injected_after_the_stage_fails_each_rerank_path(), test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), injecting()

### Community 206 - "DocumentRepository"
Cohesion: 0.13
Nodes (15): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Document manifest, DocumentRepository (+7 more)

### Community 207 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 208 - "build_security_index"
Cohesion: 0.17
Nodes (6): build_security_index(), _forbidden_payload(), _lexical_forbidden_entries(), _lexical_non_applicable_entries(), _non_applicable_payload(), require_security_base()

### Community 210 - "Spec 005 dense retrieval baseline"
Cohesion: 0.10
Nodes (31): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role (+23 more)

### Community 211 - "live_suite_rows"
Cohesion: 0.20
Nodes (10): Implementation, Review, T3 — round 1, live_suite_rows(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries() (+2 more)

### Community 212 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.10
Nodes (23): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed (+15 more)

### Community 213 - "test_suite_v4.py"
Cohesion: 0.24
Nodes (7): manifest(), rows(), test_candidate_decisions_and_promotions(), test_v3_dataset_files_match_their_committed_hashes(), test_v3_manifest_differs_from_v4_lineage_only_in_status(), test_v3_rows_equal_their_v4_copy_except_suite_id(), test_v4_manifest_counts_and_lineage()

### Community 214 - "Round 1 — 2026-11-04"
Cohesion: 0.17
Nodes (11): 010 — Multilingual Retrieval: Retrospective Review, Deviations from the approved plan, Documentation reconciled, Final handoff, Findings, Notes for the next spec, Patterns in `task-reviews.md`, Protected-data check (+3 more)

### Community 215 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 216 - "dense_equivalence.py"
Cohesion: 0.24
Nodes (4): deterministic_clock(), equivalence_suite(), chunks_per_document_dense(), unanswerable()

### Community 217 - "Review"
Cohesion: 0.20
Nodes (6): Implementation, Review, Review, T3 — round 2, _group_installed(), test_default_embedder_identity_equals_the_bge_m3_adapter_identity()

### Community 218 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.20
Nodes (9): 007 — Hybrid Retrieval Tasks, Notes for the retrospective, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Verification (+1 more)

### Community 219 - "subprocess"
Cohesion: 0.22
Nodes (6): _inside_git_work_tree(), _is_git_ignored(), test_importing_the_module_does_not_import_the_sdk(), test_the_import_recorder_catches_an_sdk_import_attempt(), test_no_pytorch_import(), test_bm25_path_imports_neither_the_model_adapter_nor_the_model_stack()

### Community 220 - "T6 — suite v4 (round 1, stage 4)"
Cohesion: 0.22
Nodes (9): Commands for the user (not run by the agent), Implementation, Open items before the T6 task review, Owner and fluent-speaker review, 2026-11-13 (user decisions, verbatim), Suite v4 contents, T6 — suite v4 (round 1, stage 4), Test changes (each listed), User decisions (2026-11-13, after stage 4) (+1 more)

### Community 223 - "versions"
Cohesion: 0.29
Nodes (6): schema_version, versions, files, prompt_id, prompt_version, sha256

### Community 224 - "D049 Suite public-eval-v2 and the closed v1 reference (Spec 007)"
Cohesion: 0.29
Nodes (7): D049 Suite public-eval-v2 and the closed v1 reference (Spec 007), suite public-eval-v2, Acceptance criteria, R13 strategy comparison and default-strategy rule, R1 Evaluation Suite public-eval-v2 (91 cases), R2 — v2 dense baseline (user-owned gate), T9 strategy comparison and default-strategy decision

### Community 225 - "RetrievalConfigurationError"
Cohesion: 0.08
Nodes (27): Error and failure behavior, Acceptance criteria, Acceptance criteria, Error and failure behavior, Interfaces / models, 011 — Multilingual Reranking Design, Alternatives / deferred decisions, Components / boundaries (+19 more)

### Community 226 - "test_both_lote_modes_on_every_path_and_chunker"
Cohesion: 0.13
Nodes (8): test_both_lote_modes_on_every_path_and_chunker(), counting(), test_every_path_is_gated_for_every_query(), counting(), test_rerank_paths_pass_over_every_chunker_in_both_lote_modes(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

### Community 227 - "T1 — round 1"
Cohesion: 0.67
Nodes (3): Implementation, T1 — round 1, User decision

### Community 228 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 229 - "retrieval_eval.py"
Cohesion: 0.06
Nodes (40): Implementation, Review, T5 — round 1, User decision, T5 — Evaluation result 2.2 and `eval-compare` by served strategy, Verification, Implementation, Review (+32 more)

### Community 230 - "Roadmap 11 - Observability"
Cohesion: 0.33
Nodes (6): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, Amazon CloudWatch, Langfuse, Observability

### Community 236 - "query_terms"
Cohesion: 0.40
Nodes (3): query_terms(), _query_terms_from(), QueryTerms

### Community 237 - "test_changed_unanswerable_field_is_a_problem_without_text"
Cohesion: 0.47
Nodes (4): edit_jsonl(), root(), test_changed_unanswerable_field_is_a_problem_without_text(), change()

### Community 241 - "test_a_rerank_path_that_fell_back_is_a_harness_error"
Cohesion: 0.50
Nodes (3): test_a_plain_hybrid_path_that_falls_back_is_a_harness_error(), falling_back(), test_a_rerank_path_that_fell_back_is_a_harness_error()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-rag`, `way2australia-core`, `way2australia`, `way2australia-api`, `way2australia-observability` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1888 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `D055 Default strategy is hybrid (Spec 007)` to `Spec 007 hybrid retrieval`, `Spec 006 evaluation framework`, `retrieval.yaml`, `DECISIONS.md architecture decision log`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `LocalDocumentRepository` (e.g. with `Implementation detail by spec (as merged)` and `Dependencies`) actually correct?**
  _`LocalDocumentRepository` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-rag`, `way2australia-core`, `way2australia` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12480169222633528 - nodes in this community are weakly interconnected._
- **Why does `Change log` connect `security_eval.py` to `check_hit`, `retrieval_eval.py`, `check_target_allowed`, `compare.py`, `LexicalIndex`, `DenseRetriever`, `D055 Default strategy is hybrid (Spec 007)`, `007 — Hybrid Retrieval Requirements`, `MonkeyPatch`, `ResolvedAccess`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `DenseIndex` (e.g. with `Implementation detail by spec (as merged)` and `Spec status table (full rows, as of 2026-11-07)`) actually correct?**
  _`DenseIndex` has 87 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._