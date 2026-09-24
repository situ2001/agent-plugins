# Native source on a compatible host

Use this route when the disputed behavior lives in a native source file but its decisive APIs also exist on the available host. An iOS networking class using Foundation can, for example, be checked on macOS without launching the app. Choose an iOS device or simulator when the disputed behavior depends on WebView interception, app configuration, or another device-only link.

## Keep the source real

- Trace the path from the app entry to the subsystem. State which link the host check starts at, and which earlier links it leaves unverified.
- Compile the original source file where possible. If its imports pull in unavailable UI dependencies, copy the file unchanged into a uniquely named temporary build directory and supply small headers or implementations for the collaborators outside the question. Compare the copy with the selected revision using a hash or byte comparison before and after the run.
- Keep the framework or system API under investigation real. A replacement WebView task wrapper, logger, or capacity provider can record calls or supply setup values; a replacement network task, cache, transport, scheduler, or persistence layer would erase a question about that layer.
- If compilation needs a scratch edit to the source body, verify and disclose the exact edit. Narrow the claim to the behavior still preserved. Stop and use the supported platform when shims begin recreating the subsystem.

## Ask a question the host can answer

Choose inputs that distinguish the proposed mechanism: for a cache, an uncached resource, the same request repeated, a request with a changed key, and a request with an explicit reload policy. Keep the relevant headers, policy, and URL identity observable. Use a real permitted endpoint when its response contract matters, or a controlled local server that serves faithful headers when repeatability matters; identify which one supplied the response.

Assert the source of the result rather than inferring it from a successful response or missing packet. Use platform metrics or an equivalent system signal when available, alongside status and payload checks. For example, `URLSessionTaskMetrics.resourceFetchType` distinguishes a network load from a local-cache load even when both complete with HTTP 200. Bound asynchronous completion waits and fail the process if the expected source differs.

Compare a baseline with a nearby control that would break the hypothesis. Report the original-source hash or revision, compiler and linked system frameworks, substituted boundaries, inputs, observed results, and the earliest untested app or device link. A compatible-host pass demonstrates the shared subsystem under that host's OS and configuration; confirm device behavior separately when OS version, WebView, app settings, or persistent device state could change the result.

Build and run from an owned scratch directory when the source creates relative cache or database paths. Inspect generated files and remove only owned artifacts after the session has released them. Keep production source, manifests, and lockfiles untouched for a one-off check.
