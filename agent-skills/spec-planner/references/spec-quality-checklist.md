# Spec Quality Checklist

- One coherent major capability.
- Phase boundary and out-of-scope work are explicit.
- Requirements are observable/testable and do not depend on chat history.
- Decision Brief outcomes are captured in the spec files, not only in chat.
- Security/reliability requirements exist where relevant.
- Design maps to approved requirements and respects constitution/architecture.
- Public interfaces, package placement and storage boundaries are explicit.
- Important failure modes are covered.
- Deferred decisions are clearly marked.
- All tasks for the spec are generated together.
- Tasks are dependency ordered, list requirement IDs and have verification.
- Every verification command exists in the `Makefile` or is created by a task.
- Every requirement maps to task(s) in the traceability table; no orphan tasks.
- Each file carries an accurate `Status:` line.
- Another coding agent can implement without the planning conversation.
