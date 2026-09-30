---
name: show-me-the-architecture
description: Explain the architecture of an existing repository or subsystem through source-backed responsibility maps, real call paths, data flow, and state ownership. Use for architecture walkthroughs and shareable diagrams or HTML, rather than refactoring proposals or an ongoing course.
---

# Show Me the Architecture

Give developers a navigable explanation of how the existing system works. Organize it around responsibilities and representative behavior, with source entry points they can follow.

## Establish the scope

Use the requested repository, subsystem, questions, audience, and output format. For a broad request, start with the system map and select representative paths that explain its main boundaries. For a focused question, trace that behavior before widening the map.

Read repository guidance, relevant manifests, domain terminology, and existing architecture documents or ADRs. Record the source revision and relevant working-tree changes. Treat documents as orientation and evidence of stated intent; verify current implementation in source.

This step is complete when the explanation's scope, source state, and questions are explicit. A request to explain architecture authorizes investigation and the requested artifact; implementation changes belong to a separate request.

## Build the evidence

Find the actual entry points: executable startup, routes, exported APIs, framework registration, or extension contributions. Follow registrations and callers into the responsible modules. Distinguish a module that exists from one wired into the selected application.

For the paths that carry the explanation, establish:

- What starts the operation and which entry receives it.
- Which modules coordinate the work and which perform it.
- What data crosses each consequential boundary, including protocols and persistence where relevant.
- Who owns mutable state, who can change it, and how consumers learn about changes.
- What result or effect reaches the caller or user.

Verify dynamic dispatch, generated bindings, feature flags, or alternate frontends when they change the selected path. Static source can establish wiring; use a focused runtime observation when a material claim depends on execution and remains unresolved.

Keep source anchors for consequential relationships, not just a list of filenames. A dependency declaration establishes availability, not a runtime call. Use concrete operations to explain state management or UI/core separation rather than assigning a familiar pattern from superficial similarity.

This step is complete when the selected paths connect real entries to their observable outcomes and each consequential edge has supporting evidence. Identify unresolved edges explicitly instead of filling them with a plausible design.

## Explain the system

Lead with the system's purpose and responsibility map. Connect the map to real paths so readers can see how the parts cooperate. Choose the views that answer the request: a module map, call sequence, data flow, state transitions, or deployment boundaries. Keep module dependencies, runtime calls, and data flow distinguishable in diagrams.

Separate three kinds of statement:

- **Implementation facts:** supported by source or observed execution.
- **Responsibility summaries:** your synthesis of those facts.
- **Design intent:** attributed to an ADR, documentation, or other explicit evidence; otherwise label it as interpretation.

For a user's proposed architectural model, confirm supported relationships and correct mismatches with source. Analogies can explain a mechanism, but name the concrete correspondence and where the analogy stops. Claims about maintainability or AI navigability need specific examples of locality, interfaces, or change paths, rather than an inferred quality score.

Attach useful file/symbol anchors to the explanation. Identify the source revision for durable or shared artifacts; use revision links when available. Match depth and format to the audience. An explanation need not create a learning workspace or a refactoring plan.

## Deliver and verify

For Markdown or chat, check that source links and diagrams agree with the traced paths. For HTML, provide readable navigation and source references, inspect the rendered result, and exercise any controls used to reveal architectural content. Use the requested destination; when none is specified, choose a suitable artifact location and provide its path. Explain external rendering dependencies when they affect sharing or offline use.

Finish when the requested questions are answered, the artifact is readable in its target format, and readers have concrete entries for further investigation. Report material verification limits alongside the affected claims.
