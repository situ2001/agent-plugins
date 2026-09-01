# agent-plugins

Personal Claude Code and Codex plugin — shell safety hooks created by situ2001.

## Layout

```
agent-plugins/
├── .claude-plugin/
│   └── plugin.json          # plugin manifest
├── .codex-plugin/
│   └── plugin.json          # Codex plugin manifest
├── hooks/
│   └── hooks.json           # PreToolUse hook registration for Claude Code and Codex
└── scripts/
    ├── check-rg-footgun.py  # blocks rg -r footgun
    └── check-rm-scope.py    # blocks unsafe rm -rf
```

## Claude Code

```bash
claude --plugin-dir .
```

Or inside a session: `/plugin` → install from folder.

## Codex

Codex discovers `.codex-plugin/plugin.json` and the default `hooks/hooks.json` when this folder is installed as a local plugin. Review and trust the hooks with `/hooks` after installation.

Validate the plugin from this repository:

```bash
python3 ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

## Test

```bash
rg -rn "foo"           # blocked -> use rg -n / grep -rn
rg -r n "foo"          # blocked
rm -rf .git            # blocked (touches .git)
rm -rf ../             # blocked (outside cwd)
rm -rf ./src           # allowed (safe)
```
