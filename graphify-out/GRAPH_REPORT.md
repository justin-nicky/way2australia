# Graph Report - way2australia  (2026-11-04)

## Corpus Check
- 297 files · ~336,061 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 36 file(s) not represented in the graph (top: (none) 20, .jsonl 13, .mdc 1)

## Summary
- 4604 nodes · 13984 edges · 196 communities (165 shown, 31 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 3015 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78aca843`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_compare.py
- retrieval_eval.py
- open_retrieval
- typing
- test_validate.py
- test_service.py
- security_eval.py
- test_index.py
- asyncio
- evaluation/validate.py
- chunker_build.py
- IngestionConfigurationError
- HeadingChunker
- load_retrieval_config
- test_lexical_cli.py
- json
- Spec 008 retrieval fallback
- BgeM3Embedder
- QdrantIndexStore
- test_retriever.py
- 007 — Hybrid Retrieval Requirements
- test_validate_knowledge.py
- test_availability.py
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- FakeTokenizer
- test_suite_v3.py
- test_strategy_eval.py
- Evaluation CLI Tests
- suite.py
- KnowledgeDocument
- test_baseline.py
- evaluation/test_cli.py
- 010 — Multilingual Retrieval Requirements
- .search
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- ResolvedAccess
- build_security_index
- open_retrieval
- typing
- IndexSettings
- Workflow Reviewer
- LocalDocumentRepository
- test_lexical_standalone.py
- test_cli_config.py
- test_repository_contract.py
- Ingestion (Phase 1 baseline, Spec 004)
- 007 — Hybrid Retrieval Requirements
- test_recursive.py
- HeadingChunker
- LocalRepositoryConfig
- FallbackRetriever
- hashing.py
- LexicalIndexBindingError
- Development Workflow
- retrieval/test_access.py
- 008 — Retrieval Fallback Requirements
- json
- Evaluation Phase 1 framework (Spec 006)
- security_eval.py
- Retrieval fallback (Spec 008, D056-D062)
- evaluation/cli.py
- test_legacy_baseline_snapshot.py
- Chunk
- make index-lexical
- CURRENT_STATE.md current state document
- check_hit
- test_applicability.py
- embedder
- Phase 1 RAG query pipeline
- build_lexical_index
- Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)
- Constitution
- Section: Next step
- dense
- retrieval/test_cli.py
- embedder
- chunking.py
- FakeTokenizer
- list_eligible_documents
- Ingestion pipeline (Spec 004)
- make eval-retrieval
- AccessContext
- test_bm25.py
- LexicalIndex
- Backend stack
- embedder
- D023 Task-gated agent workflow
- Path
- test_schemas.py
- Roadmap 12 - Security
- pathlib
- Spec status table
- DenseIndex
- retrieval_client_factory
- SpyIndex
- transcript_metrics.py
- CURRENT_STATE.md
- QdrantIndexStore
- repositories/__init__.py
- AWS target
- make retrieve
- Retrieval package (Spec 005 and 007)
- D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)
- Qdrant (vector database)
- Review
- structure.py
- FakeEmbedder
- sync_agent_skills.py
- test_content_hash.py
- Spec 005 dense retrieval baseline
- test_violation_names_the_document_from_the_error_attribute
- D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)
- test_non_guest_roles_refused
- fusion
- R1 — Failure classification (`errors.py`, `availability.py`)
- Development Workflow
- re
- failing_client
- test_status_handling.py
- DroppedClauseLexical
- conftest.py
- QdrantIndexStore
- Baseline runner and result JSON
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Phase 1 - Production-oriented RAG
- RuntimeSettings
- test_goldens.py
- Vocabulary, flashcards and free access
- .search
- test_seed_corpus.py
- Spec 002 document model and repository
- R12 — Real runs (user-owned gate)
- Evaluation Framework Goal
- list_eligible_documents
- IndexIdentity
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- eval-compare
- Payments, account access and support boundaries
- make eval-compare
- make test
- Mission
- test_fallback.py
- 009 — Chunking Experiments Tasks
- Spec 004 retrospective round 1 (PASS)
- policy
- policy
- policy
- test_empty_tenant_setting_refused
- Roadmap 3 - Ingestion baseline
- stalled_port
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- test_a_lexical_sanity_failure_is_a_harness_error
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
- .retrieve
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
- DocumentRepository
- Authorization enforced before generation
- Roadmap 10 - Grounded generation + citations
- policy
- test_every_path_is_gated_for_every_query

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 112 edges
2. `LocalDocumentRepository` - 102 edges
3. `Strategy` - 79 edges
4. `DenseRetriever` - 79 edges
5. `FakeTokenizer` - 78 edges
6. `ResolvedAccess` - 77 edges
7. `run_retrieval_evaluation()` - 73 edges
8. `FakeEmbedder` - 73 edges
9. `HeadingChunker` - 68 edges
10. `open_retrieval()` - 67 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Change log` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `T4 review follow-ups (planner amendment 2026-11-02)` --references--> `run_retrieval_evaluation()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/tasks.md → packages/rag/src/way2australia_rag/evaluation/retrieval_eval.py
- `Phase 2 compatibility / migration` --references--> `ChunkerIdentity`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
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

## Communities (196 total, 31 thin omitted)

### Community 0 - "test_compare.py"
Cohesion: 0.06
Nodes (102): Implementation, Review, T7 — round 1, User decision, _changed(), _chunker_text(), compare(), Comparison (+94 more)

### Community 1 - "retrieval_eval.py"
Cohesion: 0.04
Nodes (58): Implementation, Review, T2 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, Implementation, Review (+50 more)

### Community 2 - "open_retrieval"
Cohesion: 0.08
Nodes (44): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Components / boundaries, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+36 more)

### Community 3 - "typing"
Cohesion: 0.09
Nodes (5): RuntimeSettings, Embedder, default_lexical_dir(), settings(), live_client()

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "test_service.py"
Cohesion: 0.15
Nodes (25): doc(), Harness, ShortResultEmbedder, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_chunk_too_long_report_has_no_chunk_text() (+17 more)

### Community 6 - "security_eval.py"
Cohesion: 0.08
Nodes (42): As-built notes, Design summary, Package / file placement, R6 — `BM25Retriever` (`retrieval/bm25.py`), Change log, Implementation, Review, T4 — round 1 (+34 more)

### Community 7 - "test_index.py"
Cohesion: 0.15
Nodes (38): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), make_settings(), open_index(), payload() (+30 more)

### Community 8 - "asyncio"
Cohesion: 0.31
Nodes (14): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+6 more)

### Community 9 - "evaluation/validate.py"
Cohesion: 0.12
Nodes (19): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+11 more)

### Community 10 - "chunker_build.py"
Cohesion: 0.08
Nodes (31): Chunker identity, settings and configuration (R5), Dependencies, Implementation, Implementation, Implementation, Review, T3 — round 2, User decision (+23 more)

### Community 11 - "IngestionConfigurationError"
Cohesion: 0.08
Nodes (19): `structure` v1 (R3), Tokenizer (R1), T1 — Tokenizer and truncation guard, Verification, IngestionConfigurationError, BgeM3Tokenizer, _download_hub_file(), _tokenizer_config_error() (+11 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.07
Nodes (48): build_index_settings(), deterministic_clock(), equivalence_suite(), basic_suite(), build(), chunks_per_document_dense(), default_eval_extras(), fusion_config() (+40 more)

### Community 13 - "load_retrieval_config"
Cohesion: 0.15
Nodes (15): load_retrieval_config(), block_model_stack(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model(), test_build_retriever_converts_a_string_value_and_refuses_unknown(), test_build_retriever_maps_each_strategy(), test_committed_config_loads() (+7 more)

### Community 14 - "test_lexical_cli.py"
Cohesion: 0.09
Nodes (37): Implementation, Implementation, Review, T3 — round 2, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree() (+29 more)

### Community 15 - "json"
Cohesion: 0.15
Nodes (25): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+17 more)

### Community 16 - "Spec 008 retrieval fallback"
Cohesion: 0.11
Nodes (26): Default retrieval strategy hybrid degrades to BM25, RetrievalUnavailableError and availability classification, FallbackRetriever and open_retrieval wiring (merged 1107b67), Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: Qdrant client lifecycle leak on failed open, Spec 008 retro F3: post-approval amendments lacked change-log lines; resolved 2026-11-01, spec-planner added eight dated lines to requirements.md Change log, Spec 008 retro F4: duplicated standalone open wiring (+18 more)

### Community 17 - "BgeM3Embedder"
Cohesion: 0.10
Nodes (15): BgeM3Embedder, _group_installed(), OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+7 more)

### Community 18 - "QdrantIndexStore"
Cohesion: 0.09
Nodes (33): IndexSettingsMismatchError, IndexedDocument, QdrantIndexStore, read_index_settings(), client_factory(), CountingStore, client(), _keyword_indexed() (+25 more)

### Community 19 - "test_retriever.py"
Cohesion: 0.08
Nodes (27): IndexPoint, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), build_client(), docs(), guest() (+19 more)

### Community 20 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (32): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+24 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.21
Nodes (27): load(), test_bad_date_fails_loading_naming_document_and_field(), test_guest_policy_agrees_with_access_policy_config(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for() (+19 more)

### Community 22 - "test_availability.py"
Cohesion: 0.11
Nodes (23): Review, classify_model_error(), classify_qdrant_error(), _optional_types(), FallbackReason, caused_by(), handled_error(), reason() (+15 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.10
Nodes (25): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+17 more)

### Community 26 - "FakeTokenizer"
Cohesion: 0.08
Nodes (34): Implementation, Implementation, Implementation, Implementation, Review, Review, Review, Review (+26 more)

### Community 27 - "test_suite_v3.py"
Cohesion: 0.10
Nodes (32): Implementation, Review, Spec 010 — task reviews, T1 — round 1, T2 — round 1, User decision, candidate_row(), candidates() (+24 more)

### Community 28 - "test_strategy_eval.py"
Cohesion: 0.12
Nodes (25): User decision, eval_world(), lexical_env(), retrieve(), retrieve_world(), test_2_3_keys_for_each_strategy(), test_a_2_2_file_reads_with_strategy_and_lexical(), test_a_2_3_file_reads_lote_as_none() (+17 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "suite.py"
Cohesion: 0.12
Nodes (23): CaseBase, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, UnanswerableCase, declared_release_id(), inside() (+15 more)

### Community 31 - "KnowledgeDocument"
Cohesion: 0.07
Nodes (10): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, DocumentNotFoundError (+2 more)

### Community 32 - "test_baseline.py"
Cohesion: 0.09
Nodes (25): manifest_document_count(), case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded() (+17 more)

### Community 33 - "evaluation/test_cli.py"
Cohesion: 0.16
Nodes (19): load_production_ingestion_config(), clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_cli_has_no_embedder_or_allow_fake_flag(), test_existing_output_exits_2_before_qdrant() (+11 more)

### Community 34 - "010 — Multilingual Retrieval Requirements"
Cohesion: 0.07
Nodes (27): 010 — Multilingual Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+19 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "ResolvedAccess"
Cohesion: 0.05
Nodes (39): Security / authorization, Dependencies, Acceptance criteria, Acceptance criteria, Dependencies, R7 — Marking degraded results, Acceptance criteria, `ResolvedLote` and validation (R2) (+31 more)

### Community 39 - "build_security_index"
Cohesion: 0.10
Nodes (9): R11 — Security gate (`security_index.py`, `security_eval.py`), build_security_index(), delete_security_index(), _forbidden_payload(), _lexical_forbidden_entries(), require_security_base(), live_client(), test_recursive_v1_full_gate_on_docker() (+1 more)

### Community 40 - "open_retrieval"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-retrieval, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation (+23 more)

### Community 42 - "IndexSettings"
Cohesion: 0.07
Nodes (22): Acceptance criteria, Design summary, point_id(), compare(), IndexSettings, mismatch_message(), _DenseLike, test_index_settings_1_0_upgrades_in_memory() (+14 more)

### Community 43 - "Workflow Reviewer"
Cohesion: 0.07
Nodes (25): Considered and rejected, Evidence, F1 — <title> [waste | quality risk | process slip] (confidence: high/medium/low), Findings, New features and tools (official sources, since <date>), Not measurable here, P1 — <title> (addresses F#; expected saving: ...), Proposals (+17 more)

### Community 44 - "LocalDocumentRepository"
Cohesion: 0.12
Nodes (32): LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), security_result(), seed_repository(), spied() (+24 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.18
Nodes (19): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+11 more)

### Community 46 - "test_cli_config.py"
Cohesion: 0.16
Nodes (18): clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file(), test_exit_0_then_idempotent_second_run() (+10 more)

### Community 47 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 48 - "Ingestion (Phase 1 baseline, Spec 004)"
Cohesion: 0.10
Nodes (28): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+20 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "test_recursive.py"
Cohesion: 0.19
Nodes (16): assert_matches_snapshot(), assert_recursive_chunks_whitespace_fidelity(), chunks_to_records(), collapse_whitespace(), load_snapshot(), snapshot_for_document(), recursive_chunker(), test_deterministic() (+8 more)

### Community 51 - "HeadingChunker"
Cohesion: 0.08
Nodes (46): HeadingChunker, _is_word_char(), slugify(), assert_structure_chunks_whitespace_fidelity(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+38 more)

### Community 52 - "LocalRepositoryConfig"
Cohesion: 0.05
Nodes (40): format_summary(), main(), _parser(), load_ingestion_config(), load_runtime_settings(), IngestionError, DocumentFailure, IngestionService (+32 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.07
Nodes (31): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+23 more)

### Community 54 - "hashing.py"
Cohesion: 0.10
Nodes (24): _StringDateLoader, canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), normalize_body(), sha256_hex() (+16 more)

### Community 55 - "LexicalIndexBindingError"
Cohesion: 0.10
Nodes (33): R4 — Freshness from the repository (`lexical/freshness.py`), LexicalIndexBindingError, test_verify_fresh_refuses_chunker_name_mismatch(), build_production(), identity(), ingest_dense(), open_lexical(), payload() (+25 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (30): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+22 more)

### Community 57 - "retrieval/test_access.py"
Cohesion: 0.32
Nodes (9): guest(), payload(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload(), test_check_hit_rejects_violations(), test_default_tenant(), test_filter_derived_from_policy_and_context(), test_guest_resolves_to_identical_policy() (+1 more)

### Community 58 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.06
Nodes (38): Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+30 more)

### Community 59 - "json"
Cohesion: 0.10
Nodes (20): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+12 more)

### Community 60 - "Evaluation Phase 1 framework (Spec 006)"
Cohesion: 0.06
Nodes (37): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, schemas.py, validate.py (referencing registry, validate-evaluation checks), Section-level keys <document_id>#<section_id> (+29 more)

### Community 61 - "security_eval.py"
Cohesion: 0.11
Nodes (25): Review, T8 — round 1, User decision, R10 — Security gate (`security_eval.py`), Implementation, Review, T6 — round 1, User decision (+17 more)

### Community 62 - "Retrieval fallback (Spec 008, D056-D062)"
Cohesion: 0.07
Nodes (36): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+28 more)

### Community 63 - "evaluation/cli.py"
Cohesion: 0.12
Nodes (25): R8 — Result format 2.2 (`retrieval_eval.py`), T5 — Evaluation result 2.2 and `eval-compare` by served strategy, Verification, Review, _compare(), default_security_output_path(), format_security_summary(), format_summary() (+17 more)

### Community 64 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 65 - "Chunk"
Cohesion: 0.10
Nodes (19): Package / file placement, Requirements traceability, T2 — Structure and recursive chunkers, Verification, security_gate_chunkers(), Chunk, check_chunks(), ChunkTooLongError (+11 more)

### Community 66 - "make index-lexical"
Cohesion: 0.08
Nodes (32): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1) (+24 more)

### Community 67 - "CURRENT_STATE.md current state document"
Cohesion: 0.08
Nodes (38): make retrieval-baseline legacy frozen, build_retriever, CURRENT_STATE.md current state document, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both (+30 more)

### Community 68 - "check_hit"
Cohesion: 0.05
Nodes (48): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Error and failure behavior, Interfaces / models, Observability, Phase 2 compatibility / migration, Testing / evaluation strategy (+40 more)

### Community 69 - "test_applicability.py"
Cohesion: 0.16
Nodes (30): Review, active_lote_codes(), _active_list(), resolve_lote(), build_lexical(), _dropped_lote_setup(), DroppedFilterIndex, DroppedLoteClauseLexical (+22 more)

### Community 70 - "embedder"
Cohesion: 0.11
Nodes (17): chunker, context_prefix, name, overlap_tokens, target_tokens, version, embedder, batch_size (+9 more)

### Community 71 - "Phase 1 RAG query pipeline"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 72 - "build_lexical_index"
Cohesion: 0.04
Nodes (52): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Implementation, Implementation, Review, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical` (+44 more)

### Community 73 - "Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 74 - "Constitution"
Cohesion: 0.16
Nodes (28): load_schema(), chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank() (+20 more)

### Community 75 - "Section: Next step"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "dense"
Cohesion: 0.04
Nodes (67): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), R4 — `make index-lexical` (`lexical/cli.py`), R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`) (+59 more)

### Community 77 - "retrieval/test_cli.py"
Cohesion: 0.15
Nodes (23): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+15 more)

### Community 78 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 79 - "chunking.py"
Cohesion: 0.13
Nodes (17): Implementation, _char_split(), _merge_pieces(), _merge_word_pieces(), _parse_sections(), _Section, split_at_sentence_ends(), _split_body() (+9 more)

### Community 80 - "FakeTokenizer"
Cohesion: 0.06
Nodes (37): 009 — Chunking Experiments Design, Alternatives / deferred decisions, As-built notes, Carry-over clean-ups (R11), Cross-index comparison (R8), Data flow, Error and failure behavior, Interfaces / models (+29 more)

### Community 81 - "list_eligible_documents"
Cohesion: 0.25
Nodes (14): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+6 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (17): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+9 more)

### Community 83 - "make eval-retrieval"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 84 - "AccessContext"
Cohesion: 0.16
Nodes (9): Alternatives / deferred decisions, AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+1 more)

### Community 85 - "test_bm25.py"
Cohesion: 0.17
Nodes (23): LexicalRow, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+15 more)

### Community 86 - "LexicalIndex"
Cohesion: 0.07
Nodes (24): R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), T2: where the shared pieces live (2026-10-31), Implementation, Review, T2 — round 1, User decision, Lexical identity and per-document freshness (R6), Tokenizers (R5, R6) (+16 more)

### Community 87 - "Backend stack"
Cohesion: 0.07
Nodes (38): Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Backend stack, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Custom retrieval metrics (plain Python), DeepEval (not yet a dependency) (+30 more)

### Community 88 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Path"
Cohesion: 0.12
Nodes (20): build_security_repository(), _fixture_files(), security_repository(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper() (+12 more)

### Community 91 - "test_schemas.py"
Cohesion: 0.16
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 92 - "Roadmap 12 - Security"
Cohesion: 0.25
Nodes (8): Authorization regression and staff canary, BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline, Roadmap 12 - Security, Prompt injection and poisoned retrieved content tests, Public access filter

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "Spec status table"
Cohesion: 0.12
Nodes (19): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+11 more)

### Community 95 - "DenseIndex"
Cohesion: 0.15
Nodes (6): EmbedderInfo, DenseIndex, OddIdStore, http_client(), test_a_closed_port_is_unavailable(), test_a_stalled_open_times_out_within_the_connect_bound()

### Community 96 - "retrieval_client_factory"
Cohesion: 0.12
Nodes (13): Decisions D056-D062, Spec 008 Retrieval Fallback Design, Repeated finding: graphify update ownership, Spec 008 Task Reviews, Implementation, Implementer Sonnet 5.5 / reviewer Opus 5.5 pattern, T1 — round 1, User decision (+5 more)

### Community 97 - "SpyIndex"
Cohesion: 0.19
Nodes (14): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+6 more)

### Community 98 - "transcript_metrics.py"
Cohesion: 0.17
Nodes (12): analyse(), category(), command_kinds(), executed_text(), expand(), main(), parse_time(), render() (+4 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "repositories/__init__.py"
Cohesion: 0.06
Nodes (27): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), document_fields(), under_root(), check_manifest_documents() (+19 more)

### Community 102 - "AWS target"
Cohesion: 0.05
Nodes (42): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Local multilingual BGE reranker, BM25 via FTS5 bm25() (+34 more)

### Community 103 - "make retrieve"
Cohesion: 0.11
Nodes (20): make retrieve, resolve_access (only role-to-policy mapping), ResolvedAccess(policy, tenant_id), docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Hybrid hit lines show per-leg ranks dense=<rank|-> bm25=<rank|->; truncation note above 64 distinct terms, Lexical file <W2A_LEXICAL_INDEX_DIR>/<collection>.sqlite (default .local/lexical, git-ignored), No option for role, scope or tenant; access is always guest/public for W2A_TENANT_ID (+12 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "D035 One filter builder, fail-closed re-check, same path for later fallbacks (Spec 005)"
Cohesion: 0.09
Nodes (33): DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Known issue: no circuit breaker, ~3 s per query with hanging Qdrant, Spec 008 retro F1: open-time outage makes BM25 serve whole run, Next step 7: Spec 008 hand-off carry-overs for HTTP route spec (circuit breaker, startup policy, 5xx, freshness cost, async check, client lifecycle), BM25Retriever, build_access_filter (+25 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "Review"
Cohesion: 0.23
Nodes (7): Implementation, Review, T5 — round 1, User decision, security_document(), security_run_record(), SecurityReport

### Community 108 - "structure.py"
Cohesion: 0.21
Nodes (12): _build_prefix(), _compose_chunk(), DuplicateSectionError, _is_list_item(), _join_blocks(), _pack_blocks(), body_fits(), _parse_blocks() (+4 more)

### Community 109 - "FakeEmbedder"
Cohesion: 0.12
Nodes (15): FakeEmbedder, _cosine_to_query(), _text_with_score_below(), __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none() (+7 more)

### Community 110 - "sync_agent_skills.py"
Cohesion: 0.27
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Spec 005 dense retrieval baseline"
Cohesion: 0.18
Nodes (15): AccessContext, Role, W2A_TENANT_ID, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e, AccessContext and Role, D033 AccessContext and Role live in core (Spec 005), D034 W2A_TENANT_ID is a server setting (Spec 005) (+7 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)"
Cohesion: 0.19
Nodes (15): make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Known issue: verify_fresh asyncio.run in event loop, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: freshness check rereads every document, Malayalam BM25 limit: exact tokens only, no stemming, D010 Qdrant primary, SQLite FTS5 fallback (+7 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "R1 — Failure classification (`errors.py`, `availability.py`)"
Cohesion: 0.23
Nodes (8): As-built notes, R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy, GatedRepoError, LocalEntryNotFoundError, RepositoryNotFoundError, RevisionNotFoundError

### Community 118 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 119 - "re"
Cohesion: 0.19
Nodes (9): active_registry_languages(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error(), test_no_language_literal_in_evaluation_code(), test_real_registry_lists_en_and_the_active_product_language(), test_slice_keys_come_from_data_and_carry_n(), test_small_sample_threshold_is_ten() (+1 more)

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "DroppedClauseLexical"
Cohesion: 0.25
Nodes (4): DroppedClauseLexical, test_a_dropped_lexical_clause_names_the_four_lexical_paths(), test_a_lexical_store_without_the_clause_fails_bm25_and_hybrid(), __init__()

### Community 123 - "conftest.py"
Cohesion: 0.29
Nodes (6): live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), test_dataset_types_loaded_by_type()

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

### Community 132 - "test_goldens.py"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "test_seed_corpus.py"
Cohesion: 0.48
Nodes (4): manifest_records(), seed_documents(), test_security_fixtures_are_not_in_the_production_corpus(), test_seed_ids_and_versions_are_unique()

### Community 136 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 137 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "list_eligible_documents"
Cohesion: 0.14
Nodes (8): _authority_map(), collect(), _document_ids(), collect(), DocumentQuery, EligibilityPolicy, list_eligible_documents(), test_seed_corpus_is_entirely_eligible_for_guest()

### Community 140 - "IndexIdentity"
Cohesion: 0.10
Nodes (18): IndexIdentity, leg_order(), make_world(), run_strategy(), strategy_suite(), test_hybrid_leg_ranks_beyond_top_k_are_real_document_ranks(), test_runner_requires_fusion_for_hybrid(), chunk() (+10 more)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "make eval-compare"
Cohesion: 0.15
Nodes (14): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+6 more)

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "test_fallback.py"
Cohesion: 0.12
Nodes (23): access(), client_at(), closed_port(), Fallback, open_hybrid(), Primary, run_cli(), stalled_port() (+15 more)

### Community 150 - "009 — Chunking Experiments Tasks"
Cohesion: 0.17
Nodes (11): 009 — Chunking Experiments Tasks, Security gate (R9), T4 — Distinct-document metrics, result 2.3 and cross-index compare, T4 review follow-ups (planner amendment 2026-11-02), T5 — Security gate across chunkers, T6 — User-owned real runs and the default index, T7 — Documentation, decisions, carry-over clean-ups and hand-off, Verification (+3 more)

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

### Community 155 - "test_empty_tenant_setting_refused"
Cohesion: 0.33
Nodes (3): clean_env(), test_empty_tenant_setting_refused(), test_guest_access_uses_settings_tenant()

### Community 156 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 161 - "test_a_lexical_sanity_failure_is_a_harness_error"
Cohesion: 0.50
Nodes (3): strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error(), wrapper()

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 169 - "DocumentRepository Protocol (async)"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 193 - "DocumentRepository"
Cohesion: 0.14
Nodes (14): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Document manifest, DocumentRepository, LocalDocumentRepository (+6 more)

### Community 195 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 198 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.20
Nodes (12): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 10 - Grounded generation + citations, Roadmap 13 - Graceful degradation, Roadmap 14 - AWS deployment (+4 more)

### Community 204 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.29
Nodes (4): test_every_path_is_gated_for_every_query(), counting(), test_the_gate_runs_all_three_strategies_on_v2(), counting()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1377 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Retrieval (dense baseline Spec 005, hybrid Spec 007, fallback Spec 008)` connect `008 — Retrieval Fallback Requirements` to `make index-lexical`, `ResolvedAccess`, `Target repository shape (apps, packages, knowledge, sources, evaluation, tests, config, experiments, analytics, prompts, docs, infra)`, `Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__`, `Ingestion (Phase 1 baseline, Spec 004)`, `Retrieval fallback (Spec 008, D056-D062)`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 84 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 84 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_compare.py` be split into smaller, more focused modules?**
  _Cohesion score 0.055337004982953054 - nodes in this community are weakly interconnected._
- **Why does `Change log` connect `security_eval.py` to `test_compare.py`, `test_a_lexical_sanity_failure_is_a_harness_error`, `CURRENT_STATE.md current state document`, `check_hit`, `dense`, `test_lexical_cli.py`, `007 — Hybrid Retrieval Requirements`, `LexicalIndex`, `security_eval.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 36 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._