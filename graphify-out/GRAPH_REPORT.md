# Graph Report - way2australia  (2026-11-01)

## Corpus Check
- 266 files · ~285,898 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 32 file(s) not represented in the graph (top: (none) 20, .jsonl 9, .mdc 1)

## Summary
- 4046 nodes · 11841 edges · 181 communities (148 shown, 33 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 2329 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be4ed5d6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DenseRetriever
- typing
- repositories/validate.py
- DenseIndex
- test_validate.py
- HeadingChunker
- test_index_contract.py
- test_index.py
- verify_fresh
- retrieval_eval.py
- retrieval/access.py
- test_seed_corpus.py
- HeadingChunker
- LocalDocumentRepository
- BgeM3Embedder
- Day-1 Data and Sources
- Strategy Eval Tests
- 008 — Retrieval Fallback Requirements
- Index Binding Errors
- Document Model Tests
- Retrieval Eval Tests
- test_validate_knowledge.py
- Date and Policy Tests
- BGE-M3 Adapter
- test_lexical_standalone.py
- Spec 004 ingestion baseline
- IngestionConfigurationError
- test_baseline.py
- rrf_fuse
- Evaluation CLI Tests
- test_security_eval.py
- test_suite_v2.py
- build_security_index
- test_lexical_standalone.py
- test_lexical_cli.py
- test_fallback.py
- 009 — Chunking Experiments Requirements
- 008 — Retrieval Fallback Requirements
- ResolvedAccess
- Evaluation Slices
- open_retrieval
- typing
- test_legacy_baseline_snapshot.py
- FakeTokenizer
- Roadmap 10 - Grounded generation + citations
- test_lexical_standalone.py
- lexical/cli.py
- dense_equivalence.py
- make eval-retrieval
- 007 — Hybrid Retrieval Requirements
- KnowledgeDocument
- evaluation/cli.py
- Roadmap
- FallbackRetriever
- SecurityIndex
- test_suite_v2.py
- Development Workflow
- query_terms
- Phase 2 Knowledge Release workflow
- json
- COMMANDS.md (project command surface)
- RetrievalConfigurationError
- test_content_hash.py
- test_schemas.py
- ARCHITECTURE.md
- Security gate five paths, result 1.2
- BGE-M3 embeddings
- Spec 007 hybrid retrieval
- Strategy
- test_strategy.py
- Phase 1 RAG query pipeline
- healthcheck
- LoadedSuite
- pytest
- Constitution
- Section: Next step
- Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)
- pathlib
- test_repository_contract.py
- Spec 005 dense retrieval baseline
- Spec 002 document model and repository
- packages/rag
- Ingestion pipeline (Spec 004)
- Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__
- git_state
- AccessContext
- open_hybrid
- Backend stack
- open_retrieval / OpenedRetrieval
- D023 Task-gated agent workflow
- Roadmap 12 - Security
- DocumentRepository
- make eval-compare
- pathlib
- AGENTS.md Project Rules
- make index-lexical
- IngestionService
- SpyIndex
- test_failed_write_removes_partial_file
- CURRENT_STATE.md
- QdrantIndexStore
- DocumentQuery
- 006 Evaluation Framework Tasks
- Scripted
- Retrieval package (Spec 005 and 007)
- 007 — Hybrid Retrieval Tasks
- Qdrant (vector database)
- IndexIdentity
- test_eval_cli_bm25_needs_neither_qdrant_nor_the_embedder
- Authorization enforced before generation
- test_every_path_is_gated_for_every_query
- test_content_hash.py
- R8 — Evaluation results for degraded runs
- test_violation_names_the_document_from_the_error_attribute
- pytest
- test_bm25.py
- fusion
- evaluation/cli.py
- Roadmap 3 - Ingestion baseline
- failing_client
- test_status_handling.py
- dense
- SpyIndex
- hashing.py
- test_security_eval.py
- test_failed_write_removes_partial_file
- Development Workflow
- test_status_handling.py
- absent_query_languages
- Evaluation result format 2.2
- RuntimeSettings
- R12 — Real runs (user-owned gate)
- Vocabulary, flashcards and free access
- .search
- Spec 008 Retrieval Fallback Requirements
- stalled_port
- Evaluation Framework Goal
- pytest
- BGE-M3 (initial embedding model)
- Way2Australia AI Platform Master Implementation Plan
- eval-compare
- Payments, account access and support boundaries
- Home Affairs credentialled community language points
- make test
- Mission
- policy
- policy
- policy
- policy
- Orchestrator State Machine
- way2australia_api/__init__.py
- Project Context README
- .__init__
- way2australia_rag/__init__.py
- Scripted
- way2australia-core
- Phase 1 analytics event contract
- Spec-driven development workflow
- api/__init__.py
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

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 105 edges
2. `LocalDocumentRepository` - 86 edges
3. `Strategy` - 73 edges
4. `FakeEmbedder` - 63 edges
5. `HeadingChunker` - 62 edges
6. `DECISIONS.md architecture decision log` - 62 edges
7. `run_retrieval_evaluation()` - 61 edges
8. `ResolvedAccess` - 61 edges
9. `open_retrieval()` - 60 edges
10. `DenseRetriever` - 60 edges

## Surprising Connections (you probably didn't know these)
- `R10 — `eval-compare` identity rules (`compare.py`)` --references--> `_refusals()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/evaluation/compare.py
- `Acceptance criteria` --references--> `slugify()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/chunking.py
- `Error and failure behavior` --references--> `IngestionConfigurationError`  [INFERRED]
  .kiro/specs/009-chunking-experiments/design.md → packages/rag/src/way2australia_rag/ingestion/errors.py
- `Acceptance criteria` --references--> `ChunkTokenizer`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/tokenization.py
- `Traceability` --references--> `build_tokenizer()`  [INFERRED]
  .kiro/specs/009-chunking-experiments/requirements.md → packages/rag/src/way2australia_rag/ingestion/tokenization.py

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

## Communities (181 total, 33 thin omitted)

### Community 0 - "DenseRetriever"
Cohesion: 0.06
Nodes (89): Implementation, Review, T7 — round 1, User decision, Implementation, Review, T5 — round 1, User decision (+81 more)

### Community 1 - "typing"
Cohesion: 0.05
Nodes (19): _forbidden_payload(), _lexical_forbidden_entries(), lexical_probe_text(), _group_installed(), Chunker, _parse_sections(), _Section, _split_body() (+11 more)

### Community 2 - "repositories/validate.py"
Cohesion: 0.06
Nodes (34): DocumentNotFoundError, DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, under_root() (+26 more)

### Community 3 - "DenseIndex"
Cohesion: 0.09
Nodes (39): T8 — Security gate for BM25 and hybrid, Docker isolation test, Verification, LexicalIndex, LexicalRow, DenseIndex, build(), dense_fixture(), DroppedClauseIndex (+31 more)

### Community 4 - "test_validate.py"
Cohesion: 0.14
Nodes (31): edit_rows(), edit_suite(), root(), run(), test_active_golden_without_relevant_documents(), test_candidate_ineligible_document_is_not_unknown(), test_candidate_not_suggested(), test_candidate_referenced_by_suite() (+23 more)

### Community 5 - "HeadingChunker"
Cohesion: 0.05
Nodes (65): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), slugify(), _is_token_char(), QueryTerms, tokenize(), ids() (+57 more)

### Community 6 - "test_index_contract.py"
Cohesion: 0.07
Nodes (25): R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), Acceptance criteria, Truncation guard (R2), T7 — Documentation, decisions, carry-over clean-ups and hand-off, Verification, _canary_points(), format_summary(), point_id() (+17 more)

### Community 7 - "test_index.py"
Cohesion: 0.11
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "verify_fresh"
Cohesion: 0.07
Nodes (31): Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R4 — Freshness from the repository (`lexical/freshness.py`), T2: where the shared pieces live (2026-10-31) (+23 more)

### Community 9 - "retrieval_eval.py"
Cohesion: 0.05
Nodes (50): Implementation, Implementation, Review, Review, Review, T2 — round 1, T6 — round 1, T6 — round 2 (+42 more)

### Community 10 - "retrieval/access.py"
Cohesion: 0.08
Nodes (26): Acceptance criteria, R7 — Marking degraded results, _retrieval(), load_runtime_settings(), guest_access(), resolve_access(), _aggregate(), BaselineResult (+18 more)

### Community 11 - "test_seed_corpus.py"
Cohesion: 0.09
Nodes (38): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, check_target_allowed() (+30 more)

### Community 12 - "HeadingChunker"
Cohesion: 0.15
Nodes (33): write_document(), basic_suite(), build(), fusion_config(), golden(), run(), scripted_run(), suite_of() (+25 more)

### Community 13 - "LocalDocumentRepository"
Cohesion: 0.16
Nodes (29): run_security_evaluation(), LocalDocumentRepository, build(), guest_access(), new_base(), real_queries(), seed_repository(), spied() (+21 more)

### Community 14 - "BgeM3Embedder"
Cohesion: 0.11
Nodes (12): BgeM3Embedder, group_installed(), test_constructing_does_not_load_the_model(), test_device_none_before_load_and_recorded_after(), test_missing_group_at_load_raises_optional_dependency_error(), test_missing_group_refused_at_construction(), test_model_loaded_once_with_revision_and_batches(), fake_loader() (+4 more)

### Community 15 - "Day-1 Data and Sources"
Cohesion: 0.12
Nodes (28): build_lexical(), eval_world(), lexical_env(), fake_tokenizer_without_hub(), make_world(), retrieve(), retrieve_world(), run_strategy() (+20 more)

### Community 16 - "Strategy Eval Tests"
Cohesion: 0.08
Nodes (45): RetrievalUnavailableError and availability classification, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Evaluation Suite includes goldens, refusal, multilingual, security, regression, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible (+37 more)

### Community 17 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.14
Nodes (15): 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Spec 008 taken ahead of roadmap 7 (chunking), Decisions resolved before drafting, Definition of Done (+7 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.07
Nodes (40): IndexSettingsMismatchError, compare(), IndexSettings, mismatch_message(), QdrantIndexStore, read_index_settings(), base_settings(), test_build_index_settings_records_embedder_and_chunker() (+32 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.08
Nodes (33): Embedder, DenseRetriever, client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), test_formula_shows_the_cap_when_k_reaches_document_count(), build_client() (+25 more)

### Community 20 - "Retrieval Eval Tests"
Cohesion: 0.04
Nodes (45): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, RRF fusion (k 60, equal weights, depth 50, fail closed), Security gate over dense, bm25 and hybrid (+37 more)

### Community 21 - "test_validate_knowledge.py"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.09
Nodes (25): As-built notes, T1: Hugging Face error shapes (confirmed 2026-10-29), classify_model_error(), _optional_types(), caused_by(), GatedRepoError, handled_error(), LocalEntryNotFoundError (+17 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "test_lexical_standalone.py"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Spec 004 ingestion baseline"
Cohesion: 0.14
Nodes (18): HeadingChunker heading v1 2000-char cap, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs, QdrantIndexStore with companion settings collection, Heading chunking only synthetic-tested, none of 13 docs has headings, Spec 004 open review findings (T3 F1, T5 F2, T7 F1-F3, T8 F1, retro F1) (+10 more)

### Community 26 - "IngestionConfigurationError"
Cohesion: 0.11
Nodes (16): `structure` v1 (R3), Tokenizer (R1), IngestionConfigurationError, BgeM3Tokenizer, _download_hub_file(), _tokenizer_config_error(), hub(), test_bge_m3_cache_hit_counts() (+8 more)

### Community 27 - "test_baseline.py"
Cohesion: 0.06
Nodes (45): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+37 more)

### Community 28 - "rrf_fuse"
Cohesion: 0.11
Nodes (24): Implementation, Implementation, Review, Review, T5 — round 1, T5 — round 2, User decision, T5 — RRF fusion, hybrid retriever and `config/retrieval.yaml` (+16 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "test_security_eval.py"
Cohesion: 0.11
Nodes (21): build_security_repository(), _fixture_files(), security_repository(), clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper() (+13 more)

### Community 31 - "test_suite_v2.py"
Cohesion: 0.14
Nodes (24): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+16 more)

### Community 32 - "build_security_index"
Cohesion: 0.11
Nodes (6): build_security_index(), forbidden_variant(), require_security_base(), DocumentRepository, EligibilityPolicy, list_eligible_documents()

### Community 33 - "test_lexical_standalone.py"
Cohesion: 0.11
Nodes (28): build_production(), identity(), ingest_dense(), open_lexical(), payload(), rewrite_settings(), synthetic_entries(), test_bind_does_not_write_to_qdrant() (+20 more)

### Community 34 - "test_lexical_cli.py"
Cohesion: 0.17
Nodes (20): DenseIndex, build_access_filter, check_hit, DenseRetriever, make eval-retrieval, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, Spec 008 retro F4: duplicated standalone open wiring, Next step 1: real eval-retrieval and eval-compare PASS 2026-10-24, retrieval-evaluation-idx-v1-20261024T193140Z.json v1 2.0 closed baseline (+12 more)

### Community 35 - "test_fallback.py"
Cohesion: 0.27
Nodes (12): access(), Fallback, Primary, test_a_fallback_error_is_raised(), test_dense_leg_failure_on_one_query_leaves_the_others_hybrid(), test_every_reason_falls_back_with_the_same_access_and_top_k(), test_fusion_and_hybrid_are_unchanged(), test_latency_includes_the_failed_attempt() (+4 more)

### Community 36 - "009 — Chunking Experiments Requirements"
Cohesion: 0.07
Nodes (28): 009 — Chunking Experiments Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria, Acceptance criteria (+20 more)

### Community 37 - "008 — Retrieval Fallback Requirements"
Cohesion: 0.09
Nodes (36): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50) (+28 more)

### Community 38 - "ResolvedAccess"
Cohesion: 0.07
Nodes (48): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, As-built notes, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability (+40 more)

### Community 39 - "Evaluation Slices"
Cohesion: 0.14
Nodes (19): manifest_document_count(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment(), test_config_refuses_missing_or_floating_revision(), test_config_refuses_unknown_field_and_missing_file() (+11 more)

### Community 40 - "open_retrieval"
Cohesion: 0.09
Nodes (15): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+7 more)

### Community 41 - "typing"
Cohesion: 0.09
Nodes (32): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+24 more)

### Community 42 - "test_legacy_baseline_snapshot.py"
Cohesion: 0.13
Nodes (15): clean_env(), _Factory, _FixedDatetime, _record_opens(), note(), wrap_func(), inner(), wrap_method() (+7 more)

### Community 43 - "FakeTokenizer"
Cohesion: 0.06
Nodes (40): 009 — Chunking Experiments Design, Alternatives / deferred decisions, Data flow, Design summary, Error and failure behavior, Interfaces / models, Observability, Package / file placement (+32 more)

### Community 44 - "Roadmap 10 - Grounded generation + citations"
Cohesion: 0.20
Nodes (12): Answerability and insufficient-evidence response, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Dense to BM25 degradation, Roadmap 10 - Grounded generation + citations, Roadmap 13 - Graceful degradation, Roadmap 14 - AWS deployment (+4 more)

### Community 45 - "test_lexical_standalone.py"
Cohesion: 0.12
Nodes (23): LexicalIndexBindingError, LexicalSettings, _read_only_connection(), build_from(), built(), copy_repository(), expected(), first_document_id() (+15 more)

### Community 46 - "lexical/cli.py"
Cohesion: 0.06
Nodes (32): Implementation, Implementation, Implementation, Review, Spec 009 — Task reviews, T1 — round 1, T1 — round 2, T3 — Configuration, index settings, lexical identity and per-document freshness (+24 more)

### Community 47 - "dense_equivalence.py"
Cohesion: 0.18
Nodes (8): CaseBase, GoldenCase, SecurityCase, UnanswerableCase, deterministic_clock(), equivalence_suite(), unanswerable(), unanswerable()

### Community 48 - "make eval-retrieval"
Cohesion: 0.12
Nodes (23): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, FakeEmbedder (deterministic), GUEST_PUBLIC_POLICY, HeadingChunker (heading v1, character cap, stable section_id slugs), IndexSettings and mismatch comparison (+15 more)

### Community 49 - "007 — Hybrid Retrieval Requirements"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "KnowledgeDocument"
Cohesion: 0.10
Nodes (8): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, _check_language_code(), KnowledgeDocument, ListRepository

### Community 51 - "evaluation/cli.py"
Cohesion: 0.13
Nodes (13): _authority_map(), collect(), _compare(), default_security_output_path(), format_security_summary(), format_summary(), main(), _security() (+5 more)

### Community 52 - "Roadmap"
Cohesion: 0.11
Nodes (19): Implementation, Review, T1 — round 1, User decision, EvaluationSchemas, _candidate_rules(), problem(), _describe() (+11 more)

### Community 53 - "FallbackRetriever"
Cohesion: 0.15
Nodes (14): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, FallbackRetriever, Hugging Face error shapes (T1 As-built), HybridRetriever / rrf_fuse (unchanged, fail closed) (+6 more)

### Community 54 - "SecurityIndex"
Cohesion: 0.16
Nodes (12): Review, EvaluationHarnessError, _lexical_sanity_check(), _open_lexical_sanity(), _sanity_check(), SecurityQuery, is_forbidden_document(), SecurityIndex (+4 more)

### Community 55 - "test_suite_v2.py"
Cohesion: 0.16
Nodes (21): LocalRepositoryConfig, test_agrees_with_day1_baseline(), test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found() (+13 more)

### Community 56 - "Development Workflow"
Cohesion: 0.10
Nodes (32): Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, Ingestion operating notes (QDRANT_COLLECTION_BASE for fake runs, make setup-bge-m3), agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+24 more)

### Community 57 - "query_terms"
Cohesion: 0.18
Nodes (6): query_terms(), test_a_forbidden_hit_injected_into_a_path_fails_the_gate_naming_it(), test_builder_refuses_a_non_throwaway_base_before_any_write(), test_builder_refuses_an_existing_collection(), test_each_forbidden_row_type_is_in_the_lexical_file(), test_zero_term_queries_skip_the_lexical_sanity_and_are_counted()

### Community 58 - "Phase 2 Knowledge Release workflow"
Cohesion: 0.16
Nodes (17): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+9 more)

### Community 59 - "json"
Cohesion: 0.09
Nodes (21): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+13 more)

### Community 60 - "COMMANDS.md (project command surface)"
Cohesion: 0.09
Nodes (24): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id>, Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder (+16 more)

### Community 61 - "RetrievalConfigurationError"
Cohesion: 0.13
Nodes (13): FakeEmbedder, __init__(), test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected() (+5 more)

### Community 62 - "test_content_hash.py"
Cohesion: 0.11
Nodes (24): canonical_json(), _canonical_value(), _canonical_value_mapping(), compute_body_sha256(), compute_content_hash(), normalize_body(), sha256_hex(), document_fields() (+16 more)

### Community 63 - "test_schemas.py"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 64 - "ARCHITECTURE.md"
Cohesion: 0.06
Nodes (38): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, bm25 builds no embedder and no Qdrant client, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned) (+30 more)

### Community 65 - "Security gate five paths, result 1.2"
Cohesion: 0.67
Nodes (3): Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), T6 security bm25 seed-subset check instead of verify_fresh

### Community 66 - "BGE-M3 embeddings"
Cohesion: 0.07
Nodes (32): make retrieve, D061 fallback marking, docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, strategy: bm25 (requested: hybrid; fallback: <reason>) plus stderr WARNING, exit 0, Fallback reasons qdrant_unavailable, qdrant_timeout, model_unavailable (never exception text), make index-lexical (+24 more)

### Community 67 - "Spec 007 hybrid retrieval"
Cohesion: 0.08
Nodes (35): build_retriever, make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: evaluation-data gaps (ml goldens, relevant_section_ids empty), Known issue: g004 overlaps u001, keep_both, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted) (+27 more)

### Community 68 - "Strategy"
Cohesion: 0.05
Nodes (70): Implementation, User decision, T10 — Documentation, decisions and hand-off, Verification, Alternatives / deferred decisions, Design summary, Interfaces / models, Package / file placement (+62 more)

### Community 69 - "test_strategy.py"
Cohesion: 0.27
Nodes (9): test_roles_match_policy_file(), test_committed_config_loads(), test_good_config_loads(), test_invalid_config_is_refused_naming_the_field(), test_timeout_bounds_are_inclusive(), test_unreadable_and_non_mapping_files_are_refused(), variant(), write() (+1 more)

### Community 70 - "Phase 1 RAG query pipeline"
Cohesion: 0.08
Nodes (33): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused) (+25 more)

### Community 71 - "healthcheck"
Cohesion: 0.10
Nodes (22): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Derived retrieval index in Qdrant (+14 more)

### Community 72 - "LoadedSuite"
Cohesion: 0.13
Nodes (9): CaseStatus, DatasetType, LoadedSuite, active_golden_cases(), _notes(), select_security_queries(), test_attack_types_are_split_into_run_deferred_and_unclassified(), case() (+1 more)

### Community 73 - "pytest"
Cohesion: 0.16
Nodes (15): clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload(), test_check_hit_rejects_malformed_payload() (+7 more)

### Community 74 - "Constitution"
Cohesion: 0.30
Nodes (16): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_errors(), test_frontmatter_missing_required_field(), test_frontmatter_schema_violation_names_document_and_field() (+8 more)

### Community 75 - "Section: Next step"
Cohesion: 0.15
Nodes (12): Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1), Generation metrics, Evaluation impact detection (+4 more)

### Community 76 - "Spec 007 - hybrid retrieval (verified 2026-10-28, merged 3cf70eb; 10 tasks)"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 77 - "pathlib"
Cohesion: 0.07
Nodes (24): EvaluationConfigurationError, DatasetRef, SuiteManifest, absent_query_languages(), active_registry_languages(), aggregate(), _mean(), slice_by() (+16 more)

### Community 78 - "test_repository_contract.py"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 79 - "Spec 005 dense retrieval baseline"
Cohesion: 0.16
Nodes (16): AccessContext, Role, W2A_TENANT_ID, make retrieval-baseline legacy frozen, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5, Next step 2: real BGE-M3 baseline committed, experiments/results/retrieval-baseline-idx-v1-20261023T063534Z.json real BGE-M3 baseline, Spec 005 dense retrieval baseline, Spec 005 status: verified 2026-10-23 merged b33462e (+8 more)

### Community 80 - "Spec 002 document model and repository"
Cohesion: 0.16
Nodes (15): Pydantic document models and enums, EligibilityPolicy for guest/public, LocalDocumentRepository with manifest schema validation, make validate-knowledge, Spec 002 decisions made before approval (content_hash, fixtures, validate-knowledge), Seed data status: 13 public docs, evaluation datasets, security fixtures, Spec 002 retrospective findings F1-F6, Spec 002 document model and repository (+7 more)

### Community 81 - "packages/rag"
Cohesion: 0.17
Nodes (16): eligible_ids(), IgnoresQueryRepository, make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded() (+8 more)

### Community 82 - "Ingestion pipeline (Spec 004)"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__"
Cohesion: 0.32
Nodes (8): classify_model_error, classify_qdrant_error, D057 Fallback eligibility classification, D062 5xx not eligible, Eligible failures: Qdrant connect/network, Qdrant timeout, model load/download failure with network __cause__, FallbackReason (qdrant_unavailable, qdrant_timeout, model_unavailable), RetrievalUnavailableError(reason), Non-fallback failures exit 2 (missing extra, model failure w/o network cause, HTTP error status, missing collection, mismatch, stale lexical file, authorization error)

### Community 84 - "git_state"
Cohesion: 0.09
Nodes (12): Change log, Implementation, Implementation, Review, T8 — round 1, T9 — round 1, User decision, security_document() (+4 more)

### Community 85 - "AccessContext"
Cohesion: 0.14
Nodes (9): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_tenant_is_stripped(), test_unknown_role_refused(), test_valid_context_is_frozen() (+1 more)

### Community 86 - "open_hybrid"
Cohesion: 0.23
Nodes (11): client_at(), closed_port(), open_hybrid(), run_cli(), test_a_missing_extra_at_open_is_raised_not_a_fallback(), no_extra(), test_cli_explicit_dense_with_qdrant_down_exits_2(), test_cli_hybrid_with_qdrant_down_prints_the_fallback_header() (+3 more)

### Community 87 - "Backend stack"
Cohesion: 0.06
Nodes (39): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Full agent orchestration (avoided), Intentionally avoided choices, Backend stack, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Custom retrieval metrics (plain Python) (+31 more)

### Community 88 - "open_retrieval / OpenedRetrieval"
Cohesion: 0.18
Nodes (11): open_retrieval / OpenedRetrieval, Open-time fallback lasts for the run, Qdrant connect/query timeouts (config 1.1), retrieval_client_factory, R5 — `bm25` without Qdrant or the `bge-m3` extra, Review F1: open-time outage serves whole run, Review F4: duplicated standalone open wiring, Review F5: bind_to scroll fallback untested end to end (+3 more)

### Community 89 - "D023 Task-gated agent workflow"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Roadmap 12 - Security"
Cohesion: 0.25
Nodes (8): Authorization regression and staff canary, BGE-M3 (roadmap), Citation manipulation tests and input/cost limits, Backend-owned citation validation, Roadmap 4 - Dense retrieval baseline, Roadmap 12 - Security, Prompt injection and poisoned retrieved content tests, Public access filter

### Community 91 - "DocumentRepository"
Cohesion: 0.14
Nodes (14): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, Way2Australia AI Platform Master Implementation Plan, Phase 1 Definition of Done, Document manifest, DocumentRepository, LocalDocumentRepository (+6 more)

### Community 92 - "make eval-compare"
Cohesion: 0.09
Nodes (24): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), schemas.py, validate.py (referencing registry, validate-evaluation checks), eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+16 more)

### Community 93 - "pathlib"
Cohesion: 0.25
Nodes (9): apps/api, apps/web, CloudWatch, Future multimodal mock-test evaluation, Langfuse tracing, packages/core, packages/observability, packages/rag (+1 more)

### Community 94 - "AGENTS.md Project Rules"
Cohesion: 0.23
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 95 - "make index-lexical"
Cohesion: 0.18
Nodes (15): load_suite(), live_suite_rows(), golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned(), copy_suite(), test_access_context_is_loaded_but_ignored() (+7 more)

### Community 96 - "IngestionService"
Cohesion: 0.17
Nodes (13): Deduplication, context budgeting, evidence ordering, Roadmap 9 - Reranking + context building, Reranker failure to hybrid results, Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus (+5 more)

### Community 97 - "SpyIndex"
Cohesion: 0.19
Nodes (14): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Evaluation Governance (keep/modify/deprecate/replace), Versioned Evaluation Suite (+6 more)

### Community 99 - "CURRENT_STATE.md"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "DocumentQuery"
Cohesion: 0.22
Nodes (4): _document_ids(), collect(), DocumentQuery, test_ineligible_document()

### Community 102 - "006 Evaluation Framework Tasks"
Cohesion: 0.09
Nodes (24): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical (+16 more)

### Community 104 - "Retrieval package (Spec 005 and 007)"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "007 — Hybrid Retrieval Tasks"
Cohesion: 0.22
Nodes (8): 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Verification, Verification

### Community 106 - "Qdrant (vector database)"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "IndexIdentity"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 109 - "Authorization enforced before generation"
Cohesion: 0.29
Nodes (6): Authorization model (guest/public), Graceful degradation, Poisoned public document fixture, Security plan (threats and controls), SQLite FTS5 fallback, Staff-only canary fixture

### Community 110 - "test_every_path_is_gated_for_every_query"
Cohesion: 0.33
Nodes (3): test_every_path_is_gated_for_every_query(), counting(), counting()

### Community 111 - "test_content_hash.py"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "R8 — Evaluation results for degraded runs"
Cohesion: 0.40
Nodes (6): Acceptance criteria, Acceptance criteria, R8 — Evaluation results for degraded runs, R9 — `eval-compare` by served strategy, index_settings=None refusal rule (T3 F2), T5 Result 2.2 and eval-compare by served strategy

### Community 113 - "test_violation_names_the_document_from_the_error_attribute"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "pytest"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 115 - "test_bm25.py"
Cohesion: 0.12
Nodes (19): BM25, Deterministic regression gates, FastAPI skeleton, Golden, refusal and security cases, HitRate@5, Roadmap 1 - Project foundation, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval (+11 more)

### Community 116 - "fusion"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "evaluation/cli.py"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 119 - "Roadmap 3 - Ingestion baseline"
Cohesion: 0.67
Nodes (4): Content hashing, Idempotent ingestion, Roadmap 3 - Ingestion baseline, Preview indexing

### Community 120 - "failing_client"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "test_status_handling.py"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "dense"
Cohesion: 0.04
Nodes (43): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R11 — Security gate (`security_index.py`, `security_eval.py`), R12 — Docker test, R1 — Suite v2, R4 — `make index-lexical` (`lexical/cli.py`), R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`) (+35 more)

### Community 124 - "hashing.py"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 125 - "test_security_eval.py"
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

### Community 130 - "Evaluation result format 2.2"
Cohesion: 0.33
Nodes (6): eval-compare by served strategy (mixed refused), Latency grouped by served path, Evaluation result format 2.2, RetrievalResult marking (requested_strategy, fallback_reason), Review F2: result 2.2 does not record fallback stage, T4 deviations (header only on fallback, requested_strategy by wrapper)

### Community 131 - "RuntimeSettings"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 132 - "R12 — Real runs (user-owned gate)"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 133 - "Vocabulary, flashcards and free access"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - ".search"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "Spec 008 Retrieval Fallback Requirements"
Cohesion: 0.50
Nodes (4): Change log, Spec 008 Retrieval Fallback Requirements, Spec 008 Retrospective Review round 1, Review F3: missing change-log lines (resolved)

### Community 138 - "Evaluation Framework Goal"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 140 - "pytest"
Cohesion: 0.22
Nodes (8): live_client(), chunk(), test_dedupe_keeps_first_rank(), test_hit_rate_and_cutoff(), test_percentile_nearest_rank(), test_random_hit_rate_cap_and_minimum(), test_recall_with_several_relevant(), test_reciprocal_rank()

### Community 141 - "BGE-M3 (initial embedding model)"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Way2Australia AI Platform Master Implementation Plan"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 144 - "eval-compare"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Payments, account access and support boundaries"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "Home Affairs credentialled community language points"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 147 - "make test"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Mission"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 151 - "policy"
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

### Community 158 - "Orchestrator State Machine"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "way2australia_api/__init__.py"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Project Context README"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 167 - "api/__init__.py"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 170 - "tests/evaluation/__init__.py"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-api`, `way2australia-core`, `way2australia-observability`, `way2australia-rag`, `way2australia` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1229 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `git_state` to `DenseRetriever`, `Spec 007 hybrid retrieval`, `Strategy`, `ResolvedAccess`, `test_seed_corpus.py`, `LocalDocumentRepository`, `Document Model Tests`, `Retrieval Eval Tests`, `SecurityIndex`, `rrf_fuse`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 78 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 78 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-api`, `way2australia-core`, `way2australia-observability` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DenseRetriever` be split into smaller, more focused modules?**
  _Cohesion score 0.05855855855855856 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Spec 007 hybrid retrieval` to `Development Workflow`, `typing`, `Ingestion pipeline (Spec 004)`, `test_lexical_cli.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `LocalDocumentRepository` (e.g. with `Dependencies` and `Design summary`) actually correct?**
  _`LocalDocumentRepository` has 21 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._