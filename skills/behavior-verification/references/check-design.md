# Designing a check that can be wrong

Use this reference when the difficult part is deciding what to assert, selecting inputs, or reviewing a generated harness. Finish with a small set of cases where each has an independent expected result and a named defect it would detect.

## Follow the causal path

Trace trigger → production entry → relevant collaborators → observable effect. Mark the links that must remain real. Place fixtures outside those links. Keep the transformation or coordination under investigation real; replace external producers or consumers only where their internals are outside the question. Record the inputs and outputs at those boundaries.

Choose the seam by the failure mechanism, not by what is easiest to stub. If routing, disabled controls, module initialization, or event registration could be the failure, calling the final handler skips the disputed link. Use the real entry or narrow the claim explicitly. A replacement child can test parent wiring but cannot validate the child's internals.

## Establish an oracle

Use the requirement or protocol first; use a reported reproduction or established externally visible behavior when appropriate. State assumptions when these conflict. Existing behavior is a compatibility baseline, not automatic evidence of correctness.

For exploration without a specification, report observed outputs, transitions, and side effects. Classify a difference as a regression only when it violates an established requirement or compatibility obligation.

Assert observable consequences rather than internal implementation choices:

| Contract | Useful assertion | Weak substitute |
| --- | --- | --- |
| Preserve identity through a URL | Parse destination and compare decoded parameter | String contains the parameter name |
| Send correct request | Exact relevant method, identifier, mask, and count | Some request occurred |
| Display the specific failure | Fallback plus meaningful error identity/message | Any error text exists |
| Perform an effect exactly once | Exact count and relevant payload | Count is at least one |
| Latest selection wins | Resolve new response, then old; inspect final selection | Render only one resolved response |
| Retry recovers | Fail, invoke retry, succeed, verify error clears | Retry button exists |
| Cleanup prevents effects | Dispose, deliver the event/response, assert no forbidden effect | Cleanup function exists |

Use exact counts only when their meaning is justified. Development instrumentation can produce extra events; investigate and separate that observation from a production guarantee. Compare error identity only when the same object should propagate; serialized errors need field assertions. Use tolerances for numerical contracts that allow approximation, with units and a justified bound.

## Select discriminating cases

Start with the reported failure and one nearby valid case that rules out “always error” or “always success.” Add only boundaries that could change the decision under review:

- Presence semantics: missing, zero, empty, or false when these have distinct meanings.
- Thresholds: just below, at, and above the relevant threshold.
- Ordering: pending versus resolved; stale versus current response.
- Lifecycle: before mount, mounted, disposed, or remounted when subscriptions/resources matter.
- Recovery: failure → retry → success when retry is part of the contract.

Do not generate a Cartesian product of every option. Each case should name the distinct failure it detects. Distinctive fixture values help reveal swapped fields or stale state; identical IDs, balances, or messages hide them. Use contract-valid error/empty shapes as well as successful shapes. An invalid fixture that production could never receive may test robustness, but it does not reproduce the reported failure.

Where exact output is unavailable, a justified invariant or metamorphic relation can help: round trips preserve supported values, output ordering respects a documented rule, or an irrelevant field does not change the result. Derive the relation from the contract, not an assumption about the implementation.

## Define the observation window

For stateful behavior, establish the initial state, trigger the actual operation, and await a specific observable consequence. Register completion signals before the trigger and bound waits. Control external completion order when needed; advancing one scheduler turn is not evidence that all relevant work finished.

Assertions about absence or exact counts need a defined observation window: after controlled operations settle or the contract's deadline expires. An immediate zero count can pass before the relevant work executes. A final-state assertion alone does not establish that intermediate or repeated side effects were correct.

When effects repeat, record each producer, payload, and operation identity. Distinguish multiple delivery paths, retries, lifecycle re-entry, leaked state, and instrumentation effects before changing the expected count.

## Preserve delivery and isolation

Distinguish direct return values, exceptions, asynchronous failures, and runtime-generated notifications. Exercise the actual delivery channel when registration, routing, propagation, or removal is part of the question. Calling the final callback proves only callback behavior. Synthetic delivery verifies consumption, not automatic generation or platform scheduling; disclose that boundary.

Scope failure capture to the expected operation so unrelated failures remain visible. Observe consequential payloads and side effects as well as the final state. For disposal behavior, release a pending result or deliver an event after disposal and verify no forbidden effect.

Use fresh fixtures and restore owned resources even after failed assertions. Prior subscriptions, cached state, or pending operations can supply a later case's apparent success. Keep cleanup failures visible without erasing the original assertion failure.

## Test the test

For a fix, run the same behavioral assertion on original and changed source. The original must fail for the target reason; a compilation failure is not a useful negative control. Separate old-behavior characterization from this regression assertion: two versions passing different expectations demonstrates a difference, not that the regression test detects the bug.

When the baseline cannot expose the risk, make one relevant mutation in a scratch copy: remove the listener, drop an identifier, remove cancellation, or allow duplicate dispatch. Confirm the core assertion fails, then discard the mutation. A wrapper that expects the negative control to fail may exit successfully, but record the actual violated assertion. Do not claim sensitivity merely because two outputs differ or a branch named “negative control” ran.

A mutation can be optional when an existing focused regression already supplies the evidence. When used, keep fixtures, runtime, and assertions constant so the mutated behavior is the reason for failure. Syntax errors and unrelated invalid inputs do not qualify.

## Evaluate a harness

Review five things: source fidelity, oracle independence, preservation of the causal path, sensitivity to a plausible defect, and repeatability. Case count and framework sophistication are not quality measures.

A broad harness with permissive mocks can be weaker than one precise case. Conversely, a precise failure-only check can miss a change that breaks every successful input. State the missing evidence instead of combining unlike checks into an unsupported overall score.

## Turn the contract into an executable case

Use this sequence when translating a question into a harness; fill in only the dimensions relevant to the behavior:

1. Establish the initial state and assert the precondition needed for the trigger.
2. Invoke the real entry with distinguishable, contract-valid inputs.
3. Control external completion or failure only where determinism requires it.
4. Await the specific observable consequence with a bounded wait.
5. Assert the required result and any consequential forbidden side effect.
6. Challenge the assertion with a baseline or targeted fault when sensitivity is uncertain.
7. Dispose owned resources and record what the selected environment cannot establish.

If a step can succeed without reaching the production behavior, inspect the seam or observation before adding more cases. Adapt the sequence to pure functions, stateful modules, command-line programs, or service flows; it does not require a UI or asynchronous work.

## Triage a failed run

| Observation | Next action | Evidence status |
| --- | --- | --- |
| Missing module, incompatible renderer, unsupported transform | Repair resolution/runtime without changing the business expectation | Harness did not reach behavior |
| Unexpected API or fixture shape | Inspect actual call and protocol; fix fixture only if its contract was wrong | Unresolved until provenance is clear |
| Intended source reached, valid trigger, observable mismatch | Preserve the failing case and report/fix within authorized scope | Product failure under stated assumptions |
| Timeout | Capture pending calls/listeners and the last observed state; identify the missing transition | Neither pass nor automatic product failure |
| Pass plus warnings or extra side effects | Identify their producer and impact before claiming the whole contract passed | Selected assertion passed; other evidence unresolved |
| Baseline and mutant both pass the core assertion | Check the executed source, trigger, mock seam, and assertion | Sensitivity not established |
