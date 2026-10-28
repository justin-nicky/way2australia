# Graph Report - way2australia  (2026-10-28)

## Corpus Check
- 239 files · ~215,587 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .example 1)

## Summary
- 2825 nodes · 8283 edges · 140 communities (118 shown, 22 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 1345 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `20aae904`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QdrantIndexStore
- evaluation/validate.py
- typing
- HeadingChunker
- test_validate.py
- LocalRepositoryConfig
- LexicalIndex
- Eval Compare Gate
- DenseRetriever
- DenseRetriever
- test_suite_v2.py
- Model Tiers
- KnowledgeDocument
- test_retrieval_eval.py
- ingestion/cli.py
- security_index.py
- Day-1 Data and Sources
- Architecture Decisions
- Index Binding Errors
- Document Model Tests
- rrf_fuse
- Date and Policy Tests
- BGE-M3 Adapter
- Live-count Test Helpers
- test_schemas.py
- test_service.py
- list_eligible_documents
- LocalDocumentRepository
- suite.py
- Architecture Components
- FastAPI Health Endpoint
- Manifest Loading
- asyncio
- LocalDocumentRepository
- test_lexical_tokenizer.py
- Roadmap
- json
- 007 — Hybrid Retrieval Requirements
- test_lexical_build.py
- LexicalIndexBindingError
- test_goldens.py
- repositories/__init__.py
- Access Policy Config
- Constitution Principles
- Docker Compose Qdrant
- Authorization Design
- Agent Workflow Skills
- Ingestion Config File
- Engineering Conventions
- Phase 2 Governance
- Project Commands
- chunking.py
- Packages and Pricing
- Agent Project Rules
- retrieval/test_cli.py
- Spec 002 Repository Design
- Language Onboarding
- Current State
- Spec 001 Foundation
- Spec 005 Retrieval Design
- Spec 006 Loader and Snapshot
- Tech Stack
- CCL Booking and Fees
- Retrieval Roadmap Ideas
- Spec 006 Security Gate
- Source Precedence Config
- CCL Candidate Rules
- Planned Apps and AWS
- Spec 004 Eligibility Design
- Product Context
- CCL Format and Scoring
- Spec 006 Validation Design
- Spec 006 Retrieval Eval Design
- Vocabulary and Free Access
- Spec 002 Reviews
- Spec 006 Overview
- Versioning and Releases
- build.py
- Master Plan Overview
- Deployment and Degradation Plan
- Plan Repository Concepts
- Spec 004-005 Retros
- Spec 006 Compare Design
- Payments and Support
- Migration Points
- Security Plan
- Multilingual Plan
- Mission
- Business Overview
- Materials and Practice
- Implementer Codex Policy
- Orchestrator Codex Policy
- Spec Reviewer Codex Policy
- Task Reviewer Codex Policy
- Analytics Schemas
- Source Truth Principles
- Plan Metadata
- Docs Reading Order
- Workspace Packages
- Analytics Plan
- Plan Spec Sequence
- Root Project
- API Project
- Observability Project
- ingest_dense
- test_repository_contract.py
- test_violation_names_the_document_from_the_error_attribute
- re
- DenseIndex
- fusion
- evaluation/cli.py
- retrieval/test_access.py
- AccessContext
- Strategy
- test_content_hash.py
- test_lexical_cli.py
- Strategy
- hashing.py
- test_security_eval.py
- test_failed_write_removes_partial_file
- Development Workflow
- test_strategy_eval.py
- FakeEmbedder
- evaluation/test_cli.py
- LoadedSuite
- retrieval_eval.py
- Review
- .open
- security_eval.py
- security_repository
- dense_equivalence.py
- metrics.py
- point_id

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 88 edges
2. `LocalDocumentRepository` - 61 edges
3. `FakeEmbedder` - 56 edges
4. `EvaluationConfigurationError` - 55 edges
5. `DenseRetriever` - 51 edges
6. `run_retrieval_evaluation()` - 49 edges
7. `HeadingChunker` - 49 edges
8. `QdrantIndexStore` - 49 edges
9. `Architecture Decisions` - 47 edges
10. `Strategy` - 46 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Testing / evaluation strategy` --references--> `rrf_fuse()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/retrieval/fusion.py
- `R9 — Result format 2.1` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/tests/retrieval/test_bm25.py
- `Acceptance criteria` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/tests/retrieval/test_bm25.py
- `Acceptance criteria` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/tests/retrieval/test_bm25.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Authorization enforced inside every retrieval leg** — docs_project_decisions_d035, docs_project_decisions_d040, docs_project_architecture_check_hit, docs_project_architecture_build_access_filter [EXTRACTED 1.00]
- **Evaluation make targets sharing the suite loader** — _kiro_specs_006_evaluation_framework_design_validate_evaluation, _kiro_specs_006_evaluation_framework_design_eval_retrieval, _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_eval_compare, _kiro_specs_006_evaluation_framework_design_suite_loader [EXTRACTED 1.00]
- **Guest authorization path (resolve, filter, re-check)** — _kiro_specs_005_dense_retrieval_baseline_design_accesscontext, _kiro_specs_005_dense_retrieval_baseline_design_resolve_access, _kiro_specs_005_dense_retrieval_baseline_design_build_access_filter, _kiro_specs_005_dense_retrieval_baseline_design_check_hit [EXTRACTED 1.00]
- **Ingestion pipeline components** — _kiro_specs_004_ingestion_baseline_design_ingestionservice, _kiro_specs_004_ingestion_baseline_design_headingchunker, _kiro_specs_004_ingestion_baseline_design_embedder_protocol, _kiro_specs_004_ingestion_baseline_design_qdrantindexstore [EXTRACTED 1.00]
- **Authorization hard gate construction** — _kiro_specs_006_evaluation_framework_design_eval_security, _kiro_specs_006_evaluation_framework_design_security_index, _kiro_specs_006_evaluation_framework_design_forbidden_variants, _kiro_specs_006_evaluation_framework_design_one_access_path, _kiro_specs_006_evaluation_framework_design_security_gate [EXTRACTED 1.00]
- **Task-gated spec workflow roles** — agent_skills_spec_orchestrator_skill_spec_orchestrator_skill, agent_skills_spec_planner_skill_spec_planner_skill, agent_skills_spec_implementer_skill_spec_implementer_skill, agent_skills_task_reviewer_skill_task_reviewer_skill, agent_skills_spec_reviewer_skill_spec_reviewer_skill [EXTRACTED 1.00]
- **Task-gated workflow roles** — _kiro_specs_003_task_gated_workflow_design_spec_orchestrator, _kiro_specs_003_task_gated_workflow_design_spec_implementer, _kiro_specs_003_task_gated_workflow_design_task_reviewer, _kiro_specs_003_task_gated_workflow_design_spec_planner, _kiro_specs_003_task_gated_workflow_design_spec_reviewer [EXTRACTED 1.00]
- **Language, access and source authority separation** — docs_knowledge_schema_and_metadata_access_scope, docs_knowledge_schema_and_metadata_lote_languages, docs_knowledge_schema_and_metadata_authorization_vs_language_independence, docs_knowledge_source_of_truth_source_precedence [INFERRED 0.75]
- **Knowledge Release composition** — way2australia_ai_platform_implementation_plan_knowledge_release, way2australia_ai_platform_implementation_plan_evaluation_suite, way2australia_ai_platform_implementation_plan_release_manifest, way2australia_ai_platform_implementation_plan_document_manifest [INFERRED 0.75]
- **Security regression controls** — way2australia_ai_platform_implementation_plan_staff_only_canary, way2australia_ai_platform_implementation_plan_poisoned_public_document, way2australia_ai_platform_implementation_plan_graceful_degradation, way2australia_ai_platform_implementation_plan_authorization_before_generation [INFERRED 0.75]
- **Hybrid retrieval pipeline (dense, BM25, RRF, reranker)** — way2australia_ai_platform_implementation_plan_bge_m3, way2australia_ai_platform_implementation_plan_hybrid_rrf, way2australia_ai_platform_implementation_plan_reranker, way2australia_ai_platform_implementation_plan_qdrant [INFERRED 0.85]
- **Task-gated spec workflow** — docs_project_decisions_d023, docs_project_decisions_d031, docs_project_workflow_task_gated_loop, docs_project_workflow_retrospective [INFERRED 0.85]

## Communities (140 total, 22 thin omitted)

### Community 0 - "QdrantIndexStore"
Cohesion: 0.06
Nodes (50): IndexSettingsMismatchError, PointPayload, build_index_settings(), collection_name(), compare(), IndexSettings, mismatch_message(), IndexedDocument (+42 more)

### Community 1 - "evaluation/validate.py"
Cohesion: 0.11
Nodes (19): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+11 more)

### Community 2 - "typing"
Cohesion: 0.10
Nodes (8): build_embedder(), default_client_factory(), resolve_access(), _parser(), RetrievalError, chunk(), pub_chunk(), test_seed_corpus_retrieval_under_guest_access()

### Community 3 - "HeadingChunker"
Cohesion: 0.14
Nodes (27): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+19 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "LocalRepositoryConfig"
Cohesion: 0.13
Nodes (13): document_fields(), LocalRepositoryConfig, under_root(), _duplicate_reason(), _error_problems(), main(), _model_problems(), _unlisted_files() (+5 more)

### Community 6 - "LexicalIndex"
Cohesion: 0.08
Nodes (15): Acceptance criteria, Decisions resolved before drafting, 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test, T9 — Strategy comparison and default-strategy decision (user-owned gate) (+7 more)

### Community 7 - "Eval Compare Gate"
Cohesion: 0.07
Nodes (65): _changed(), compare(), Comparison, _delta_line(), _embedder(), _fmt_key(), _hits(), _identity_problems() (+57 more)

### Community 8 - "DenseRetriever"
Cohesion: 0.10
Nodes (39): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+31 more)

### Community 9 - "DenseRetriever"
Cohesion: 0.06
Nodes (42): IndexPoint, case(), clean_env(), cli_run(), DeviceStub, run(), seeded(), setup() (+34 more)

### Community 10 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 11 - "Model Tiers"
Cohesion: 0.05
Nodes (20): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Orchestrator State Machine, Spec Orchestrator Skill, Design Template (+12 more)

### Community 12 - "KnowledgeDocument"
Cohesion: 0.09
Nodes (7): _check_language_code(), KnowledgeDocument, _canary_points(), Chunker, CountingEmbedder, ListRepository, IgnoresQueryRepository

### Community 13 - "test_retrieval_eval.py"
Cohesion: 0.17
Nodes (27): basic_suite(), build(), golden(), run(), suite_of(), suite_with_unanswerable(), test_active_golden_without_relevant_documents_is_refused(), test_case_access_context_never_widens_access() (+19 more)

### Community 14 - "ingestion/cli.py"
Cohesion: 0.11
Nodes (12): build_chunker(), format_summary(), main(), _parser(), ChunkerConfig, EmbedderConfig, IngestionConfig, load_ingestion_config() (+4 more)

### Community 15 - "security_index.py"
Cohesion: 0.13
Nodes (8): R11 — Security gate (`security_index.py`, `security_eval.py`), build_security_index(), delete_security_index(), _forbidden_payload(), require_security_base(), SecurityIndex, live_client(), test_server_filter_keeps_every_forbidden_point_out()

### Community 16 - "Day-1 Data and Sources"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 17 - "Architecture Decisions"
Cohesion: 0.08
Nodes (37): eval-compare quality gate, D001 - Python-first backend, D002 - RAG as reusable internal package, D003 - Knowledge outside RAG package, D006 - Authorization during retrieval, D007 - Public-only Phase 1, D008 - Language and authorization are independent, D009 - Source precedence (+29 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.17
Nodes (28): IndexBindingError, client(), fake_info(), make_settings(), open_index(), payload(), scope_filter(), seed() (+20 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 20 - "rrf_fuse"
Cohesion: 0.22
Nodes (13): rrf_fuse(), chunk(), test_both_legs_empty(), test_duplicate_in_a_leg_counts_best_rank_only(), test_empty_leg_keeps_the_other_order(), test_equal_scores_and_ranks_break_by_point_id(), test_equal_scores_break_by_best_rank_before_point_id(), test_first_seen_chunk_is_kept() (+5 more)

### Community 21 - "Date and Policy Tests"
Cohesion: 0.19
Nodes (28): test_roles_match_policy_file(), load(), test_bad_date_fails_loading_naming_document_and_field(), test_guest_policy_agrees_with_access_policy_config(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata() (+20 more)

### Community 22 - "BGE-M3 Adapter"
Cohesion: 0.10
Nodes (14): BgeM3Embedder, OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction() (+6 more)

### Community 23 - "Live-count Test Helpers"
Cohesion: 0.14
Nodes (20): clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+12 more)

### Community 24 - "test_schemas.py"
Cohesion: 0.18
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 25 - "test_service.py"
Cohesion: 0.21
Nodes (20): doc(), Harness, test_bumped_document_version_updates(), test_changed_body_updates(), test_changed_metadata_field_updates(), test_chunk_shrink_leaves_no_orphan(), test_delete_failure_is_reported_and_run_continues(), test_embedding_failure_keeps_old_points_and_continues() (+12 more)

### Community 26 - "list_eligible_documents"
Cohesion: 0.20
Nodes (16): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+8 more)

### Community 27 - "LocalDocumentRepository"
Cohesion: 0.17
Nodes (14): LocalDocumentRepository, build(), guest_access(), real_queries(), test_builder_refuses_a_non_throwaway_base_before_any_write(), test_builder_refuses_an_existing_collection(), test_case_access_context_never_changes_the_filter(), test_filter_is_identical_for_every_query_including_after_s003() (+6 more)

### Community 28 - "suite.py"
Cohesion: 0.14
Nodes (14): CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, UnanswerableCase, declared_release_id() (+6 more)

### Community 29 - "Architecture Components"
Cohesion: 0.09
Nodes (28): AccessContext and Role, apps/api FastAPI layer, Amazon Bedrock Runtime, BGE-M3, Architecture, DocumentRepository Protocol, HeadingChunker, Ingestion pipeline (Spec 004) (+20 more)

### Community 30 - "FastAPI Health Endpoint"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 31 - "Manifest Loading"
Cohesion: 0.31
Nodes (17): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field(), test_malformed_json_line_reports_line_number() (+9 more)

### Community 32 - "asyncio"
Cohesion: 0.32
Nodes (14): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+6 more)

### Community 33 - "LocalDocumentRepository"
Cohesion: 0.11
Nodes (8): _document_ids(), collect(), DocumentQuery, DocumentRepository, EligibilityPolicy, list_eligible_documents(), _corpus_problems(), test_ineligible_document()

### Community 34 - "test_lexical_tokenizer.py"
Cohesion: 0.13
Nodes (14): _is_token_char(), tokenize(), test_no_language_literal_in_evaluation_code(), test_no_malayalam_specific_lote_languages_in_ingestion_code(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case(), test_golden_file_is_the_source_of_the_pins() (+6 more)

### Community 35 - "Roadmap"
Cohesion: 0.17
Nodes (21): Roadmap, Evaluation Governance (keep/modify/deprecate/replace), Future capabilities, Phase 0 bootstrap, Roadmap item 1 - Project foundation, Roadmap item 10 - Grounded generation + citations, Roadmap item 11 - Observability, Roadmap item 12 - Security (+13 more)

### Community 36 - "json"
Cohesion: 0.16
Nodes (16): load_suite(), live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_access_context_is_loaded_but_ignored() (+8 more)

### Community 37 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (32): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+24 more)

### Community 38 - "test_lexical_build.py"
Cohesion: 0.20
Nodes (18): build_lexical_index(), identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings() (+10 more)

### Community 39 - "LexicalIndexBindingError"
Cohesion: 0.29
Nodes (3): LexicalIndexBindingError, LexicalSettings, _read_only_connection()

### Community 40 - "test_goldens.py"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 41 - "repositories/__init__.py"
Cohesion: 0.09
Nodes (20): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, check_integrity_hashes(), check_manifest_documents(), compare_manifest_to_metadata() (+12 more)

### Community 42 - "Access Policy Config"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 43 - "Constitution Principles"
Cohesion: 0.15
Nodes (3): Constitution, D014 - Evaluation Suite model, D015 - Human-governed LLM suggestions

### Community 44 - "Docker Compose Qdrant"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 45 - "Authorization Design"
Cohesion: 0.14
Nodes (14): build_access_filter, check_hit fail-closed re-check, DenseIndex, DenseRetriever, Evaluation framework (Spec 006), Retrieval fallback paths, Security gate (eval-security), Target RAG query flow (+6 more)

### Community 46 - "Agent Workflow Skills"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 47 - "Ingestion Config File"
Cohesion: 0.14
Nodes (13): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+5 more)

### Community 48 - "Engineering Conventions"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 49 - "Phase 2 Governance"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 50 - "Project Commands"
Cohesion: 0.21
Nodes (13): Project Commands, CLI exit code convention 0/1/2, make eval-compare, make eval-retrieval, make eval-security, make ingest, make retrieval-baseline (legacy), make retrieve (+5 more)

### Community 51 - "chunking.py"
Cohesion: 0.09
Nodes (16): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, Chunk, _parse_sections(), _Section (+8 more)

### Community 52 - "Packages and Pricing"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 53 - "Agent Project Rules"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 54 - "retrieval/test_cli.py"
Cohesion: 0.06
Nodes (38): RuntimeSettings, _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client() (+30 more)

### Community 55 - "Spec 002 Repository Design"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 56 - "Language Onboarding"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 57 - "Current State"
Cohesion: 0.29
Nodes (11): Current State, Known issues: no pure ml golden, empty relevant_section_ids, Next step: Spec 007 hybrid retrieval, Not yet implemented list, Real BGE-M3 retrieval baseline (HitRate@5 0.952, MRR 0.878), Spec 001 project foundation, Spec 002 document model and repository, Spec 003 task-gated agent workflow (+3 more)

### Community 58 - "Spec 001 Foundation"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 59 - "Spec 005 Retrieval Design"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 60 - "Spec 006 Loader and Snapshot"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 61 - "Tech Stack"
Cohesion: 0.20
Nodes (9): Intentionally avoided choices, AWS Mumbai ap-south-1 target, Backend: Python, FastAPI, Pydantic, Tech Stack, Evaluation tooling: pytest, custom metrics, Generation: Amazon Bedrock Runtime, graphify developer tooling, Observability: Langfuse and CloudWatch (+1 more)

### Community 62 - "CCL Booking and Fees"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 63 - "Retrieval Roadmap Ideas"
Cohesion: 0.22
Nodes (10): Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Phase 1 RAG query pipeline, Raw sources (sources/raw), Multilingual reranker (+2 more)

### Community 64 - "Spec 006 Security Gate"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 65 - "Source Precedence Config"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 66 - "CCL Candidate Rules"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 67 - "Planned Apps and AWS"
Cohesion: 0.28
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 68 - "Spec 004 Eligibility Design"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 69 - "Product Context"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 70 - "CCL Format and Scoring"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 71 - "Spec 006 Validation Design"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 72 - "Spec 006 Retrieval Eval Design"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 73 - "Vocabulary and Free Access"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 74 - "Spec 002 Reviews"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 75 - "Spec 006 Overview"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 76 - "Versioning and Releases"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 77 - "build.py"
Cohesion: 0.21
Nodes (4): _identity(), _insert(), LexicalIdentityInput, LexicalIndexError

### Community 78 - "Master Plan Overview"
Cohesion: 0.33
Nodes (6): Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Phase 1 Scope (public/guest RAG), Recruiter / portfolio story, Project Mission, Seven-day Phase 1 execution plan

### Community 79 - "Deployment and Degradation Plan"
Cohesion: 0.33
Nodes (6): AWS deployment architecture (ap-south-1), CI/CD pipeline, Graceful degradation, Qdrant, SQLite FTS5 fallback, Terraform scope

### Community 80 - "Plan Repository Concepts"
Cohesion: 0.33
Nodes (5): Document manifest, DocumentRepository, LocalDocumentRepository, Phase 2 Knowledge Operations, S3DocumentRepository

### Community 81 - "Spec 004-005 Retros"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

### Community 82 - "Spec 006 Compare Design"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 83 - "Payments and Support"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 84 - "Migration Points"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 85 - "Security Plan"
Cohesion: 0.40
Nodes (4): Authorization model (guest/public), Poisoned public document fixture, Security plan (threats and controls), Staff-only canary fixture

### Community 86 - "Multilingual Plan"
Cohesion: 0.40
Nodes (4): Amazon Bedrock Runtime, BGE-M3 embeddings, Multilingual design (lote_languages), Technology stack

### Community 87 - "Mission"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 88 - "Business Overview"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 89 - "Materials and Practice"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 96 - "Plan Metadata"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

### Community 111 - "ingest_dense"
Cohesion: 0.18
Nodes (11): build_production(), ingest_dense(), open_lexical(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

### Community 112 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.10
Nodes (6): new_base(), OddIdStore, seed_repository(), test_builder_refuses_a_real_embedder_identity(), __init__(), test_violation_names_the_document_from_the_error_attribute()

### Community 114 - "re"
Cohesion: 0.13
Nodes (13): absent_query_languages(), active_registry_languages(), aggregate(), _mean(), slice_by(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry() (+5 more)

### Community 115 - "DenseIndex"
Cohesion: 0.11
Nodes (31): LexicalRow, DenseIndex, build(), DroppedClauseIndex, guest(), pub(), retriever(), _shape() (+23 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (9): default_strategy, fusion, candidate_depth, k, method, weights, schema_version, bm25 (+1 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.13
Nodes (17): _authority_map(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), _security() (+9 more)

### Community 118 - "retrieval/test_access.py"
Cohesion: 0.16
Nodes (16): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+8 more)

### Community 119 - "AccessContext"
Cohesion: 0.14
Nodes (8): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen()

### Community 120 - "Strategy"
Cohesion: 0.12
Nodes (25): Implementation, Implementation, Review, Review, T6 — round 1, T6 — round 2, document_leg_ranks(), _leg_ranks_for() (+17 more)

### Community 121 - "test_content_hash.py"
Cohesion: 0.18
Nodes (15): manifest_document_count(), _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically() (+7 more)

### Community 122 - "test_lexical_cli.py"
Cohesion: 0.06
Nodes (54): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, User decision (+46 more)

### Community 123 - "Strategy"
Cohesion: 0.10
Nodes (27): R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Implementation, Implementation, Review, Review, T5 — round 1, T5 — round 2, User decision (+19 more)

### Community 124 - "hashing.py"
Cohesion: 0.10
Nodes (15): build_security_repository(), _fixture_files(), split_frontmatter(), _StringDateLoader, canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256() (+7 more)

### Community 125 - "test_security_eval.py"
Cohesion: 0.18
Nodes (13): clean_env(), copy_fixtures(), spied(), SpyIndex, test_a_filter_dropping_index_fails_the_gate(), test_cli_harness_error_exits_two_and_writes_nothing(), test_cli_pass_writes_a_result_and_exits_zero(), test_cli_violation_exits_one_naming_ids_not_text() (+5 more)

### Community 127 - "Development Workflow"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 128 - "test_strategy_eval.py"
Cohesion: 0.12
Nodes (28): User decision, build_lexical(), eval_world(), leg_order(), lexical_env(), make_world(), retrieve(), retrieve_world() (+20 more)

### Community 129 - "FakeEmbedder"
Cohesion: 0.15
Nodes (12): FakeEmbedder, __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected() (+4 more)

### Community 130 - "evaluation/test_cli.py"
Cohesion: 0.18
Nodes (16): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+8 more)

### Community 131 - "LoadedSuite"
Cohesion: 0.17
Nodes (9): R1 — Suite v2, DatasetType, LoadedSuite, active_golden_cases(), _notes(), security_document(), select_security_queries(), test_attack_types_are_split_into_run_deferred_and_unclassified() (+1 more)

### Community 132 - "retrieval_eval.py"
Cohesion: 0.06
Nodes (37): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Implementation, Review, T2 — round 1, User decision, T2 — v2 dense baseline (user-owned gate), Verification, _fusion_report() (+29 more)

### Community 133 - "Review"
Cohesion: 0.17
Nodes (10): Implementation, Review, T3 — round 1, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, source_chunk_digest(), query_terms(), QueryTerms (+2 more)

### Community 134 - ".open"
Cohesion: 0.17
Nodes (5): EmbedderInfo, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed()

### Community 135 - "security_eval.py"
Cohesion: 0.25
Nodes (8): EvaluationHarnessError, run_security_evaluation(), _sanity_check(), SecurityQuery, SecurityReport, forbidden_variant(), is_forbidden_document(), test_sanity_check_failure_is_a_harness_error()

### Community 137 - "dense_equivalence.py"
Cohesion: 0.29
Nodes (4): deterministic_clock(), equivalence_suite(), run_equivalence(), unanswerable()

### Community 138 - "metrics.py"
Cohesion: 0.22
Nodes (8): chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank(), live_client()

### Community 141 - "point_id"
Cohesion: 0.14
Nodes (13): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R4 — `make index-lexical` (`lexical/cli.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), R9 — Result format 2.1, collect(), point_id() (+5 more)

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **186 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 861 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DenseIndex` connect `DenseIndex` to `QdrantIndexStore`, `test_strategy_eval.py`, `typing`, `evaluation/test_cli.py`, `retrieval_eval.py`, `Review`, `LexicalIndex`, `.open`, `DenseRetriever`, `DenseRetriever`, `test_retrieval_eval.py`, `security_index.py`, `Index Binding Errors`, `retrieval/test_cli.py`, `ingest_dense`, `test_violation_names_the_document_from_the_error_attribute`, `evaluation/cli.py`, `Strategy`, `Strategy`, `test_security_eval.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 60 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 60 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _186 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `QdrantIndexStore` be split into smaller, more focused modules?**
  _Cohesion score 0.055757575757575756 - nodes in this community are weakly interconnected._
- **Why does `FakeEmbedder` connect `FakeEmbedder` to `test_strategy_eval.py`, `QdrantIndexStore`, `typing`, `evaluation/test_cli.py`, `Review`, `LexicalIndex`, `DenseRetriever`, `KnowledgeDocument`, `test_retrieval_eval.py`, `ingestion/cli.py`, `security_index.py`, `Index Binding Errors`, `Live-count Test Helpers`, `LocalDocumentRepository`, `test_lexical_build.py`, `ingest_dense`, `test_violation_names_the_document_from_the_error_attribute`, `DenseIndex`, `evaluation/cli.py`, `test_lexical_cli.py`, `Strategy`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `DocumentQuery`) actually correct?**
  _`LocalDocumentRepository` has 15 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._