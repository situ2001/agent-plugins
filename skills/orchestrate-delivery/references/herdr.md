# Herdr runtime

When the [delivery workflow](../SKILL.md) selects Herdr, read and follow the official `herdr` skill from the skill catalog or `~/.agents/skills/herdr/SKILL.md`. If it is not installed, use `herdr --skill` for the bundled instructions; [setup-my-skills](../../setup-my-skills/SKILL.md) installs or refreshes the official skill when requested.

The official skill owns CLI discovery, caller context, pane layout, agent lifecycle, messaging, wait semantics, output retrieval, and cleanup. This reference adds delivery settings and the director's waiting workflow.

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

## Wait for delivery

After launching ready work, use `herdr agent wait <target> --timeout <milliseconds>` when the next decision depends on an executor's result. Choose the wait duration within the calling environment's responsiveness requirements. Independent waits may run concurrently.

Keep two kinds of return distinct:

- **The tool yields a running process or cell handle:** resume that same execution through the tool's continuation API until it returns. The Herdr wait is still active; do not launch a second wait or a sleep-and-read loop for that target.
- **The Herdr wait returns:** on `idle` or `done`, read the delivered response and assess the commitment; on `blocked`, inspect and handle the requested interaction. An ordinary timeout is an opportunity to continue waiting, not evidence of a stalled executor. Resume with another bounded wait unless a concrete failure or unresolved dependency calls for investigation. Handle other errors through the official skill's diagnostic procedure.

Keep required user updates separate from executor inspection. A communication interval alone is not a reason to read terminal output, send another prompt, or summarize unfinished work. Continue waiting until there is a result to assess, a blocker to resolve, or new user direction to apply.
