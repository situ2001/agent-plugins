# Herdr runtime

When the [delivery workflow](../SKILL.md) selects Herdr, read and follow the official `herdr` skill from the skill catalog or `~/.agents/skills/herdr/SKILL.md`. If it is not installed, use `herdr --skill` for the bundled instructions; [setup-my-skills](../../setup-my-skills/SKILL.md) installs or refreshes the official skill when requested.

The official skill owns CLI discovery, caller context, pane layout, agent lifecycle, messaging, waits, output retrieval, and cleanup. This reference adds only delivery-specific settings.

## Launch settings

Use the official skill to create a shell pane, then launch the requested CLI with automatic approval review:

```bash
herdr agent start <unique-name> --kind codex --pane <new-pane-id> -- --no-daemon --approve-for-me -m gpt-6.1-sol -c 'model_reasoning_effort="high"'
herdr agent start <unique-name> --kind claude --pane <new-pane-id> -- --permission-mode auto
```

Honor explicit model and effort choices. Codex's `--no-daemon` keeps tool commands in the new pane's environment; `--approve-for-me` uses automatic approval review with the workspace-write sandbox. Claude Code uses its configured model unless the user specifies one. Report the actual model used and any launch failure. Automatic review can still block actions; handle those decisions through the authorized approval route.

## Shared Codex daemon context

Routine Herdr detection only needs `HERDR_ENV=1` and the CLI. If `pane_not_found` occurs, compare the current TUI's `HERDR_*` environment with the tool process's: a shared daemon can retain an old pane ID. Match the TUI PID to `herdr pane process-info`, then explicitly target that live pane. If the current TUI cannot be identified, report the missing context.

## Delivery coordination

Give each executor the shared workflow's self-contained brief and its peers' live Herdr addresses. The director collects results explicitly using the official skill's output-retrieval procedure; Herdr does not deliver a built-in parent mailbox. Accept only after reading the deliverable and its validation evidence.
