---
name: agent-team
description: Orchestrate multi-agent delivery with GPT-6 Astra Medium direction and GPT-6.1 Sol High execution when explicitly invoked by the user.
---

# Agent Team

Give the user control over intent, constraints, and success criteria; give agents ownership of completing the work. Treat the main agent as the **director**: reserve its attention for the big picture, direction, consequential decisions, and acceptance. Delegate concrete execution as fully as practical; the director need not perform hands-on work to own the outcome.

## Establish the director

Prefer **GPT-6 Astra Medium** for the director. The current agent directs the work and communicates with the user directly, without checking its model or requiring a model switch. Default to **GPT-6.1 Sol High** for Codex executors, including investigators and independent verifiers. Honor an explicitly requested agent CLI or model; Claude Code uses its configured model unless the user specifies one.

Use the user's explicitly chosen runtime. For `auto`, or when none is specified, choose Herdr when `HERDR_ENV=1` and the `herdr` CLI is available; otherwise choose Codex built-in collaboration. Report the selected runtime briefly. Read only the matching runtime guide: [Codex built-in](references/codex-builtin.md) or [Herdr](references/herdr.md). The guide supplies the launch, communication, wait, and cleanup mechanics; the workflow below is shared. Launch CLI executors with automatic approval review as described there. When the selected runtime cannot provide the required models, effort settings, or delegation, explain the limitation and ask the user to choose a supported arrangement before proceeding. Do not silently switch runtimes or claim a model switch. A role assignment grants no additional filesystem, external-action, or cross-chat permissions.

## Confirm the direction

Before implementation, read and apply [grilling-focused](../grilling-focused/SKILL.md), including its required `grilling` base. If the relative location is unavailable, find `grilling-focused` in the available skill catalog; report a missing dependency instead of inventing a replacement interview.

Carry forward already confirmed decisions. Build the focused design tree only from unresolved choices that need user judgment and could materially change the goal, scope, core approach, or acceptance criteria. Investigators establish facts; executors decide local, reversible implementation details. While direction is unresolved, discovery can supply evidence for decisions, but implementation waits for its scope to be confirmed.

Follow the focused/base interview's frontier and completion rules. Summarize the resulting direction and obtain confirmation before executing a newly agreed scope. An existing confirmation covering the current scope remains valid; unanswered questions and elapsed time are not confirmation.

## Delegate commitments

The director owns task decomposition, shared interfaces, consequential tradeoffs, and final acceptance. Delegate investigation, implementation, debugging, routine validation, and integration work to executors by default. Use their findings to refine the plan, resolve dependencies, and give guidance. When work stalls, clarify the commitment, supply missing context, or reassign it so execution stays with an executor.

Choose roles and concurrency to fit the work; a developer can investigate and test its own change. Add an independent verifier when behavioral uncertainty or the cost of a mistake justifies a separate perspective. A small task can use one executor while the main agent remains the director.

Run independent workstreams in parallel when dependencies, write ownership, and available agent slots allow it. Launch ready work before waiting for results; wait when dependent work or acceptance needs those results.

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

Use completion notifications or runtime-appropriate agent waits. Investigate status when a dependency is blocked or intervention could help; avoid turning routine progress into repeated polling and summaries. Keep the user informed of meaningful findings, decisions, and remaining uncertainty.

For a Codex director using Herdr with no independent work left while a delegated result is pending, read [interrupt, wait, and continue](references/codex-herdr-wait.md) before handing the wait to an independent controller.

## Accept and deliver

The director checks the key commitments against the delivered interface and acceptance evidence, including integration between workstreams. When a concrete discrepancy, missing evidence, or integration risk needs investigation or another check, delegate that follow-up and assess the returned evidence. Inspect source directly only when needed for a specific director-level decision; routine acceptance relies on the delivered evidence.

For Herdr, preserve the accepted results and complete the runtime guide's executor cleanup before final delivery or handoff, unless the user asks to keep executors available.

Accept when the confirmed criteria are supported and material gaps are resolved or explicitly accepted by the user. Report what was delivered, how to use its interface or entry point, what the evidence establishes, and any remaining limits. Keep implementation logs and internal coordination out of the user's delivery summary.
