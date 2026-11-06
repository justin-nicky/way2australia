# Graph Report - way2australia  (2026-11-06)

## Corpus Check
- 327 files · ~379,486 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 5277 nodes · 16338 edges · 223 communities (186 shown, 37 thin omitted)
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 3715 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e83762af`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- hashing.py
- test_fallback.py
- DenseIndex
- test_validate.py
- test_reranking.py
- test_applicability.py
- test_index.py
- test_opening_rerank.py
- Factory
- FakeTokenizer
- FakeTokenizer
- HeadingChunker
- compare.py
- test_lexical_cli.py
- test_suite_v2.py
- CURRENT_STATE.md current state document
- test_availability.py
- QdrantIndexStore
- test_retriever.py
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- tokenizer.py
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- validate_evaluation
- way2australia_api/config.py
- IngestionConfigurationError
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- test_lexical_standalone.py
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- repositories/__init__.py
- KnowledgeDocument
- test_legacy_baseline_snapshot.py
- typing
- EvaluationConfigurationError
- Workflow Reviewer
- LocalDocumentRepository
- dense
- test_cli_config.py
- pytest
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- test_lexical_tokenizer.py
- HeadingChunker
- retrieval_eval.py
- FallbackRetriever
- IndexSettings
- BgeM3Embedder
- Development Workflow
- LocalRepositoryConfig
- test_security_eval.py
- json
- Evaluation Phase 1 framework (Spec 006)
- test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote
- FakeReranker
- make eval-retrieval
- hub_offline_empty_cache
- lexical_support.py
- make index-lexical
- Spec 007 hybrid retrieval
- test_manifest_validation.py
- RetrievalConfigurationError
- embedder
- Phase 1 RAG query pipeline
- test_lexical_build.py
- 008 — Retrieval Fallback Requirements
- ChunkerIdentity
- Section: Next step
- test_rerank_eval.py
- test_baseline.py
- embedder
- repositories/__init__.py
- hashlib
- test_verify_budget_hook.py
- Ingestion pipeline (Spec 004)
- test_recursive.py
- pytest
- open_retrieval
- rerank
- Backend stack
- embedder
- D023 Task-gated agent workflow
- guest_access
- re
- Roadmap 10 - Grounded generation + citations
- pathlib
- Spec status table
- test_eligibility.py
- test_rerank_bge.py
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- read_result
- test_structure.py
- make retrieve
- Retrieval package (Spec 005 and 007)
- Qdrant (vector database)
- subprocess
- Development Workflow
- FakeEmbedder
- evaluation/cli.py
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- security_corpus.py
- test_repository_contract.py
- fusion
- AWS target
- SpyIndex
- test_index_contract.py
- failing_client
- test_status_handling.py
- test_qdrant_client.py
- ingestion/config.py
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- sync_agent_skills.py
- Vocabulary, flashcards and free access
- .search
- asyncio
- verify_budget.py
- Any
- Evaluation Framework Goal
- test_opening.py
- Phase 1 - Production-oriented RAG
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Retrieval fallback (Spec 008, D056-D062)
- eval-compare
- Payments, account access and support boundaries
- make retrieve
- make test
- Mission
- script_mix
- documents/__init__.py
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- Strategy
- test_cli_config.py
- baseline.py
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- test_schemas.py
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- dense_equivalence.py
- DocumentRepository Protocol (async)
- tests/evaluation/__init__.py
- tests/retrieval/__init__.py
- way2australia-api
- way2australia-observability
- stalled_port
- Retrospective verdict PASS
- way2australia-core
- .document_count
- Spec-driven development workflow
- D025 persona_scope informational
- T9 deviation: git_dirty true in BM25 and hybrid result files
- way2australia
- way2australia-api
- way2australia-observability
- continuity.py
- security_eval.py
- AccessContext
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- R8 — Evaluation results for degraded runs
- live_suite_rows
- Round 1 — 2026-11-04
- test_both_lote_modes_on_every_path_and_chunker
- ShortResultEmbedder
- policy
- open_retrieval / OpenedRetrieval
- test_non_guest_roles_refused
- CountingEmbedder
- ResolvedLote
- test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it
- DocumentRepository
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- test_store_integration.py
- test_hybrid.py
- Evaluation result format 2.2
- TestRunsBudgetedMake
- Review
- Spec 011 — task reviews
- CountingStore
- Authorization enforced before generation
- R12 — Real runs (user-owned gate)
- TestAgentAndBudget
- Roadmap 3 - Ingestion baseline
- Spec 008 Retrieval Fallback Requirements
- IndexedDocument
- stalled_port
- memory_client

## God Nodes (most connected - your core abstractions)
1. `LocalDocumentRepository` - 120 edges
2. `DenseIndex` - 113 edges
3. `Strategy` - 93 edges
4. `RetrievalConfigurationError` - 92 edges
5. `open_retrieval()` - 88 edges
6. `ResolvedAccess` - 87 edges
7. `DenseRetriever` - 83 edges
8. `run_retrieval_evaluation()` - 82 edges
9. `FakeTokenizer` - 79 edges
10. `FakeEmbedder` - 75 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Acceptance criteria` --references--> `script_mix()`  [INFERRED]
  .kiro/specs/010-multilingual-retrieval/requirements.md → packages/rag/src/way2australia_rag/evaluation/script_mix.py
- `Interfaces / models` --references--> `Chunk`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py

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

## Communities (223 total, 37 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.12
Nodes (57): case(), doc(), doc21(), doc22(), ranked(), refusal(), run(), run_cross() (+49 more)

### Community 1 - "hashing.py"
Cohesion: 0.14
Nodes (19): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_content_hash(), _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null() (+11 more)

### Community 2 - "test_fallback.py"
Cohesion: 0.08
Nodes (37): Acceptance criteria, R7 — Marking degraded results, Implementation, Review, T4 — round 1, User decision, T4 — Fallback policy for `hybrid` and result marking, Verification (+29 more)

### Community 3 - "DenseIndex"
Cohesion: 0.16
Nodes (23): LexicalRow, DenseIndex, build(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+15 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_reranking.py"
Cohesion: 0.06
Nodes (49): 011 — Multilingual Reranking Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+41 more)

### Community 6 - "test_applicability.py"
Cohesion: 0.17
Nodes (27): active_lote_codes(), build_lexical(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical, _fallback_query_primary(), retrieve(), guest() (+19 more)

### Community 7 - "test_index.py"
Cohesion: 0.10
Nodes (43): EmbedderInfo, IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings() (+35 more)

### Community 8 - "test_opening_rerank.py"
Cohesion: 0.12
Nodes (22): access(), MustNotBuild, open_with(), RecordingFactory, retrieval_config(), run(), test_cli_no_rerank_builds_nothing(), test_cli_prints_rerank_off_with_no_rerank() (+14 more)

### Community 9 - "Factory"
Cohesion: 0.15
Nodes (24): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+16 more)

### Community 10 - "FakeTokenizer"
Cohesion: 0.05
Nodes (51): Implementation, Implementation, Review, Review, Review, T2 — round 2, T2 — round 3, User decision (+43 more)

### Community 11 - "FakeTokenizer"
Cohesion: 0.04
Nodes (73): Acceptance criteria, Acceptance criteria, R3 — Lexical index without Qdrant, R4 — Freshness check from the repository, T2 — Index identity, standalone lexical open and freshness check, Verification, As-built notes, Carry-over clean-ups (R11) (+65 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.08
Nodes (45): test_a_reranker_without_the_flag_or_depth_is_refused(), test_reranking_off_has_null_identity_and_no_rerank_unanswerable_keys(), test_unanswerable_rerank_distributions_are_informational(), basic_suite(), build(), default_eval_extras(), fusion_config(), golden() (+37 more)

### Community 13 - "compare.py"
Cohesion: 0.12
Nodes (35): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+27 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.20
Nodes (20): lexical_dir(), _no_qdrant(), run(), test_bad_config_exits_2(), test_cased_name_cannot_write_into_the_real_repository(), test_env_dir_into_tracked_directory_is_refused(), test_file_holds_the_identity_and_no_chunk_text_is_printed(), test_lexical_location_is_git_ignored() (+12 more)

### Community 15 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "CURRENT_STATE.md current state document"
Cohesion: 0.09
Nodes (40): RetrievalUnavailableError and availability classification, CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: verify_fresh asyncio.run in event loop, Known issue: Qdrant client lifecycle leak on failed open, Known issue: freshness check rereads every document (+32 more)

### Community 17 - "test_availability.py"
Cohesion: 0.07
Nodes (35): R1 — Failure classification (`errors.py`, `availability.py`), R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, Review, 008 — Retrieval Fallback Tasks, T1 — Failure classification and Qdrant timeouts, Verification (+27 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.17
Nodes (22): QdrantIndexStore, client_factory(), client(), test_replace_and_delete_flows(), make_points(), make_settings(), snapshot(), store() (+14 more)

### Community 19 - "test_retriever.py"
Cohesion: 0.07
Nodes (30): IndexPoint, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), build_client(), docs(), guest() (+22 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (33): D049 Suite public-eval-v2 and the closed v1 reference (Spec 007), suite public-eval-v2, 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+25 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.08
Nodes (51): Implementation, Implementation, Implementation, Review, Review, Review, Spec 010 — task reviews, T3 — round 1 (+43 more)

### Community 22 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.09
Nodes (31): DenseIndex, build_access_filter, check_hit, DenseRetriever, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, BM25Retriever, build_access_filter, check_hit fail-closed re-check (+23 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.08
Nodes (31): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, LocalDocumentRepository with manifest schema validation, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings (+23 more)

### Community 26 - "tokenizer.py"
Cohesion: 0.19
Nodes (10): _is_token_char(), query_terms(), _query_terms_from(), QueryTerms, replace_sequences(), _tokenize_after_nfc(), _tokenize_v1(), _tokenize_v2() (+2 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.12
Nodes (29): Implementation, Review, T1 — round 1, User decision, candidate_row(), candidates(), edit_jsonl(), errors() (+21 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.09
Nodes (36): Review, User decision, User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world() (+28 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "validate_evaluation"
Cohesion: 0.09
Nodes (23): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+15 more)

### Community 31 - "way2australia_api/config.py"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 32 - "IngestionConfigurationError"
Cohesion: 0.06
Nodes (29): Chunk, build_embedder(), format_summary(), main(), _parser(), IngestionConfigurationError, IngestionError, check_chunks() (+21 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.18
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (28): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 35 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+11 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "repositories/__init__.py"
Cohesion: 0.07
Nodes (7): _check_language_code(), KnowledgeDocument, DocumentQuery, EligibilityPolicy, DocumentNotFoundError, ListRepository, IgnoresQueryRepository

### Community 39 - "KnowledgeDocument"
Cohesion: 0.19
Nodes (24): doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text(), test_chunker_exception_is_per_document_failure() (+16 more)

### Community 40 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.12
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 41 - "typing"
Cohesion: 0.10
Nodes (29): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+21 more)

### Community 42 - "EvaluationConfigurationError"
Cohesion: 0.09
Nodes (23): T5 — Evaluation result 2.2 and `eval-compare` by served strategy, Verification, EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase (+15 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.16
Nodes (23): User decision, LocalDocumentRepository, build(), real_queries(), test_a_skip_path_that_records_no_skip_fails_the_gate(), test_access_only_sanity_requires_non_applicable_first(), test_builder_refuses_a_non_throwaway_base_before_any_write(), test_builder_refuses_an_existing_collection() (+15 more)

### Community 45 - "dense"
Cohesion: 0.07
Nodes (30): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), R9 — Result format 2.1, Acceptance criteria (+22 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.20
Nodes (11): _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_exit_1_on_document_failure(), test_exit_2_when_optional_group_missing_writes_nothing(), test_exit_2_when_qdrant_unreachable(), test_repository_error_message_is_printed_without_paths() (+3 more)

### Community 47 - "pytest"
Cohesion: 0.11
Nodes (23): NotComparableError, read_result(), test_2_2_bm25_without_a_lexical_object_is_refused(), test_2_2_file_with_only_unanswerable_cases_served_differently_is_refused(), test_committed_1_0_versus_2_0_passes_with_identity_rules(), test_cross_tokenizer_still_refuses_digest_mismatch(), test_duplicate_case_id_is_refused(), test_unreadable_and_malformed_files() (+15 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.10
Nodes (28): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+20 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_lexical_tokenizer.py"
Cohesion: 0.09
Nodes (7): test_no_language_literal_in_evaluation_code(), test_no_malayalam_specific_lote_languages_in_ingestion_code(), test_chillu_pairs_tokenize_the_same_inside_and_at_end(), test_golden_file_is_the_source_of_the_pins(), test_golden_queries_pin_exact_tokens(), test_module_has_no_language_code_literal(), test_v2_matches_v1_without_listed_sequences()

### Community 51 - "HeadingChunker"
Cohesion: 0.11
Nodes (27): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order(), test_duplicate_suffix_does_not_collide_with_literal_heading() (+19 more)

### Community 52 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (49): R8 — Result format 2.2 (`retrieval_eval.py`), Implementation, Review, T5 — round 1, User decision, Implementation, Review, T4 — round 1 (+41 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.15
Nodes (14): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed) (+6 more)

### Community 54 - "IndexSettings"
Cohesion: 0.11
Nodes (7): IndexSettingsMismatchError, build_index_settings(), IndexSettings, read_index_settings(), test_index_settings_1_0_upgrades_in_memory(), live_client(), test_collection_with_1_0_settings_still_binds()

### Community 55 - "BgeM3Embedder"
Cohesion: 0.10
Nodes (14): BgeM3Embedder, OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction() (+6 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (30): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+22 more)

### Community 57 - "LocalRepositoryConfig"
Cohesion: 0.04
Nodes (51): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, What happens to existing lexical files (user request) (+43 more)

### Community 58 - "test_security_eval.py"
Cohesion: 0.14
Nodes (10): clean_env(), _lexical_work_dir(), new_base(), seed_repository(), strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error(), test_builder_refuses_a_real_embedder_identity(), __init__() (+2 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote"
Cohesion: 0.50
Nodes (3): test_the_post_rerank_applicability_recheck_fails_closed_with_a_lote(), defective(), defective()

### Community 62 - "FakeReranker"
Cohesion: 0.03
Nodes (77): 011 — Multilingual Reranking Design, Alternatives / deferred decisions, As-built notes, Components / boundaries, Data flow, Error and failure behavior, Interfaces / models, Latency scaling (+69 more)

### Community 63 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 64 - "hub_offline_empty_cache"
Cohesion: 0.16
Nodes (8): Verification run, Verification run, apply_hub_offline_empty_cache(), hub_offline_empty_cache(), security_repository(), _clear_opt_outs(), test_each_opt_out_alone_lifts_the_offline_setup(), test_offline_setup_applied_when_no_opt_out_is_set()

### Community 65 - "lexical_support.py"
Cohesion: 0.15
Nodes (13): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+5 more)

### Community 66 - "make index-lexical"
Cohesion: 0.08
Nodes (32): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1) (+24 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.07
Nodes (39): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty) (+31 more)

### Community 68 - "test_manifest_validation.py"
Cohesion: 0.18
Nodes (23): load_manifest(), load_schema(), validate_manifest(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected() (+15 more)

### Community 69 - "RetrievalConfigurationError"
Cohesion: 0.07
Nodes (39): Design summary, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Change log, Implementation, Implementation, Implementation, Review, Review (+31 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 72 - "test_lexical_build.py"
Cohesion: 0.20
Nodes (19): identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings(), test_build_records_tokenizer_name() (+11 more)

### Community 73 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.12
Nodes (17): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Decisions resolved before drafting (+9 more)

### Community 74 - "ChunkerIdentity"
Cohesion: 0.06
Nodes (25): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Chunker identity, settings and configuration (R5), Components / boundaries, Data flow, Design summary, Distinct-document metrics (R7), Error and failure behavior (+17 more)

### Community 75 - "Section: Next step"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "test_rerank_eval.py"
Cohesion: 0.12
Nodes (31): doc23(), _FieldSpy, go(), multi_chunk(), reranked_run(), test_a_2_4_file_reads_as_not_reranked(), test_a_2_4_reference_compares_with_a_2_5_arm_across_index(), test_a_chunker_difference_is_still_refused_in_every_multi_chunk_pair() (+23 more)

### Community 77 - "test_baseline.py"
Cohesion: 0.10
Nodes (24): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+16 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "repositories/__init__.py"
Cohesion: 0.05
Nodes (32): build_security_repository(), _fixture_files(), DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader (+24 more)

### Community 80 - "hashlib"
Cohesion: 0.29
Nodes (8): load_suite(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused(), tree_hashes(), write_suite()

### Community 81 - "test_verify_budget_hook.py"
Cohesion: 0.23
Nodes (5): hook_env(), _load_hook_module(), _run_settings_hook(), TestRepoRoot, TestSettingsHookCommand

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.07
Nodes (28): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+20 more)

### Community 83 - "test_recursive.py"
Cohesion: 0.14
Nodes (21): _authority_map(), collect(), list_eligible_documents(), assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), assert_structure_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace() (+13 more)

### Community 84 - "pytest"
Cohesion: 0.27
Nodes (12): guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload(), test_check_hit_rejects_violations() (+4 more)

### Community 85 - "open_retrieval"
Cohesion: 0.04
Nodes (63): 008 — Retrieval Fallback Design, As-built notes, Components / boundaries, Data flow, Decisions D056-D062, Spec 008 Retrieval Fallback Design, Interfaces / models, Observability (+55 more)

### Community 86 - "rerank"
Cohesion: 0.09
Nodes (22): default_strategy, fusion, candidate_depth, k, method, weights, lexical, tokenizer (+14 more)

### Community 87 - "Backend stack"
Cohesion: 0.07
Nodes (38): Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Backend stack, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency) (+30 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "guest_access"
Cohesion: 0.24
Nodes (14): guest_access(), run_gate(), security_result(), spied(), test_a_filter_dropping_index_fails_the_gate(), test_a_forbidden_candidate_is_never_returned_even_when_the_reranker_prefers_it(), test_case_access_context_never_changes_the_filter(), test_filter_is_identical_for_every_query_including_after_s003() (+6 more)

### Community 91 - "re"
Cohesion: 0.11
Nodes (15): Implementation, Review, T2 — round 1, User decision, absent_query_languages(), aggregate(), _mean(), slice_by() (+7 more)

### Community 92 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.20
Nodes (12): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 10 - Grounded generation + citations, Roadmap 13 - Graceful degradation, Roadmap 14 - AWS deployment (+4 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.09
Nodes (26): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), Pydantic document models and enums, GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches (+18 more)

### Community 95 - "test_eligibility.py"
Cohesion: 0.20
Nodes (16): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+8 more)

### Community 96 - "test_rerank_bge.py"
Cohesion: 0.07
Nodes (31): extra_installed(), failing(), raised(), test_missing_extra_at_load(), test_missing_extra_is_refused_naming_the_setup_command(), test_network_failure_at_load_becomes_a_skip_with_the_cause_chain(), test_offline_not_cached_is_a_configuration_error_with_advice(), test_refuses_missing_or_floating_revision() (+23 more)

### Community 97 - "SpyIndex"
Cohesion: 0.19
Nodes (14): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+6 more)

### Community 98 - "transcript_metrics.py"
Cohesion: 0.17
Nodes (12): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+4 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "read_result"
Cohesion: 0.19
Nodes (8): _build_run(), default_output_path(), _mixed(), _num(), _rerank_fields(), _served_strategy(), _unreadable(), write_document()

### Community 102 - "test_structure.py"
Cohesion: 0.22
Nodes (19): make_document(), structure_chunker(), test_duplicate_sibling_headings_raise(), test_fence_blocks_are_atomic_and_headings_inside_ignored(), test_long_list_splits_only_between_items(), test_main_collision_with_heading_slug(), test_malayalam_paragraph_packs(), test_malayalam_paragraph_splits_when_over_cap() (+11 more)

### Community 103 - "make retrieve"
Cohesion: 0.11
Nodes (20): make retrieve, resolve_access (only role-to-policy mapping), ResolvedAccess(policy, tenant_id), docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Hybrid hit lines show per-leg ranks dense=<rank|-> bm25=<rank|->; truncation note above 64 distinct terms, Lexical file <W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite (default .local/lexical, git-ignored), No option for role, scope or tenant; access is always guest/public for W2A_TENANT_ID (+12 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "subprocess"
Cohesion: 0.16
Nodes (15): Implementation, Review, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree(), _is_git_ignored(), LexicalTargetRefusedError (+7 more)

### Community 108 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.16
Nodes (15): FakeEmbedder, _cosine_to_query(), test_run_retrieval_evaluation_on_multi_chunk_recursive_index(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64() (+7 more)

### Community 110 - "evaluation/cli.py"
Cohesion: 0.08
Nodes (24): _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _rerank_lines(), _security(), _unanswerable_line() (+16 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.13
Nodes (20): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, EligibilityPolicy for guest/public, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline (+12 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "security_corpus.py"
Cohesion: 0.15
Nodes (20): SecurityIndex, copy_fixtures(), spy_lexical_path(), wrapper(), test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(), test_a_plain_hybrid_path_that_falls_back_is_a_harness_error(), falling_back(), test_a_rerank_path_that_fell_back_is_a_harness_error() (+12 more)

### Community 115 - "test_repository_contract.py"
Cohesion: 0.26
Nodes (8): InMemoryDocumentRepository, make_document(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters(), test_query_matches_is_the_single_language_and_scope_rule(), use_repository()

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "AWS target"
Cohesion: 0.05
Nodes (42): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Local multilingual BGE reranker, BM25 via FTS5 bm25() (+34 more)

### Community 118 - "SpyIndex"
Cohesion: 0.25
Nodes (3): OddIdStore, SpyIndex, broken()

### Community 119 - "test_index_contract.py"
Cohesion: 0.12
Nodes (17): compare(), mismatch_message(), base_settings(), test_authorization_and_language_fields_are_separate(), test_build_index_settings_records_embedder_and_chunker(), test_build_payload_copies_document_and_chunk(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract() (+9 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 123 - "ingestion/config.py"
Cohesion: 0.11
Nodes (26): Package / file placement, Implementation, Implementation, Review, T3 — round 2, User decision, T3 — Configuration, index settings, lexical identity and per-document freshness, T4 — Distinct-document metrics, result 2.3 and cross-index compare (+18 more)

### Community 124 - "QdrantIndexStore"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 125 - "Baseline runner and result JSON"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 126 - "test_failed_write_removes_partial_file"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 127 - "Development Workflow"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 128 - "test_status_handling.py"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 129 - "absent_query_languages"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 130 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.12
Nodes (19): BM25, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases, HitRate@5, Roadmap 1 - Project foundation, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval (+11 more)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "sync_agent_skills.py"
Cohesion: 0.29
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "asyncio"
Cohesion: 0.21
Nodes (18): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+10 more)

### Community 136 - "verify_budget.py"
Cohesion: 0.17
Nodes (14): agent_key(), _budget(), count_run(), decide(), _dedupe_window_s(), in_repo(), _load_counts(), log() (+6 more)

### Community 137 - "Any"
Cohesion: 0.13
Nodes (6): DroppedClauseLexical, DroppedLoteClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), test_dropped_access_filter_still_reports_authorization(), test_dropped_applicability_filter_reports_applicability_not_authorization()

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "test_opening.py"
Cohesion: 0.18
Nodes (7): manifest_document_count(), test_exit_0_then_idempotent_second_run(), block_model_stack(), Raises, test_bm25_path_imports_neither_the_model_adapter_nor_the_model_stack(), test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 140 - "Phase 1 - Production-oriented RAG"
Cohesion: 0.25
Nodes (8): Authorization regression and staff canary, BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline, Roadmap 12 - Security, Prompt injection and poisoned retrieved content tests, Public access filter

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.07
Nodes (36): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+28 more)

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make retrieve"
Cohesion: 0.15
Nodes (14): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+6 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "script_mix"
Cohesion: 0.24
Nodes (8): Review, script_mix(), test_every_v3_query_letter_matches_script_fixture(), test_g062_is_latin_only(), test_non_letters_add_no_script(), test_representative_v3_queries(), test_virama_and_vowel_sign_add_no_script(), test_nfd_equals_nfc()

### Community 150 - "documents/__init__.py"
Cohesion: 0.23
Nodes (5): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority

### Community 151 - "Spec 004 retrospective round 1 (PASS)"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

### Community 152 - "policy"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 153 - "policy"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 154 - "policy"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 155 - "Strategy"
Cohesion: 0.05
Nodes (73): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Error and failure behavior, Interfaces / models, Observability, Package / file placement (+65 more)

### Community 156 - "test_cli_config.py"
Cohesion: 0.26
Nodes (7): clean_env(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file(), test_exit_2_on_bad_config(), test_exit_2_on_settings_mismatch(), test_real_config_loads_with_pinned_revision(), _write()

### Community 157 - "baseline.py"
Cohesion: 0.06
Nodes (40): Review, T9 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, Continuity command (R10), T3 — `lexical-v2`, tokenizer selection, script mix, `--cross-tokenizer`, continuity command, Verification (+32 more)

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "dense_equivalence.py"
Cohesion: 0.24
Nodes (6): deterministic_clock(), equivalence_suite(), run_equivalence(), chunks_per_document_dense(), unanswerable(), test_dense_2_2_equals_the_pre_change_2_0_result()

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 191 - "continuity.py"
Cohesion: 0.15
Nodes (20): rerank_identity(), skipped_rerank_problems(), _case_keys(), compare_continuity(), _embedder_pair_from_doc(), _fmt_key(), _identity_refusals(), _info_lines() (+12 more)

### Community 192 - "security_eval.py"
Cohesion: 0.05
Nodes (58): R11 — Security gate (`security_index.py`, `security_eval.py`), Acceptance criteria, Implementation, Review, T8 — round 1, User decision, T10 — Documentation, decisions and hand-off, Verification (+50 more)

### Community 193 - "AccessContext"
Cohesion: 0.16
Nodes (9): Alternatives / deferred decisions, AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+1 more)

### Community 194 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 195 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 196 - "live_suite_rows"
Cohesion: 0.19
Nodes (15): load_suite(), live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_access_context_is_loaded_but_ignored() (+7 more)

### Community 197 - "Round 1 — 2026-11-04"
Cohesion: 0.17
Nodes (11): 010 — Multilingual Retrieval: Retrospective Review, Deviations from the approved plan, Documentation reconciled, Final handoff, Findings, Notes for the next spec, Patterns in `task-reviews.md`, Protected-data check (+3 more)

### Community 198 - "test_both_lote_modes_on_every_path_and_chunker"
Cohesion: 0.13
Nodes (8): test_both_lote_modes_on_every_path_and_chunker(), counting(), test_every_path_is_gated_for_every_query(), counting(), test_rerank_paths_pass_over_every_chunker_in_both_lote_modes(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

### Community 201 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.18
Nodes (11): open_retrieval / OpenedRetrieval, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory, R5 — `bm25` without Qdrant or the `bge-m3` extra, Review F1: open-time outage serves whole run, Review F4: duplicated standalone open wiring, Review F5: bind_to scroll fallback untested end to end (+3 more)

### Community 202 - "test_non_guest_roles_refused"
Cohesion: 0.18
Nodes (5): Role, clean_env(), test_empty_tenant_setting_refused(), test_guest_access_uses_settings_tenant(), test_non_guest_roles_refused()

### Community 204 - "ResolvedLote"
Cohesion: 0.09
Nodes (40): Acceptance criteria, 010 — Multilingual Retrieval Design, Applicability builders (R3), Components / boundaries, Data flow, Error and failure behavior, Interfaces / models, Observability (+32 more)

### Community 205 - "test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it"
Cohesion: 0.25
Nodes (3): test_a_forbidden_hit_injected_after_the_stage_fails_each_rerank_path(), test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), injecting()

### Community 206 - "DocumentRepository"
Cohesion: 0.14
Nodes (14): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Document manifest, DocumentRepository, LocalDocumentRepository (+6 more)

### Community 207 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 208 - "test_store_integration.py"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 209 - "test_hybrid.py"
Cohesion: 0.14
Nodes (12): User decision, _DenseLike, dense_pair(), ForbiddenDenseIndex, production_lexical(), real_hybrid(), test_empty_bm25_leg_keeps_the_dense_order(), test_forbidden_bm25_hit_fails_the_whole_query() (+4 more)

### Community 210 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 212 - "Review"
Cohesion: 0.29
Nodes (5): Implementation, Review, T3 — round 2, _group_installed(), test_default_embedder_identity_equals_the_bge_m3_adapter_identity()

### Community 213 - "Spec 011 — task reviews"
Cohesion: 0.29
Nodes (6): Implementation, Spec 011 — task reviews, T1 — round 1, T5 — round 1, User decision (2026-11-05), User decision (2026-11-06)

### Community 215 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 216 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 218 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 219 - "Spec 008 Retrieval Fallback Requirements"
Cohesion: 0.50
Nodes (4): Change log, Spec 008 Retrieval Fallback Requirements, Spec 008 Retrospective Review round 1, Review F3: missing change-log lines (resolved)

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1573 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `RetrievalConfigurationError` to `security_eval.py`, `Spec 007 hybrid retrieval`, `subprocess`, `compare.py`, `007 — Hybrid Retrieval Requirements`, `open_retrieval`, `test_security_eval.py`, `Strategy`, `baseline.py`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11755952380952381 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 85 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 85 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._