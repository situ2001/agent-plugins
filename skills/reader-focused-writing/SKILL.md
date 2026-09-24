---
name: reader-focused-writing
description: Write or refine UI copy, product documentation, and delivery summaries around the reader's decisions and actions. Use when editing redundant explanations, defensive wording, or conversational residue while preserving necessary detail.
---

# Reader-Focused Writing

Give readers the information they need to choose, act, or understand a result. Select information before shortening sentences. Let the reader's task and requested depth determine the length.

## Shared approach

Identify the audience, the action or understanding the text should support, and the facts established by the implementation, specification, or verified work. Write from that evidence.

Use conversation history to determine the intended outcome. Treat intermediate corrections as editing instructions; carry them into the artifact when they establish a requirement relevant to its reader. A finished document should make sense independently of the conversation.

Lead with the action, capability, or observable result. Replace defensive contrasts with the useful fact they were trying to communicate. Keep explanations of implementation when they help the audience decide, troubleshoot, or review a change.

Evaluate qualifications by their effect on the reader. Preserve prerequisites, uncertainty, compatibility limits, accessibility guidance, and consequential warnings. Positive phrasing should retain the underlying meaning: “The action requires an administrator account” communicates a real condition. A factual API removal belongs in migration guidance. Choose wording by meaning rather than by a blacklist of negative words.

## UI copy

Let labels and controls carry instructions. Show defaults in fields, label actions by their outcomes, and add supporting text when it contributes to the current decision. For copy-only tasks, work within the existing controls and behavior.

Place guidance beside the relevant field, consequences at the decision point, and detailed technical notes in accessible disclosure. Keep qualifications visible when they change a result's meaning, such as costs excluded from a displayed total. Repeat a fact when separate contexts each need it.

For example, a daily-limit field can show its default and offer “Unlimited,” with the note: “Requests pause at the limit and resume at 00:00 Shanghai time.” The reader can act on the control and its effect; storage conventions belong with implementation details.

## Documentation

Describe the current contract: supported entry points, defaults, prerequisites, and working examples. Use the existing document structure and place information according to reader need:

- README and usage guide: current capabilities and how to use them.
- Changeset and migration guide: affected versions, changed APIs, replacements, and upgrade actions.
- Design rationale: choices and tradeoffs when the document's purpose calls for them.

A README may include a migration note when its audience needs one. Create additional documents when the requested deliverable calls for them.

For a plugin whose entry points were consolidated, a README can say: “Import the package root and instantiate the plugin. It injects the runtime through Webpack.” A changeset can say: “The `/runtime` export has been removed. Use the plugin from the package root for runtime injection.” Each passage serves its own reader's task.

## Delivery summaries

Lead with what changed or what was found. Add verification, unresolved issues, and rationale to the extent they affect use or confidence. Distinguish completed work from proposals and checks performed from assumptions. Link the deliverable when useful.

A small task may need one or two sentences. Expand for requested detail, meaningful tradeoffs, or evidence needed to assess the result. Select completed outcomes and material limits; leave chronological work logs and demonstrations of diligence out of routine summaries.

Example: “Simplified channel labels and moved limit guidance beside each field. Build passed; browser behavior remains unverified.”

## Final editing pass

Ask of each sentence: **What would the reader lose if this were removed?**

Keep information whose absence could cause a wrong action, misleading interpretation, or uncertainty about completion. Move details needed later to the place where they become relevant. Delete passages that merely repeat the interface or prove compliance with earlier corrections.

Check examples and claims against the available evidence. Preserve requested depth in tutorials, analysis, and detailed documentation. When useful information feels crowded, improve its placement and structure. Deliver the edited artifact with a brief result appropriate to the task.
