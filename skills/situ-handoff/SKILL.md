---
name: situ-handoff
description: Save a concise conversation handoff for another agent or session to continue the work. Use when the user asks to hand off the current context or prepare a continuation document.
---

# Situ Handoff

Write a Markdown document that gives a fresh agent enough context to continue the current work. If the user supplies a focus for the next session, tailor the handoff to it.

Capture the objective, relevant decisions and constraints, current progress, unresolved questions or blockers, and concrete next steps. Include workspace and branch details when needed to resume. Distinguish completed work from proposals and unverified assumptions.

Reference existing specs, plans, ADRs, issues, commits, and diffs by absolute path or URL instead of duplicating their contents. Preserve context and reasoning that exist only in the conversation.

Include a **Suggested skills** section naming relevant available skills, their paths when known, and why the next agent should invoke them. If none apply, say so briefly.

Redact sensitive information, including API keys, passwords, and personally identifiable information. Keep the operational paths needed to locate the work.

## Save the handoff

Unless the user specifies another destination, prefer this directory:

```text
/Users/situ/Library/Mobile Documents/iCloud~md~obsidian/Documents/situ-vault/002 Handoff
```

Use the literal path above; quote it when used in shell commands. Use this directory only if it exists and is readable and writable. If it is missing, inaccessible, or the write fails, save directly in the current working directory (`pwd`) instead. Do not create the preferred directory when it is missing. A user-specified destination takes precedence over this default and fallback.

Choose a descriptive, unique Markdown filename such as `YYYY-MM-DD-HHmmss-topic.md` and preserve existing handoffs.

Verify that the document was saved, then return a clickable link to its absolute path with a brief description of its focus. Mention when the current working directory was used as the fallback. If the fallback or a user-specified destination cannot be written, report the blocker.
