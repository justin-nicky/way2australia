# Knowledge schema and metadata

The two dimensions below are intentionally independent:

## Authorization/persona
`access_scope` controls **who may retrieve a document**.

Planned scopes:
- `public`
- `staff`
- `subscriber`
- `user_private`
- `admin`

The current release retrieves only `public`.

## Language
Language fields control **which language/topic the content applies to**, not who can access it.

Fields:
- `content_language`: language in which the document text is written.
- `language_scope`: `global` or `language_specific`.
- `lote_languages`: list of CCL languages to which the knowledge applies; `["*"]` means shared/global.

Examples:
- CCL scoring rules: `access_scope=public`, `language_scope=global`, `lote_languages=["*"]`.
- Malayalam language policy: `access_scope=public`, `language_scope=language_specific`, `lote_languages=["ml"]`.
- Future Tamil policy: same access scope, but `lote_languages=["ta"]`.
- Future private student feedback: `access_scope=user_private` plus `owner_user_id`.

Never encode authorization as a language filter.
