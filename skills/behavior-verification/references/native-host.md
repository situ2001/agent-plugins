# Native source on a compatible host

For iOS/macOS source, first consider a focused macOS compile-and-run check. Many behaviors can be exercised locally even when the full iOS app cannot build or launch: compile the original files and keep the system APIs relevant to the question real. Choose an iOS simulator or device when the result depends on iOS-only APIs, app lifecycle, entitlements, or platform configuration that the macOS check cannot preserve.

## Keep the source real

- Trace the path from the app entry to the subsystem. State which link the host check starts at, and which earlier links it leaves unverified.
- Compile the original source file where possible. If its imports pull in unavailable UI dependencies, copy the file unchanged into a uniquely named temporary build directory and supply small headers or implementations for the collaborators outside the question. Compare the copy with the selected revision using a hash or byte comparison before and after the run.
- Keep the framework or system API under investigation real. Replace only collaborators outside the disputed path, such as a UI adapter, logger, or configuration provider; replacing the operation under test would erase the question.
- If compilation needs a scratch edit to the source body, verify and disclose the exact edit. Narrow the claim to the behavior still preserved. Stop and use the supported platform when shims begin recreating the subsystem.

## Ask a question the host can answer

Choose a baseline and a nearby variation that would produce different outcomes if the proposed mechanism is real. Change one consequential input or condition at a time, and keep the other relevant configuration observable. Derive expected results from the requirement, protocol, or reported behavior; label exploratory checks as characterization.

Observe the behavior through the host's own result, callback, metric, or side effect. A successful final value may have several causes, so measure the disputed mechanism directly when the platform exposes it. Use a real permitted service when its behavior is part of the question; otherwise use a controlled boundary with contract-faithful responses. Bound asynchronous waits and make mismatches fail the process.

Report the original-source hash or revision, compiler and linked system frameworks, substituted boundaries, inputs, observed results, and the earliest untested app or device link. A compatible-host pass demonstrates the shared subsystem under that host's OS and configuration; confirm device behavior separately when platform differences could change the result.

## iOS and macOS hints

- Objective-C files can often be built and run in a scratch macOS target with `clang`, ARC and blocks flags, and the Apple frameworks they actually use. Swift files can use `swiftc`. Start with the source and its reachable dependencies rather than requiring an entire Xcode app target. Check API availability and conditional compilation before treating the result as equivalent to the iOS target.
- Keep the platform framework relevant to the question real. Use small declarations or adapters to satisfy unrelated UIKit or WebKit references, and record what those substitutions exclude. Use an iOS simulator or device when the actual UIKit, WebKit, app lifecycle, or entitlements decide the outcome.
- Native APIs may create files relative to the working directory or persist state between runs. Run from an owned scratch directory, isolate initial state, and inspect generated artifacts before cleanup.

Remove only owned artifacts after the native runtime releases them. Keep production source, manifests, and lockfiles untouched for a one-off check.
