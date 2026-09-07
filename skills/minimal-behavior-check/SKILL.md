---
name: minimal-behavior-check
description: Reproduce a specific bug or verify an uncertain behavior with a minimal executable check against actual source, especially when a usable test harness is missing or the full application cannot run. Use for concrete behavioral questions, not automatically for every edit or as a substitute for integration testing.
---

# Minimal Behavior Check

Turn a concrete uncertainty into an executable check whose result can contradict the implementation. Choose the smallest environment that preserves the behavior being investigated. Node `vm` is one option, not the methodology itself.

## Choose the check

State the question and expected observable outcome before building a harness. Derive expectations from the requirement, protocol, or reported failure, rather than copying the implementation's conditions into assertions.

- For a bug, capture a triggering input and an observable failure. When the original version is available, run the same check against original and fixed source using an isolated copy; the original should fail for the reported reason, and the fix should pass.
- For new logic, select representative inputs and the boundaries that could change the result: for example zero versus missing values, or URL encoding and preservation of required identifiers. Avoid accumulating unrelated cases.
- If reading the code and existing checks already settle the question, finish without adding another script. A reversible cosmetic edit alone does not justify a custom harness.

Inspect the repository's available checks first. Prefer an existing focused test, then a direct import in a supported runtime. Use temporary transpilation and an isolated context only when loading the source normally is impractical. Keep required type/lint checks: executing a few cases answers a different question.

## Preserve the behavior under investigation

Load the actual source, invoke its exported function or component, and assert observable outputs or effects. Rewriting the algorithm in the check only verifies the rewrite. Extracting a source fragment weakens the evidence by bypassing its module and call path; prefer loading the whole module and disclose any necessary extraction.

Supply only the environment needed for the question. Use real dependencies where practical and explicit stubs at unrelated boundaries. Unexpected imports or side effects should fail visibly; a catch-all loader returning `{}` can conceal missing dependencies and false passes. A stub must not supply the answer the check is intended to prove.

For TS/TSX that cannot be imported directly, read [the Node/TypeScript recipe](references/node-typescript.md). For other languages, use the same pattern with their native loading and assertion tools; no Node dependency is required.

## Execute and interpret

Run the check and inspect its output and exit status. Await asynchronous work so failures reach the process exit status. Distinguish a harness failure, such as an unresolved import, from a failed business assertion. Repair only the environment mismatch; preserve the expected behavior unless new requirements justify changing it.

For a fix, prefer the original failure as the negative control. Otherwise, when a false pass is plausible, use one deliberately incorrect input or a temporary source mutation to confirm the assertion detects the relevant defect. Keep mutations in scratch copies, not the user's working files.

Stop once the specific question is answered and required repository checks pass. If verification requires recreating a framework, a large dependency graph, or the production integration itself, use an existing integration environment or explain the unresolved boundary. Do not refactor production code, add dependencies, or introduce a test framework solely to make a one-off check convenient.

## Keep the result reviewable

One-off scripts belong in a uniquely named temporary location or an inline command. Include the source path and chosen inputs so the check can be understood and repeated. A useful recurring regression check can move into the repository's established test structure when that fits the task.

Report briefly:

- What actual source behavior was exercised and which cases passed or failed.
- Which dependencies or environment objects were replaced.
- What remains unverified, where material to the task.

For example: “Checked the actual URL builder with an item ID containing `+` and `/`; the ID survived encoding and a preview-only parameter was removed. The check supplied `window.location`; it did not exercise browser navigation or the backend.”

Static component rendering proves emitted markup for the supplied props. It does not prove browser layout, hydration, interactions, or native bridge behavior. A mocked request proves the caller's behavior under that response, not the service contract or authorization.
