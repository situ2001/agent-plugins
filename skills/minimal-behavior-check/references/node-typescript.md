# Node / TypeScript checks without a project test runner

Use this recipe when a small TS/TSX module cannot be loaded through the project's normal runtime. Prefer a direct import when an existing runner already supports it.

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
- For TSX static rendering, use the project's JSX convention and the same React instance for both the component and renderer. CSS/asset stubs are acceptable for a markup assertion, but invalidate claims about their real loading or appearance.
- If an imported module contains the logic being checked, load that real module through a suitable runner. Stubbing it would erase the behavior under investigation. Several nested TS imports are usually a reason to use the project's loader rather than grow this recipe into a bundler.
- Values created in a `vm` context have different prototypes. Prefer assertions on observable primitive fields. For JSON-shaped output, deliberate serialization can normalize realms, but loses values such as `undefined` and cannot validate prototype-sensitive behavior.
- Await promise-returning functions in an async entrypoint and set `process.exitCode = 1` on rejection. The `vm` timeout above limits synchronous module evaluation only; it does not bound later exported calls, pending promises, or external effects.
- `vm` isolates globals; it is not a security sandbox. Evaluate trusted local source, inspect initialization effects, and keep live network calls or client mutations outside the check.
