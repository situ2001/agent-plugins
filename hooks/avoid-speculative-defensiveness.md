## Avoid Speculative Defensiveness

Do not add guards, fallbacks, retries, compatibility paths,
version checks, arbitrary limits, or recovery logic merely
because a failure is theoretically imaginable.

Trust established internal invariants and framework contracts.
Use assertions or fail-fast behavior when an invariant violation
would indicate a programming error; do not silently recover from it.

Defensive handling is justified when there is a concrete source:
- an external or untrusted boundary;
- an explicit requirement;
- a documented platform/API behavior;
- an observed failure or regression.

Do not invent restrictions such as maximum page counts, step counts,
file sizes, supported versions, or timeouts without such a source.

When debugging, first check whether an existing guard, fallback,
validation rule, or self-imposed restriction is causing the failure
before adding another layer around it.
