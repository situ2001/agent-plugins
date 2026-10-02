# Codex built-in collaboration

Use the `collaboration` tools exposed in the current task. Read their live declarations for limits and supported arguments; these tools create agents in this task's team, not user-owned chats.

## Launch

With `collaboration.spawn_agent`, use these exact settings:

| Role | `model` | `reasoning_effort` | `fork_turns` |
| --- | --- | --- | --- |
| Executor, investigator, verifier | `gpt-6.1-sol` | `high` | `none` |

Full-history forks inherit their parent's settings and cannot accept model or effort overrides. Give every fresh agent a self-contained brief with essential background, confirmed decisions, applicable instructions, ownership, and accessible resources. Respect the live concurrency limit.

## Coordinate

Use the returned canonical task names as peer addresses. Send a message with `collaboration.send_message` to a working agent; use `collaboration.followup_task` to give an idle agent another task. Send missing peer IDs after all relevant agents exist.

Wait for completion notifications or use `collaboration.wait_agent` with a bounded wait. Check `collaboration.list_agents` when status needs investigation. An agent's final answer is delivered to its parent; a message or intermediate update is not completion. Keep peer defect exchanges direct, then have the verifier send its verdict to the director.
