# Browser checks and E2E

Use a real browser when the uncertainty depends on browser behavior: layout, focus, scroll, navigation, hydration, browser APIs, or a complete user journey. Playwright is one option; use the available browser tool according to its own API and permissions. A failed automation setup is not an application failure.

## Choose the real entry and scope

Prefer the existing focused browser test, then an already running authorized application, then a temporary entry that imports the actual component and its relevant CSS/providers. Use the project's supported build transforms. `page.setContent` containing a manually recreated UI does not verify the implementation. A component-only entry cannot establish that the real route, initialization, or parent wiring works.

Inspect available runner/browser versions and launch support before building a harness. Respect repository instructions about servers; use an existing environment or report the boundary when startup is disallowed. When allowed, keep any temporary server local, wait for readiness with a timeout, record its process, and stop only processes the check owns. Leave project dependencies and configuration unchanged solely for convenience.

Identify the intended evidence:

- **Browser component check:** actual component in a temporary page; app routing and startup may be absent.
- **Browser integration with fixtures:** actual application flow with named external boundaries replaced.
- **E2E:** user actions through the real application and stated real services/host in an authorized test environment. Specify any remaining substitutions.

Choose the least expensive scope that can answer the question. A request mock can validate frontend behavior without invoking a real payment, message, or destructive operation. Verification alone does not authorize those effects. A Web browser does not replace a Hippy/native host.

## Establish deterministic boundaries

Start with a fresh browser context and explicit route, storage/auth state, viewport, and fixture data as relevant. Ensure the served build contains the source being checked; an old server or deployment can silently test another revision.

Install request interception before navigation or the triggering action. Match consequential URL, method, and body; record/assert them before returning a response. Keep fixtures faithful to the relevant protocol and empty/error shapes. Allow known app assets and expose unexpected application API calls rather than returning success for every URL. Account for caches or service workers if they bypass interception. Requests originating in an SSR server require a server-side fixture boundary; page routing does not intercept them.

When order matters, hold and release responses explicitly. Use an actual app action to trigger the request; injecting the desired DOM or directly setting the expected state would bypass the behavior.

## Act and assert

Use accessible roles, labels, or stable existing selectors to exercise the interface. Assert the initial state, perform the user's action, and await a specific observable result. For example, in an existing Playwright test with an actual `appUrl` and fixture setup:

```js
await page.goto(appUrl);
await expect(page.getByRole('button', { name: 'Retry' })).toBeVisible();
await page.getByRole('button', { name: 'Retry' }).click();
await expect(page.getByRole('status')).toHaveText('Saved');
```

Adapt the assertion to the requirement: navigation destination and preserved parameters, button enabled state, focus target, rendered content, request count, or geometry. For hydration, wait for and use a real client interaction; receiving SSR HTML alone does not prove hydration worked. For a layout defect, assert the relevant bounds/overflow or inspect a screenshot at the relevant viewport with assets/fonts ready. A screenshot alone is not an interaction assertion.

Use bounded locator assertions or event/response waits. Register event waits before actions that could fire them immediately. `networkidle` is not a reliable readiness signal for polling apps, and fixed sleeps make timing cases fragile. Disable retries while establishing a deterministic reproduction; investigate a first failure rather than treating a retry pass as proof.

For browser-generated errors or events, trigger the actual producer when generation or scheduling is the uncertainty. Dispatching a synthetic event tests its consumers only. Install listeners before the trigger and retain the relevant error payload; callback invocation alone bypasses event registration and propagation.

Capture relevant page errors and failed requests. On failure retain a useful screenshot, trace, or concise DOM/request evidence, avoiding credentials in shared artifacts. Distinguish launch failures, missing fixtures, and stale builds from failed business assertions. Run the same flow on the original version when available to establish the negative control.

## Finish

Close owned contexts/browsers and temporary servers in cleanup paths even after an assertion fails. With a shared browser connection, close only what the check created. Report the actual entry/build, browser and relevant viewport, actions/assertions, result, mocked boundaries, and material missing integrations. A fixture-driven flow should be reported as such even if its test file lives in an `e2e` directory.
