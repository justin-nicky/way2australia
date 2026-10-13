# Model Preferences

Model tiers are **advisory**. No supported host lets a skill pin a model across a multi-turn workflow:
- Claude Code's per-skill `model:` lasts for one turn only, except inside a forked subagent.
- Codex skill metadata has no model field.

Choose the model before invoking a skill, and record the model actually used in the implementer handoff and in `review.md`.

## Capability policy

- `spec-planner` → **BEST**
- `spec-implementer` → **BEST_MINUS_ONE**
- `spec-reviewer` → **BEST** (ideally a different session, and optionally a different model, from the implementer)

## Preferred models

Fill these in with exact model IDs. Leave a placeholder unset if you have no preference.

| Tool | BEST | BEST_MINUS_ONE |
|---|---|---|
| Codex | `<CODEX_BEST_MODEL>` | `<CODEX_BEST_MINUS_ONE_MODEL>` |
| Claude Code | `Opus` | `Sonnet` |
| Kiro | `<KIRO_BEST_MODEL>` | `<KIRO_BEST_MINUS_ONE_MODEL>` |

## Runtime rule

1. Read the tier for the active skill.
2. If an exact model is configured and the host can switch, use it.
3. If the host cannot switch, tell the user which configured model is intended.
4. If the placeholder is unset, do not invent a model name and do not block the workflow.
