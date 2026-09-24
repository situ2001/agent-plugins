---
name: reader-focused-writing
description: Write or refine UI copy, technical documentation, and delivery summaries around the reader's decisions and actions. Use when editing redundant explanations, defensive wording, or conversational residue while preserving necessary detail.
---

# Reader-Focused Writing

Give readers the information they need to choose, act, or understand a result. Select information before shortening sentences. Let the reader's task and requested depth determine the length.

## Shared approach

Identify the audience, the action or understanding the text should support, and the facts established by the implementation, specification, or verified work. Use conversation history to understand the task, then make the finished text stand on its own.

Lead with the action, capability, or observable result. Explain implementation where it helps the reader decide, troubleshoot, reproduce, or review. Preserve prerequisites, uncertainty, compatibility limits, accessibility guidance, and consequential warnings when they change the reader's decision. State those conditions directly.

## UI copy

Let labels and controls carry instructions. Show defaults in fields, label actions by their outcomes, and add supporting text when it contributes to the current decision. For copy-only tasks, work within the existing controls and behavior.

Place guidance beside the relevant field, consequences at the decision point, and detailed technical notes in accessible disclosure. Keep qualifications visible when they change a displayed result's meaning. Repeat a fact when separate contexts each need it.

## Technical documentation

Describe the current contract: supported entry points, defaults, prerequisites, and working examples. Place information where its reader needs it:

- Usage guides explain how to use the current capability.
- Migration guidance identifies affected versions, changed behavior or APIs, replacements, and upgrade actions.
- Design documents explain choices and tradeoffs when readers need to evaluate them.

Use the existing document structure unless the requested deliverable needs a new one. Check examples against the actual implementation and distinguish observed behavior from inference.

### iOS and macOS development notes

- For build or reproduction steps, name the relevant workspace or project, scheme, configuration, and destination when they affect the outcome. State the required Xcode or OS version when compatibility matters.
- Identify where a check ran: macOS host, iOS simulator, or device. If a macOS check compiles shared iOS source, name the Apple APIs kept real, the substituted dependencies, and the iOS integration it leaves untested.
- For networking, caches, persistence, or lifecycle behavior, name the layer that owns the state and the signal used to observe it. Give the precise reset or inspection step when it helps someone reproduce or troubleshoot the result.

## Delivery summaries

Lead with what changed or what was found. Add verification, unresolved issues, rationale, and links to the extent they affect use or confidence. Distinguish completed work from proposals and checks performed from assumptions.

A small task may need one or two sentences. Expand for requested detail or evidence needed to assess the result. Select completed outcomes and material limits; leave chronological work logs out of routine summaries.

## Final editing pass

Ask of each sentence: **What would the reader lose if this were removed?** Keep information whose absence could cause a wrong action, misleading interpretation, or uncertainty about completion. Move details needed later to the place where they become relevant. Delete passages that merely repeat the interface or prove compliance with earlier corrections.
