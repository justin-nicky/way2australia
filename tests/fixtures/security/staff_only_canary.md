---
schema_version: "1.0"
document_id: "fixture_staff_canary"
document_version: 1
tenant_id: "way2australia"
title: "Synthetic staff-only authorization canary"
knowledge_domain: "security_fixture"
access_scope: "staff"
persona_scope: ["staff"]
owner_user_id: null
language_scope: "global"
lote_languages: ["*"]
content_language: "en"
source_authority: "synthetic"
source_type: "security_fixture"
source_url: "fixture://staff-canary"
approval_status: "test_only"
last_reviewed_at: "2026-10-09"
lifecycle_status: "active"
introduced_in_release: "security-fixtures"
retrieval_enabled: true
synthetic: true
---

SECURITY_CANARY_9F72

This is a synthetic staff-only document used only to prove that guest/public retrieval cannot fetch staff-scoped content.

It must never enter a guest user's context, including when Qdrant fails and the application uses a fallback retriever.
