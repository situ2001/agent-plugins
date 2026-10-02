# Herdr runtime

When the [delivery workflow](../SKILL.md) selects Herdr, read and follow the official `herdr` skill from the skill catalog or `~/.agents/skills/herdr/SKILL.md`. If it is not installed, use `herdr --skill` for the bundled instructions; [setup-my-skills](../../setup-my-skills/SKILL.md) installs or refreshes the official skill when requested.

The official skill owns CLI discovery and command semantics. This reference keeps the delivery lifecycle's key commands together; use the installed CLI and official skill when syntax or behavior needs clarification. Replace angle-bracket placeholders with observed IDs or task-specific values.

## Create and launch

Inspect the caller's layout, then create a sibling shell pane with the same working directory and keep user focus unchanged:

```bash
herdr pane layout --current
herdr pane split --current --direction <right-or-down> --cwd "$PWD" --no-focus
```

Choose the split direction using the official skill's geometry guidance. Read the new pane ID from `.result.pane.pane_id`, record it as owned by this delivery, then launch the requested CLI with automatic approval review. Choose one launch command:

```bash
herdr agent start <unique-name> --kind codex --pane <new-pane-id> -- --no-daemon --approve-for-me -m gpt-6.1-sol -c 'model_reasoning_effort="high"'
herdr agent start <unique-name> --kind claude --pane <new-pane-id> -- --permission-mode auto
```

Honor explicit model and effort choices. Codex's `--no-daemon` keeps tool commands in the new pane's environment; `--approve-for-me` uses automatic approval review with the workspace-write sandbox. Claude Code uses its configured model unless the user specifies one. Report the actual model used and any launch failure. Automatic review can still block actions; handle those decisions through the authorized approval route.

## Shared Codex daemon context

Routine Herdr detection only needs `HERDR_ENV=1` and the CLI. If `pane_not_found` occurs, compare the current TUI's `HERDR_*` environment with the tool process's: a shared daemon can retain an old pane ID. Match the TUI PID to `herdr pane process-info`, then explicitly target that live pane. If the current TUI cannot be identified, report the missing context.

## Delivery coordination

Give each executor the shared workflow's self-contained brief and its peers' live Herdr addresses. The director collects results explicitly using the official skill's output-retrieval procedure; Herdr does not deliver a built-in parent mailbox. Accept only after reading the deliverable and its validation evidence.

Use a unique live agent name or returned pane ID to submit a brief or peer message:

```bash
herdr agent prompt <target> '<self-contained brief or peer message>'
```

Submission alone does not establish completion. Launch independent work before waiting; peers can use the same command to exchange findings directly. Quote message text as shell data, preserving literal characters.

## Wait for delivery

When a Codex director has no independent work left and needs to yield its current turn until a delegated target settles, use the [independent interrupt/wait controller](codex-herdr-wait.md). It saves continuation context, interrupts the registered turn, waits outside that turn, and starts a new turn on the same thread. Use the ordinary wait below when retaining the current turn is appropriate.

After launching ready work, wait when the next decision depends on an executor's result:

```bash
herdr agent wait <target>
```

Default to an indefinite wait. Add `--timeout <milliseconds>` only when a concrete task or calling-environment requirement needs a bounded wait. Independent waits may run concurrently.

Keep two kinds of return distinct:

- **The tool yields a running process or cell handle:** resume that same execution through the tool's continuation API until it returns. The Herdr wait is still active; do not launch a second wait or a sleep-and-read loop for that target.
- **The Herdr wait returns:** on `idle` or `done`, read the delivered response and assess the commitment; on `blocked`, inspect and handle the requested interaction. An ordinary timeout is an opportunity to continue waiting, not evidence of a stalled executor. Continue with another wait, indefinite by default, unless a concrete failure or unresolved dependency calls for investigation. Handle other errors through the official skill's diagnostic procedure.

Keep required user updates separate from executor inspection. A communication interval alone is not a reason to read terminal output, send another prompt, or summarize unfinished work. Continue waiting until there is a result to assess, a blocker to resolve, or new user direction to apply.

Once the executor settles, collect its response:

```bash
herdr agent get <target>
herdr agent read <target> --source recent-unwrapped --lines <needed-lines>
```

Use the official skill's output-retrieval procedure if available history is incomplete. A settled state establishes readiness for input; the actual response establishes whether the commitment was met.

## Exit and clean up

After accepting and preserving the results, finish the executor lifecycle before the final delivery or handoff. Unless the user requests keeping it available, exit each idle executor and close the pane created for it. For an idle Codex executor, the following graceful exit was verified in this workflow:

```bash
herdr agent send-keys <target> ctrl+d
herdr pane process-info --pane <owned-pane-id>
```

Confirm the foreground process has returned to the shell, then close that owned pane:

```bash
herdr pane close <owned-pane-id>
herdr pane list --workspace <workspace-id>
```

For another agent CLI, use its documented exit action. If the executor remains active, inspect its visible UI before proceeding. Cleanup is complete when the recorded owned panes are absent and unrelated panes remain. Leave panes, tabs, workspaces, and sessions created by others intact.
