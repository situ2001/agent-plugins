#!/usr/bin/env python3
"""PreToolUse hook: block ripgrep's `rg -r` footgun.

1. `rg -rn "pattern"` is parsed by ripgrep as `-r n` (--replace n), silently
   replacing every match with the letter n.
2. A trailing bare `rg ... -r` (missing replacement value) fails with
   `missing value for flag -r`.

`grep -rn` is fine (grep's -r is recursive) and is never blocked; rg is
recursive by default, so prefer `rg -n` or `grep -rn`.
"""
import json
import sys

SHELL_OP = set("|;&<>()")


def is_rg_token(tok: str) -> bool:
    """True if the token is the rg command itself (quotes/shell ops stripped)."""
    base = tok.strip('"\'')
    # Allow `command rg` style wrappers, but exclude grep/ugrep/ripgrep
    if base == "rg":
        return True
    # rg with a path/npx prefix is rare; keep it simple
    return False


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print("{}")
        return

    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command") or ""
    if not cmd:
        print("{}")
        return

    tokens = cmd.split()
    reasons = []

    def strip_tok(tok: str) -> str:
        s = tok.strip('"\'')
        return s.rstrip("".join(SHELL_OP)) if s.endswith(tuple(SHELL_OP)) else s

    is_rg = any(strip_tok(t) == "rg" for t in tokens)
    if not is_rg:
        print("{}")
        return

    for i, tok in enumerate(tokens):
        t = strip_tok(tok)
        if not t.startswith("-") or t.startswith("--"):
            continue
        if t == "-r":
            val_raw = tokens[i + 1] if i + 1 < len(tokens) else None
            # Missing value when: next token is a shell operator (| ; && || > ...),
            # the token itself carries a trailing separator, or there is no next token
            if val_raw is None or val_raw.startswith(tuple(SHELL_OP)) or tok != t:
                reasons.append(
                    "`rg ... -r` ends with a bare `-r` that has no replacement value; "
                    "it will fail with `missing value for flag -r`. In ripgrep, `-r` "
                    "is --replace, not recursive; recursion is the default, so use "
                    "`rg -n` or `grep -rn`."
                )
                continue
            val = strip_tok(val_raw)
            if val == "n":
                reasons.append(
                    "`rg -r n` replaces every match with the letter n. Use `rg -n` "
                    "(rg is recursive by default) or `grep -rn`."
                )
            continue
        # Combined short flag -rX: X is -r's replacement value; only block when it is n
        if t.startswith("-r") and len(t) > 2:
            replace_val = t[2:]
            if replace_val == "n":
                reasons.append(
                    "`rg -rn` is parsed by ripgrep as `-r n` (--replace n), silently "
                    "replacing every match with the letter n and corrupting output. "
                    "Use `rg -n` (rg is recursive by default) or `grep -rn`."
                )
            continue

    if reasons:
        msg = "Blocked ripgrep `-r` misuse:\n- " + "\n- ".join(reasons)
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": msg,
                    "stopReason": msg,
                    "systemMessage": msg,
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": msg,
                    },
                },
                ensure_ascii=False,
            )
        )
        return

    print("{}")


if __name__ == "__main__":
    main()
