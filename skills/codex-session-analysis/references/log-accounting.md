# Rollout accounting

## Event boundaries

Common JSONL records use `type` and `payload`. `session_meta` supplies cwd, ID, and Git metadata. `turn_context` supplies model/effort and sometimes tier. `event_msg` payloads include `task_started`, `task_complete`, `turn_aborted`, and `token_count`. User and assistant messages and tool calls often appear as `response_item`. Formats vary by client version.

Select the task bounded by its start and terminal event, matching turn IDs where available. Count repeated event/message representations once. A user message embedded in a response item is distinct from a quote in assistant output. Aborted or active tasks have no successful completion latency; keep their observed usage separate. For older logs with no task boundaries, explicitly use user-message-to-final-message timing and explain the fallback rather than fabricating `duration_ms`.

Prefer `task_complete.duration_ms` for completed latency and `time_to_first_token_ms` for reported TTFT. If duration is absent, timestamp subtraction is an observed event interval, not an identical measurement. Final-message timestamps may represent message completion rather than its first token.

## Usage

`token_count.info.total_token_usage` is cumulative and must not be summed across events. Subtract the last cumulative snapshot before the turn from the last within it. Fresh sessions whose first total equals their first `last_token_usage` can establish a zero baseline. With inherited context or a missing baseline, mark the delta unknown. Do not assume a later turn starts from zero.

Preserve available fields: `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens`, and `total_tokens`. Missing fields are unknown, not zero. Check for decreasing counters, repeated events, missing end snapshots, and total/input/output inconsistencies. If a reset or fork makes subtraction unreliable, split accounting intervals only with evidence; otherwise report unknown.

For compatible logs:

```text
uncached input = input - cached input
cache hit ratio = cached input / input
total = input + output
```

Reasoning output is a subset of output. Output includes generated tool calls and other generated content, not only the final answer. A zero reasoning field is not proof of absent reasoning. Image input is already represented in aggregated usage when the log includes it; do not also charge by image count without an explicit rate/metering model.

Cache-write overlap with input requires checking the producer's schema before applying a write surcharge. The simple uncached formula is sufficient for the observed zero-write cases, not a universal cache-write billing contract.

Use each event's `last_token_usage` to inspect per-request context sizes, not as an automatic alternative sum: duplicated snapshots may double-count requests. An incomplete set of snapshots makes the observed maximum a lower bound, not proof that long-context thresholds were never crossed.

## Tool traces

Match `function_call`/`custom_tool_call` with the corresponding output by `call_id`. Record the tool name and raw arguments/input as data. CUA or other shapes may need an adapter. Outer orchestration code can contain several shell invocations, loops, or parallel batches; static occurrences of `exec_command` do not reliably count actual commands.

Report both summed tool response latency and, when calls overlap, the union of intervals. Their sum can exceed elapsed task time. Tools returning a live process ID or `Script running` have yielded, not necessarily completed: label the duration as time to tool response and include subsequent waits when reconstructing process lifetime. Missing outputs mean incomplete timing. Never count source code's `original_token_count` truncation marker as API input usage.

The bundled extractor omits image bytes, hashes decoded data-URL image bytes, and emits trace text only with `--trace`. Hash equality establishes identical bytes, not equivalent cropping/rendering or model image processing. Non-data image URLs are references, not content identity. Unknown schemas should remain visible in warnings rather than be normalized into false precision.
