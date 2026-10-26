# Graph Report - way2australia  (2026-10-25)

## Corpus Check
- 226 files · ~198,436 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .example 1)

## Summary
- 2573 nodes · 7089 edges · 128 communities (107 shown, 21 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 966 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3375924e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- QdrantIndexStore
- repositories/__init__.py
- security_index.py
- HeadingChunker
- test_validate.py
- evaluation/cli.py
- ingestion/cli.py
- Eval Compare Gate
- DenseRetriever
- DenseIndex
- evaluation/validate.py
- Model Tiers
- KnowledgeDocument
- test_retrieval_eval.py
- retrieval_eval.py
- test_security_eval.py
- Day-1 Data and Sources
- Architecture Decisions
- Index Binding Errors
- Document Model Tests
- conftest.py
- Date and Policy Tests
- BGE-M3 Adapter
- Live-count Test Helpers
- source_chunk_digest
- Legacy Snapshot Test
- test_eligibility.py
- test_index_contract.py
- Evaluation Error Hierarchy
- Architecture Components
- FastAPI Health Endpoint
- Manifest Loading
- asyncio
- documents/__init__.py
- test_lexical_tokenizer.py
- Roadmap
- json
- 007 — Hybrid Retrieval Requirements
- test_lexical_build.py
- lexical/store.py
- test_goldens.py
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
- evaluation/cli.py
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
- test_lexical_bind.py
- test_repository_contract.py
- build_lexical_index
- slices.py
- 007 — Hybrid Retrieval Tasks
- LocalDocumentRepository
- test_lexical_cli.py
- retrieval/test_access.py
- AccessContext
- Path
- Components / boundaries
- lexical/cli.py
- SecurityIndex
- RuntimeSettings
- chunking.py
- run_retrieval_evaluation
- pytest

## God Nodes (most connected - your core abstractions)
1. `LocalDocumentRepository` - 61 edges
2. `DenseIndex` - 59 edges
3. `EvaluationConfigurationError` - 54 edges
4. `FakeEmbedder` - 50 edges
5. `QdrantIndexStore` - 48 edges
6. `HeadingChunker` - 47 edges
7. `Architecture Decisions` - 47 edges
8. `KnowledgeDocument` - 45 edges
9. `DenseRetriever` - 44 edges
10. `LocalRepositoryConfig` - 41 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `User decision` --references--> `embedder_identity()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/task-reviews.md → packages/rag/src/way2australia_rag/lexical/cli.py
- `Acceptance criteria` --references--> `RetrievalAuthorizationError`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/src/way2australia_rag/retrieval/errors.py
- `Acceptance criteria` --references--> `safe_text()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/src/way2australia_rag/retrieval/text.py
- `Dependencies` --references--> `AccessContext`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/core/src/way2australia_core/access.py

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

## Communities (128 total, 21 thin omitted)

### Community 0 - "QdrantIndexStore"
Cohesion: 0.07
Nodes (41): IndexSettingsMismatchError, compare(), IndexSettings, mismatch_message(), IndexedDocument, QdrantIndexStore, read_index_settings(), base_settings() (+33 more)

### Community 1 - "repositories/__init__.py"
Cohesion: 0.07
Nodes (26): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, document_fields(), LocalRepositoryConfig, under_root(), check_manifest_documents() (+18 more)

### Community 2 - "security_index.py"
Cohesion: 0.11
Nodes (11): R11 — Security gate (`security_index.py`, `security_eval.py`), R4 — `make index-lexical` (`lexical/cli.py`), Acceptance criteria, EvaluationHarnessError, build_security_index(), _canary_points(), _forbidden_payload(), require_security_base() (+3 more)

### Community 3 - "HeadingChunker"
Cohesion: 0.08
Nodes (48): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), ids(), make_document(), test_deterministic(), test_duplicate_headings_get_unique_ids_in_order() (+40 more)

### Community 4 - "test_validate.py"
Cohesion: 0.13
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "evaluation/cli.py"
Cohesion: 0.12
Nodes (8): require_real_embedder(), Embedder, BaselineResult, check_output_free(), format_summary(), default_output_path(), git_state(), write_result()

### Community 6 - "ingestion/cli.py"
Cohesion: 0.11
Nodes (17): build_chunker(), build_embedder(), default_client_factory(), format_summary(), main(), _parser(), ChunkerConfig, EmbedderConfig (+9 more)

### Community 7 - "Eval Compare Gate"
Cohesion: 0.09
Nodes (49): _changed(), compare(), Comparison, _delta_line(), _fmt_key(), _hits(), _listed(), _mean() (+41 more)

### Community 8 - "DenseRetriever"
Cohesion: 0.12
Nodes (22): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability, Package / file placement (+14 more)

### Community 9 - "DenseIndex"
Cohesion: 0.12
Nodes (24): Decisions resolved before drafting, IndexPoint, DenseIndex, DenseRetriever, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed() (+16 more)

### Community 10 - "evaluation/validate.py"
Cohesion: 0.07
Nodes (25): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, load_schemas(), _candidate_rules(), problem() (+17 more)

### Community 11 - "Model Tiers"
Cohesion: 0.05
Nodes (20): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Orchestrator State Machine, Spec Orchestrator Skill, Design Template (+12 more)

### Community 12 - "KnowledgeDocument"
Cohesion: 0.07
Nodes (9): _check_language_code(), KnowledgeDocument, DocumentQuery, DocumentNotFoundError, test_real_fixture_folder_builds(), test_ineligible_document(), CountingEmbedder, ListRepository (+1 more)

### Community 13 - "test_retrieval_eval.py"
Cohesion: 0.05
Nodes (59): UnanswerableCase, write_document(), FakeEmbedder, clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2() (+51 more)

### Community 14 - "retrieval_eval.py"
Cohesion: 0.07
Nodes (24): R6 — `BM25Retriever` (`retrieval/bm25.py`), Review, T2 — v2 dense baseline (user-owned gate), Verification, score_distribution(), dedupe_sections(), section_key(), section_report() (+16 more)

### Community 15 - "test_security_eval.py"
Cohesion: 0.12
Nodes (25): run_security_evaluation(), forbidden_variant(), build(), clean_env(), guest_access(), new_base(), OddIdStore, real_queries() (+17 more)

### Community 16 - "Day-1 Data and Sources"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 17 - "Architecture Decisions"
Cohesion: 0.08
Nodes (37): eval-compare quality gate, D001 - Python-first backend, D002 - RAG as reusable internal package, D003 - Knowledge outside RAG package, D006 - Authorization during retrieval, D007 - Public-only Phase 1, D008 - Language and authorization are independent, D009 - Source precedence (+29 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.16
Nodes (28): IndexBindingError, client(), fake_info(), make_settings(), open_index(), payload(), scope_filter(), seed() (+20 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 20 - "conftest.py"
Cohesion: 0.12
Nodes (5): Role, live_client(), test_server_filter_keeps_every_forbidden_point_out(), test_namespace_constant_is_pinned(), test_point_id_stable_and_valid_uuid()

### Community 21 - "Date and Policy Tests"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "BGE-M3 Adapter"
Cohesion: 0.08
Nodes (14): BgeM3Embedder, _group_installed(), EmbedderInfo, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction() (+6 more)

### Community 23 - "Live-count Test Helpers"
Cohesion: 0.14
Nodes (19): manifest_document_count(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+11 more)

### Community 24 - "source_chunk_digest"
Cohesion: 0.17
Nodes (8): As-built notes, Change log, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, source_chunk_digest()

### Community 25 - "Legacy Snapshot Test"
Cohesion: 0.11
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 26 - "test_eligibility.py"
Cohesion: 0.12
Nodes (21): collect(), _document_ids(), collect(), EligibilityPolicy, list_eligible_documents(), eligible_ids(), make_document(), test_active_approved_public_document_is_eligible() (+13 more)

### Community 27 - "test_index_contract.py"
Cohesion: 0.14
Nodes (13): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), build_payload(), PointPayload, test_no_language_literal_in_evaluation_code(), test_authorization_and_language_fields_are_separate(), test_build_payload_copies_document_and_chunk(), test_collection_name_derivation(), test_no_malayalam_specific_lote_languages_in_ingestion_code() (+5 more)

### Community 28 - "Evaluation Error Hierarchy"
Cohesion: 0.13
Nodes (15): EvaluationConfigurationError, CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, declared_release_id() (+7 more)

### Community 29 - "Architecture Components"
Cohesion: 0.09
Nodes (28): AccessContext and Role, apps/api FastAPI layer, Amazon Bedrock Runtime, BGE-M3, Architecture, DocumentRepository Protocol, HeadingChunker, Ingestion pipeline (Spec 004) (+20 more)

### Community 30 - "FastAPI Health Endpoint"
Cohesion: 0.12
Nodes (13): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+5 more)

### Community 31 - "Manifest Loading"
Cohesion: 0.29
Nodes (19): load_schema(), metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field() (+11 more)

### Community 32 - "asyncio"
Cohesion: 0.32
Nodes (14): _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found(), test_invalid_document_fails_load_without_leaking_paths(), test_invalid_schema_raises_repository_error(), test_language_filter_is_data_driven_and_does_not_affect_access() (+6 more)

### Community 33 - "documents/__init__.py"
Cohesion: 0.21
Nodes (6): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, test_guest_policy_agrees_with_access_policy_config()

### Community 34 - "test_lexical_tokenizer.py"
Cohesion: 0.12
Nodes (16): Implementation, _is_token_char(), query_terms(), QueryTerms, tokenize(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case() (+8 more)

### Community 35 - "Roadmap"
Cohesion: 0.17
Nodes (21): Roadmap, Evaluation Governance (keep/modify/deprecate/replace), Future capabilities, Phase 0 bootstrap, Roadmap item 1 - Project foundation, Roadmap item 10 - Grounded generation + citations, Roadmap item 11 - Observability, Roadmap item 12 - Security (+13 more)

### Community 36 - "json"
Cohesion: 0.05
Nodes (62): load_suite(), live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_access_context_is_loaded_but_ignored() (+54 more)

### Community 37 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.06
Nodes (32): 007 — Hybrid Retrieval Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+24 more)

### Community 38 - "test_lexical_build.py"
Cohesion: 0.19
Nodes (18): identity(), open_lexical(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_records_settings(), test_digest_is_stable_and_order_independent() (+10 more)

### Community 39 - "lexical/store.py"
Cohesion: 0.14
Nodes (8): _differences(), LexicalIdentityInput, LexicalIndex, LexicalIndexBindingError, LexicalRow, LexicalSettings, _read_only_connection(), test_build_production_helper_runs()

### Community 40 - "test_goldens.py"
Cohesion: 0.15
Nodes (15): main(), _parser(), RetrievalConfigurationError, RetrievalError, declared_release_id(), load_golden_cases(), load_suite(), test_declared_release() (+7 more)

### Community 41 - "hashing.py"
Cohesion: 0.09
Nodes (16): build_security_repository(), _fixture_files(), split_frontmatter(), _StringDateLoader, canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256() (+8 more)

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

### Community 52 - "Packages and Pricing"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 53 - "Agent Project Rules"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 54 - "test_baseline.py"
Cohesion: 0.06
Nodes (45): case(), clean_env(), cli_run(), DeviceStub, run(), seeded(), setup(), test_case_access_context_never_widens_access() (+37 more)

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

### Community 77 - "evaluation/cli.py"
Cohesion: 0.12
Nodes (16): _authority_map(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _retrieval(), _security() (+8 more)

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

### Community 111 - "test_lexical_bind.py"
Cohesion: 0.18
Nodes (11): build_production(), ingest_dense(), repository(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch(), test_bind_refuses_when_qdrant_content_changed() (+3 more)

### Community 112 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 113 - "build_lexical_index"
Cohesion: 0.24
Nodes (4): build_lexical_index(), _identity(), _insert(), LexicalIndexError

### Community 114 - "slices.py"
Cohesion: 0.15
Nodes (10): absent_query_languages(), active_registry_languages(), source_authority_key(), row(), test_absent_languages_from_a_temp_registry(), test_missing_registry_section_is_a_configuration_error(), test_real_registry_lists_en_and_the_active_product_language(), test_slice_keys_come_from_data_and_carry_n() (+2 more)

### Community 115 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.12
Nodes (16): 007 — Hybrid Retrieval Tasks, Out of this spec, T10 — Documentation, decisions and hand-off, T1 — Evaluation Suite `public-eval-v2`, T5 — RRF fusion, hybrid retriever and `config/retrieval.yaml`, T6 — Strategy option in the CLIs and result format 2.1, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test (+8 more)

### Community 116 - "LocalDocumentRepository"
Cohesion: 0.18
Nodes (7): LocalDocumentRepository, security_repository(), test_repository_content_hash_is_content_hash_v1(), manifest_records(), seed_documents(), test_security_fixtures_are_not_in_the_production_corpus(), test_seed_ids_and_versions_are_unique()

### Community 117 - "test_lexical_cli.py"
Cohesion: 0.07
Nodes (48): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+40 more)

### Community 118 - "retrieval/test_access.py"
Cohesion: 0.19
Nodes (11): clean_env(), guest(), payload(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload(), test_check_hit_rejects_violations(), test_default_tenant(), test_empty_tenant_setting_refused() (+3 more)

### Community 119 - "AccessContext"
Cohesion: 0.21
Nodes (8): AccessContext, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen()

### Community 120 - "Path"
Cohesion: 0.31
Nodes (8): copy_fixtures(), test_cli_harness_error_exits_two_and_writes_nothing(), test_cli_pass_writes_a_result_and_exits_zero(), test_cli_violation_exits_one_naming_ids_not_text(), broken(), test_hidden_entries_are_ignored(), test_missing_fixture_is_refused(), test_stray_fixture_file_is_refused_before_any_copy()

### Community 121 - "Components / boundaries"
Cohesion: 0.29
Nodes (7): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R1 — Suite v2, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), R9 — Result format 2.1

### Community 122 - "lexical/cli.py"
Cohesion: 0.22
Nodes (7): collection_name(), lexical_index_path(), embedder_identity(), main(), _parser(), shown_path(), DenseIdentity

### Community 123 - "SecurityIndex"
Cohesion: 0.22
Nodes (6): _sanity_check(), SecurityQuery, delete_security_index(), is_forbidden_document(), SecurityIndex, test_the_security_index_records_a_fake_embedder_and_is_removed()

### Community 124 - "RuntimeSettings"
Cohesion: 0.28
Nodes (3): RuntimeSettings, guest_access(), test_guest_access_uses_settings_tenant()

### Community 125 - "chunking.py"
Cohesion: 0.09
Nodes (14): Chunk, Chunker, _parse_sections(), _Section, _split_body(), _split_words(), IngestionError, OptionalDependencyError (+6 more)

### Community 126 - "run_retrieval_evaluation"
Cohesion: 0.12
Nodes (13): DatasetType, LoadedSuite, active_golden_cases(), _notes(), require_active_suite(), run_retrieval_evaluation(), unanswerable_report(), security_document() (+5 more)

### Community 138 - "pytest"
Cohesion: 0.22
Nodes (8): chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank(), live_client()

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **186 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 812 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DenseIndex` connect `DenseIndex` to `QdrantIndexStore`, `security_index.py`, `evaluation/cli.py`, `ingestion/cli.py`, `DenseRetriever`, `test_retrieval_eval.py`, `retrieval_eval.py`, `test_security_eval.py`, `Index Binding Errors`, `BGE-M3 Adapter`, `source_chunk_digest`, `lexical/store.py`, `test_goldens.py`, `.search`, `test_baseline.py`, `evaluation/cli.py`, `test_lexical_bind.py`, `SecurityIndex`, `chunking.py`, `run_retrieval_evaluation`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `DocumentQuery`) actually correct?**
  _`LocalDocumentRepository` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _186 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `QdrantIndexStore` be split into smaller, more focused modules?**
  _Cohesion score 0.07140538786108407 - nodes in this community are weakly interconnected._
- **Why does `FakeEmbedder` connect `test_retrieval_eval.py` to `QdrantIndexStore`, `test_lexical_tokenizer.py`, `evaluation/cli.py`, `ingestion/cli.py`, `test_lexical_build.py`, `DenseIndex`, `KnowledgeDocument`, `evaluation/cli.py`, `test_security_eval.py`, `test_lexical_bind.py`, `Index Binding Errors`, `007 — Hybrid Retrieval Tasks`, `conftest.py`, `test_baseline.py`, `Live-count Test Helpers`, `lexical/cli.py`, `chunking.py`?**
  _High betweenness centrality (0.017) - this node is a cross-community bridge._
- **Are the 35 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 35 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._