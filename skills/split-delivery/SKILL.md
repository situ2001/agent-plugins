---
name: split-delivery
description: Organize existing mixed changes into cohesive commits or branches that can be reviewed and adopted separately. Use for staged and unstaged work or splitting existing commits, including dependent branches; not for implementing new work or merely writing a PR description.
---

# Split Delivery

Turn an existing change set into delivery units whose purpose, contents, and dependencies are clear. Preserve the original work and implement the requested split, rather than stopping at a proposed grouping when commits or branches were requested.

## Inventory the source

Read repository guidance and inspect branch state, the index, the working tree, and untracked files. Inspect the complete staged and unstaged diffs, including relevant new files. For committed work, establish the requested base and inspect the full commit range. Respect an explicit committed-only scope while preserving unrelated local work.

Record the original base, commits, and local changes sufficiently to reconstruct the source. Before rewriting local commits or reconstructing overlapping edits, retain the original commits through a named ref and preserve staged, unstaged, and untracked content in an appropriate snapshot. Preserve their distinction when it matters to the request. Use isolated worktrees when they let you assemble deliveries without disturbing ongoing work.

This step is complete when every in-scope change has been read and the original work is recoverable. Authorization to split work covers the requested local commits or branches; rewriting shared history and pushing require authorization for those actions.

## Choose delivery units

Group by behavior or purpose, following related changes across files and within individual files. Include the tests, configuration, generated files, and documentation that make each unit coherent. File boundaries and existing commit boundaries are evidence, not mandatory split boundaries.

Identify prerequisites before choosing topology:

- **Sequential commits:** order prerequisites before the changes that use them.
- **Independent branches:** construct each from the agreed base, containing only its own change and any explicitly included prerequisite.
- **Dependent branches:** make the prerequisite branch the base of its dependent branch and state the adoption order.

Use the user's requested shipping order. If independence requires a small adaptation, preserve behavior and explain it; if it requires substantive new implementation, surface that decision before expanding the task. Shared prerequisites should have a clear home rather than appearing accidentally in every branch.

Show a concise map of units, bases, and dependencies before mutation; continue under the authorization already given. Ask only when an unresolved choice changes what the user can ship or would require an unauthorized action.

This step is complete when every in-scope change belongs to a unit or an explicitly retained remainder, and dependencies match the requested adoption model.

## Assemble the split

Stage or apply selected hunks and files deliberately. For overlapping edits in one file, reconstruct the intended intermediate versions or use selective patches; whole-file staging can combine unrelated work. Review the staged diff immediately before each commit, including staged content that predates this task.

Create the requested commits or branches with messages describing their behavior and purpose. Keep unrelated work outside the delivery units. Resolve conflicts according to the intended final behavior and validate the resolved content. Preserve original refs and snapshots until reconciliation is complete.

## Validate and reconcile

Run repository checks appropriate to the changed behavior. Validate each unit at the state where the user is meant to adopt it: an independent branch from its base, or a dependent branch with its declared prerequisites. A passing combined tip does not establish that a standalone delivery works.

Compare the combined result against the original change set. Account for every original hunk and relevant new file; inspect any differences introduced during reconstruction. When topology differs, compare resulting trees or content in an isolated integration workspace rather than relying on commit counts. Explain intentional adaptations and retained remainders.

Finish when the requested units exist, their dependencies and checks are known, the combined result preserves the intended work, and remaining local changes are accounted for. Report branch names, commit IDs, bases, adoption order, and material validation limits. Include remote or PR links only when those deliveries were requested and completed.
