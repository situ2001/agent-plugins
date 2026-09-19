# Repository guidance

Read [README.md](README.md) for the plugin overview and installation entry points.

## Update and refresh the plugin

After changing plugin skills, hooks, scripts, or metadata:

1. Keep `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` descriptions and release versions consistent where applicable. Keep plugin descriptions at the collection level; skill-specific behavior belongs in its `SKILL.md`.
2. Refresh the Codex manifest version with `python3 scripts/refresh-plugin-version.py`. Use `<version>+<YYMMDDHHmmss>`, with a UTC timestamp, for example `1.1.0+260919053349`. Preserve the release version before `+` and replace the entire old suffix. Do not add `codex.`. The Claude Code manifest keeps the release version without a timestamp; change that version only for an intended release.
3. Validate before committing or reinstalling:

   ```bash
   python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
   python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/<changed-skill>
   git diff --check
   ```

   Run the skill validator for each changed skill. Use a Python environment with PyYAML available. Run relevant checks for executable changes.
4. When committing and pushing is requested, include the updated manifest with the related changes. Integrate remote changes without overwriting others' work.
5. Read the configured personal marketplace name, then reinstall using the returned name:

   ```bash
   python3 ~/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py
   codex plugin add agent-plugins@<marketplace-name>
   ```

   The personal marketplace is discovered implicitly; do not register it again. For another marketplace, follow [codex-plugin-setup](skills/codex-plugin-setup/SKILL.md).
6. Tell the user to start a new Codex task to load the refreshed plugin. Reinstall last: the current task may retain hook paths into the old cache after it is removed.

This repository's timestamp format takes precedence over the bundled plugin-creator helper's `+codex.<timestamp>` convention. Use the repository script above when updating this plugin.
