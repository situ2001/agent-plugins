# React hooks and component behavior

Use a mounted React runtime when the question involves state, effects, callbacks, or cleanup. Static rendering does not run effects. Calling a function component directly or replacing `useState`, `useEffect`, or `useRef` with homemade implementations removes the lifecycle you need to observe.

## Load the real component

Prefer the project's existing React Testing Library, hook harness, or supported component runner. Inspect the application's actual React version and renderer, especially in monorepos where the root dependency can be older than the app runtime. Component, hooks, JSX runtime, and renderer must resolve to the same compatible React instance. An existing compatible `react-test-renderer` can serve legacy projects; it is not a universal default for new React projects.

If isolated dependencies are necessary, keep versions compatible with the app and resolve all React imports through the same dependency root. For TSX, preserve the project's JSX convention; use the [Node recipe](node-typescript.md) only when its limited loader is sufficient. Keep actual reducers, stores, hooks, and child components whose behavior is part of the question.

A native `View` replaced with an inert host tag can expose props and handlers to a renderer. This verifies handler/state behavior, not touch delivery, scrolling, layout, or the native bridge. Likewise, capturing a child's props verifies the parent contract; checking the child's payment behavior requires mounting that real child in the relevant check.

## Drive transitions, not just initial state

Mount with the providers/context that matter. Use the runner's `act`, user-event utilities, and bounded async assertions to let React commit updates. For a hook without a hook runner, a tiny host component can call the real hook and expose its committed result. Read fresh output after each update rather than retaining an obsolete render's closure, unless a stale callback is the scenario under test.

Choose sequences relevant to the change, such as:

- Mount with existing data → refresh returns zero, empty, or an error → observe the required resulting state.
- Start request A → change selection → start B → resolve B then A → verify A cannot overwrite B.
- Begin an action → invoke it again while pending → resolve or reject → verify count, retry, and resulting UI.
- Begin an action → change props → deliver a callback twice → verify the required input snapshot and single effect.
- Mount → subscribe → trigger the relevant event → unmount → verify subscription cleanup and, if relevant, that a late response causes no external effect.

Use controlled promises to make race cases deterministic. This helper controls a boundary response; it does not implement the component's cancellation policy:

```js
function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}
```

For duplicate-click protection, keep the first action pending while issuing the second. Awaiting the first action to completion before the second tests sequential actions instead. For timer-driven behavior, advance the existing fake clock with the renderer's supported update mechanism; changing every timeout into an immediate callback erases debounce and ordering semantics. An inert animation-frame callback excludes frame-driven behavior from the evidence.

## Make fixtures sensitive to the contract

Record request arguments and consequential call counts, as well as output state. Provide responses that distinguish valid and invalid requests where needed. A fixture that ignores a balance mask or always supplies a complete price map can make a broken caller pass.

Include the reported data shape: for example, a list entry with no price followed by a detail response, rather than only a convenient fully populated object. Assert the required empty/error/retry behavior without recreating the backend. A mocked service is evidence about the caller under that contract; it cannot prove the real service implements it.

Reset state between cases: unmount components, create fresh stores and fixtures, and restore timers/subscriptions. Keep unexpected React errors visible; suppress only a specific expected diagnostic when the scenario requires it. For Strict Mode issues, exercise the application's relevant mode rather than changing the mode to silence duplicate effects.

## Verify lifecycle and error paths

Keep the actual boundary and its subscription lifecycle when testing error handling. A mocked boundary that directly renders fallback would assume the result.

Use a success case to establish that the boundary still renders its children, and an applicable error case to establish fallback behavior. If retry is required, invoke it and drive recovery; inspecting the presence of a button is only a markup check. Keep fallback rendering and recovery behavior as separate claims.

Resolve framework, renderer, and test utilities from a compatible runtime. Initialize required DOM globals before importing modules that inspect them. Preserve the app's relevant development/production and Strict Mode semantics; record when the harness differs. React warnings about updates or cleanup may identify a broken harness or a real lifecycle issue, even when text assertions pass.

### Runtime-generated errors in DOM harnesses

A custom boundary may install global listeners in addition to React lifecycle handling. Simulated DOM environments may not generate browser `unhandledrejection` from Node promises. If needed, a scoped Node listener can forward the specific rejection into a DOM event carrying `promise` and `reason`; dispatch it on the actual registered target. Label this as simulated delivery: it does not verify browser generation, timing, cross-origin suppression, or host compatibility. Restore the listener afterward and expose unrelated rejections.

Development renderers may deliver the same error through both a global listener and a component boundary. Inspect both paths before attributing duplicate effects to production behavior. A synthetic event carrying a rejected promise may itself create an unhandled rejection; use a supported runner pattern or deliberately capture that specific promise.

## Know when to move to a browser

A handler invoked through renderer props bypasses disabled-element semantics, event propagation, focus, hit testing, and real navigation. If any of these is the question, use DOM interaction or the [browser recipe](browser-flows.md). A successful state transition is not evidence that the control is visible or reachable on screen.
