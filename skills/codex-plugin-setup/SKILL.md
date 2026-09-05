---
name: codex-plugin-setup
description: Register an existing local directory as a discoverable Codex plugin, or refresh its installed version after local changes.
---

# Codex Plugin Setup

Use this skill when a user wants the current directory (or another existing directory) to be installed as a local Codex plugin.

## Initial setup

1. Confirm the plugin root contains `.codex-plugin/plugin.json`, then validate it:

   ```bash
   python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py <plugin-root>
   ```

2. For a directory outside `~/plugins`, expose it at the conventional source location. A symlink keeps the marketplace source live during development:

   ```bash
   mkdir -p ~/plugins
   ln -s <absolute-plugin-root> ~/plugins/<plugin-name>
   ```

   Check an existing path before replacing it.

3. Create or update the default personal marketplace through the scaffold helper, not by hand-editing JSON:

   ```bash
   python3 ~/.codex/skills/.system/plugin-creator/scripts/create_basic_plugin.py \
     <plugin-name> --path ~/plugins --with-marketplace
   ```

   Preserve existing plugin files; ensure the entry points to `./plugins/<plugin-name>` and includes installation policy, authentication policy, and category.

4. Install it from the implicit personal marketplace:

   ```bash
   codex plugin add <plugin-name>@personal
   codex plugin list
   ```

   Do not run `codex plugin marketplace add` for the default `~/.agents/plugins/marketplace.json` marketplace.

## Refresh after edits

For a plugin already listed in a local marketplace, read its marketplace name, rotate the cachebuster, and reinstall:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py
python3 ~/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py <plugin-root>
codex plugin add <plugin-name>@<marketplace-name>
```

Start a new Codex thread after reinstalling so updated skills, hooks, or tools are loaded. Validate again if manifest or layout files changed.

## Boundaries

- Keep `skills/`, `hooks/`, scripts, MCP, and app declarations consistent with files that actually exist.
- Never add secrets or production data to the plugin.
- For a non-default marketplace path, install it first with `codex plugin marketplace add <marketplace-root>` and verify it with `codex plugin marketplace list`.
