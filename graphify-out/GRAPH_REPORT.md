# Graph Report - way2australia  (2026-11-01)

## Corpus Check
- 53 files · ~272,093 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 4001 nodes · 10731 edges · 191 communities (158 shown, 33 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 1826 edges (avg confidence: 0.92)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Community 0
- Task Review Log (T7)
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Model Tiers
- Day-1 Data and Sources
- Strategy Eval Tests
- Community 17
- Index Binding Errors
- Document Model Tests
- Retrieval Eval Tests
- Community 21
- Date and Policy Tests
- BGE-M3 Adapter
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Evaluation CLI Tests
- Community 30
- Community 31
- Retrieval Package
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Health Endpoint
- Evaluation Slices
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 74
- Community 75
- Community 76
- Community 77
- Community 78
- Community 79
- Community 80
- Community 81
- Community 82
- Community 83
- Community 84
- Community 85
- Community 86
- Community 87
- Community 88
- Community 89
- Community 90
- Community 91
- Community 92
- Community 93
- Community 94
- Community 95
- Community 96
- Community 97
- Community 98
- Community 99
- Community 100
- Community 101
- Community 102
- Community 103
- Community 104
- Community 105
- Community 106
- Community 107
- Community 108
- Community 109
- Community 110
- Community 111
- Community 112
- Community 113
- Community 114
- Community 115
- Community 116
- Community 117
- Community 118
- Community 119
- Community 120
- Community 121
- Community 122
- Community 123
- Community 124
- Community 125
- Community 126
- Community 127
- Community 128
- Community 129
- Community 130
- Community 131
- Community 132
- Community 133
- Community 134
- Community 135
- Community 136
- Community 137
- Community 138
- Community 139
- Community 140
- Community 141
- Community 142
- Community 143
- Community 144
- Community 145
- Community 146
- Community 147
- Community 148
- Community 149
- Community 150
- Community 151
- Community 152
- Community 153
- Community 154
- Community 155
- Community 156
- Community 157
- Community 158
- Community 159
- Community 160
- Community 161
- Community 162
- Community 163
- Community 164
- Community 165
- Community 166
- Community 167
- Community 168
- Community 169
- Community 170
- Community 171
- Community 173
- Community 174
- Community 175
- Community 176
- Community 179
- Community 180
- Community 181
- Community 184
- Community 185
- Community 188
- Community 189
- Community 190

## God Nodes (most connected - your core abstractions)
1. `DenseIndex` - 98 edges
2. `DECISIONS.md architecture decision log` - 62 edges
3. `CURRENT_STATE.md current state document` - 58 edges
4. `DenseRetriever` - 57 edges
5. `RetrievalConfigurationError` - 55 edges
6. `IndexIdentity` - 53 edges
7. `RetrievalResult` - 51 edges
8. `open_retrieval()` - 51 edges
9. `dense()` - 47 edges
10. `run_security_evaluation()` - 45 edges

## Surprising Connections (you probably didn't know these)
- `Testing / evaluation strategy` --references--> `rrf_fuse()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/design.md → packages/rag/src/way2australia_rag/retrieval/fusion.py
- `Acceptance criteria` --references--> `RetrievalConfig`  [INFERRED]
  .kiro/specs/008-retrieval-fallback/requirements.md → packages/rag/src/way2australia_rag/retrieval/strategy.py
- `Traceability` --references--> `open_retrieval()`  [INFERRED]
  .kiro/specs/008-retrieval-fallback/requirements.md → packages/rag/src/way2australia_rag/retrieval/opening.py
- `Acceptance criteria` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/tests/retrieval/test_bm25.py
- `Acceptance criteria` --references--> `dense()`  [INFERRED]
  .kiro/specs/007-hybrid-retrieval/requirements.md → packages/rag/tests/retrieval/test_bm25.py

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

## Communities (191 total, 33 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (88): Implementation, Review, T7 — round 1, User decision, Implementation, Review, T5 — round 1, User decision (+80 more)

### Community 1 - "Task Review Log (T7)"
Cohesion: 0.06
Nodes (11): default_output_path(), _parser(), ChunkerConfig, EmbedderConfig, IngestionConfig, load_ingestion_config(), _parser(), test_agrees_with_day1_baseline() (+3 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (34): DocumentRepositoryError, DocumentValidationError, DuplicateDocumentError, ManifestValidationError, split_frontmatter(), _StringDateLoader, compute_body_sha256(), compute_content_hash() (+26 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (38): LexicalRow, DenseIndex, OddIdStore, build(), dense_fixture(), DroppedClauseIndex, guest(), pub() (+30 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (55): committed(), edit_jsonl(), lines(), manifest(), problems(), read_lines(), root(), test_candidates_differ_only_in_promoted_as() (+47 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (53): R3 — Tokenizer `lexical-v1` (`lexical/tokenizer.py`), HeadingChunker, _is_word_char(), _parse_sections(), _Section, slugify(), _split_body(), _split_words() (+45 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (23): forbidden_variant(), resolve_access(), match_expression(), format_result(), main(), _parser(), _strategy_line(), RetrievalConfigurationError (+15 more)

### Community 7 - "Community 7"
Cohesion: 0.10
Nodes (42): IndexBindingError, bound_index(), client(), failing_client(), fake_info(), http_client(), make_settings(), open_index() (+34 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (33): Decisions D056-D062, Spec 008 Retrieval Fallback Design, R3 — Standalone lexical open (`identity.py`, `lexical/store.py`), R5 — `bm25` without Qdrant or the extra (`bm25.py`), R6 — `FallbackRetriever` (`fallback.py`) and `open_retrieval` (`opening.py`), Repeated finding: graphify update ownership, Spec 008 Task Reviews, Implementation (+25 more)

### Community 9 - "Community 9"
Cohesion: 0.05
Nodes (27): R8 — Result format 2.2 (`retrieval_eval.py`), User decision, _authority_map(), default_security_output_path(), format_summary(), main(), _retrieval(), real_embedder_factory() (+19 more)

### Community 10 - "Community 10"
Cohesion: 0.06
Nodes (34): T2 — v2 dense baseline (user-owned gate), Verification, dedupe_sections(), section_key(), section_report(), load_runtime_settings(), _aggregate(), BaselineResult (+26 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (41): Implementation, Implementation, Review, Review, T3 — round 2, T3 — round 3, User decision, default_lexical_dir() (+33 more)

### Community 12 - "Community 12"
Cohesion: 0.10
Nodes (27): write_document(), basic_suite(), build(), fusion_config(), run(), Scripted, scripted_run(), suite_with_unanswerable() (+19 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (33): run_security_evaluation(), build(), DroppedClauseLexical, guest_access(), new_base(), real_queries(), seed_repository(), spied() (+25 more)

### Community 14 - "Model Tiers"
Cohesion: 0.08
Nodes (17): BgeM3Embedder, _group_installed(), EmbedderInfo, IngestionConfigurationError, OptionalDependencyError, missing(), group_installed(), test_constructing_does_not_load_the_model() (+9 more)

### Community 15 - "Day-1 Data and Sources"
Cohesion: 0.11
Nodes (29): Review, User decision, build_lexical(), configured_lexical(), eval_world(), lexical_env(), retrieve(), retrieve_world() (+21 more)

### Community 16 - "Strategy Eval Tests"
Cohesion: 0.08
Nodes (44): build_retriever, CURRENT_STATE.md current state document, Current goal: Specs 001-008 complete; Spec 008 verified and merged into main (1107b67), plan next spec, Phase 2 Knowledge Release workflow designed not implemented, Public/guest retrieval only in Phase 1; English + Malayalam, Known issue: Qdrant and Hugging Face 5xx not fallback-eligible, Known issue: legacy chillu sequence does not match atomic chillu in BM25, Known issue: Qdrant client lifecycle leak on failed open (+36 more)

### Community 17 - "Community 17"
Cohesion: 0.06
Nodes (43): Error and failure behavior, R9 — `eval-compare` (`results.py`, `compare.py`), Security gate five paths, result 1.2, _UnavailableDense (harness-only fault injection), 008 — Retrieval Fallback Requirements, Acceptance criteria, Acceptance criteria, Acceptance criteria (+35 more)

### Community 18 - "Index Binding Errors"
Cohesion: 0.15
Nodes (23): IndexSettingsMismatchError, QdrantIndexStore, read_index_settings(), client(), test_replace_and_delete_flows(), make_points(), make_settings(), snapshot() (+15 more)

### Community 19 - "Document Model Tests"
Cohesion: 0.12
Nodes (21): DenseRetriever, build_client(), docs(), guest(), open_spy(), RaisingEmbedder, retriever(), test_a_network_failure_during_model_load_is_unavailable() (+13 more)

### Community 20 - "Retrieval Eval Tests"
Cohesion: 0.05
Nodes (40): BM25Retriever with SQL access clause, eval-compare identity rules (R10), HybridRetriever (dense leg then BM25 leg, no single-leg fallback), lexical-v1 tokenizer (NFC, ZWJ/ZWNJ dropped, L/N/Mn/Mc token chars, 64-term cap), Result format 2.1 and security result 1.1, config/retrieval.yaml and build_retriever strategy factory, Security gate over dense, bm25 and hybrid, SQLite FTS5 lexical store (derived, git-ignored, bound to dense index) (+32 more)

### Community 21 - "Community 21"
Cohesion: 0.10
Nodes (24): case(), clean_env(), cli_run(), DeviceStub, _git(), run(), seeded(), setup() (+16 more)

### Community 22 - "Date and Policy Tests"
Cohesion: 0.10
Nodes (22): Review, classify_model_error(), classify_qdrant_error(), _optional_types(), raise_if_unavailable(), caused_by(), handled_error(), reason() (+14 more)

### Community 23 - "BGE-M3 Adapter"
Cohesion: 0.06
Nodes (18): Model Preferences, Agent Skills README, Implementation Checklist, Spec Implementer Skill, task-reviews.md Implementation Block, Design Template, Change Log, Requirements Template (+10 more)

### Community 24 - "Community 24"
Cohesion: 0.05
Nodes (33): Day-1 Usage, document_manifest.jsonl, golden_public.jsonl, Source-of-Truth Policy, chunking, overlap_tokens, strategy, target_tokens (+25 more)

### Community 25 - "Community 25"
Cohesion: 0.07
Nodes (40): HeadingChunker heading v1 2000-char cap, Pydantic document models and enums, EligibilityPolicy for guest/public, Embedder Protocol, fake and BGE-M3 adapter, IngestionService change detection, LocalDocumentRepository with manifest schema validation, make ingest and config/ingestion.yaml, 17-field PointPayload and UUIDv5 point IDs (+32 more)

### Community 26 - "Community 26"
Cohesion: 0.09
Nodes (18): RuntimeSettings, guest_access(), test_guest_access_uses_settings_tenant(), clean_env(), _Factory, _FixedDatetime, _record_opens(), note() (+10 more)

### Community 27 - "Community 27"
Cohesion: 0.14
Nodes (22): _advice_ok(), clean_env(), Factory, indexed(), ingest(), retrieve(), test_bad_args_exit_2_without_client(), test_bad_config_exit_2_without_client() (+14 more)

### Community 28 - "Community 28"
Cohesion: 0.11
Nodes (26): As-built notes, Package / file placement, R7 — Fusion and `HybridRetriever` (`retrieval/fusion.py`, `hybrid.py`), Change log, Implementation, Implementation, Implementation, Review (+18 more)

### Community 29 - "Evaluation CLI Tests"
Cohesion: 0.12
Nodes (31): assert_invalid(), document_fields(), make_document(), test_blank_required_text_is_rejected(), test_document_is_immutable(), test_duplicate_lote_languages_are_rejected(), test_effective_window_must_be_ordered(), test_empty_lote_languages_is_rejected() (+23 more)

### Community 30 - "Community 30"
Cohesion: 0.11
Nodes (20): clean_env(), copy_fixtures(), _lexical_work_dir(), spy_lexical_path(), wrapper(), SpyIndex, strip_forbidden_terms(), test_a_lexical_sanity_failure_is_a_harness_error() (+12 more)

### Community 31 - "Community 31"
Cohesion: 0.22
Nodes (26): load(), test_bad_date_fails_loading_naming_document_and_field(), test_seed_corpus_still_loads(), test_valid_date_loads(), build_repo(), metadata(), problems_for(), run_cli() (+18 more)

### Community 32 - "Retrieval Package"
Cohesion: 0.10
Nodes (13): _document_ids(), collect(), DocumentQuery, DocumentRepository, EligibilityPolicy, list_eligible_documents(), LocalDocumentRepository, _corpus_problems() (+5 more)

### Community 33 - "Community 33"
Cohesion: 0.13
Nodes (20): build_from(), built(), copy_repository(), expected(), first_document_id(), open_it(), remove_document(), repo_at() (+12 more)

### Community 34 - "Community 34"
Cohesion: 0.09
Nodes (34): AccessContext, Role, W2A_TENANT_ID, DenseIndex, build_access_filter, check_hit, DenseRetriever, make eval-retrieval, FallbackRetriever and open_retrieval wiring (merged 1107b67), make retrieve guest/public CLI, Strategy Protocol, BM25Retriever, rrf_fuse, HybridRetriever, BGE-M3 device mps not pinned (D038), Spec 005 retrospective findings F3-F5 (+26 more)

### Community 35 - "Community 35"
Cohesion: 0.13
Nodes (17): FallbackReason, FallbackRetriever, access(), Fallback, Primary, test_a_fallback_error_is_raised(), test_a_model_load_failure_with_a_network_cause_falls_back(), test_dense_leg_failure_on_one_query_leaves_the_others_hybrid() (+9 more)

### Community 36 - "Community 36"
Cohesion: 0.10
Nodes (19): T2: where the shared pieces live (2026-10-31), Acceptance criteria, Acceptance criteria, R3 — Lexical index without Qdrant, R4 — Freshness check from the repository, Implementation, Implementation, Review (+11 more)

### Community 37 - "Community 37"
Cohesion: 0.11
Nodes (32): Binding: embedder model ID, revision, vector size, normalization, fake flag and index_version must equal recorded IndexSettings, BM25Retriever(identity, lexical), BM25 statistics (IDF, avg length) computed over every row of a lexical file, build_access_filter (the only filter builder), build_retriever (only place a strategy name becomes a retriever), retrieval_client_factory (Qdrant client with configured timeouts), config/retrieval.yaml (default_strategy hybrid, RRF k 60, depth 50), D033-D041 retrieval decisions (+24 more)

### Community 38 - "Health Endpoint"
Cohesion: 0.14
Nodes (25): Error and failure behavior, Phase 2 compatibility / migration, Security / authorization, Acceptance criteria, Acceptance criteria, Dependencies, Implementation, Review (+17 more)

### Community 39 - "Evaluation Slices"
Cohesion: 0.11
Nodes (21): format_summary(), main(), test_eval_cli_unknown_strategy_is_a_usage_error(), clean_env(), _factory(), _run(), test_builds_exactly_one_embedder_per_run(), test_collection_base_comes_from_environment() (+13 more)

### Community 40 - "Community 40"
Cohesion: 0.11
Nodes (14): get_health(), HealthResponse, get_request_settings(), get_settings(), Settings, create_app(), isolate_settings_environment(), test_create_app_wires_settings() (+6 more)

### Community 41 - "Community 41"
Cohesion: 0.10
Nodes (31): 006-candidates.jsonl with 7 suggested rows, make eval-compare, make eval-security hard gate, result 2.2 and served-strategy eval-compare, eval-security five paths, governed suite loader and schemas, make validate-evaluation, Spec 006 retrospective findings (F1 byte-identity, eval-security not in verify) (+23 more)

### Community 42 - "Community 42"
Cohesion: 0.09
Nodes (19): 008 — Retrieval Fallback Design, Alternatives / deferred decisions, Data flow, Interfaces / models, Observability, Package / file placement, Phase 2 compatibility / migration, R2 — Qdrant timeouts (`qdrant_client.py`, `config/retrieval.yaml`) (+11 more)

### Community 43 - "Community 43"
Cohesion: 0.11
Nodes (12): Chunk, Chunker, Embedder, IngestionError, build_payload(), DocumentFailure, IngestionService, _reason() (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.08
Nodes (30): Answerability and insufficient-evidence response, Authorization regression and staff canary, Docker, Terraform, EC2, ECR, CloudWatch, IAM, Bedrock, Bedrock Runtime (roadmap), BGE-M3 (roadmap), Deferred serving concerns (circuit breaker, startup policy, Qdrant 5xx D062), Citation manipulation tests and input/cost limits, Backend-owned citation validation (+22 more)

### Community 45 - "Community 45"
Cohesion: 0.09
Nodes (16): R11 — Security gate (`security_index.py`, `security_eval.py`), Implementation, Review, T8 — round 1, User decision, format_security_summary(), _security(), EvaluationHarnessError (+8 more)

### Community 46 - "Community 46"
Cohesion: 0.11
Nodes (18): Implementation, Implementation, Review, T3 — round 1, User decision, T3 — `lexical-v1` tokenizer, lexical store and `make index-lexical`, Verification, R4 — Freshness from the repository (`lexical/freshness.py`) (+10 more)

### Community 47 - "Community 47"
Cohesion: 0.11
Nodes (14): deterministic_clock(), equivalence_suite(), run_equivalence(), golden(), suite_of(), test_active_golden_without_relevant_documents_is_refused(), test_case_access_context_never_widens_access(), spy() (+6 more)

### Community 48 - "Community 48"
Cohesion: 0.09
Nodes (27): BgeM3Embedder (optional bge-m3 extra, dense only), D025-D030, D032 ingestion decisions, DocumentRepository Protocol (get_document, list_documents), Embedder Protocol, Evaluation architecture (Evaluation Suite case types), Evaluation cases have stable IDs and versions; not coupled to chunk IDs, FakeEmbedder (deterministic), HeadingChunker (heading v1, character cap, stable section_id slugs) (+19 more)

### Community 49 - "Community 49"
Cohesion: 0.09
Nodes (27): optional bge-m3 extra (sentence-transformers, PyTorch), D048 graphify tooling, make experiment CONFIG=... (target; records git commit, release, suite, chunker, embedder, strategy, metrics, latency), make format, Knowledge graph graphify (D048), /graphify . --update (user, once per spec after merge), graphify query / path / explain, graphify update . (+19 more)

### Community 50 - "Community 50"
Cohesion: 0.10
Nodes (5): _check_language_code(), KnowledgeDocument, DocumentNotFoundError, ListRepository, IgnoresQueryRepository

### Community 51 - "Community 51"
Cohesion: 0.11
Nodes (17): PointPayload, compare(), IndexSettings, mismatch_message(), base_settings(), test_build_index_settings_records_embedder_and_chunker(), test_compare_equal_and_ignores_hash_contract(), test_compare_reports_each_other_field() (+9 more)

### Community 52 - "Community 52"
Cohesion: 0.18
Nodes (16): R1 — Suite v2, Review, _notes(), _candidate_rules(), problem(), _describe(), _document_problems(), EvaluationProblem (+8 more)

### Community 53 - "Community 53"
Cohesion: 0.08
Nodes (27): Fallback authorization invariant (same ResolvedAccess), BM25Retriever (identity, lexical), classify_model_error, classify_qdrant_error, Qdrant client lifecycle gap, eval-compare by served strategy (mixed refused), FallbackRetriever, Hugging Face error shapes (T1 As-built) (+19 more)

### Community 54 - "Community 54"
Cohesion: 0.10
Nodes (13): _gate(), _lexical_sanity_check(), _open_lexical_sanity(), _path_strategy(), _sanity_check(), security_document(), SecurityQuery, SecurityReport (+5 more)

### Community 55 - "Community 55"
Cohesion: 0.21
Nodes (17): LocalRepositoryConfig, test_repository_content_hash_is_content_hash_v1(), test_seed_corpus_is_entirely_eligible_for_guest(), _copy_seed(), seed_repository(), test_documents_outside_approved_roots_are_never_loaded(), test_get_document_by_id_and_version(), test_get_document_missing_raises_not_found() (+9 more)

### Community 56 - "Community 56"
Cohesion: 0.12
Nodes (26): Evaluation Suite includes goldens, refusal, multilingual, security, regression, Finalized stack: Python/FastAPI, Next.js, Qdrant, SQLite FTS5, BGE-M3, Bedrock, Langfuse, CloudWatch, Terraform ap-south-1, GitHub Actions, agent-skills sync, D001 Python-first backend, D002 RAG as reusable internal package, D003 Knowledge outside RAG package, D005 Documents are truth; chunks are derived, D007 Public-only Phase 1 (+18 more)

### Community 57 - "Community 57"
Cohesion: 0.11
Nodes (16): _is_token_char(), query_terms(), QueryTerms, tokenize(), test_business_008_words_stay_whole(), test_deterministic(), test_english_punctuation_digits_and_case(), test_golden_file_is_the_source_of_the_pins() (+8 more)

### Community 58 - "Community 58"
Cohesion: 0.19
Nodes (14): clean_env(), index_factory(), real_factory(), run(), test_bad_top_k_exits_2(), test_existing_output_exits_2_before_qdrant(), test_fake_embedder_exits_2_before_qdrant(), test_filter_carries_the_server_tenant() (+6 more)

### Community 59 - "Community 59"
Cohesion: 0.09
Nodes (22): chunker, max_chunk_chars, name, version, embedder, batch_size, fake_vector_size, model_id (+14 more)

### Community 60 - "Community 60"
Cohesion: 0.09
Nodes (24): D042-D047, D053, D054 evaluation decisions, Evaluation assets never written by evaluation code (C6); candidates suggested and human-activated, Ingestion eligibility is the only guard against synthetic/unapproved documents; poisoned_public_document is not an authorization case, Evaluation isolation and gates, models.py, suite.py (tolerant typed cases, read-only load_suite), retrieval_eval.py, slices.py, sections.py, Section-level keys <document_id>#<section_id>, Security gate on throwaway w2a-sectest-<8 hex> collection with fake embedder (+16 more)

### Community 61 - "Community 61"
Cohesion: 0.14
Nodes (13): FakeEmbedder, test_conforms_to_protocol(), test_declared_vector_size(), test_default_size_is_64(), test_fake_device_is_none(), test_info_reports_fake_identity(), test_invalid_vector_size_rejected(), test_no_pytorch_import() (+5 more)

### Community 62 - "Community 62"
Cohesion: 0.15
Nodes (15): build_access_filter(), clean_env(), guest(), payload(), _policy(), test_a_different_policy_changes_both_builders(), test_both_builders_cover_the_same_three_conditions(), test_check_hit_accepts_valid_payload() (+7 more)

### Community 63 - "Community 63"
Cohesion: 0.19
Nodes (12): build_production(), ingest_dense(), open_lexical(), repository(), rewrite_settings(), test_bind_does_not_write_to_qdrant(), test_bind_refuses_chunk_set_mismatch_with_counts(), test_bind_refuses_identity_and_chunker_mismatch() (+4 more)

### Community 64 - "Community 64"
Cohesion: 0.21
Nodes (17): identity(), payload(), synthetic_entries(), build(), test_atomic_replace_keeps_old_file_after_failure(), test_build_production_helper_runs(), test_build_records_settings(), test_digest_is_stable_and_order_independent() (+9 more)

### Community 65 - "Community 65"
Cohesion: 0.11
Nodes (23): Answerability / insufficient-evidence decision, Authorization applied inside each retriever before fusion, never after RRF, reranking or generation, Authorization filter is part of the Qdrant query so unauthorized points never leave the store, Amazon Bedrock generation, check_hit (fail-closed re-check, second line of defense), Citation validation, Context builder (planned), D035 Future fallbacks must take the same ResolvedAccess and call check_hit (+15 more)

### Community 66 - "Community 66"
Cohesion: 0.09
Nodes (23): make retrieve, docker compose up -d / down (local Qdrant), Environment: QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION_BASE, W2A_TENANT_ID, Fake embedder needs throwaway QDRANT_COLLECTION_BASE, make ingest, INGEST_ARGS (--embedder {bge_m3,fake}, --config), ingest exit codes 0 success, 1 document failed, 2 refusal, Ingest summary lines (index:, added/updated/unchanged/deleted, ERROR lines) (+15 more)

### Community 67 - "Community 67"
Cohesion: 0.10
Nodes (23): make retrieval-baseline legacy frozen, RetrievalUnavailableError and availability classification, Known issue: git_dirty true in Spec 007 BM25/hybrid result files (user-accepted), Latency hybrid p50 80.3 ms p95 103.6 ms; bm25 p50 0.19 ms, BM25 metrics: 64/69 goldens, MRR 0.7082, Hybrid metrics: 68/69 goldens, MRR 0.9094, Retrieval misses g004 g026 g061, Next step 2: real BGE-M3 baseline committed (+15 more)

### Community 68 - "Community 68"
Cohesion: 0.13
Nodes (15): As-built notes, Components / boundaries, Design summary, R10 — Security gate (`security_eval.py`), R1 — Failure classification (`errors.py`, `availability.py`), R7 — Marking (`models.py`, `retrieval/cli.py`), T1: Hugging Face error shapes (confirmed 2026-10-29), Testing / evaluation strategy (+7 more)

### Community 69 - "Community 69"
Cohesion: 0.18
Nodes (12): client_at(), closed_port(), open_hybrid(), run_cli(), stalled_port(), test_a_missing_extra_at_open_is_raised_not_a_fallback(), no_extra(), test_cli_explicit_dense_with_qdrant_down_exits_2() (+4 more)

### Community 70 - "Community 70"
Cohesion: 0.13
Nodes (22): bm25 strategy, bm25 needs neither Qdrant nor the bge-m3 extra (Spec 008), config/retrieval.yaml schema 1.1 (default_strategy hybrid, qdrant.connect_timeout_s 2, query_timeout_s 3; 1.0 refused), dense strategy, --strategy dense needs no lexical file, Embedder pair from index_settings or dense_identity; fallback-only 2.2 file compares against Spec 007 bm25 file, eval-retrieval fallback: Qdrant unreachable with default hybrid is served by bm25 for every case, eval-retrieval options (--top-k, --strategy, --retrieval-config, --suite default public-eval-v2, --release seed-v1, --output, --repo-root, --config); no --embedder or --allow-fake (+14 more)

### Community 71 - "Community 71"
Cohesion: 0.10
Nodes (22): Roadmap 11 - Observability, Langfuse traces, Stage latency, model/tokens/cost, release/config IDs, AWS target, Bedrock Knowledge Bases as core RAG (avoided), Bedrock model selection criteria, Amazon CloudWatch, Derived retrieval index in Qdrant (+14 more)

### Community 72 - "Community 72"
Cohesion: 0.18
Nodes (8): CaseBase, CaseStatus, DatasetRef, GoldenCase, SecurityCase, SuiteManifest, UnanswerableCase, load_golden_cases()

### Community 73 - "Community 73"
Cohesion: 0.14
Nodes (11): AccessContext, Role, test_blank_tenant_refused(), test_empty_tenant_refused(), test_no_language_or_scope_fields(), test_roles_match_policy_file(), test_tenant_is_stripped(), test_unknown_role_refused() (+3 more)

### Community 74 - "Community 74"
Cohesion: 0.29
Nodes (18): metadata(), record(), run(), test_duplicate_document_id_rejected(), test_duplicate_document_version_rejected(), test_frontmatter_missing_required_field(), test_frontmatter_parsing_keeps_dates_as_strings(), test_frontmatter_schema_violation_names_document_and_field() (+10 more)

### Community 75 - "Community 75"
Cohesion: 0.10
Nodes (20): Way2Australia AI Platform Master Implementation Plan, Atomic publish and rollback, Phase 2 audit trail, Controlled document-change workflow (Release Candidate), Phase 1 Definition of Done, Evaluation governance states, Evaluation slices, Evaluation Suite (public-eval-v1) (+12 more)

### Community 76 - "Community 76"
Cohesion: 0.10
Nodes (21): Completion: retrospective, Spec-Review commit, merge, verified status, Spec orchestrator loop (route, role subagents, user approval, merge), GET /health endpoint, make setup, packages core/rag/observability skeletons, task-gated spec skills and skills-sync, task State lifecycle and spec/NNN branches, uv workspace and uv.lock (+13 more)

### Community 77 - "Community 77"
Cohesion: 0.11
Nodes (15): Implementation, Review, T2 — round 1, User decision, absent_query_languages(), aggregate(), _mean(), slice_by() (+7 more)

### Community 78 - "Community 78"
Cohesion: 0.16
Nodes (11): EvaluationConfigurationError, active_registry_languages(), declared_release_id(), inside(), read_dataset(), read_json(), read_manifest(), test_missing_registry_section_is_a_configuration_error() (+3 more)

### Community 79 - "Community 79"
Cohesion: 0.10
Nodes (6): collection_name(), IndexedDocument, IndexPoint, test_collection_name_derivation(), CountingEmbedder, CountingStore

### Community 80 - "Community 80"
Cohesion: 0.14
Nodes (9): test_hybrid_leg_ranks_use_document_rank_and_null_for_absence(), chunk(), retrieve(), client_with_forbidden(), FilterDroppingIndex, test_forbidden_points_are_never_returned(), test_store_dropping_the_filter_fails_closed(), make_payload() (+1 more)

### Community 81 - "Community 81"
Cohesion: 0.23
Nodes (15): eligible_ids(), make_document(), test_active_approved_public_document_is_eligible(), test_language_filter_narrows_eligible_documents_only(), test_language_metadata_does_not_broaden_access(), test_local_repository_applies_the_policy_query(), test_non_active_lifecycle_is_excluded(), test_non_approved_status_is_excluded() (+7 more)

### Community 82 - "Community 82"
Cohesion: 0.11
Nodes (18): default_strategy, fusion, candidate_depth, k, method, weights, qdrant, connect_timeout_s (+10 more)

### Community 83 - "Community 83"
Cohesion: 0.12
Nodes (19): bm25 builds no embedder and no Qdrant client, classify_model_error, classify_qdrant_error, D056-D062 fallback decisions, D057 Fallback eligibility classification, D058 Fallback policy per query, D061 Marking and evaluation of fallback, D062 5xx not eligible (+11 more)

### Community 84 - "Community 84"
Cohesion: 0.19
Nodes (11): InMemoryDocumentRepository, make_document(), test_document_query_has_no_filesystem_concepts(), test_document_query_is_immutable(), test_get_document_missing_raises_not_found(), test_get_document_returns_latest_or_requested_version(), test_in_memory_repository_satisfies_protocol(), test_list_documents_applies_query_filters() (+3 more)

### Community 85 - "Community 85"
Cohesion: 0.20
Nodes (12): rrf_fuse(), chunk(), test_both_legs_empty(), test_duplicate_in_a_leg_counts_best_rank_only(), test_empty_leg_keeps_the_other_order(), test_equal_scores_and_ranks_break_by_point_id(), test_equal_scores_break_by_best_rank_before_point_id(), test_first_seen_chunk_is_kept() (+4 more)

### Community 86 - "Community 86"
Cohesion: 0.23
Nodes (13): _copy_seed(), h(), _load(), test_absent_optional_fields_hash_as_null(), test_body_change_changes_content_hash(), test_content_hash_is_stable_and_pinned(), test_crlf_and_lf_bodies_hash_identically(), test_lote_languages_keep_stored_order() (+5 more)

### Community 87 - "Community 87"
Cohesion: 0.12
Nodes (18): Lexical file is a derived artifact, one per collection, bound by identity and chunk digest, Source documents are truth; chunks, embeddings, sparse entries, Qdrant points and preview indexes are derived artifacts, Backend stack, FastAPI, httpx, jsonschema, Multiple vector databases (avoided), Pandas (+10 more)

### Community 88 - "Community 88"
Cohesion: 0.11
Nodes (16): Components / boundaries, R10 — `eval-compare` identity rules (`compare.py`), R12 — Docker test, R4 — `make index-lexical` (`lexical/cli.py`), R4/R5 — Lexical store (`lexical/store.py`, `lexical/build.py`), R6 — `BM25Retriever` (`retrieval/bm25.py`), R8 — Strategy and config (`retrieval/strategy.py`, `config/retrieval.yaml`), R9 — Result format 2.1 (+8 more)

### Community 89 - "Community 89"
Cohesion: 0.12
Nodes (16): allowed_scopes, current_release, default_role, implemented_roles, allowed_scopes, allowed_scopes, roles, admin (+8 more)

### Community 90 - "Community 90"
Cohesion: 0.17
Nodes (6): load_schemas(), test_existing_schema_is_referenced_not_copied(), test_missing_schema_is_configuration_error(), test_per_type_required_field_enforced(), test_schema_files_are_valid_draft_2020_12(), test_valid_rows_pass()

### Community 91 - "Community 91"
Cohesion: 0.18
Nodes (6): AccessScope, ApprovalStatus, LanguageScope, LifecycleStatus, SourceAuthority, test_guest_policy_agrees_with_access_policy_config()

### Community 92 - "Community 92"
Cohesion: 0.12
Nodes (17): --allow-fake (plumbing only, never a recorded baseline), make retrieval-baseline (legacy, frozen Spec 005 producer), BASELINE_ARGS (--embedder, --allow-fake, --top-k, --suite, --release, --output, --config), Baseline metrics HitRate@5, random expectation min(1,5/N), Recall@5, MRR, p50/p95 latency, experiments/results/retrieval-baseline-<index_version>-<UTC>.json, never overwritten, D036 binding rules, D053 result 2.1, eval-retrieval exit 0 or 2 (+9 more)

### Community 93 - "Community 93"
Cohesion: 0.13
Nodes (16): Roadmap 2 - Document model + repository, KnowledgeDocument, Manifest/schema validation, S3DocumentRepository and external storage, apps/api, apps/web, CloudWatch, Document manifest (+8 more)

### Community 94 - "Community 94"
Cohesion: 0.22
Nodes (10): declared_release_id(), load_suite(), test_declared_release(), test_filtering_in_temporary_suite(), test_invalid_line_names_file_and_line_only(), test_path_escaping_repo_root_refused(), test_real_suite_loads_every_golden_case_and_leaves_evaluation_unchanged(), test_release_id_mismatch_refused() (+2 more)

### Community 95 - "Community 95"
Cohesion: 0.28
Nodes (11): load_suite(), live_suite_rows(), copy_suite(), test_access_context_is_loaded_but_ignored(), test_dataset_types_loaded_by_type(), test_escaping_path_refused(), test_extra_fields_tolerated(), test_malformed_line_names_file_and_line_only() (+3 more)

### Community 96 - "Community 96"
Cohesion: 0.12
Nodes (16): Authorization model (guest/public), Small documents and chunking strategy, Citation strategy (backend-owned validation), FAQ-aware retrieval experiment, Graceful degradation, Hybrid retrieval (dense + BM25 + RRF), Production knowledge corpus, Poisoned public document fixture (+8 more)

### Community 97 - "Community 97"
Cohesion: 0.17
Nodes (16): Admin content management, Agent capabilities only where they solve a real product problem, Audit trail, Basic analytics, Candidate evaluation, Change impact analysis, Content hashing, Evaluation Governance (keep/modify/deprecate/replace) (+8 more)

### Community 98 - "Community 98"
Cohesion: 0.17
Nodes (3): _differences(), LexicalIndexBindingError, _read_only_connection()

### Community 99 - "Community 99"
Cohesion: 0.13
Nodes (14): interval, retries, start_period, test, timeout, container_name, healthcheck, image (+6 more)

### Community 101 - "Community 101"
Cohesion: 0.19
Nodes (15): make index-lexical, lexical package: lexical-v1 tokenizer, FTS5 store, builder, standalone bm25 without Qdrant or extra (IndexIdentity, freshness), Known issue: verify_fresh asyncio.run in event loop, Known issue: BM25 statistics corpus-wide per file; needs per-scope files for roles, Known issue: freshness check rereads every document, Malayalam BM25 limit: exact tokens only, no stemming, D010 Qdrant primary, SQLite FTS5 fallback (+7 more)

### Community 102 - "Community 102"
Cohesion: 0.16
Nodes (15): RRF, Local multilingual BGE reranker, BM25 via FTS5 bm25(), Derived local lexical file per collection, Fusion, Lexical store, lexical-v1 tokens (D051), make index-lexical (+7 more)

### Community 103 - "Community 103"
Cohesion: 0.25
Nodes (6): DatasetType, LoadedSuite, golden_count(), suite_with_statuses(), test_exclusions_counted_by_status(), test_suggested_never_returned()

### Community 104 - "Community 104"
Cohesion: 0.14
Nodes (12): graphify skill pointer, spec/NNN branch and Spec-Task trailers, spec-implementer skill (one task per run), spec-orchestrator skill, spec-planner skill, spec-reviewer retrospective skill, Task-gated agent workflow loop, task-reviewer skill (read-only) (+4 more)

### Community 105 - "Community 105"
Cohesion: 0.15
Nodes (14): results.py, compare.py (reads 1.0, 2.0, 2.1; quality gate; identity refusals), D061 fallback marking, eval-compare exit 0 pass, 1 gate failure, 2 refusal, WARNING flipped hit->miss / miss->hit lines (<case_id> v<case_version>), Gate: fail if more than 1 fewer hit cases or MRR drop above 1/n, Fallback path latency marked 'includes failed dense attempt' (informational), Not-comparable refusals (suite, case sets, top_k, fake, collection, index_version, embedder, lexical index, mixed served strategies), BASE and CANDIDATE variables (+6 more)

### Community 106 - "Community 106"
Cohesion: 0.14
Nodes (13): Authorization metadata (access_scope, owner_user_id, tenant_id), Engineering Conventions, IDs and versions conventions, Knowledge files with provenance, Language metadata (content_language, lote_languages), Logging and tracing hygiene, Domain naming terms, Prompts as versioned assets (+5 more)

### Community 107 - "Community 107"
Cohesion: 0.31
Nodes (9): discover_skills(), expected_tree(), find_problems(), inject_frontmatter(), main(), managed_skills(), read_tree(), remove() (+1 more)

### Community 108 - "Community 108"
Cohesion: 0.15
Nodes (13): schemas.py, validate.py (referencing registry, validate-evaluation checks), Error format ERROR <ClassName>: <message>; eval-compare refusals start with 'not comparable:', EVAL_ARGS, python -m way2australia_rag.evaluation.cli {validate,retrieval,security,compare}, make eval-generation does not exist yet, Retrieval evaluation supports Recall@5, MRR, HitRate@5 and language/category/source-authority slices, Evaluation commands (single module evaluation.cli), Suite status draft, active, deprecated, replaced (+5 more)

### Community 109 - "Community 109"
Cohesion: 0.18
Nodes (13): Full agent orchestration (avoided), Intentionally avoided choices, Bedrock Agents / AgentCore for Phase 1 (avoided), Containers, Docker, Docker Compose, ECR, Fine-tuning (avoided) (+5 more)

### Community 110 - "Community 110"
Cohesion: 0.22
Nodes (7): Review, _check_standalone_open(), _retrievers(), SecurityIndex, test_a_fallback_path_that_does_not_fall_back_is_a_harness_error(), test_every_path_is_gated_for_every_query(), counting()

### Community 111 - "Community 111"
Cohesion: 0.15
Nodes (12): Approved packages, pricing and validity, Six approved packages and prices, 60-day package validity, 24-hour cancellation notice, Personal coaching package, 60-minute coaching session on Google Meet, Individual coaching and live appointments, Mock assessments, scoring, feedback and review windows (+4 more)

### Community 112 - "Community 112"
Cohesion: 0.22
Nodes (5): block_model_stack(), fake_lexical(), Raises, test_open_retrieval_bm25_builds_no_embedder_and_no_client(), test_retrieve_cli_bm25_needs_neither_qdrant_nor_the_model()

### Community 113 - "Community 113"
Cohesion: 0.18
Nodes (12): AGENTS.md Project Rules, DocumentRepository Abstraction, Evaluation Governance Rules, Language Separation Rules, Phase 1 Scope, Task-gated Spec Loop, CLAUDE.md Project Instructions, graphify Knowledge Graph Rules (+4 more)

### Community 114 - "Community 114"
Cohesion: 0.17
Nodes (12): AccessContext(role, tenant_id) with blank tenant refused, Future agent folders intentionally not created, apps/api (FastAPI application layer), apps/web (Next.js/TypeScript frontend: recruiter assistant, RAG Lab, engineering views), core/access.py (Role, frozen AccessContext), guest_access, Knowledge model metadata (document_id, document_version, tenant_id, access_scope, lote_languages, content_language, source_authority...), No language filter, score threshold or reranking yet (+4 more)

### Community 115 - "Community 115"
Cohesion: 0.17
Nodes (12): BM25, Deterministic regression gates, Versioned Evaluation Suite, Golden, refusal and security cases, HitRate@5, Roadmap 5 - Evaluation framework, Roadmap 6 - Hybrid retrieval, Roadmap 15 - CI/CD + regression gates (+4 more)

### Community 116 - "Community 116"
Cohesion: 0.20
Nodes (12): English, Malayalam and mixed queries, FAQ-aware retrieval/indexing, Roadmap 7 - Chunking experiments, Roadmap 8 - Multilingual retrieval, Language applicability handling, Parent-heading context and order-independent section_ids, Recursive chunking baseline, Optional semantic chunking (+4 more)

### Community 117 - "Community 117"
Cohesion: 0.21
Nodes (12): Branching and commits (spec/NNN, Spec-Task trailer), Development Workflow, Multi-agent handoff, Implementation rule: BLOCKED spec issue, Phase discipline, Protected source-of-truth data, Required spec-reviewer retrospective, Agent skills (orchestrator, planner, implementer, task-reviewer, spec-reviewer) (+4 more)

### Community 119 - "Community 119"
Cohesion: 0.21
Nodes (5): _DenseLike, leg_order(), make_world(), test_hybrid_leg_ranks_beyond_top_k_are_real_document_ranks(), test_runner_requires_fusion_for_hybrid()

### Community 120 - "Community 120"
Cohesion: 0.18
Nodes (10): content-hash-v1 (sole change-detection signal), LocalDocumentRepository, Document manifest and JSON Schema validation, make validate-knowledge, persona_scope spec defect (F2), BgeM3Embedder (optional extra, pinned revision), Embedder Protocol and FakeEmbedder, HeadingChunker and slugify rule (+2 more)

### Community 121 - "Community 121"
Cohesion: 0.20
Nodes (8): Adding a New Language Guide, language_registry.json, Public Assistant Content Boundaries, access_scope, content_language, Knowledge Schema and Metadata, language_scope, lote_languages

### Community 122 - "Community 122"
Cohesion: 0.18
Nodes (10): 007 — Hybrid Retrieval Tasks, Out of this spec, T1 — Evaluation Suite `public-eval-v2`, T7 — `eval-compare` identity rules, T8 — Security gate for BM25 and hybrid, Docker isolation test, T9 — Strategy comparison and default-strategy decision (user-owned gate), Verification, Verification (+2 more)

### Community 123 - "Community 123"
Cohesion: 0.36
Nodes (7): _keyword_indexed(), live_client(), store(), test_collection_has_keyword_indexes_and_cosine_dense_vector(), test_empty_without_settings_recreates_dropped_indexes(), test_repeated_create_payload_index_is_harmless(), test_settings_storage_and_refusal()

### Community 124 - "Community 124"
Cohesion: 0.22
Nodes (10): Local Qdrant Docker Compose service, Make command surface (setup, lint, typecheck, test, verify), Python monorepo foundation (FastAPI, uv, Makefile), Typed runtime Settings (Pydantic Settings), Spec 001 Project Foundation (implemented), IndexSettings and mismatch refusal, UUIDv5 point identity (INGESTION_NAMESPACE), QdrantIndexStore (+2 more)

### Community 125 - "Community 125"
Cohesion: 0.22
Nodes (8): Baseline runner and result JSON, build_access_filter (single filter builder), check_hit (fail-closed re-check), DenseRetriever, Read-only golden loader (stand-in for Spec 006), Document-level metrics (HitRate, Recall, MRR, random k/N), safe_text output sanitizer, Real BGE-M3 baseline (user-owned, pending)

### Community 126 - "Community 126"
Cohesion: 0.24
Nodes (8): Legacy goldens.py Compatibility Wrapper, Legacy Baseline Snapshot Test, Governed Suite Loader, 006 Task Reviews, 006 Evaluation Framework Tasks, T1 Snapshot, Models, Loader, T8a Deferred Fixes, T8b Docs and Handoff

### Community 127 - "Community 127"
Cohesion: 0.29
Nodes (10): NAATI CCL booking, fees, cancellation, results and credential validity, One week advance booking, 75% refund for cancellation one hour before, CCL test fee A$814, Credential validity five years from 9 August 2022, myNAATI, Expired credential not extended, Rescheduling up to eight days before test (+2 more)

### Community 128 - "Community 128"
Cohesion: 0.25
Nodes (7): RetrievalAuthorizationError.document_id, eval-security, Forbidden Point Variants, Authorization Hard Gate, Throwaway Security Index (w2a-sectest-*), T5 Security Gate, Authorization Rules

### Community 129 - "Community 129"
Cohesion: 0.22
Nodes (8): last_reviewed_at, precedence, business_information, language_specific_exam_policy, migration_points_and_visa_rules, official_exam_rules, rules, schema_version

### Community 130 - "Community 130"
Cohesion: 0.22
Nodes (9): D060 Standalone lexical freshness, Standalone freshness proves lexical file matches repository, not live Qdrant (D060), lexical/cli.py (make index-lexical writes only git-ignored file), freshness.py (verify_fresh, chunk digest recomputed from repository), lexical/ package (Spec 007), store.py (SQLite FTS5: chunks table, chunk_terms FTS5 table, settings row; LexicalIndex.open, bind_to, search), tokenizer.py (lexical-v1), make index-lexical (+1 more)

### Community 131 - "Community 131"
Cohesion: 0.33
Nodes (9): NAATI CCL candidate rules and test-day setup, Direct first-person speech requirement, Report technical incidents within 24 hours, NAATI, Online proctoring with separate phone or tablet, Prohibited materials and tools, Recording under 20 minutes, One repeated segment per dialogue without penalty (+1 more)

### Community 133 - "Community 133"
Cohesion: 0.29
Nodes (7): EligibilityPolicy / GUEST_PUBLIC_POLICY, Security fixtures (valid but ineligible), config/ingestion.yaml and RuntimeSettings, Ingestion pipeline (target vs current state diff), AccessContext and Role (core), resolve_access / ResolvedAccess, W2A_TENANT_ID server tenant setting

### Community 134 - "Community 134"
Cohesion: 0.25
Nodes (8): Phase 2 basic analytics, Assistant behavior rules, Product Context, English and Malayalam language scope, Future personas, Phase 1 guest-only scope, Way2Australia AI product, Source-of-truth priorities

### Community 135 - "Community 135"
Cohesion: 0.36
Nodes (8): Custom retrieval metrics (plain Python), DeepEval (not yet a dependency), Evaluation tooling, Generation/e2e metrics (correctness, faithfulness, citations, refusal), GitHub Actions, LLM-as-judge not sole source of truth, Primary retrieval metrics (Recall@5, MRR, HitRate@5), pytest

### Community 136 - "Community 136"
Cohesion: 0.25
Nodes (7): 007 — Hybrid Retrieval Design, Alternatives / deferred decisions, Data flow, Design summary, Interfaces / models, Observability, Testing / evaluation strategy

### Community 137 - "Community 137"
Cohesion: 0.29
Nodes (6): Implementation, Review, T9 — round 1, User decision, git_state(), _is_untracked_result()

### Community 138 - "Community 138"
Cohesion: 0.39
Nodes (8): NAATI CCL test format, scoring and results, NAATI CCL test, Deduction-based assessment, Begin interpreting within five seconds of chime, NAATI, CCL is not professional interpreter certification, Pass requirement 63/90 overall and 29/45 per dialogue, Results within 4-6 weeks

### Community 139 - "Community 139"
Cohesion: 0.29
Nodes (3): build_security_repository(), _fixture_files(), security_repository()

### Community 141 - "Community 141"
Cohesion: 0.38
Nodes (6): Evaluation Candidates File, Evaluation Package (evaluation/), Evaluation Suite and Case-type Schemas, validate-evaluation, T2 Schemas and validate-evaluation, T7 Candidates

### Community 142 - "Community 142"
Cohesion: 0.29
Nodes (7): eval-retrieval, Retrieval Result Document 2.0, Section-level Metrics, Slices and small_sample, Unanswerable Reporting, T3 Retrieval Runner, T4 Unanswerable Reporting

### Community 143 - "Community 143"
Cohesion: 0.29
Nodes (7): D049 Suite public-eval-v2 and the closed v1 reference (Spec 007), suite public-eval-v2, Acceptance criteria, R13 strategy comparison and default-strategy rule, R1 Evaluation Suite public-eval-v2 (91 cases), R2 — v2 dense baseline (user-owned gate), T9 strategy comparison and default-strategy decision

### Community 144 - "Community 144"
Cohesion: 0.29
Nodes (7): AGENTS.md, Claude adapter, Initial specs, Phase 0 - Project bootstrap, Project context files, SDD workflow (Spec 003 task-gated agent workflow), Stable command interface

### Community 145 - "Community 145"
Cohesion: 0.29
Nodes (6): Vocabulary, flashcards and free access, Spaced-repetition flashcards, Free access allowance, 12 subject domains plus General vocabulary, Approved public learning samples, Sample neighbour-greeting dialogue

### Community 146 - "Community 146"
Cohesion: 0.33
Nodes (6): DocumentRepository Protocol (async), KnowledgeDocument model, Spec 002 retrospective round 1, Spec 002 task review log (T3-T9), Spec 002 Document model and repository (verified), Acceptance dry run on Spec 002 T3

### Community 147 - "Community 147"
Cohesion: 0.33
Nodes (6): 006 Evaluation Framework Design, Decision Brief Q1-Q10, 006 Evaluation Framework Requirements, Evaluation Framework Goal, 006 Spec Retrospective Review, Retrospective Round 1 PASS

### Community 148 - "Community 148"
Cohesion: 0.33
Nodes (5): Evaluation case_id and case_version, Versioning and Releases, document_id and document_version, Phase 2 Knowledge Release Candidates, Release seed-v1

### Community 149 - "Community 149"
Cohesion: 0.33
Nodes (6): Acceptance criteria, R12 — Real runs (user-owned gate), Spec 007 BM25 and hybrid reference results, T7 real runs: fallback-only and Qdrant-up results, T7 — Real runs (user-owned gate), Verification

### Community 150 - "Community 150"
Cohesion: 0.47
Nodes (4): canonical_json(), _canonical_value(), _canonical_value_mapping(), test_canonical_json_is_sorted_compact_and_keeps_unicode()

### Community 151 - "Community 151"
Cohesion: 0.40
Nodes (5): Spec 004 retrospective round 1 (PASS), Spec 004 Ingestion baseline (verified), retrieval package (dense baseline), Spec 005 retrospective round 1 (PASS), Spec 005 Dense retrieval baseline (verified)

### Community 152 - "Community 152"
Cohesion: 0.40
Nodes (4): eval-compare, Quality Gate (1 case, MRR 1/n), Release Candidates Need Compare-shared-cases, T6 eval-compare

### Community 153 - "Community 153"
Cohesion: 0.40
Nodes (4): Public contact channels, Payments, account access and support boundaries, Payments non-refundable, One active login session

### Community 154 - "Community 154"
Cohesion: 0.70
Nodes (5): Home Affairs credentialled community language points, 5 points for credentialled community language, Australian Department of Home Affairs, Refer to Home Affairs or migration adviser, No automatic visa eligibility from passing CCL

### Community 157 - "Community 157"
Cohesion: 0.50
Nodes (4): Baseline runner (refuses fake index without --allow-fake; HitRate@k, Recall@k, MRR, p50/p95, min(1,k/N) random expectation), D037 Baseline runner decisions, make retrieval-baseline (legacy dense-only), metrics.py, goldens.py, baseline.py, baseline_cli.py

### Community 158 - "Community 158"
Cohesion: 0.50
Nodes (4): Mission, Phase 1 public/guest vs Phase 2 Knowledge Operations, Mission purpose: grounded multilingual RAG assistant, Useful product, engineering learning, portfolio evidence

### Community 159 - "Community 159"
Cohesion: 0.50
Nodes (3): Coaching is optional, Way2Australia public offering and assistant scope, English-Malayalam CCL preparation offering

### Community 160 - "Community 160"
Cohesion: 0.50
Nodes (4): 120+ practice dialogues, Materials and dialogue practice, Recordings stay in browser, No automatic score in ordinary practice

### Community 167 - "Community 167"
Cohesion: 0.67
Nodes (3): Frontend stack, Next.js, TypeScript

### Community 168 - "Community 168"
Cohesion: 0.67
Nodes (3): Implementation, T1 — round 1, User decision

### Community 170 - "Community 170"
Cohesion: 0.67
Nodes (3): Canonical document metadata, Chunk metadata, Source authority precedence

## Ambiguous Edges - Review These
- `Task-gated agent workflow loop` → `graphify skill pointer`  [AMBIGUOUS]
  .claude/CLAUDE.md · relation: conceptually_related_to

## Knowledge Gaps
- **380 isolated node(s):** `way2australia-core`, `way2australia-rag`, `way2australia`, `way2australia-api`, `way2australia-observability` (+375 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1245 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Change log` connect `Community 28` to `Community 0`, `Community 67`, `Community 36`, `Health Endpoint`, `Community 6`, `Community 137`, `Community 11`, `Community 13`, `Document Model Tests`, `Retrieval Eval Tests`, `Community 54`, `Community 30`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Are the 71 inferred relationships involving `DenseIndex` (e.g. with `Design summary` and `Decisions resolved before drafting`) actually correct?**
  _`DenseIndex` has 71 INFERRED edges - model-reasoned connections that need verification._
- **What connects `way2australia-core`, `way2australia-rag`, `way2australia` to the rest of the system?**
  _380 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.05995415270675366 - nodes in this community are weakly interconnected._
- **Why does `D055 Default strategy is hybrid (Spec 007)` connect `Community 67` to `Community 34`, `Community 41`, `Strategy Eval Tests`, `Community 82`, `Community 56`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Should `Task Review Log (T7)` be split into smaller, more focused modules?**
  _Cohesion score 0.05515151515151515 - nodes in this community are weakly interconnected._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Task-gated agent workflow loop` and `graphify skill pointer`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._