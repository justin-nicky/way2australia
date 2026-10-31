# Graph Report - way2australia  (2026-10-31)

## Corpus Check
- 255 files · ~254,972 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .example 1)

## Summary
- 3582 nodes · 10645 edges · 170 communities (144 shown, 26 thin omitted)
- Extraction: 81% EXTRACTED · 19% INFERRED · 0% AMBIGUOUS · INFERRED: 1972 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd2d2bfe`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DenseRetriever
- Task Review Log (T7)
- Security Fixture Corpus
- test_eligibility.py
- Evaluation Schemas
- Strategy
- RetrievalConfigurationError
- test_cli_config.py
- test_retriever.py
- evaluation/cli.py
- QdrantIndexStore
- documents/__init__.py
- retrieval_eval.py
- security_index.py
- Model Tiers
- Day-1 Data and Sources
- Strategy Eval Tests
- KnowledgeDocument
- Index Binding Errors
- Document Model Tests
- Retrieval Eval Tests
- HeadingChunker
- Date and Policy Tests
- BGE-M3 Adapter
- test_lexical_build.py
- retrieval/errors.py
- typing
- FakeEmbedder
- test_manifest_validation.py
- Evaluation CLI Tests
- test_security_eval.py
- repositories/__init__.py
- Retrieval Package
- test_baseline.py
- test_lexical_cli.py
- Architecture Decisions (DECISIONS.md)
- Review
- 008 — Retrieval Fallback Requirements
- Health Endpoint
- Evaluation Slices
- pytest
- lexical/store.py
- test_date_and_policy.py
- asyncio
- Strategy
- test_repository_contract.py
- evaluation/validate.py
- DenseIndex
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- Evaluation Suite (public-eval-v1)
- documents/__init__.py
- Roadmap
- 007 — Hybrid Retrieval Tasks
- test_server_filter_keeps_every_forbidden_point_out
- test_suite_v2.py
- Development Workflow
- test_opening.py
- Phase 2 Knowledge Release workflow
- test_status_handling.py
- COMMANDS.md (project command surface)
- conftest.py
- test_strategy.py
- roles
- test_text.py
- DenseRetriever
- BGE-M3 embeddings
- D042 Governed suite loader, validator and schema files (Spec 006)
- FallbackReason
- test_goldens.py
- Phase 1 RAG query pipeline
- healthcheck
- Evaluation framework (Spec 006)
- make ingest
- Constitution
- Section: Next step
- Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)
- typing
- HybridRetriever (dense leg then BM25 leg, no single-leg fallback)
- Task-gated agent workflow loop
- embedder
- packages/rag
- Ingestion pipeline (Spec 004)
- DocumentRepository Protocol
- Engineering Conventions
- D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)
- D055 Default strategy is hybrid (Spec 007)
- test_lexical_tokenizer.py
- D023 Task-gated agent workflow
- LexicalIndex (SQLite FTS5 store)
- Spec 005 - dense retrieval baseline (verified 2026-10-23, merged b33462e)
- Mock assessments, scoring, feedback and review windows
- pathlib
- AGENTS.md Project Rules
- make index-lexical
- IngestionService
- Knowledge Schema and Metadata
- CURRENT_STATE.md
- QdrantIndexStore
- Baseline runner and result JSON
- 006 Evaluation Framework Tasks
- fusion
- Retrieval package (Spec 005 and 007)
- Section: Spec status table
- Qdrant (vector database)
- opening.py
- NAATI CCL booking, fees, cancellation, results and credential validity
- retrieval/test_access.py
- test_content_hash.py
- test_repository_contract.py
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- retrieval/test_access.py
- test_authorization_isolation.py
- build_security_repository
- test_status_handling.py
- test_index_contract.py
- hashing.py
- test_security_eval.py
- test_failed_write_removes_partial_file
- Development Workflow
- evaluation/test_cli.py
- RuntimeSettings
- retrieval_eval.py
- Vocabulary, flashcards and free access
- test_failed_write_removes_partial_file
- test_schemas.py
- dense_equivalence.py
- Evaluation Framework Goal
- Versioning and Releases
- make eval-security
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- Spec 004 retrospective round 1 (PASS)
- eval-compare
- Payments, account access and support boundaries
- Home Affairs credentialled community language points
- make test
- Mission
- Way2Australia public offering and assistant scope
- Materials and dialogue practice
- policy
- policy
- policy
- policy
- Phase 2 Analytics Event Contract
- Canonical document metadata
- Orchestrator State Machine
- Project Context README
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- T9 deviation: git_dirty true in BM25 and hybrid result files
- way2australia
- way2australia-api
- way2australia-observability
- sync_agent_skills.py
- AccessContext
- canonical_json

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 101 edges
2. `LocalDocumentRepository` - 78 edges
3. `Strategy` - 67 edges
4. `FakeEmbedder` - 61 edges
5. `DenseRetriever` - 60 edges
6. `ResolvedAccess` - 58 edges
7. `EvaluationConfigurationError` - 57 edges
8. `open_retrieval()` - 56 edges
9. `run_retrieval_evaluation()` - 55 edges
10. `HeadingChunker` - 55 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `User decision` --references--> `git_state()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/task-reviews.md → packages/rag/src/way2australia_rag/retrieval/baseline.py
- `Traceability` --references--> `open_retrieval()`  [INFERRED]
  .kiro/specs/008-retrieval-fallback/requirements.md → packages/rag/src/way2australia_rag/retrieval/opening.py
- `Acceptance criteria` --references--> `RetrievalConfig`  [INFERRED]
  .kiro/specs/008-retrieval-fallback/requirements.md → packages/rag/src/way2australia_rag/retrieval/strategy.py
- `Acceptance criteria` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/tests/retrieval/test_bm25.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Authorization applied inside every retrieval leg before fusion** — docs_project_decisions_d035, docs_project_decisions_d040, kiro_specs_007_hybrid_retrieval_design_bm25_retriever, kiro_specs_007_hybrid_retrieval_design_hybrid_retriever [EXTRACTED 0.95]
- **Default strategy decision: R13 rule, T9 runs, D055** — kiro_specs_007_hybrid_retrieval_requirements_r13_default_strategy_decision, kiro_specs_007_hybrid_retrieval_tasks_t9_comparison_gate, docs_project_decisions_d055 [EXTRACTED 0.95]
- **Authorization enforcement chain inside retrievers** — docs_project_architecture_resolve_access, docs_project_architecture_build_access_filter, docs_project_architecture_sql_access_clause, docs_project_architecture_check_hit [EXTRACTED 1.00]
- **Knowledge Release components** — docs_project_architecture_document_snapshot, docs_project_decisions_c_evaluation_suite, docs_project_architecture_rag_config, docs_project_architecture_index_version, docs_project_architecture_knowledge_release [EXTRACTED 1.00]
- **Evaluation command group sharing evaluation.cli module** — docs_project_commands_make_validate_evaluation, docs_project_commands_make_eval_retrieval, docs_project_commands_make_eval_security, docs_project_commands_make_eval_compare, docs_project_commands_evaluation_cli_module [EXTRACTED 1.00]
- **Hybrid retrieval setup order: ingest, index-lexical, retrieve/eval** — docs_project_commands_make_ingest, docs_project_commands_make_index_lexical, docs_project_commands_make_retrieve, docs_project_commands_make_eval_retrieval [EXTRACTED 1.00]
- **Evaluation toolchain: eval-retrieval, eval-security, eval-compare, suite v2** — docs_project_current_state_cap_eval_framework, docs_project_current_state_cap_eval_security, docs_project_current_state_cap_eval_compare, docs_project_current_state_cap_suite_v2 [EXTRACTED 1.00]
- **Hybrid retrieval stack implemented by Spec 007** — docs_project_current_state_cap_lexical_index, docs_project_current_state_cap_bm25_retriever, docs_project_current_state_cap_hybrid_rrf, docs_project_current_state_cap_strategy_flag, docs_project_current_state_cap_dense_retrieval [EXTRACTED 1.00]
- **Spec 007 real strategy comparison (dense, BM25, hybrid) on public-eval-v2** — docs_project_current_state_result_dense_2_1, docs_project_current_state_result_bm25, docs_project_current_state_result_hybrid, docs_project_current_state_baseline_dense_v2_20261025 [EXTRACTED 1.00]
- **Intentionally avoided choices group** — docs_project_tech_stack_langgraph, docs_project_tech_stack_bedrock_kb, docs_project_tech_stack_bedrock_agents, docs_project_tech_stack_kubernetes, docs_project_tech_stack_multi_vector_db, docs_project_tech_stack_agent_orchestration, docs_project_tech_stack_fine_tuning, docs_project_tech_stack_microservices, docs_project_tech_stack_heavy_frameworks [EXTRACTED 1.00]
- **Evaluation make targets sharing the suite loader** — _kiro_specs_006_evaluation_framework_design_validate_evaluation, _kiro_specs_006_evaluation_framework_design_eval_retrieval, _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_eval_compare, _kiro_specs_006_evaluation_framework_design_suite_loader [EXTRACTED 1.00]
- **Guest authorization path (resolve, filter, re-check)** — _kiro_specs_005_dense_retrieval_baseline_design_accesscontext, _kiro_specs_005_dense_retrieval_baseline_design_resolve_access, _kiro_specs_005_dense_retrieval_baseline_design_build_access_filter, _kiro_specs_005_dense_retrieval_baseline_design_check_hit [EXTRACTED 1.00]
- **Ingestion pipeline components** — _kiro_specs_004_ingestion_baseline_design_ingestionservice, _kiro_specs_004_ingestion_baseline_design_headingchunker, _kiro_specs_004_ingestion_baseline_design_embedder_protocol, _kiro_specs_004_ingestion_baseline_design_qdrantindexstore [EXTRACTED 1.00]
- **Authorization hard gate construction** — _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_security_index, _kiro_specs_006_evaluation_framework_design_forbidden_variants, _kiro_specs_006_evaluation_framework_design_one_access_path, _kiro_specs_006_evaluation_framework_design_security_gate [EXTRACTED 1.00]
- **Task-gated spec workflow roles** — agent_skills_spec_planner_skill_spec_planner_skill, agent_skills_spec_implementer_skill_spec_implementer_skill, agent_skills_task_reviewer_skill_task_reviewer_skill, agent_skills_spec_reviewer_skill_spec_reviewer_skill [EXTRACTED 1.00]
- **Task-gated workflow roles** — _kiro_specs_003_task_gated_workflow_design_spec_orchestrator, _kiro_specs_003_task_gated_workflow_design_spec_implementer, _kiro_specs_003_task_gated_workflow_design_task_reviewer, _kiro_specs_003_task_gated_workflow_design_spec_planner, _kiro_specs_003_task_gated_workflow_design_spec_reviewer [EXTRACTED 1.00]
- **Phase 1 AWS deployment stack** — docs_project_tech_stack_mumbai_region, docs_project_tech_stack_phase1_aws_services, docs_project_tech_stack_terraform, docs_project_tech_stack_github_actions, docs_project_tech_stack_cloudwatch [INFERRED 0.75]
- **Language, access and source authority separation** — docs_knowledge_schema_and_metadata_access_scope, docs_knowledge_schema_and_metadata_lote_languages, docs_knowledge_schema_and_metadata_authorization_vs_language_independence, docs_knowledge_source_of_truth_source_precedence [INFERRED 0.75]
- **Knowledge Release composition** — way2australia_ai_platform_implementation_plan_knowledge_release, way2australia_ai_platform_implementation_plan_evaluation_suite, way2australia_ai_platform_implementation_plan_release_manifest, way2australia_ai_platform_implementation_plan_document_manifest [INFERRED 0.75]
- **Security regression controls** — way2australia_ai_platform_implementation_plan_staff_only_canary, way2australia_ai_platform_implementation_plan_poisoned_public_document, way2australia_ai_platform_implementation_plan_graceful_degradation, way2australia_ai_platform_implementation_plan_authorization_before_generation [INFERRED 0.75]
- **Strategy retrievers sharing the Retriever Protocol** — docs_project_architecture_dense_retriever, docs_project_architecture_bm25_retriever, docs_project_architecture_hybrid_retriever, docs_project_architecture_retriever_protocol [INFERRED 0.85]
- **Checks composing make verify** — docs_project_commands_make_verify, docs_project_commands_make_lint, docs_project_commands_make_typecheck, docs_project_commands_make_test, docs_project_commands_make_skills_check, docs_project_commands_make_validate_knowledge, docs_project_commands_make_validate_evaluation [INFERRED 0.85]
- **Authorization-during-retrieval chain** — docs_project_decisions_d006, docs_project_decisions_d035, docs_project_decisions_d040, docs_project_decisions_d045, docs_project_decisions_d052 [INFERRED 0.85]
- **Evaluation format and gates** — docs_project_decisions_d037, docs_project_decisions_d043, docs_project_decisions_d044, docs_project_decisions_d047, docs_project_decisions_d053, docs_project_decisions_d054 [INFERRED 0.85]
- **Spec-driven workflow decisions** — docs_project_decisions_d021, docs_project_decisions_d022, docs_project_decisions_d023, docs_project_decisions_d031 [INFERRED 0.85]
- **Hybrid retrieval pipeline: dense, lexical, fusion, rerank** — docs_project_tech_stack_qdrant, docs_project_tech_stack_bge_m3, docs_project_tech_stack_sqlite_fts5, docs_project_tech_stack_bm25, docs_project_tech_stack_rrf, docs_project_tech_stack_reranking [INFERRED 0.85]
- **Hybrid retrieval pipeline (dense, BM25, RRF, reranker)** — way2australia_ai_platform_implementation_plan_bge_m3, way2australia_ai_platform_implementation_plan_hybrid_rrf, way2australia_ai_platform_implementation_plan_reranker, way2australia_ai_platform_implementation_plan_qdrant [INFERRED 0.85]
- **Lexical stack: tokenizer, FTS5 store and index-lexical command** — kiro_specs_007_hybrid_retrieval_design_lexical_v1_tokenizer, kiro_specs_007_hybrid_retrieval_design_sqlite_fts5_lexical_store, docs_project_commands_make_index_lexical [INFERRED 0.85]
- **Task-gated spec workflow** — docs_project_decisions_d023, docs_project_decisions_d031, docs_project_workflow_task_gated_loop, docs_project_workflow_retrospective [INFERRED 0.85]

## Communities (170 total, 26 thin omitted)

### Community 0 - "DenseRetriever"
Cohesion: 0.07
Nodes (54): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+46 more)

### Community 1 - "Task Review Log (T7)"
Cohesion: 0.08
Nodes (68): Implementation, Review, T7 — round 1, User decision, _changed(), compare(), Comparison, _delta_line() (+60 more)

### Community 2 - "Security Fixture Corpus"
Cohesion: 0.06
Nodes (28): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, normalize_body(), document_fields() (+20 more)

### Community 3 - "test_eligibility.py"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 4 - "Evaluation Schemas"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_not_suggested(), test_candidate_referenced_by_suite(), test_candidate_unknown_and_ineligible_documents() (+23 more)

### Community 5 - "Strategy"
Cohesion: 0.08
Nodes (31): R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Testing / evaluation strategy, Implementation, Implementation, Review, Review, T5 — round 1, T5 — round 2 (+23 more)

### Community 6 - "RetrievalConfigurationError"
Cohesion: 0.08
Nodes (23): Implementation, Review, T2 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, dedupe_sections(), section_key() (+15 more)

### Community 7 - "test_cli_config.py"
Cohesion: 0.14
Nodes (20): clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+12 more)

### Community 8 - "test_retriever.py"
Cohesion: 0.13
Nodes (22): IndexPoint, build_client(), docs(), guest(), make_point(), open_spy(), RaisingEmbedder, retriever() (+14 more)

### Community 9 - "evaluation/cli.py"
Cohesion: 0.07
Nodes (32): R8 — Result format 2.2 (`retrieval_eval.py`), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), real_embedder_factory() (+24 more)

### Community 10 - "QdrantIndexStore"
Cohesion: 0.09
Nodes (33): IndexSettingsMismatchError, IndexSettings, IndexedDocument, QdrantIndexStore, read_index_settings(), CountingStore, client(), _keyword_indexed() (+25 more)

### Community 11 - "documents/__init__.py"
Cohesion: 0.21
Nodes (5): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority

### Community 12 - "retrieval_eval.py"
Cohesion: 0.12
Nodes (16): CaseStatus, DatasetType, LoadedSuite, active_golden_cases(), _fusion_report(), _leg_latency(), _lexical_report(), _notes() (+8 more)

### Community 13 - "security_index.py"
Cohesion: 0.07
Nodes (25): R11 — Security gate (`security_index.py`, `security_eval.py`), Acceptance criteria, Implementation, Review, T8 — round 1, EvaluationHarnessError, _lexical_sanity_check(), _open_lexical_sanity() (+17 more)

### Community 14 - "Model Tiers"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 15 - "Day-1 Data and Sources"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 16 - "Strategy Eval Tests"
Cohesion: 0.11
Nodes (28): User decision, build_lexical(), eval_world(), lexical_env(), make_world(), retrieve(), retrieve_world(), run_strategy() (+20 more)

### Community 17 - "KnowledgeDocument"
Cohesion: 0.08
Nodes (8): _check_language_code(), KnowledgeDocument, DocumentNotFoundError, LocalDocumentRepository, _corpus_problems(), test_real_fixture_folder_builds(), ListRepository, IgnoresQueryRepository

### Community 18 - "Index Binding Errors"
Cohesion: 0.10
Nodes (43): EmbedderInfo, IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings() (+35 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 20 - "Retrieval Eval Tests"
Cohesion: 0.13
Nodes (31): UnanswerableCase, deterministic_clock(), equivalence_suite(), basic_suite(), build(), golden(), run(), suite_of() (+23 more)

### Community 21 - "HeadingChunker"
Cohesion: 0.08
Nodes (48): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+40 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.33
Nodes (22): build_repo(), metadata(), problems_for(), run_cli(), test_all_model_errors_are_listed(), test_disabled_synthetic_document_is_not_retrievable(), test_duplicate_id_exits_one_with_document_id(), test_entry_outside_approved_roots_is_reported() (+14 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.11
Nodes (12): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+4 more)

### Community 24 - "test_lexical_build.py"
Cohesion: 0.06
Nodes (51): LexicalIndexBindingError, _read_only_connection(), build_production(), identity(), ingest_dense(), open_lexical(), payload(), rewrite_settings() (+43 more)

### Community 25 - "retrieval/errors.py"
Cohesion: 0.09
Nodes (26): R1 — Failure classification (`errors.py`, `availability.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), classify_model_error(), _optional_types(), caused_by(), GatedRepoError, handled_error(), LocalEntryNotFoundError (+18 more)

### Community 26 - "typing"
Cohesion: 0.07
Nodes (17): _group_installed(), _parse_sections(), _Section, _split_body(), _split_words(), format_summary(), main(), _parser() (+9 more)

### Community 27 - "FakeEmbedder"
Cohesion: 0.09
Nodes (15): FakeEmbedder, __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected() (+7 more)

### Community 28 - "test_manifest_validation.py"
Cohesion: 0.21
Nodes (22): load_schema(), manifest_document_count(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors() (+14 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.16
Nodes (18): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+10 more)

### Community 30 - "test_security_eval.py"
Cohesion: 0.06
Nodes (56): run_security_evaluation(), security_document(), SecurityQuery, SecurityReport, build(), clean_env(), copy_fixtures(), DroppedClauseLexical (+48 more)

### Community 31 - "repositories/__init__.py"
Cohesion: 0.10
Nodes (10): _authority_map(), collect(), _document_ids(), collect(), DocumentQuery, EligibilityPolicy, list_eligible_documents(), test_candidate_ineligible_document_is_not_unknown() (+2 more)

### Community 32 - "Retrieval Package"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 33 - "test_baseline.py"
Cohesion: 0.06
Nodes (46): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+38 more)

### Community 34 - "test_lexical_cli.py"
Cohesion: 0.10
Nodes (35): Implementation, Implementation, Review, T3 — round 2, T3 — round 3, User decision, check_target_allowed(), _inside_git_work_tree() (+27 more)

### Community 35 - "Architecture Decisions (DECISIONS.md)"
Cohesion: 0.10
Nodes (27): Phase 2 analytics event contracts, BGE-M3 embedder, DenseIndex / DenseRetriever, Heading chunker (2000-char cap), Index settings and index_version, Phase 2 storage (S3 plus metadata DB), Python/FastAPI backend and Next.js frontend, packages/rag reusable package (+19 more)

### Community 36 - "Review"
Cohesion: 0.14
Nodes (19): Implementation, Implementation, Review, Review, T6 — round 1, T6 — round 2, User decision, document_leg_ranks() (+11 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.06
Nodes (31): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+23 more)

### Community 38 - "Health Endpoint"
Cohesion: 0.09
Nodes (15): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+7 more)

### Community 39 - "Evaluation Slices"
Cohesion: 0.13
Nodes (12): active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error() (+4 more)

### Community 40 - "pytest"
Cohesion: 0.31
Nodes (7): chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank()

### Community 41 - "lexical/store.py"
Cohesion: 0.09
Nodes (25): Implementation, Review, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R4 — Freshness from the repository (`lexical/freshness.py`) (+17 more)

### Community 42 - "test_date_and_policy.py"
Cohesion: 0.39
Nodes (4): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads()

### Community 43 - "asyncio"
Cohesion: 0.14
Nodes (22): LocalRepositoryConfig, test_seed_corpus_is_one_main_chunk_per_document(), test_repository_content_hash_is_content_hash_v1(), test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version() (+14 more)

### Community 44 - "Strategy"
Cohesion: 0.13
Nodes (27): T4 — Fallback policy for `hybrid` and result marking, Verification, Strategy, FallbackRetriever, access(), client_at(), closed_port(), Fallback (+19 more)

### Community 45 - "test_repository_contract.py"
Cohesion: 0.21
Nodes (10): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+2 more)

### Community 46 - "evaluation/validate.py"
Cohesion: 0.11
Nodes (18): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+10 more)

### Community 47 - "DenseIndex"
Cohesion: 0.09
Nodes (37): LexicalRow, DenseIndex, build(), dense_fixture(), DroppedClauseIndex, guest(), pub(), retriever() (+29 more)

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (24): --allow-fake, BASELINE_ARGS (--allow-fake, --suite, --release, --output), retrieval-baseline-<index_version>-<UTC>.json (format 1.0), evaluation/candidates/ candidate files, eval-compare gate rule (more than 1 fewer hits or MRR drop above 1/n), retrieval-evaluation result format (kind retrieval_evaluation, schema 2.1), python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, evaluation schemas (evaluation_suite, evaluation_case_types, evaluation_case) (+16 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.07
Nodes (27): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+19 more)

### Community 50 - "Evaluation Suite (public-eval-v1)"
Cohesion: 0.09
Nodes (20): Atomic publish and rollback, Phase 2 audit trail, AWS deployment architecture (ap-south-1), Controlled document-change workflow (Release Candidate), CI/CD pipeline, Document manifest, DocumentRepository, Evaluation governance states (+12 more)

### Community 51 - "documents/__init__.py"
Cohesion: 0.11
Nodes (22): Chunks, embeddings and indexes as derived artifacts, content-hash-v1 change detection, DocumentRepository Protocol, EligibilityPolicy, 17-field index payload and point IDs, IngestionService, Language vs authorization separation, LocalDocumentRepository (+14 more)

### Community 52 - "Roadmap"
Cohesion: 0.17
Nodes (21): Roadmap, Evaluation Governance (keep/modify/deprecate/replace), Future capabilities, Phase 0 bootstrap, Roadmap item 1 - Project foundation, Roadmap item 10 - Grounded generation + citations, Roadmap item 11 - Observability, Roadmap item 12 - Security (+13 more)

### Community 53 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.07
Nodes (25): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), R9 — Result format 2.1, Acceptance criteria (+17 more)

### Community 55 - "test_suite_v2.py"
Cohesion: 0.16
Nodes (21): committed(), edit_jsonl(), lines(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as(), test_changed_query_is_a_problem_without_text() (+13 more)

### Community 56 - "Development Workflow"
Cohesion: 0.14
Nodes (17): Completion: retrospective, Spec-Review commit, merge, verified status, graphify knowledge graph, D031 Required retrospective that reconciles documentation, D048 graphify knowledge graph for coding agents (developer tooling), Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue (+9 more)

### Community 57 - "test_opening.py"
Cohesion: 0.11
Nodes (10): load_ingestion_config(), collection_name(), test_collection_name_derivation(), block_model_stack(), fake_lexical(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model() (+2 more)

### Community 58 - "Phase 2 Knowledge Release workflow"
Cohesion: 0.11
Nodes (16): Admin review actions (keep, modify, deprecate, replace, accept, reject), Atomic publish, Document Snapshot, Evaluation architecture (Evaluation Suite), Deterministic impact analysis, index_version (new version means new collection), Knowledge Release, LLM gap analysis / suggested cases (+8 more)

### Community 59 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 60 - "COMMANDS.md (project command surface)"
Cohesion: 0.12
Nodes (17): COMMANDS.md (project command surface), agent-skills/ canonical source and mirrors (.claude/.agents/.kiro skills), optional bge-m3 extra (sentence-transformers, PyTorch), Experiment result record fields (commit, release, suite, chunker, embedding, strategy, reranker, prompt, metrics), graphify developer tooling (update, query, path, explain, /graphify . --update), make experiment CONFIG=..., make format, make lint (ruff check + ruff format --check) (+9 more)

### Community 62 - "test_strategy.py"
Cohesion: 0.20
Nodes (13): _DenseLike, load_retrieval_config(), test_build_retriever_converts_a_string_value_and_refuses_unknown(), test_build_retriever_maps_each_strategy(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_lexical_strategies_need_the_lexical_index() (+5 more)

### Community 63 - "roles"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 64 - "test_text.py"
Cohesion: 0.29
Nodes (4): test_retrieve_cli_hit_line_is_single_clean_line(), test_safe_text_keeps_malayalam_joiners(), test_safe_text_strips_bidi_controls_but_keeps_zwj_zwnj(), test_safe_text_strips_controls_and_ansi()

### Community 65 - "DenseRetriever"
Cohesion: 0.15
Nodes (17): BM25Retriever, build_access_filter, build_retriever, check_hit (fail-closed re-check), Dense query flow, DenseRetriever, HybridRetriever, resolve_access / ResolvedAccess / guest_access (+9 more)

### Community 66 - "BGE-M3 embeddings"
Cohesion: 0.25
Nodes (7): BgeM3Embedder, Embedder Protocol, FakeEmbedder, Amazon Bedrock Runtime, BGE-M3 embeddings, Multilingual design (lote_languages), Technology stack

### Community 67 - "D042 Governed suite loader, validator and schema files (Spec 006)"
Cohesion: 0.15
Nodes (17): AccessContext, Role and resolve_access, Guest/public access scope, Human-governed LLM suggestions (candidates), Suite public-eval-v2, Governed suite loader and validator, D007 Public-only Phase 1, D014 Evaluation Suite model, D015 Human-governed LLM suggestions (+9 more)

### Community 68 - "FallbackReason"
Cohesion: 0.09
Nodes (23): 008 — Retrieval Fallback Design, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability, Package / file placement, R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`) (+15 more)

### Community 69 - "test_goldens.py"
Cohesion: 0.22
Nodes (12): RetrievalConfigurationError, declared_release_id(), load_golden_cases(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused() (+4 more)

### Community 70 - "Phase 1 RAG query pipeline"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 71 - "healthcheck"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 72 - "Evaluation framework (Spec 006)"
Cohesion: 0.15
Nodes (15): Decisions D042-D047, eval-compare quality gate and identity refusals, Evaluation schemas (referencing registry), Evaluation framework (Spec 006), load_suite (read-only suite loader), make eval-compare, make eval-retrieval, make eval-security (+7 more)

### Community 73 - "make ingest"
Cohesion: 0.16
Nodes (15): docker compose up/down, --embedder {bge_m3,fake}, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, Guest/public access (server-resolved, no role/scope/tenant option), INGEST_ARGS (--embedder, --config), Stale lexical file refusal (LexicalIndexBindingError), make ingest, make retrieve (+7 more)

### Community 75 - "Section: Next step"
Cohesion: 0.23
Nodes (15): Result: real BGE-M3 dense baseline 2026-10-23 (HitRate@5 0.952, MRR 0.878, 63 cases), Result: dense reference on public-eval-v2, 2026-10-25 (66/69 hits, MRR 0.8816), Golden g004 (business_001_overview_scope): dense miss, hybrid hit, Golden g026 (business_006_mock_assessments): dense miss, hybrid hit, Golden g061 (official_002_candidate_rules_setup): miss in dense, BM25 and hybrid, Unanswerable case u001 (overlaps g004; owner decided keep_both), Finding: hybrid ranks relevant doc lower than dense in g006, g029, g064, g065, Known issue: BM25/hybrid need Qdrant and bge-m3 extra (no graceful degradation, roadmap 13) (+7 more)

### Community 76 - "Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)"
Cohesion: 0.18
Nodes (15): Result: eval-retrieval 2.0 on public-eval-v1, 2026-10-24 (60 hits, MRR 0.8783), Capability: BM25Retriever with SQL access clause; Retriever Protocol and Strategy (retrieval/base.py), Capability: make eval-compare (1/n MRR gate, identity refusals), Capability: make eval-security authorization hard gate (throwaway w2a-sectest collection; dense, bm25, hybrid; result 1.1), Capability: rrf_fuse, HybridRetriever, config/retrieval.yaml (RRF k 60, depth 50), build_retriever, Capability: lexical-v1 tokenizer, SQLite FTS5 lexical store, make index-lexical, W2A_LEXICAL_INDEX_DIR, Capability: --strategy flag on make retrieve / eval-retrieval, result format 2.1, Decisions D042-D046 (Spec 006 evaluation framework) (+7 more)

### Community 77 - "typing"
Cohesion: 0.14
Nodes (15): Evaluation candidate rows file 006-candidates.jsonl (7 suggested rows), Evaluation suite public-eval-v2 (91 cases, Malayalam goldens g064-g069; v1 replaced), Decision D049: public-eval-v2 replaces v1; releases are Phase 2, Decision D050: lexical index design; one lexical file per access scope in future, Decision D051: lexical-v1 tokenizer and chillu handling, Known issue: BM25 statistics span all rows of a lexical file (safe today; per-scope files needed for roles), Deferred: fluent-speaker/owner review of agent-drafted Malayalam candidates and g004/u001 proposal, Known issue: lexical-v1 legacy chillu sequence not matched with atomic chillu (+7 more)

### Community 78 - "HybridRetriever (dense leg then BM25 leg, no single-leg fallback)"
Cohesion: 0.14
Nodes (14): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, RRF fusion (k 60, equal weights, depth 50, fail closed), Security gate over dense, bm25 and hybrid (+6 more)

### Community 79 - "Task-gated agent workflow loop"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 80 - "embedder"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 81 - "packages/rag"
Cohesion: 0.20
Nodes (12): apps/api (FastAPI layer), apps/web (Next.js frontend), Repository boundaries, apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing (+4 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.13
Nodes (20): Embedder and index settings binding, Chunker Protocol, Decisions D025-D030, D032, DenseIndex, HeadingChunker (heading v1), IndexSettings, Ingestion pipeline (Spec 004), ingestion cli (exit codes 0/1/2) (+12 more)

### Community 83 - "DocumentRepository Protocol"
Cohesion: 0.18
Nodes (10): Derived artifacts (chunks, embeddings, sparse index, Qdrant points), DocumentRepository Protocol, KnowledgeDocument, Knowledge model metadata, LocalDocumentRepository, Phase 1 (guest/public RAG), Phase 2, S3 immutable document bodies (+2 more)

### Community 84 - "Engineering Conventions"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 85 - "D050 SQLite FTS5 lexical store, not Qdrant sparse vectors (Spec 007)"
Cohesion: 0.24
Nodes (14): Server-created authorization filter, build_access_filter and check_hit, Lexical FTS5 file and index-lexical, Qdrant primary vector index, Reciprocal Rank Fusion / HybridRetriever, SQLite FTS5 lexical store, D006 Authorization during retrieval, D010 Qdrant primary, SQLite FTS5 fallback (+6 more)

### Community 86 - "D055 Default strategy is hybrid (Spec 007)"
Cohesion: 0.23
Nodes (14): Baseline result format 1.0, Default retrieval strategy hybrid, eval-compare quality gate, Retrieval evaluation result 2.0/2.1, make eval-security hard gate, D037 Baseline result format (Spec 005), D043 Result format 2.0 for retrieval evaluation; compare still reads 1.0 (Spec 006), D044 Quality gate for eval-compare (Spec 006) (+6 more)

### Community 87 - "test_lexical_tokenizer.py"
Cohesion: 0.11
Nodes (18): _is_token_char(), query_terms(), QueryTerms, tokenize(), test_no_language_literal_in_evaluation_code(), test_no_malayalam_specific_lote_languages_in_ingestion_code(), test_business_008_words_stay_whole(), test_deterministic() (+10 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.29
Nodes (7): Spec orchestrator loop (route, role subagents, user approval, merge), Portable agent skills (agent-skills/ mirrors), Spec Status lines and review.md, Task-gated workflow, D021 Portable spec-driven agent skills, D022 Spec approval and review state live in the repository, D023 Task-gated agent workflow

### Community 90 - "LexicalIndex (SQLite FTS5 store)"
Cohesion: 0.17
Nodes (12): build_lexical_index / production_entries, D050 per-scope lexical files, D055 default strategy hybrid, Decisions D049-D055, GUEST_PUBLIC_POLICY / EligibilityPolicy, Hybrid retrieval flow (default strategy), LexicalIndex (SQLite FTS5 store), lexical package (Spec 007) (+4 more)

### Community 91 - "Spec 005 - dense retrieval baseline (verified 2026-10-23, merged b33462e)"
Cohesion: 0.18
Nodes (13): Capability: dense retrieval (AccessContext, DenseIndex, build_access_filter, check_hit, DenseRetriever, make retrieve), Capability: Pydantic document models, DocumentRepository, LocalDocumentRepository, content-hash-v1, EligibilityPolicy, make validate-knowledge, Capability: evaluation suite loader, make validate-evaluation, make eval-retrieval (result 2.0), Capability: ingestion (HeadingChunker, Embedder Protocol + fake/BGE-M3, QdrantIndexStore, IngestionService, make ingest), Capability: make retrieval-baseline (legacy, frozen; HitRate@k, Recall@k, MRR, latency), Decisions D025-D030 and D032 (ingestion; persona_scope informational, one version per document_id, chunking), Decisions D033-D041 (Spec 005; D040/D041 added by retrospective), Section: Ingestion operating notes (+5 more)

### Community 92 - "Mock assessments, scoring, feedback and review windows"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 93 - "pathlib"
Cohesion: 0.11
Nodes (24): EvaluationConfigurationError, CaseBase, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, declared_release_id(), inside() (+16 more)

### Community 94 - "AGENTS.md Project Rules"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 95 - "make index-lexical"
Cohesion: 0.23
Nodes (11): BM25 lexical retrieval, dense retrieval strategy, hybrid retrieval (RRF fusion of dense and BM25), LEXICAL_ARGS (--embedder, --output, --config), lexical SQLite FTS5 file (.local/lexical/<collection>.sqlite), Lexical output target refusal rules (knowledge/, evaluation/, config/, non-ignored in git), lexical-v1 tokenizer, make index-lexical (+3 more)

### Community 96 - "IngestionService"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 98 - "Knowledge Schema and Metadata"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.20
Nodes (9): Section: Current goal (Spec 007 merged, next spec not chosen), Decision D038: BGE-M3 device recorded in results, not pinned, Decision D055: default strategy hybrid, Outcome: default_strategy set to hybrid (R13 rule satisfied), Section: Finalized high-level decisions, Section: Current implementation status, Known issue: BGE-M3 device (mps) not pinned; reproducibility across machines, Section: Seed data status (+1 more)

### Community 100 - "QdrantIndexStore"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 101 - "Baseline runner and result JSON"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 103 - "fusion"
Cohesion: 0.15
Nodes (12): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+4 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.20
Nodes (10): AccessContext and Role, Baseline runner (baseline.py), D035 fallbacks take the same ResolvedAccess, Decisions D033-D041, make retrieval-baseline (legacy), make retrieve, Document-level metrics (HitRate@k, Recall@k, MRR), Retrieval package (Spec 005 and 007) (+2 more)

### Community 105 - "Section: Spec status table"
Cohesion: 0.22
Nodes (10): Foundation: uv workspace, FastAPI /health, settings, pytest, Ruff/Pyright, make verify, local Qdrant compose, Task-gated spec skills (spec-orchestrator, planner, implementer, task-reviewer, spec-reviewer) and make skills-sync/check, Section: Current phase (Phase 1 foundation complete), Decision D023: task state lifecycle and spec Status values, Decision D031: spec-reviewer retrospective required, Spec 002 retrospective round 1 (F1-F6, handled by Spec 004 or open), Spec 001 - project foundation (implemented, no review.md), Spec 002 - document model and repository (verified 2026-10-15, merged dca6cbd) (+2 more)

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.20
Nodes (10): Containers layer, Docker, Docker Compose, Kubernetes / EKS (avoided), Multiple vector databases (avoided), Phase 2 storage direction, Qdrant (vector database), qdrant-client (+2 more)

### Community 107 - "opening.py"
Cohesion: 0.04
Nodes (53): T8 — Security gate for BM25 and hybrid, Docker isolation test, Verification, As-built notes, Components / boundaries, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R5 — `bm25` without Qdrant or the extra (`bm25.py`), R6 — `FallbackRetriever` (`fallback.py`) and `open_retrieval` (`opening.py`), R9 — `eval-compare` (`results.py`, `compare.py`) (+45 more)

### Community 108 - "NAATI CCL booking, fees, cancellation, results and credential validity"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 109 - "retrieval/test_access.py"
Cohesion: 0.17
Nodes (13): clean_env(), guest(), payload(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload(), test_check_hit_rejects_violations(), test_default_tenant(), test_empty_tenant_setting_refused() (+5 more)

### Community 111 - "test_content_hash.py"
Cohesion: 0.23
Nodes (13): _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order() (+5 more)

### Community 112 - "test_repository_contract.py"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 114 - "pytest"
Cohesion: 0.25
Nodes (9): Answerability / insufficient-evidence decision, Amazon Bedrock generation, Citation validation, Context builder (planned), Langfuse AI observability, LanguageContext, Primary stack, Multilingual reranker (planned) (+1 more)

### Community 115 - "test_bm25.py"
Cohesion: 0.22
Nodes (8): Amazon Bedrock Runtime generator, D012 Bedrock Runtime for generation, Bedrock Knowledge Bases as core RAG (avoided), Amazon CloudWatch (infrastructure/application operations), Langfuse (RAG/application tracing), AWS Mumbai ap-south-1 initial region, Observability layer, Likely Phase 1 AWS services: EC2, ECR, EBS, S3, IAM, CloudWatch, SSM, Bedrock Runtime

### Community 116 - "fusion"
Cohesion: 0.25
Nodes (8): AWS target, Developer tooling, Frontend layer, GitHub Actions (CI/CD), graphify (graphifyy) knowledge graph for coding agents, D048; not a product dependency, Next.js, Terraform (Infrastructure as Code), TypeScript

### Community 117 - "evaluation/cli.py"
Cohesion: 0.28
Nodes (9): Backend layer, FastAPI, httpx, jsonschema (manifest validation), Pandas (where useful), Pydantic / Pydantic Settings, Python, pyyaml (frontmatter parsing) (+1 more)

### Community 118 - "retrieval/test_access.py"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 119 - "test_authorization_isolation.py"
Cohesion: 0.21
Nodes (4): client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed()

### Community 120 - "build_security_repository"
Cohesion: 0.20
Nodes (7): build_security_repository(), _fixture_files(), compute_body_sha256(), compute_content_hash(), sha256_hex(), security_repository(), test_seed_documents_match_manifest_hashes()

### Community 121 - "test_status_handling.py"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 122 - "test_index_contract.py"
Cohesion: 0.09
Nodes (20): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Chunk, build_payload(), PointPayload, compare(), mismatch_message(), base_settings(), test_authorization_and_language_fields_are_separate() (+12 more)

### Community 124 - "hashing.py"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 125 - "test_security_eval.py"
Cohesion: 0.36
Nodes (7): Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Fine-tuning (avoided), Heavyweight framework abstractions hiding retrieval/evaluation (avoided), LangGraph (avoided), Complex microservices (avoided)

### Community 126 - "test_failed_write_removes_partial_file"
Cohesion: 0.32
Nodes (7): Custom retrieval metrics (HitRate@k, Recall@k, MRR; plain Python, Spec 005), DeepEval (where useful, not yet a dependency), Evaluation layer, Generation/e2e metrics: correctness, faithfulness, answer relevance, citation correctness/coverage, refusal quality, failure rate, Primary retrieval metrics: Recall@5, MRR, HitRate@5, pytest, referencing (evaluation schema $ref registry, Spec 006)

### Community 127 - "Development Workflow"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 130 - "evaluation/test_cli.py"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 131 - "RuntimeSettings"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 132 - "retrieval_eval.py"
Cohesion: 0.43
Nodes (6): Sparse retrieval: BM25 via FTS5 bm25() over lexical-v1 tokens (D051), make index-lexical, RAG core layer, Reranking: local multilingual BGE reranker (planned), Reciprocal Rank Fusion (RRF), D052, config/retrieval.yaml, SQLite FTS5 lexical store (Spec 007, D050)

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 136 - "test_schemas.py"
Cohesion: 0.15
Nodes (9): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass(), manifest(), test_v1_manifest_differs_only_in_status() (+1 more)

### Community 137 - "dense_equivalence.py"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 139 - "Versioning and Releases"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 140 - "make eval-security"
Cohesion: 0.33
Nodes (6): Authorization hard gate (forbidden points never returned), EVAL_ARGS, make eval-security, throwaway collection w2a-sectest-<8 hex>, security fixtures (poisoned_public_document.md, staff_only_canary.md), security-evaluation result (kind security_evaluation, schema 1.1)

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.40
Nodes (5): BGE-M3 (initial embedding model), Embeddings, Deterministic fake embedder (tests and CI), Pinned model revision (commit SHA in config/ingestion.yaml); device not pinned, recorded (D038), sentence-transformers (optional bge-m3 extra, brings PyTorch)

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 143 - "Spec 004 retrospective round 1 (PASS)"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

### Community 144 - "eval-compare"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 146 - "Home Affairs credentialled community language points"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 147 - "make test"
Cohesion: 0.50
Nodes (4): integration-marked tests (skip when Qdrant unreachable), make test, make test-integration, make test-unit

### Community 148 - "Mission"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 149 - "Way2Australia public offering and assistant scope"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 150 - "Materials and dialogue practice"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 157 - "Canonical document metadata"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 175 - "sync_agent_skills.py"
Cohesion: 0.29
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 178 - "AccessContext"
Cohesion: 0.14
Nodes (9): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+1 more)

### Community 179 - "canonical_json"
Cohesion: 0.47
Nodes (4): canonical_json(), _canonical_value(), _canonical_value_mapping(), test_canonical_json_is_sorted_compact_and_keeps_unicode()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **282 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+277 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1077 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `As-built notes` connect `DenseRetriever` to `DenseRetriever`, `opening.py`, `Strategy`, `HybridRetriever (dense leg then BM25 leg, no single-leg fallback)`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 74 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 74 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _282 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DenseRetriever` be split into smaller, more focused modules?**
  _Cohesion score 0.06835290575127974 - nodes in this community are weakly interconnected._
- **Why does `Spec 007 retrospective round 1 PASS` connect `DenseRetriever` to `Development Workflow`, `DenseRetriever`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 20 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._