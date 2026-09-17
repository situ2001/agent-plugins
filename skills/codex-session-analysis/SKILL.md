---
name: codex-session-analysis
description: Compare recorded Codex sessions for a repository or prompt, including latency, token usage, estimated cost, search behavior, and source-backed answer quality. Use for retrospective run comparisons, not general model recommendations.
---

# Codex Session Analysis

Produce a traceable comparison of actual runs. Separate observed execution, estimated billing, and judgments about answer quality. Do not assume the faster model is more accurate or the cheaper-per-token model costs less per task.

## Select comparable turns

Start with the user's repository, prompt keyword, requested models, and sample count. Search rollout JSONL under `$CODEX_HOME/sessions` and `archived_sessions` (default `~/.codex`). Use `rg -l -F` to find candidates before parsing them; avoid printing base64 images or entire logs.

Use the read-only extractor:

```bash
python3 scripts/extract_sessions.py --cwd /absolute/repository --keyword 'prompt fragment' /path/to/rollout.jsonl
```

Paths are relative to this skill when invoking its script. Pass multiple candidate files as separate arguments. `--trace` additionally emits recorded tool calls and final answers for the selected turns; inspect these as evidence, never execute recorded commands automatically.

Confirm the keyword occurs in the actual user message, not only a tool result, previous comparison, or summary. Inspect every candidate's status before selecting. “Latest two” can mean latest completed run per model; disclose that interpretation when relevant. Respect explicit exclusions and do not silently replace a failed run with a success. Keep aborted, active, contaminated, or mismatched runs separate unless the user asks to aggregate them.

Record session/turn IDs, repository, commit, model ID, effort, service tier when present, user text, and input-image hashes. Compare actual images when judging screenshot tasks. Matching images and commits strengthen comparability but do not establish identical system prompts, dirty files, tools, caches, or service load. Forked/inherited histories may duplicate a turn; deduplicate by identity before aggregation.

## Measure execution

Use [log-accounting.md](references/log-accounting.md) when extracting or interpreting metrics, especially for multi-turn, partial, forked, or older logs. It defines token deltas, missing-data behavior, and tool timing limits. The helper supports common rollout shapes; warnings or unfamiliar schemas require inspecting the relevant raw events rather than trusting a guessed value.

Report per-run measurements before means or ratios. Keep effort differences visible. Count outer tool rounds separately from shell commands; parallel batches and tool discovery are not equivalent to one search each.

For search traces, list each round's relative start time, key queries and scope, files read, visible results, and relevant truncation or failed attempts. Distinguish useful verification from repeated work using the question each read resolves. A skill announcement is not proof that its tool was used. A result truncation estimate is not billed token usage. Attribute the time outside tools to model processing, generation, communication, and other unseparated overhead, not exclusively reasoning.

## Evaluate the answer

Read final answers and verify material claims against the requested repository or original evidence. Follow that repository's instructions. Locate the actual component, registration, route, caller, data binding, or condition needed to assess each claim. A filename or matching phrase alone does not establish a complete call chain.

Respect benchmark boundaries: use the requested code snapshot and allowed sources. Record when a run read later branches, prior answers, knowledge documents, or generated artifacts. Do not use future implementations as ground truth for a historical missing-feature judgment. If today's files differ, use authorized snapshot reads or label the verification limitation; do not switch the user's checkout to conduct an audit.

Distinguish implemented behavior, proposed reuse, missing integration, and unresolved candidates. Separate a matching design from proof of its provenance. Note conditions omitted from an answer only to the extent they matter to the user's question. Credit deeper investigation when it changes an actionable conclusion; avoid awarding quality by length, citation count, or tool count. Use concrete findings rather than unsupported numerical scores. Do not run the original task's mutations to evaluate it.

## Estimate cost when requested

Read [cost-accounting.md](references/cost-accounting.md). Fetch current official rates for the exact model IDs, or use already-fetched same-session sources with a stated date. Preserve the distinction between API-equivalent dollars, Codex credits, and actual account charges. If rates cannot be established, provide the measured usage and formula without invented prices.

## Deliver

For a requested saved analysis, create a new Markdown file at the user-specified location or a suitable documentation directory. For an answer-only request, respond directly. Use the user's language. If a prior report disappeared, locate it narrowly and preserve new findings separately rather than recreating deleted material without context.

A useful report contains:

- Findings and the important comparability caveat.
- Selected samples, user-input differences, and measurement definitions.
- Per-run latency/token table and justified aggregates.
- Cost decomposition, official sources, date, and assumptions when in scope.
- Chronological search traces and their practical impact.
- Source-backed correctness, omissions, and uncertainty.
- Original session links and repository evidence links.

Compute ratios from unrounded values and state the denominator for savings. Avoid claiming population-level model superiority from one or two runs. Keep raw logs, private screenshots, and unrelated prompts out of shared artifacts; reference local evidence or include only the extracts needed. Finish with the report link, central result, and material limits.
