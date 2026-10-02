# Codex interrupt, Herdr wait, and continuation

Use this when the **Codex director has no other independent work** and its next decision requires an already-delegated Herdr executor's result. The controller runs in a separate shell pane, interrupts the director's exact registered turn, waits for the executor, then delivers continuation input to a **new turn on the same thread**. This relinquishes the current turn; it does not preserve a Python/tool call stack. Codex built-in collaboration and Claude directors keep their own runtime mechanics.

The MVP waits for **one target**. Choose an executor representing the next actual dependency. With several outstanding executors whose blockers must wake the director, retain ordinary concurrent waits; chaining this controller's waits would hide an earlier blocked target behind another long-running target.

## Prepare the handoff

Read the official Herdr skill as required by [the Herdr runtime guide](herdr.md). Use observed live addresses in the same Herdr session. The CLI uses `herdr agent get/wait` and never retrieves executor history itself.

1. Finish all director work that can proceed independently. Save the task, confirmed scope, remaining decisions, executor address, expected result locations, acceptance criteria, and cleanup ownership in a continuation text file. Include enough context to handle blocked or failed delivery. The controller copies this text into its registration; later edits to the source do not change the handoff.
2. Identify the director's actual live pane/name explicitly. `CODEX_THREAD_ID` from the director's tool process is the source of thread identity; an explicit `--thread-id` overrides it. The observed `CODEX_SESSION_ID` was the same value, and `CODEX_TURN_ID` was absent. The script reads the current `inProgress` turn through RPC, optionally checking `--turn-id`. A shared daemon exposed a stale `HERDR_PANE_ID`, so that environment value cannot identify the director's thread or reliably locate its pane.
3. When Herdr exposes the director's `agent_session`, the CLI checks its thread ID. The successful prototype's director lacked this metadata; in that case verify the live Codex TUI PID against `herdr pane process-info` before supplying `--director`. The explicit director pane is used to wait for cancellation to settle, while RPC always targets the registered thread/turn. Executor registration requires `agent_session`, binding its session plus pane, terminal, and agent kind so a replaced occupant cannot satisfy the old commitment.
4. Register a fresh evidence directory while the director's current turn is active:

```bash
wait_script=/absolute/plugin/skills/agent-team/scripts/codex-herdr-wait.py
wait_root=/absolute/task-evidence
wait_job="$wait_root/dependency-1"
director_pane=<observed-director-pane-id>
executor_target=<observed-executor-name-or-pane-id>

uv run --script "$wait_script" prepare \
  --job "$wait_job" \
  --director "$director_pane" \
  --target "$executor_target" \
  --resume-file "$wait_root/continuation.md"
```

`prepare` performs no interruption. Review `plan.json`: exact `threadId`/`turnId`, live identities, socket, and frozen continuation. The directory must be new; the CLI refuses to replace an existing registration. Use `--help` on the CLI or subcommands for arguments. Python and the pinned `websockets` dependency run through uv's PEP 723 support, with no repository `node_modules` dependency. Resolve dependencies before yielding the director, for example by running the CLI's help command.

The default socket is `$CODEX_HOME/app-server-control/app-server-control.sock`, or `~/.codex/app-server-control/app-server-control.sock` when `CODEX_HOME` is unset. `--socket` selects a different **existing daemon's Unix WebSocket**. A new tool process with the same home does not necessarily have access to the loaded thread. Connection/access failures are explicit errors; the tool never creates another server, resumes/reloads a thread, or restarts a daemon to work around them.

## Launch the independent controller

Create an owned sibling **shell** pane with the director's working directory and preserve user focus. Inspect geometry and use the appropriate split direction. Explicitly target the verified pane when inherited caller context is stale:

```bash
herdr pane layout --pane "$director_pane"
herdr pane split --pane "$director_pane" --direction <right-or-down> --cwd "$PWD" --no-focus
```

Read the new `.result.pane.pane_id` into `controller_pane`. Launch the controller as an ordinary command through `pane run`; the independent pane owns its process even when the director's turn is interrupted. Encode the shell command as data:

```bash
controller_command=$(python3 - "$wait_script" "$wait_job" <<'PY'
import shlex, sys
print(shlex.join(["uv", "run", "--script", sys.argv[1], "run", "--job", sys.argv[2]]))
PY
)
herdr pane run "$controller_pane" "$controller_command"
```

Make this launch the director's final handoff action. Keep the controller in the same Herdr session, with the same daemon access and usable CLI paths. A background command inside the director's own tool execution does not establish this independent lifetime.

The one-shot sequence is:

1. Claim the registration once. Check both live identities and confirm the latest director turn is the registered `inProgress` turn.
2. Persist the interrupt intent and call `turn/interrupt(threadId, turnId)`. Wait for the explicitly registered director's Herdr UI to settle, then confirm that exact turn is `interrupted`.
3. Wait indefinitely for the single registered executor using Herdr's default `idle`, `done`, or `blocked` states. Recheck its identity/state and preserve raw wait/get evidence.
4. Check cancellation and re-read the thread. Continue only while its latest turn is still the registered interrupted turn and the thread is idle. Persist start intent before `turn/start` with the frozen continuation and evidence paths; record the returned new turn ID.

## Return and failure semantics

| Outcome | Controller behavior | Director action |
| --- | --- | --- |
| Executor `idle` / `done` | Start a continuation with `wakeReason: ready` | Read the real response and validate the commitment. Readiness alone is not acceptance. |
| Executor `blocked` | Start a continuation with `wakeReason: blocked` | Inspect `agent get` and the visible UI; handle the requested interaction. |
| Herdr wait/get error, replaced target during wait, or unsettled target after wait | Save the error and start a continuation with `wakeReason: wait_failed`, if the old director turn remains eligible | Inspect the evidence and live state before deciding the next action. |
| Later director turn, including a completed or interrupted user turn | Save `phase: superseded`; send no continuation | Inspect retained executor/evidence results manually in the user's current workflow. |
| Cancellation marker | Save `phase: cancelled`; send no continuation | Inspect retained results when wanted. |
| RPC/access failure, unconfirmed interrupt, or controller failure | Save `phase: failed` plus `failedPhase`/error and exit; recovery may require the user/director | Diagnose the actual error. A disconnected daemon cannot deliver a wake-up. |
| Repeated/concurrent `run` | Exit without further RPC | Inspect the original run's evidence. |

`result.json` preserves the latest phase, exact IDs, wake reason, and command evidence; `events.jsonl` preserves the phase sequence. `plan.json` is the frozen registration. Exit codes are `0` for registration/cancellation recording or successful continuation, `1` for failure, `3` for an already-claimed run, and `4` for cancelled/superseded execution.

`run.claim` is permanent. A crash or lost mutation response leaves a consumed registration; a second invocation cannot repeat interrupt/start. This provides **at most one attempt**, not guaranteed delivery. For `failedPhase: start_requested`, the server may have accepted the continuation before the response was lost. Inspect the thread and saved events before deciding anything further; deleting the claim and retrying can duplicate delivery.

Suppress a pending continuation explicitly:

```bash
uv run --script "$wait_script" cancel --job "$wait_job"
```

This records cancellation without sending agent input. An active Herdr wait continues until it settles, retaining the result. To stop waiting immediately, stop only the owned controller process/pane; preserve its files for inspection. Cancellation received after the start request cannot retract an accepted turn.

Follow Herdr's official retrieval rules after wake-up: busy or blocked agents may be inspected through their visible UI, but application history/scrolling waits for a settled state. For ready executors, use `agent get`, then `agent read --source recent-unwrapped` with the needed lines; use the official file-output fallback when history cannot recover the delivered response. Accept the real artifacts and checks before cleaning up executors and the owned controller pane.

## Protocol and evidence boundaries

The [official Codex App Server documentation](https://learn.chatgpt.com/docs/app-server) defines initialization, `thread/read(includeTurns=true)`, `turn/interrupt`, and `turn/start`. Each connection sends `initialize` with `clientInfo`, then `initialized`. Interruption acknowledges cancellation; completion must be confirmed before continuation. `thread/read` does not itself load or resume a thread. The existing control socket was verified with `websockets.sync.client.unix_connect`: it requires a WebSocket handshake. A stdio proxy only forwards bytes and does not turn this socket into a JSONL transport.

The generated local `TurnStartParams` schema has no expected-previous-turn compare-and-start field. Rechecking immediately before start prevents delivery after an **observed** user turn change, but there remains a race between that read and `turn/start` (an active new turn may be steered by the server). This CLI cannot claim an atomic guarantee against simultaneous user input. Keep this limitation explicit; stronger protection requires a server contract, not another polling check. Likewise, cancelling without any observable thread change requires the explicit cancellation marker.

The supplied live experiment established transport and independent lifetime: one same-thread interrupt/wait/start cycle and 60.517 seconds without director session events. Its tool returned in segments around 30 seconds; that observation is not a general Codex maximum wait duration. The maintained tests execute the real CLI against a temporary Unix WebSocket and fake Herdr; they do not call a paid model or touch a real director thread:

```bash
uv run --script skills/agent-team/tests/test_codex_herdr_wait.py
uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/agent-team
git diff --check
```

They cover registration, exact interrupt/wait/start ordering, same-thread continuation, blocked/failure wake-up, changed user turns, cancellation, target replacement, concurrent/repeated runs, and lost RPC responses. They establish the CLI contracts under controlled inputs. On 2026-10-02, the packaged CLI also completed a live `prepare`/`run` cycle against the existing local daemon and an already-idle Herdr executor: the registered turn was interrupted and a new turn started on the same thread. This validates the packaged integration; the earlier prototype establishes the 45-second wait. Simultaneous user input remains subject to the non-atomic read/start limitation above.
