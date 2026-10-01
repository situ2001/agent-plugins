---
name: grilling-focused
description: Use grilling to ask only the key questions that could change a plan's direction, then summarize for user confirmation. Use when the user wants a focused interview about consequential decisions.
---

# Grilling Focused

Find and read the available `grilling` skill as the base methodology. If it is unavailable, report that this skill requires `grilling` and stop the interview.

Apply `grilling` to the user's current task with a scoped **design tree**: include only unresolved decisions that require the user's judgment and whose plausible answers would materially change the goal, deliverable scope, core approach, or acceptance criteria.

For each candidate question, identify which downstream decisions or work would change with the answer. This consequence determines whether it belongs in the tree, regardless of its depth. Resolve facts through investigation; leave local, easily reversible implementation decisions to agent judgment.

Apply the full base methodology to this scoped tree, including its dependency, frontier, recommendation, and completion rules.

When the agent provides an available question tool, such as `AskUserQuestion` or `request_user_input`, prefer it where its usage rules permit. Offer recommended choices and allow free-text answers. Otherwise, use `grilling`'s chat question format. Use the same tool preference for the final confirmation when permitted; an unanswered question is not confirmation.
