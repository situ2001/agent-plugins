# Node / TypeScript checks without a project test runner

Use this recipe when a small TS/TSX module cannot be loaded through the project's normal runtime. Prefer a direct import when an existing runner already supports it. For effects or interactions, pair loading with the real runtime in [React behavior](react-behavior.md); transpilation alone does not run a component lifecycle.

## Resolve the runtime before building the loader

A saved script resolves bare packages from its own directory, not the shell's current directory. Use `createRequire` anchored at the repository or actual app dependency root for both package loading and plugin resolution. If the app uses nested or aliased dependencies, inspect the build configuration and resolve that runtime explicitly. Record the versions actually loaded. Merely finding a package in the root manifest does not establish compatibility.

For staged checks, obtain source through `execFileSync('git', ['show', ':' + relativePath], { cwd: repoRoot, encoding: 'utf8' })`; use `HEAD:` for the baseline. This preserves argument boundaries and avoids shell interpolation. If relevant imports also changed, load their matching snapshots or use an isolated checkout/export. Keep source filenames in transpilation and evaluation errors so failures identify the real module.

Prefer scoped loaders to process-wide `Module._load` or `require.extensions` changes. If the existing runner requires global hooks, save and restore them in cleanup, scope replacements to the intended importer as well as specifier where necessary, and account for module caching between variants. A relative import such as `../../api` can name different files in different modules.

## Loading pattern

Run from the target repository root. This inline example assumes the repository already has TypeScript installed. Adapt the source path, export, cases, and explicit stubs to the actual module; it is not a universal loader.

```js
// Run as: node <<'JS' ... JS, from the target repository root.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { createRequire } = require('node:module');

const sourcePath = path.resolve('src/buildItemUrl.ts');
const projectRequire = createRequire(path.resolve('package.json'));
const sourceRequire = createRequire(sourcePath);
const ts = projectRequire('typescript');
const source = fs.readFileSync(sourcePath, 'utf8');
const compiled = ts.transpileModule(source, {
  fileName: sourcePath,
  compilerOptions: {
    target: ts.ScriptTarget.ES2020,
    module: ts.ModuleKind.CommonJS,
    esModuleInterop: true
  }
}).outputText;

const stubs = new Map(); // Add only named, unrelated boundaries if needed.
const allowedRealImports = new Set(); // Explicitly allow inspected dependencies.
const moduleObject = { exports: {} };
vm.runInNewContext(compiled, {
  module: moduleObject,
  exports: moduleObject.exports,
  require(name) {
    if (stubs.has(name)) return stubs.get(name);
    if (allowedRealImports.has(name)) return sourceRequire(name);
    throw new Error(`Unexpected dependency in check: ${name}`);
  },
  URL,
  window: { location: { href: 'https://example.test/item?preview=1' } }
}, { filename: sourcePath, timeout: 1000 });

// Adapt to the actual exported API and requirements.
const { buildItemUrl } = moduleObject.exports;
const result = new URL(buildItemUrl({ itemId: 'example+a/b=' }));
assert.equal(result.searchParams.get('item'), 'example+a/b=');
assert.equal(result.searchParams.has('preview'), false);
console.log('PASS: item identity, encoding, and preview parameter removal');
```

## Adapt only what the question requires

- `transpileModule` emits JavaScript; it neither type-checks the project nor resolves path aliases, bundles assets, or reproduces framework transforms. Keep the project's actual compilation checks separate.
- `sourceRequire` resolves real dependencies relative to the source file. A helper saved under `/tmp` should resolve TypeScript and project packages through `createRequire` rooted in the repository rather than relying on `/tmp/node_modules`.
- For TSX, use the project's JSX convention and the same React instance for both the component and renderer, including `react/jsx-runtime` when used. CSS/asset stubs are acceptable for a markup assertion, but invalidate claims about their real loading or appearance. Inspect required build globals (such as `__DEV__`) and supply explicit values without swallowing runtime errors.
- If an imported module contains the logic being checked, load that real module through a suitable runner. Stubbing it would erase the behavior under investigation. Several nested TS imports are usually a reason to use the project's loader rather than grow this recipe into a bundler.
- Values created in a `vm` context have different prototypes. Prefer assertions on observable primitive fields. For JSON-shaped output, deliberate serialization can normalize realms, but loses values such as `undefined` and cannot validate prototype-sensitive behavior.
- Await promise-returning functions in an async entrypoint and set `process.exitCode = 1` on rejection. The `vm` timeout above limits synchronous module evaluation only; it does not bound later exported calls, pending promises, or external effects.
- `vm` isolates globals; it is not a security sandbox. Evaluate trusted local source, inspect initialization effects, and keep live network calls or client mutations outside the check.
- If configuration is embedded in source, prefer a supported configuration input. When a scratch-only replacement is necessary, assert the match count and resulting value before loading it; otherwise the check can silently exercise the wrong variant.

## Make unexpected behavior visible

A fixture used to replace an unrelated operation should record unexpected calls and fail the case after execution. Throwing alone may be insufficient: production code can catch that exception and render the very fallback being asserted. This is especially important in failure-path tests. Match the intended failure identity or payload, and assert that no unexpected operation supplied it.

Use small named fixtures and separate setup, action, assertions, and cleanup. Include a bounded case deadline when async code could hang. Run the exact saved command without relying on an inherited `NODE_PATH` or undocumented preload; document such environment requirements if intentionally retained. Write source snapshots to an owned directory and identify whether rerunning uses those frozen files or rereads current Git state.

## Complete asynchronous work and release resources

Await the async entrypoint and bound waits for observable results. `setImmediate` or a microtask flush does not establish that timers, I/O, and downstream promises have all completed. Virtual clocks may cover only part of that scheduler; use the runner's documented facilities for the work under test.

Restore listeners, globals, module-loader hooks, timers, and owned processes in `finally`. Prefer setting a nonzero failure status and allowing natural exit after cleanup. Forced successful termination can conceal leaked handles or unfinished assertions. If a runner requires forced termination, await assertions and cleanup first and report the limitation; an external timeout is a failure safeguard, not a successful result.
