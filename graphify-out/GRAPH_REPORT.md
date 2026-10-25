# Graph Report - way2australia  (2026-10-25)

## Corpus Check
- 216 files · ~190,296 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .example 1)

## Summary
- 2382 nodes · 6404 edges · 117 communities (97 shown, 20 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 861 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1850f5ea`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Ingestion Settings and Store
- repositories/__init__.py
- security_index.py
- Heading Chunker
- Evaluation Schemas and Validation
- retrieval/test_cli.py
- CLI Wiring and Config
- Eval Compare Gate
- build_access_filter
- Dense Index Binding
- Fake Embedder
- Model Tiers
- Document Enums and Models
- Unanswerable Reporting
- retrieval_eval.py
- test_security_eval.py
- Day-1 Data and Sources
- Architecture Decisions
- Index Binding Errors
- Document Model Tests
- typing
- Date and Policy Tests
- BGE-M3 Adapter
- Live-count Test Helpers
- test_content_hash.py
- Legacy Snapshot Test
- Eligibility and Authority
- evaluation/validate.py
- Evaluation Error Hierarchy
- Architecture Components
- FastAPI Health Endpoint
- Manifest Loading
- pytest
- Suite Loader
- Evaluation Slices
- Roadmap
- test_suite_v2.py
- 007 — Hybrid Retrieval Requirements
- Case Status and Types
- Validation Document IDs
- json
- hashing.py
- Access Policy Config
- Constitution Principles
- Docker Compose Qdrant
- Authorization Design
- Agent Workflow Skills
- Ingestion Config File
- Engineering Conventions
- Phase 2 Governance
- Project Commands
- Development Workflow
- Packages and Pricing
- Agent Project Rules
- test_baseline.py
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
- test_index_contract.py
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
- load_manifest
- repositories/validate.py
- documents/__init__.py
- chunking.py
- split_frontmatter
- test_status_handling.py

## God Nodes (most connected - your core abstractions)
1. `LocalDocumentRepository` - 58 edges
2. `EvaluationConfigurationError` - 54 edges
3. `DenseIndex` - 54 edges
4. `QdrantIndexStore` - 47 edges
5. `Architecture Decisions` - 47 edges
6. `KnowledgeDocument` - 45 edges
7. `FakeEmbedder` - 45 edges
8. `DenseRetriever` - 44 edges
9. `HeadingChunker` - 42 edges
10. `run_retrieval_evaluation()` - 40 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Acceptance criteria` --references--> `RetrievalAuthorizationError`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/src/way2australia_rag/retrieval/errors.py
- `R4 — `make index-lexical` (`lexical/cli.py`)` --references--> `safe_text()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/retrieval/text.py
- `Acceptance criteria` --references--> `safe_text()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/src/way2australia_rag/retrieval/text.py
- `R11 — Security gate (`security_index.py`, `security_eval.py`)` --references--> `EvaluationHarnessError`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/errors.py

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

## Communities (117 total, 20 thin omitted)

### Community 0 - "Ingestion Settings and Store"
Cohesion: 0.10
Nodes (32): IndexSettingsMismatchError, IndexSettings, QdrantIndexStore, read_index_settings(), CountingStore, client(), _keyword_indexed(), live_client() (+24 more)

### Community 1 - "repositories/__init__.py"
Cohesion: 0.13
Nodes (8): DocumentNotFoundError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, compare_manifest_to_metadata(), ManifestEntry, test_error_messages_name_document_and_field(), test_errors_share_base_class()

### Community 2 - "security_index.py"
Cohesion: 0.09
Nodes (18): build_security_index(), _canary_points(), delete_security_index(), _forbidden_payload(), require_security_base(), Chunk, Chunker, build_payload() (+10 more)

### Community 3 - "Heading Chunker"
Cohesion: 0.06
Nodes (57): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), R4 — `make index-lexical` (`lexical/cli.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`) (+49 more)

### Community 4 - "Evaluation Schemas and Validation"
Cohesion: 0.12
Nodes (32): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+24 more)

### Community 5 - "retrieval/test_cli.py"
Cohesion: 0.16
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 6 - "CLI Wiring and Config"
Cohesion: 0.06
Nodes (35): _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), _security(), _unanswerable_line() (+27 more)

### Community 7 - "Eval Compare Gate"
Cohesion: 0.09
Nodes (49): _changed(), compare(), Comparison, _delta_line(), _fmt_key(), _hits(), _listed(), _mean() (+41 more)

### Community 8 - "build_access_filter"
Cohesion: 0.07
Nodes (37): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability, Package / file placement (+29 more)

### Community 9 - "Dense Index Binding"
Cohesion: 0.09
Nodes (31): R6 — `BM25Retriever` (`retrieval/bm25.py`), DenseIndex, RetrievalResult, RetrievedChunk, DenseRetriever, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned() (+23 more)

### Community 10 - "Fake Embedder"
Cohesion: 0.05
Nodes (43): 007 — Hybrid Retrieval Tasks, Out of this spec, T10 — Documentation, decisions and hand-off, T1 — Evaluation Suite `public-eval-v2`, T5 — RRF fusion, hybrid retriever and `config/retrieval.yaml`, T6 — Strategy option in the CLIs and result format 2.1, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test (+35 more)

### Community 11 - "Model Tiers"
Cohesion: 0.05
Nodes (20): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Orchestrator State Machine, Spec Orchestrator Skill, Design Template (+12 more)

### Community 12 - "Document Enums and Models"
Cohesion: 0.10
Nodes (4): _check_language_code(), KnowledgeDocument, ListRepository, IgnoresQueryRepository

### Community 13 - "Unanswerable Reporting"
Cohesion: 0.13
Nodes (29): UnanswerableCase, basic_suite(), build(), golden(), run(), suite_of(), suite_with_unanswerable(), test_active_golden_without_relevant_documents_is_refused() (+21 more)

### Community 14 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (38): R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), Review, T2 — v2 dense baseline (user-owned gate), Verification, require_real_embedder(), require_real_index(), run_retrieval_evaluation(), score_distribution() (+30 more)

### Community 15 - "test_security_eval.py"
Cohesion: 0.05
Nodes (45): EvaluationHarnessError, run_security_evaluation(), _sanity_check(), security_document(), SecurityQuery, SecurityReport, forbidden_variant(), is_forbidden_document() (+37 more)

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

### Community 20 - "typing"
Cohesion: 0.08
Nodes (6): Role, EmbedderInfo, RetrievalConfigurationError, declared_release_id(), test_declared_release(), live_client()

### Community 21 - "Date and Policy Tests"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "BGE-M3 Adapter"
Cohesion: 0.07
Nodes (24): BgeM3Embedder, _group_installed(), OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error() (+16 more)

### Community 23 - "Live-count Test Helpers"
Cohesion: 0.12
Nodes (21): manifest_document_count(), clean_env(), _factory(), _run(), test_agrees_with_day1_baseline(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision() (+13 more)

### Community 24 - "test_content_hash.py"
Cohesion: 0.20
Nodes (9): _StringDateLoader, h(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order(), test_non_retrieval_metadata_does_not_change_content_hash() (+1 more)

### Community 25 - "Legacy Snapshot Test"
Cohesion: 0.12
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 26 - "Eligibility and Authority"
Cohesion: 0.21
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 27 - "evaluation/validate.py"
Cohesion: 0.12
Nodes (17): Review, EvaluationSchemas, _candidate_rules(), problem(), _describe(), _document_ids(), _document_problems(), EvaluationProblem (+9 more)

### Community 28 - "Evaluation Error Hierarchy"
Cohesion: 0.14
Nodes (15): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, declared_release_id() (+7 more)

### Community 29 - "Architecture Components"
Cohesion: 0.09
Nodes (28): AccessContext and Role, apps/api FastAPI layer, Amazon Bedrock Runtime, BGE-M3, Architecture, DocumentRepository Protocol, HeadingChunker, Ingestion pipeline (Spec 004) (+20 more)

### Community 30 - "FastAPI Health Endpoint"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 31 - "Manifest Loading"
Cohesion: 0.40
Nodes (14): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field(), test_manifest_frontmatter_mismatch_reported() (+6 more)

### Community 32 - "pytest"
Cohesion: 0.06
Nodes (54): test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen(), _authority_map() (+46 more)

### Community 33 - "Suite Loader"
Cohesion: 0.28
Nodes (11): load_suite(), live_suite_rows(), copy_suite(), test_access_context_is_loaded_but_ignored(), test_dataset_types_loaded_by_type(), test_escaping_path_refused(), test_extra_fields_tolerated(), test_malformed_line_names_file_and_line_only() (+3 more)

### Community 34 - "Evaluation Slices"
Cohesion: 0.20
Nodes (9): active_registry_languages(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error(), test_no_language_literal_in_evaluation_code(), test_real_registry_lists_en_and_the_active_product_language(), test_slice_keys_come_from_data_and_carry_n(), test_small_sample_threshold_is_ten() (+1 more)

### Community 35 - "Roadmap"
Cohesion: 0.17
Nodes (21): Roadmap, Evaluation Governance (keep/modify/deprecate/replace), Future capabilities, Phase 0 bootstrap, Roadmap item 1 - Project foundation, Roadmap item 10 - Grounded generation + citations, Roadmap item 11 - Observability, Roadmap item 12 - Security (+13 more)

### Community 36 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 37 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (33): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+25 more)

### Community 38 - "Case Status and Types"
Cohesion: 0.19
Nodes (8): DatasetType, LoadedSuite, active_golden_cases(), _notes(), unanswerable_report(), select_security_queries(), test_attack_types_are_split_into_run_deferred_and_unclassified(), case()

### Community 39 - "Validation Document IDs"
Cohesion: 0.12
Nodes (8): Acceptance criteria, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, collect(), DocumentQuery, DocumentRepository, EligibilityPolicy, list_eligible_documents()

### Community 40 - "json"
Cohesion: 0.10
Nodes (15): load_schemas(), load_suite(), security_repository(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass() (+7 more)

### Community 41 - "hashing.py"
Cohesion: 0.14
Nodes (12): build_security_repository(), _fixture_files(), canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), normalize_body() (+4 more)

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

### Community 51 - "Development Workflow"
Cohesion: 0.12
Nodes (18): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+10 more)

### Community 52 - "Packages and Pricing"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 53 - "Agent Project Rules"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 54 - "test_baseline.py"
Cohesion: 0.12
Nodes (19): case(), clean_env(), cli_run(), run(), seeded(), setup(), test_case_access_context_never_widens_access(), test_cli_release_mismatch_and_bad_args_exit_2() (+11 more)

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

### Community 77 - "test_index_contract.py"
Cohesion: 0.11
Nodes (18): point_id(), PointPayload, compare(), mismatch_message(), base_settings(), test_build_index_settings_records_embedder_and_chunker(), test_collection_name_derivation(), test_compare_equal_and_ignores_hash_contract() (+10 more)

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

### Community 111 - "load_manifest"
Cohesion: 0.15
Nodes (12): check_manifest_documents(), date_problems(), describe_error(), load_manifest(), load_schema(), _path_problem(), schema_problems(), validate_manifest() (+4 more)

### Community 112 - "repositories/validate.py"
Cohesion: 0.16
Nodes (10): DocumentRepositoryError, under_root(), ValidationProblem, _corpus_problems(), _duplicate_reason(), _error_problems(), main(), _model_problems() (+2 more)

### Community 113 - "documents/__init__.py"
Cohesion: 0.23
Nodes (5): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority

### Community 114 - "chunking.py"
Cohesion: 0.24
Nodes (4): _parse_sections(), _Section, _split_body(), _split_words()

### Community 115 - "split_frontmatter"
Cohesion: 0.20
Nodes (4): split_frontmatter(), document_fields(), test_frontmatter_errors(), test_frontmatter_parsing_keeps_dates_as_strings()

### Community 116 - "test_status_handling.py"
Cohesion: 0.57
Nodes (4): golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **186 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 766 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DenseIndex` connect `Dense Index Binding` to `Ingestion Settings and Store`, `security_index.py`, `retrieval/test_cli.py`, `CLI Wiring and Config`, `Validation Document IDs`, `build_access_filter`, `Fake Embedder`, `Unanswerable Reporting`, `retrieval_eval.py`, `test_security_eval.py`, `Index Binding Errors`, `typing`, `test_baseline.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `DocumentQuery`) actually correct?**
  _`LocalDocumentRepository` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _186 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Ingestion Settings and Store` be split into smaller, more focused modules?**
  _Cohesion score 0.09519230769230769 - nodes in this community are weakly interconnected._
- **Why does `FakeEmbedder` connect `Fake Embedder` to `Ingestion Settings and Store`, `Heading Chunker`, `CLI Wiring and Config`, `build_access_filter`, `Dense Index Binding`, `Unanswerable Reporting`, `test_index_contract.py`, `test_security_eval.py`, `Index Binding Errors`, `typing`, `test_baseline.py`, `Live-count Test Helpers`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `EvaluationConfigurationError` (e.g. with `_security()` and `declared_release_id()`) actually correct?**
  _`EvaluationConfigurationError` has 21 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._