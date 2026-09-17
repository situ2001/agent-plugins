---
name: behavior-verification
description: Verify a concrete behavioral uncertainty against actual source with a focused executable check, from individual functions and stateful components to service or application flows. Useful when a test harness is missing or the full app cannot run; not an automatic requirement for every edit.
---

# Behavior Verification

Turn a concrete uncertainty into an executable check whose result can contradict the implementation. Choose the smallest environment that preserves the behavior being investigated: a function call, stateful runtime, or integration environment. Choose tools from the failure mechanism and available runtime.

## Establish the verification contract

Before writing code, record a compact contract:

- **Source:** exact revision or staged/working-tree state and the entry to execute.
- **Trigger:** initial state, input/action, and relevant completion order.
- **Oracle:** expected observable result and its independent basis (requirement, protocol, reported failure, or established behavior).
- **Boundary:** dependencies kept real, substitutions, and what those substitutions cannot prove.
- **Discriminator:** the plausible defect that would make this check fail.

Keep this proportional: one sentence can suffice. If no independent oracle is available, label the check as characterization and report observed behavior; a plausible implementation is not its own specification. Keep verification within the requested scope; identifying a defect does not by itself authorize modifying the implementation.

Load the source state the user requested and keep relevant collaborators consistent with it. Record revisions or preserve snapshots; disclose any mixed states. A matching path does not prove that an executed file or deployed artifact contains the intended changes.

## Select the scope

- For a bug, capture the reported failure. When original source is available, run the same check against original and fixed source in isolated copies. The original should fail for the reported reason and the fix should pass.
- For new logic, choose representative inputs and boundaries that can change the outcome: zero versus missing, insufficient versus sufficient, pending versus resolved, or old versus current selection. Avoid unrelated case accumulation.
- If code reading and existing checks settle the question, finish without another script. A reversible cosmetic edit alone does not justify a custom harness. A concrete layout or interaction defect can justify a browser check.

Inspect available scripts, dependencies, runtime versions, and repository instructions. Prefer an existing focused test; otherwise create a temporary check within the task's authorized scope. Missing test infrastructure is a reason to consider a small harness, not evidence that behavior is unverifiable. Respect local limits on starting servers or using host applications, and keep required type/lint checks separate.

## Choose an environment that can observe the failure

Choose directly from the question; there is no need to run every level.

| Question | Smallest useful environment | Evidence boundary |
| --- | --- | --- |
| Transformation, validation, serialization, calculations | Actual function in its supported runtime | Outputs and effects for supplied inputs |
| State transitions, lifecycle, concurrency, retries | Actual stateful module with a compatible runner | Observed transitions and controlled completion orders |
| Framework behavior and event handling | Real framework with its supported test environment | Only the lifecycle and event semantics it implements |
| Layout, device behavior, platform APIs | Actual relevant browser, device, or host | Behavior in the tested platform and configuration |
| Persistence, transactions, process or service coordination | Relevant real integration environment | Guarantees of the exercised systems, not substituted ones |
| User journey across application boundaries | Runnable application and relevant services | Only integrations actually exercised |

Read [Check design](references/check-design.md) when choosing cases, designing assertions and observation windows, preserving delivery paths, or evaluating the strength of an existing harness. It explains how to make a passing result meaningful.

Read only the relevant execution recipe:

- [Node / TypeScript](references/node-typescript.md): direct loading is impractical and temporary transpilation or `vm` is needed.
- [React behavior](references/react-behavior.md): hooks, effects, component interactions, asynchronous transitions, or native component substitutes.
- [Browser flows](references/browser-flows.md): Playwright/browser setup, request fixtures, browser assertions, and E2E boundaries.

For other languages, apply the same method using their native runtime and assertion tools.

## Preserve the behavior under investigation

Load actual source and invoke its exported function, component, or real application entry. Prefer whole modules and their real call paths. Rewriting the algorithm only tests the rewrite; extracting a fragment bypasses module wiring and must be disclosed. For a scratch configuration edit, verify the intended replacement occurred and distinguish that variant from the unchanged source.

Use real dependencies along the path being checked. Stub only named boundaries outside it; unexpected imports or calls should fail visibly. A catch-all loader or a stub that returns the desired result regardless of input can conceal the defect. Assert consequential request arguments, and make fixture responses respect the relevant contract. Fixtures should distinguish correct and incorrect consequential inputs; an unconditional successful response can conceal malformed requests. Prefer contract-derived values or observed response shapes over invented successful data.

Use semantically appropriate assertions: compare parsed JSON fields when key order is irrelevant, and exact bytes only when serialization itself is the contract. Source-text matches and build success can supplement behavioral evidence but do not establish runtime behavior.

## Execute and interpret

Run the check and inspect output and exit status. Await asynchronous assertions, bound waits, and propagate failures to a nonzero exit. Control promise completion or timers when ordering matters; avoid relying on arbitrary sleeps. Distinguish harness failures (imports, framework versions, missing globals) from business assertion failures. Repair the environment mismatch while preserving the expected behavior unless the requirement was misunderstood. Classify each failure before editing the harness: setup, fixture/contract mismatch, product behavior, or unresolved. When changing an assertion, cite the contract or runtime evidence that justifies it and state which claim is no longer tested. A pass obtained by weakening an unexplained failing assertion is not a resolution.

For a fix, prefer the original failure as a negative control. If a false pass remains plausible and original source is unavailable, introduce the relevant defect in a scratch copy and confirm the assertion fails for that reason. An unrelated invalid input does not show that the target defect would be detected.

Stop when the stated question is answered and applicable repository checks are complete. If the harness starts recreating a framework, a large module graph, or the production integration, switch to an existing integration environment or report the unresolved boundary. Keep production code, package manifests, and lockfiles unchanged solely for harness convenience. Prefer installed tools; a small version-compatible dependency isolated in scratch space is reasonable when permitted and necessary. Do not turn a one-off check into a framework migration.

## Keep the result reviewable

Use a uniquely named temporary directory or an inline command. Write readable setup/action/assertion/cleanup blocks with case names and diagnostic assertions. A one-off script should still let another agent locate a failure without reconstructing compressed code. Execute the documented command from the final artifact location; moving a script can change dependency resolution. Preserve useful snapshots deliberately and avoid overwriting unrelated artifacts. Record the source revision or working-tree state, inputs, execution command, and any temporary dependencies sufficiently to repeat the check. Move a recurring regression into the repository's established test structure when that fits the task. Clean up owned processes, browser contexts, listeners, timers, and fixture state; retain useful failure evidence.

Report briefly:

- What actual source behavior ran, with the decisive cases and outcomes, including a negative control when used.
- Which dependencies or environment objects were replaced.
- Material behavior still unverified and the command/artifact needed to repeat the check.

Label evidence precisely: a component callback check, DOM interaction check, browser integration check with mocked services, or E2E through the listed real systems. Static rendering does not establish hydration or interaction; browser fixtures do not establish backend behavior; replacing native views does not establish native rendering or bridge correctness. A passing check supports its selected cases, not every aspect of the change.

## Completion criteria

Conclude only when the selected cases ran against the intended source, their assertions support the stated contract, failures and unexpected diagnostics are explained, and owned resources are cleaned up. A timeout, skipped case, swallowed exception, or harness import failure is unresolved evidence, not a pass. Report a concrete limit when the required runtime is unavailable. More cases are useful only when they distinguish another material failure mechanism; broad coverage claims require broader evidence.
