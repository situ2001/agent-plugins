---
name: benchmark-workload
description: Measure the performance and CPU, GPU, memory, or network cost of a real workload, including healthy systems and before/after comparisons. Use for workload benchmarks and resource measurements; not retrospective Codex session accounting or a bug diagnosis by itself.
---

# Benchmark Workload

Measure the workload the user actually cares about, with repeatable inputs and clearly defined metrics. Produce observations that support a decision without assuming a performance fault or introducing optimizations as part of measurement.

## Define the measurement

Establish the operation, input, execution target, and question from the request and available project context. Choose metrics that answer it: startup or end-to-end latency, throughput, interaction timing, CPU time or utilization, GPU activity, memory, transfer bytes, or energy when observable.

Define each metric's unit, scope, and observation window. Distinguish process, process tree, device, and whole-machine measurements; peaks, averages, and accumulated totals answer different questions. Define the completion event so timing ends on the useful result rather than merely on a launch or enqueue operation.

Record the source revision and relevant local changes, build mode, command, runtime and tool versions, hardware, execution backend, and consequential settings. Preserve input identity, such as dataset, model weights, text, resolution, or concurrency. Verify which artifact or service is actually executed, especially when comparing checkouts or deployed variants.

This step is complete when the workload, metrics, source state, and completion event are reproducible. Resolve missing information that would materially change the benchmark; state reasonable assumptions for the rest.

## Prepare observation

Prefer existing benchmark commands and available profiling tools. Add a focused temporary runner when necessary to invoke the real path and capture results. Keep workload execution and measurement overhead distinguishable. Use real dependencies required by the question; disclose fixtures and substitutions and what they exclude.

Separate cold startup, initialization or model loading, warm execution, and sustained operation when relevant. State the cache and warm-up conditions rather than blending these phases into one figure. Keep comparison variants on comparable inputs and settings; vary run order when drift could affect the conclusion.

Choose run count, sampling interval, and duration from workload variability, metric resolution, the user's constraints, and the decision being made. State the rationale; there is no universal fixed run count or measurement window. Arrange cleanup for owned processes and monitors.

For common measurement boundaries:

- **Web delivery:** distinguish raw build size, compressed artifact size, and actual transferred bytes. Capture the requested page's requests, encoding, and cache conditions; a bundle inventory alone does not measure network transfer or page readiness.
- **Inference:** separate loading from inference, identify the actual CPU/GPU backend, and wait for device completion when execution is asynchronous. Check the resulting output. For generated audio, output duration and elapsed inference time can support a real-time-factor comparison when useful.
- **Resource use:** retain the tool's CPU normalization and memory definition, such as RSS or device allocation. On shared or unified-memory systems, overlapping memory categories cannot simply be added. System GPU activity does not by itself attribute work to the target process.

This step is complete when the instruments can observe the chosen operation at the claimed scope, with their relevant limitations understood.

## Run and preserve results

Execute the real workload and verify it reaches the intended result. A fast failed operation is a failed run, not a performance result. Retain per-run measurements, status, commands, and consequential diagnostics in a machine-readable form suited to the tools. Save useful traces or profiles when they support interpretation.

For comparisons, run baseline and candidate under the defined conditions. Record changes in environment, inputs, cache state, background load, or thermal conditions that affect comparability. Keep failed or interrupted runs visible with their reasons; explain exclusions from aggregates. When a measurement tool is unavailable, report the unavailable metric and the observations that remain possible rather than presenting a proxy as that metric.

Stop when the observations answer the stated question at the required resolution. If noise prevents that conclusion, refine the relevant measurement or report the unresolved boundary. Clean up owned resources while retaining repeatable commands and raw results.

## Interpret and deliver

Report per-run results before useful aggregates, with spread when repeated runs differ. Compute changes from unrounded values and name the denominator. Keep cold and warm results, distinct metric scopes, and mismatched variants separate.

Separate observed differences from causal explanations. A smaller transfer or lower elapsed time establishes that result under the measured conditions; attribute it to a mechanism only when traces, profiles, or a controlled comparison support the claim. Optimization proposals may follow the evidence when requested, but measuring a workload does not authorize changing its implementation.

Finish with the result, comparison conditions, repeat command, raw-result or trace paths, and material limits. Completion requires successful workload outputs, attributable measurements for the claimed scope, explained failures, and enough evidence to repeat the measurement. Keep conclusions within the tested inputs and environment.
