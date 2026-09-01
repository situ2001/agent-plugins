# situ-plugins

Personal Claude Code plugins — hooks, skills, agents created by situ2001.

## Layout

```
situ-plugins/
├── .claude-plugin/
│   └── plugin.json          # plugin manifest
├── hooks/
│   └── hooks.json           # PreToolUse hook registration
└── scripts/
    ├── check-rg-footgun.py  # blocks rg -r footgun
    └── check-rm-scope.py    # blocks unsafe rm -rf
```

## Install

```bash
claude --plugin-dir ./situ-plugins
```

Or inside a session: `/plugin` → install from folder.

## Test

```bash
rg -rn "foo"           # blocked -> use rg -n / grep -rn
rg -r n "foo"          # blocked
rm -rf .git            # blocked (touches .git)
rm -rf ../             # blocked (outside cwd)
rm -rf ./src           # allowed (safe)
```
