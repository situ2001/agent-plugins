---
name: frontend-demo-preview
description: Add a reversible, fixture-driven demo mode to frontend pages so UI can be previewed without login, client bridges, or backend services.
---

# Frontend Demo Preview

Use this skill when a frontend page needs a local visual/demo path that must work without authentication, client-host APIs, or live backend data.

## Core outcome

Add an explicit demo switch (usually `?demo=1`) that renders the real page and component tree with local fixtures while isolating or disabling production integrations. The demo path is for visual and interaction preview, not authorization simulation or production behavior.

## Workflow

1. Locate the page bootstrap and all first-load side effects. Identify API dispatches, login/silence-login calls, bridge setup, timers, analytics, media, and route-specific initialization.
2. Gate real side effects at the earliest safe boundary. In demo mode, do not dispatch live requests, trigger login, initialize client-only flows, or start polling/retry loops. Keep the normal path unchanged.
3. Inject fixtures through the page's existing state boundary (Redux action/store seed, provider value, hook adapter, or component props). Prefer the same production components and selectors over a parallel demo page.
4. Make fixtures representative enough to exercise the intended layout: populated, empty, loading, long-text, and error-sensitive fields where useful. Keep them local, named, and typed; avoid copying opaque production payloads.
5. Neutralize demo-only mutations and integrations. Buttons may remain visible for layout checks, but their handlers should be safe no-ops, local state changes, or a clearly labeled preview action. Never let a demo click write to production services.
6. For generated images or share flows, provide a reversible local preview (for example, a popup layer showing the generated PNG) instead of invoking a native share bridge or downloading by default.

## Reversibility and code boundaries

- Keep the demo switch and fixture injection near the bootstrap/state boundary; do not scatter `demo` checks through business components unless necessary.
- Isolate fixtures in a dedicated constant/module and use a small demo-only reducer/action or provider override.
- Preserve production defaults, request contracts, and component APIs. Do not weaken backend authorization or infer ownership from demo state.
- Prefer additive changes that can be removed as one block. Mark temporary code clearly and avoid changing shared libraries for a single page.
- Do not commit secrets, real user data, access tokens, or production identifiers into fixtures.

## Verification

Verify that `?demo=1` reaches the page without login or network calls, while the same page without the flag retains its original initialization. Run the repository's type check/lint command and inspect the diff for accidental production-path changes. If a development server is unavailable or unsuitable, report the code-level verification limits rather than inventing runtime results.
