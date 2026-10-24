# Frozen legacy baseline fixture (Spec 006 T1, R12)

A miniature repository root used only by `../../test_legacy_baseline_snapshot.py`
to pin the output of legacy `make retrieval-baseline` byte-for-byte.

- Source commit of every verbatim copy: `0907676ae974f432b9767736c76c23180dd9aa13` (branch `spec/006`, 2026-10-23).
- **Frozen.** Copied once. Never refresh it to follow approved knowledge or
  evaluation changes, Phase 2 releases or config changes: it exists so those
  changes cannot break the legacy snapshot. The snapshot test fails only when
  legacy code behavior changes. If it fails, fix the code, not the fixture.
- Companion snapshots (generated from the unmodified Spec 005 code with the fake embedder,
  fixed clock, patched git state and deterministic timers):
  `../legacy_baseline_snapshot.json`, `../legacy_baseline_summary.txt`.

## Golden rows

`evaluation/datasets/golden_fixture.jsonl` has 9 rows.

- Copied verbatim from `evaluation/datasets/golden_public.jsonl`: `g001`, `g003`, `g005`, `g010`, `g032`, `g037`, `g055`, `g062`
  (`g003` and `g062` are two-document cases; `g055` and `g062` are `mixed`, the rest `en`).
- **Derived (not a copy):** `g001-derived-deprecated`, a copy of `g001` with a new
  `case_id` and `status: deprecated`, so the legacy selector's exclusion is exercised.

`evaluation/suites/legacy-fixture-suite.json` is new (written for this fixture, not a copy): one `golden_answerable` dataset, `case_count` 9.

## sha256 of every file

Verbatim copies (equal to the source commit's file), except `evaluation/datasets/golden_fixture.jsonl` (eight copied rows plus the derived row) and `evaluation/suites/legacy-fixture-suite.json` (new).

```
e454c7080219eee44b625bed8c58b8de9b98ae3cc613b835054e91bd8dc808c1  config/ingestion.yaml
4b32001489e23441cdb6c9a78c975f46b131662e1d21c22fb9992a7fe190ca66  evaluation/datasets/golden_fixture.jsonl
5d0459ebbccf2220b3aaa1aaa71ac76a6b24590bc23b73ccc237ab4baa56af60  evaluation/suites/legacy-fixture-suite.json
d45490973303f665bc4fe33fc4fd682f1fd7349a908de571f111ab816c64e3d4  knowledge/manifest/document_manifest.jsonl
909a118a85efdd8dcf9df2aa9a26ea383ac70551e788c880db8abaae3a65496e  knowledge/public/business/business_001_overview_scope.md
69f7d91320f58c6e2a9ea96ca609a7c0b85336e3b4a940aaa6e726d5472fe395  knowledge/public/business/business_002_packages_pricing_validity.md
7add5fffc91e4cc3b1d38335ffffb67fe814b781937ded4fb5dcfc3b2f192de9  knowledge/public/business/business_003_materials_and_dialogue_practice.md
e456facdc4bffc8b1a4ded580cec087cb6c83366c633cc24a1698371e69d396c  knowledge/public/business/business_004_vocabulary_and_free_access.md
96a659a26fc62fcd7257dc6c4155720fee4e35659e44d58ccc616a1674ddf5e3  knowledge/public/business/business_005_coaching.md
76fb311fedc00586df63b6946075d72111a98647199828260de21b75ffd4322e  knowledge/public/business/business_006_mock_assessments.md
ead219335d51fab4dcfb772d954d5830e03d513934bf74cccbec8c3a827f6f68  knowledge/public/business/business_007_payments_account_support.md
ebb369e72f791150bac797e7246342a29b9ab3ccaf5b62226763983455afbcd8  knowledge/public/business/business_008_public_samples.md
620cdb8563dbadb1694540b5ecd44fd3da0c495777508ecdc007d70ac4a2f184  knowledge/public/languages/ml/language_ml_001_naati_policy.md
6fb988c5d2582718512dbef4a38dc589db55ab01c5417887487eb3fa421b1f94  knowledge/public/official/official_001_ccl_format_scoring_results.md
ec63a7f6c6eddb91e94c9819457c250e90f16b02008c63b4af736681a8c06c84  knowledge/public/official/official_002_candidate_rules_setup.md
9b0a92f1295a4740cb139c40e160ea1ad8a6a25dc5808255c9085c94a17480e3  knowledge/public/official/official_003_booking_fees_validity.md
cc67da1291ffb45fd23366b64ca9a1313012735b9fba0d0d03ff4757e3dd718d  knowledge/public/official/official_004_migration_points.md
98692c1984ceaedb717ed9558f926c4d0b4bcf91a2918c83cb3c49e83ac74a2a  knowledge/releases/seed-v1.json
9eaf6e5e29b85610906a76e4fb48da607274e9a423043a762ba1dfc52d409417  knowledge/schemas/document_metadata.schema.json
```
