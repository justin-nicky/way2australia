# Model Preferences

Model tiers are **advisory**. No supported host lets a skill pin a model across a multi-turn workflow:
- Claude Code's per-skill `model:` lasts for one turn only, except inside a forked subagent.
- Codex skill metadata has no model field.

Choose the model when a role's session starts. **No skill switches models inside a running session**: the prompt cache is per model, so a switch re-bills the whole conversation. No skill frontmatter pins a model.

Record the model actually used in every implementer run, every task review and every `review.md` round.

## Capability policy

- `spec-orchestrator` → **BEST_MINUS_ONE**
- `spec-planner` → **BEST**
- `spec-implementer` → **BEST_MINUS_ONE**
- `task-reviewer` → **BEST** (fresh session, ideally a different model from the implementer)
- `spec-reviewer` → **BEST** (optional retrospective, fresh session)

## Preferred models

Fill these in with exact model IDs. Leave a placeholder unset if you have no preference.

| Tool | BEST | BEST_MINUS_ONE |
|---|---|---|
| Codex | `<CODEX_BEST_MODEL>` | `<CODEX_BEST_MINUS_ONE_MODEL>` |
| Claude Code | `Opus` | `Sonnet` |
| Kiro | `<KIRO_BEST_MODEL>` | `<KIRO_BEST_MINUS_ONE_MODEL>` |

## Runtime rule

1. Read the tier for the role being started.
2. If an exact model is configured and the host can start a session with it, start the role's fresh session on that model.
3. Otherwise tell the user which configured model is intended and continue.
4. If the placeholder is unset, do not invent a model name and do not block the workflow.
