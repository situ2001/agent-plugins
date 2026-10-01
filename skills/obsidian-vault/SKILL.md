---
name: obsidian-vault
description: Search, cite, organize, create, or edit notes in the user's Obsidian vault. Use when the user requests vault work or a task depends on their notes, preferences, project context, or past decisions, even if Obsidian is not explicitly mentioned.
---

# Obsidian Vault

Use the user's Obsidian vault as a knowledge base or carry out the requested note operations.

Before searching, reading, or writing notes, read the vault's root `AGENTS.md` in full. Follow its instructions for CLI usage, basic Obsidian syntax, and vault conventions:

```bash
vault="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/situ-vault"
cat "$vault/AGENTS.md"
```

Use the documented workflow to retrieve relevant notes and linked context. Cite the supporting note paths in your answer.

When the user asks to save a new AI-authored document without specifying a destination, default to `002 AI Workspace/`. Updates to existing notes and documents with clear project or topic locations belong in their corresponding locations. Follow `AGENTS.md` for topic or task subfolders and the writing workflow.
