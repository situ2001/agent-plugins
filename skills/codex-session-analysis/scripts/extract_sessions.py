#!/usr/bin/env python3
"""Read rollout JSONL; emit matching turn summaries without image bytes."""

import argparse
import base64
import hashlib
import json
from datetime import datetime
from pathlib import Path


FIELDS = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens",
          "output_tokens", "reasoning_output_tokens", "total_tokens")


def seconds(start, end):
    try:
        return (datetime.fromisoformat(end.replace("Z", "+00:00"))
                - datetime.fromisoformat(start.replace("Z", "+00:00"))).total_seconds()
    except (AttributeError, TypeError, ValueError):
        return None


def content_text(content):
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(x.get("text", "") for x in content if isinstance(x, dict))


def image_ids(content):
    result = []
    for block in content if isinstance(content, list) else []:
        if block.get("type") != "input_image":
            continue
        url = block.get("image_url", "")
        if isinstance(url, dict):
            url = url.get("url", "")
        if url.startswith("data:") and ";base64," in url:
            try:
                data = base64.b64decode(url.split(",", 1)[1], validate=True)
                result.append({"sha256": hashlib.sha256(data).hexdigest()})
            except ValueError:
                result.append({"warning": "invalid image data URL"})
        else:
            result.append({"reference": url})
    return result


def prompt_text(content):
    """Exclude recognizable injected setup blocks from prompt matching."""
    blocks = content if isinstance(content, list) else []
    return "\n".join(b.get("text", "") for b in blocks
                     if b.get("type") == "input_text" and not b.get("text", "").lstrip().startswith(
                         ("# AGENTS.md instructions", "<environment_context>", "<image ", "</image>")))


def summarize(path, records, meta, baseline, terminal, trace):
    start = records[0]
    contexts = [r["payload"] for r in records if r.get("type") == "turn_context"]
    users = [r["payload"] for r in records if r.get("type") == "response_item"
             and r["payload"].get("role") == "user"]
    snapshots = [r["payload"]["info"] for r in records
                 if r["payload"].get("type") == "token_count"
                 and r["payload"].get("info")]
    warnings = []
    usage = None
    if snapshots:
        first = snapshots[0].get("total_token_usage", {})
        if baseline is None and first and first == snapshots[0].get("last_token_usage"):
            baseline = {k: 0 for k in first}
        final = snapshots[-1].get("total_token_usage", {})
        if baseline is not None:
            usage = {k: final[k] - baseline[k] if k in final and k in baseline else None
                     for k in FIELDS}
            totals = [baseline] + [s.get("total_token_usage", {}) for s in snapshots]
            reset = any(b[k] < a[k] for a, b in zip(totals, totals[1:])
                        for k in FIELDS if k in a and k in b)
            if reset:
                warnings.append("Cumulative counter decreased; usage delta is unknown.")
                usage = None
        else:
            warnings.append("No verified usage baseline; cumulative total is not a turn delta.")
    else:
        warnings.append("No usage snapshot in this turn.")
    if usage and usage.get("input_tokens") is not None:
        inp, cached = usage["input_tokens"], usage.get("cached_input_tokens")
        usage["uncached_input_tokens"] = inp - cached if cached is not None else None
        usage["cache_hit_ratio"] = cached / inp if inp and cached is not None else None
        if cached is not None and cached > inp:
            warnings.append("Cached input exceeds input; inspect metering schema.")
        if all(usage.get(k) is not None for k in ("input_tokens", "output_tokens", "total_tokens")):
            if usage["total_tokens"] != inp + usage["output_tokens"]:
                warnings.append("Total differs from input plus output.")
    calls = [r for r in records if r["payload"].get("type") in
             ("function_call", "custom_tool_call")]
    outputs = {r["payload"].get("call_id"): r for r in records
               if r["payload"].get("type") in ("function_call_output", "custom_tool_call_output")}
    intervals, steps = [], []
    for number, call in enumerate(calls, 1):
        p = call["payload"]
        out = outputs.get(p.get("call_id"))
        offset = seconds(start.get("timestamp"), call.get("timestamp"))
        duration = seconds(call.get("timestamp"), out.get("timestamp")) if out else None
        text = content_text(out["payload"].get("output")) if out else ""
        if duration is not None and offset is not None and duration >= 0:
            intervals.append((offset, offset + duration))
        else:
            warnings.append(f"Tool round {number} has incomplete or invalid timing.")
        step = {"round": number, "name": p.get("name"), "start_offset_s": offset,
                "response_latency_s": duration, "truncation_marker": "truncated" in text.lower()}
        if trace:
            step["recorded_call"] = p.get("input", p.get("arguments"))
        steps.append(step)
    merged = []
    for left, right in sorted(intervals):
        if merged and left <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], right)
        else:
            merged.append([left, right])
    end = terminal or {}
    state = {"task_complete": "complete", "turn_aborted": "aborted"}.get(
        end.get("payload", {}).get("type"), "incomplete")
    if state != "complete":
        warnings.append("Usage is observed partial usage, not a completed-answer cost.")
    models = [{k: c.get(k) for k in ("model", "effort", "service_tier")} for c in contexts]
    result = {"file": str(path), "session_id": meta.get("id"),
              "turn_id": start["payload"].get("turn_id"), "cwd": meta.get("cwd"),
              "git": meta.get("git"), "contexts": models, "status": state,
              "started_at": start.get("timestamp"), "ended_at": end.get("timestamp"),
              "duration_ms": end.get("payload", {}).get("duration_ms"),
              "time_to_first_token_ms": end.get("payload", {}).get("time_to_first_token_ms"),
              "event_interval_s": seconds(start.get("timestamp"), end.get("timestamp")),
              "user_text": [text for u in users if (text := prompt_text(u.get("content")))],
              "images": [i for u in users for i in image_ids(u.get("content"))],
              "usage_delta": usage,
              "observed_max_request_input": max((s.get("last_token_usage", {}).get("input_tokens", 0)
                                                  for s in snapshots), default=None),
              "tool_rounds": len(calls), "tool_response_sum_s": sum(b-a for a, b in intervals),
              "tool_response_union_s": sum(b-a for a, b in merged),
              "trace": steps, "warnings": warnings}
    if trace:
        result["final_answer"] = end.get("payload", {}).get("last_agent_message")
    return result


def extract(path, cwd=None, keyword=None, trace=False):
    meta, active, baseline, latest = {}, [], None, None
    turns, warnings = [], []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                warnings.append(f"Unparseable JSON at line {number}; metrics may be incomplete.")
                continue
            p = r.get("payload")
            if not isinstance(p, dict):
                continue
            if r.get("type") == "session_meta":
                meta = p
            kind = p.get("type")
            if kind == "task_started":
                if active:
                    turns.append(summarize(path, active, meta, baseline, None, trace))
                active, baseline = [], latest
            if active or kind == "task_started":
                active.append(r)
            if kind == "token_count" and p.get("info"):
                latest = p["info"].get("total_token_usage", latest)
            if kind in ("task_complete", "turn_aborted") and active:
                expected = active[0]["payload"].get("turn_id")
                if p.get("turn_id") and expected and p["turn_id"] != expected:
                    warnings.append("Mismatched terminal turn ID; inspect raw boundaries.")
                    continue
                turns.append(summarize(path, active, meta, baseline, r, trace))
                active = []
    if active:
        turns.append(summarize(path, active, meta, baseline, None, trace))
    if not turns:
        warnings.append("No supported task boundaries; inspect this log manually.")
    selected = [t for t in turns
                if (not cwd or Path(t.get("cwd") or "").resolve() == Path(cwd).expanduser().resolve())
                and (not keyword or any(keyword in text for text in t["user_text"]))]
    return {"file": str(path), "warnings": warnings, "turns": selected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--cwd")
    parser.add_argument("--keyword")
    parser.add_argument("--trace", action="store_true")
    args = parser.parse_args()
    for path in args.files:
        print(json.dumps(extract(path.expanduser(), args.cwd, args.keyword, args.trace), ensure_ascii=False))


if __name__ == "__main__":
    main()
