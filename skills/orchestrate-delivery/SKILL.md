---
name: orchestrate-delivery
description: Orchestrate multi-agent delivery with GPT-6 Astra Medium direction and GPT-6.1 Sol High execution. Use when the user wants an agent team to deliver a task, or substantial work needs coordinated delegation.
---

# Orchestrate Delivery

Give the user control over intent, constraints, and success criteria; give agents ownership of completing the work. The director manages commitments and acceptance, while executors own implementation and routine validation.

## Establish the director

Use **GPT-6 Astra Medium** for the director and **GPT-6.1 Sol High** for executors, including investigators and independent verifiers. A skill cannot change the current model.

The current agent must be confirmed as GPT-6 Astra with medium reasoning effort before beginning orchestration. If it is using another model or effort, or its configuration is unknown, stop and ask the user to select GPT-6 Astra Medium and invoke the skill again. Do not create a replacement director. Once confirmed, the current agent directs the work and communicates with the user directly.

Use the user's chosen runtime. Otherwise use Codex built-in collaboration when available. Read only the matching runtime guide: [Codex built-in](references/codex-builtin.md) or [Herdr](references/herdr.md). The guide supplies the launch, communication, and wait mechanics; the workflow below is shared. When the selected runtime cannot provide the required models, effort settings, or delegation, explain the limitation and ask the user to choose a supported arrangement before proceeding. Do not silently switch runtimes or claim a model switch. A role assignment grants no additional filesystem, external-action, or cross-chat permissions.

## Confirm the direction

Before implementation, read and apply [grilling-focused](../grilling-focused/SKILL.md), including its required `grilling` base. If the relative location is unavailable, find `grilling-focused` in the available skill catalog; report a missing dependency instead of inventing a replacement interview.

Carry forward already confirmed decisions. Build the focused design tree only from unresolved choices that need user judgment and could materially change the goal, scope, core approach, or acceptance criteria. Investigators establish facts; executors decide local, reversible implementation details. While direction is unresolved, discovery can supply evidence for decisions, but implementation waits for its scope to be confirmed.

Follow the focused/base interview's frontier and completion rules. Summarize the resulting direction and obtain confirmation before executing a newly agreed scope. An existing confirmation covering the current scope remains valid; unanswered questions and elapsed time are not confirmation.

## Delegate commitments

The director owns task decomposition, shared interfaces, consequential tradeoffs, and final acceptance. Choose roles and concurrency to fit the work; a developer can investigate and test its own change. Add an independent verifier when behavioral uncertainty or the cost of a mistake justifies a separate perspective. Small tasks need no ceremonial team of three.

Give each executor a brief containing:

- **Outcome and authority:** confirmed intent, constraints, acceptance criteria, and decisions already settled. Identify what it can decide and which changes require escalation.
- **Context and access:** relevant source/artifact paths, applicable instructions or skills, current state, dependencies, and available tools/resources. Provide essential content when the recipient cannot access a reference. Omit unrelated conversation history.
- **Ownership and coordination:** files or modules it may write, shared interface commitments, dependent work, and peer agent IDs. Allocate one active writer for shared files; serialize changes or explicitly transfer ownership when work overlaps. Agents share a workspace unless an isolated checkout is actually supplied.
- **Return contract:** the usable deliverable, caller-relevant interface and semantics, and acceptance evidence or unresolved gaps. State where to return results and how to reach collaborators. Wire peers together using the agent IDs returned by the tools; send missing IDs once those agents exist.

Describe outcomes and constraints, not a sequence of edits for an executor to follow. Executors own implementation, debugging, and appropriate routine tests. They may adjust reversible details within their contract and complete the assigned work without reporting every step. Further delegation should have a concrete benefit and respect the available slots and ownership agreements.

At handoff, developers return the implemented interface and the semantics callers need: relevant invariants, lifecycle, failure behavior, and integration instructions. Include paths or symbols and meaningful validation results. Explain a change to a promised interface before dependent work relies on it.

## Close defects with evidence

When using an independent verifier, give it the confirmed acceptance criteria, executable resources, and the delivered interface. Have it exercise behavior independently and return an acceptance verdict with traceable evidence and remaining gaps. Developer claims are context, not proof. Evidence should identify the artifact or revision checked, the check or reproduction, and its result; raw logs remain available by reference when useful.

Connect verifier and developer directly through the available agent messaging tools. Reproducible defects within the agreed contract go to the developer; the developer fixes them and returns the changed behavior and evidence; the verifier checks the affected acceptance criteria. The verifier reports completion or an unresolved blocker to the director rather than routing each correction through it.

Escalate changes to the agreed goal, scope, shared/public interface, or authorization, and conflicting evidence that needs a decision. Include the failed commitment, relevant evidence, consequence, and a recommended next step. The director resolves tradeoffs within its authority and returns to the user for changes requiring user judgment or permission. A runtime failure or uncertain implementation detail alone belongs in the executor's investigation loop.

Use completion notifications or bounded agent waits. Investigate status when a dependency is blocked or intervention could help; avoid turning routine progress into repeated polling and summaries. Keep the user informed of meaningful findings, decisions, and remaining uncertainty.

## Accept and deliver

The director checks the key commitments against the delivered interface and acceptance evidence, including integration between workstreams. Drill into source or rerun checks when a concrete discrepancy, missing evidence, or integration risk warrants it; routine acceptance does not require rereading every implementation or repeating all tests.

Accept when the confirmed criteria are supported and material gaps are resolved or explicitly accepted by the user. Report what was delivered, how to use its interface or entry point, what the evidence establishes, and any remaining limits. Keep implementation logs and internal coordination out of the user's delivery summary.
