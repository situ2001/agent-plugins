---
name: frontend-demo-preview
description: Add or remove temporary frontend demo modes, with local data and preview behavior centralized in a removable Demo module.
---

# Frontend Demo Preview

Use this skill for temporary frontend previews that work without authentication, client-host APIs, or live backend data, and for removing their demo code before delivery.

## Core outcome

Render the real page and component tree with an explicit switch (usually `?demo=1`). Centralize the switch, fixtures, and preview functions in a project-local Demo module, then explicitly import it at the few integration points that need it. Those references make later removal discoverable. The demo path is for visual and interaction preview, not authorization simulation or production behavior.

## Add a demo

1. Locate bootstrap and effects in the page, its imports, hooks, and child components: requests, login, bridge setup, timers, analytics, and media. Account for effects that run during module import; a guard added after importing App cannot undo them.
2. Create a module such as `demo.ts`, exposing a named `Demo` object with the switch, typed data or fixture factories, and preview functions. Prefer a plain module; use a class when simulation needs state, reset, or disposal. Keep module import inert apart from reading the switch; create fixtures and resources when the demo branch runs.
3. Import `Demo` explicitly where needed. Prefer namespaced uses such as `Demo.enabled`, `Demo.getReportData()`, and `Demo.previewShare(image)` over copied flags, globals, or hidden registration. Put temporary logic in small, clearly removable branches near initialization and action boundaries.
4. Inject data through the existing state boundary: an apply-data function, store seed, provider, or component props. Keep fixtures and preview implementations in the Demo module; any necessary demo-only prop/action should have an explicit demo name and a traceable call site. For layout previews, skip live initialization. For workflow previews, provide local service behavior with finite, resettable response sequences.
5. Gate production integrations before they execute, including nested effects and login error paths. Demo clicks use local behavior or clearly labeled unavailable results, never production writes. Handle client-only guards before the action as well as the action itself. Keep sharing previews in the Demo module, for example a dismissible layer showing the generated PNG, with cleanup for temporary listeners, timers, and DOM.

Prefer branches that leave the production path intact and can be deleted together:

```ts
import { Demo } from "./demo";

async function initPage() {
  if (Demo.enabled) {
    applyReportData(Demo.getReportData());
    return;
  }
  // Existing production initialization follows.
}
```

For this temporary workflow, a Demo module and a few explicit imports are the default. Reuse established preview infrastructure when appropriate; introduce a permanent dependency-injection architecture or separate build only when the requested scope benefits from it.

## Reversibility and code boundaries

- Make each temporary behavior traceable to the Demo module. Avoid unmarked changes to production defaults, ownership rules, or component behavior merely to improve a preview; those changes survive deletion without a type error.
- Preserve production request contracts and authorization. Keep the module within the project's ownership boundary; avoid changes to shared libraries for a single page.
- Use named, typed fixtures for relevant populated, empty, loading, long-text, or failure scenarios. Prefer existing response/state/props types over `any` or unchecked assertions. Keep times, random choices, and assets repeatable where screenshots need stability.
- Keep secrets, real user data, access tokens, and production identifiers out of fixtures.

## Remove a demo

1. Establish the requested scope, including the actual diff base when one is supplied. Identify the Demo module, its imports, supporting assets, and demo-only props/actions; preserve pre-existing demos outside that scope.
2. Delete the scoped Demo module, then remove its imports. Deleting only the module may report an unresolved import without identifying every use; removing the imports exposes remaining `Demo` identifiers to type checking.
3. Run the repository's type check and use reference search to locate remaining integration points. Remove complete demo branches, supporting props/actions, and unused assets. For mixed conditions, retain the production terms: `Demo.enabled || isShareView` becomes `isShareView`. Do not silence cleanup errors with `any`, ignore comments, or replacement stubs.
4. Inspect the diff for changes that type errors cannot detect: altered defaults, inline fixtures, magic query flags, skipped effects, and preview DOM/styles. Type errors are a cleanup aid, not a complete inventory or proof of restored behavior.

## Verification

After adding, verify that the demo uses local data and safe preview actions, while the page without the flag retains its normal initialization. After removal, verify that scoped demo references and behavior are gone and production paths remain intact. Run the repository's type check/lint commands and inspect the diff in either case. Reference search is also required for JavaScript or files outside the type check's coverage. Respect repository restrictions on starting a dev server and report code-level verification limits when runtime verification is unavailable.
