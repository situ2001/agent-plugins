#!/usr/bin/env python3
"""PreToolUse hook: scope checker for `rm -rf`.

Rejects a deletion when either rule holds:
1. It touches .git -- the path has a `.git` segment, the target is the current
   repo root (contains a .git dir), or the target itself is a repo directory.
2. It escapes the current working directory -- the resolved real path is not
   inside the cwd (a `cd X &&` chain moves the base to the new directory).

Only literal paths are parsed; dynamic targets (globs / $vars / command
substitution) cannot be statically resolved and are skipped ($HOME is expanded).
"""
import json
import os
import shlex
import sys

SEPARATORS = {"&&", "||", ";", "|", "|&", "&", ">", ">>", "<", "(", ")"}


def expand_target(tgt: str):
    """Return (resolvable_path, statically_resolvable); globs/vars/subst => not resolvable."""
    if any(ch in tgt for ch in "*?[") or "`" in tgt:
        return tgt, False
    if "$" in tgt:
        # Only expand $HOME / ${HOME}; skip other variables
        if "${HOME}" in tgt:
            tgt = tgt.replace("${HOME}", os.environ.get("HOME", ""))
        elif "$HOME" in tgt:
            tgt = tgt.replace("$HOME", os.environ.get("HOME", ""))
        else:
            return tgt, False
    return tgt, True


def resolve(base: str, target: str) -> str:
    t = os.path.expanduser(target)
    p = t if os.path.isabs(t) else os.path.join(base, t)
    return os.path.realpath(p)


def inside(p: str, boundary: str) -> bool:
    try:
        rel = os.path.relpath(p, boundary)
    except ValueError:
        return False
    return rel == "." or not rel.startswith("..")


def has_git_segment(p: str) -> bool:
    return ".git" in p.split(os.sep)


def output(decision: str, msg: str = "") -> None:
    if decision == "allow":
        print("{}")
        return
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


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        output("allow")
        return
    tool_input = payload.get("tool_input") or {}
    cmd = tool_input.get("command") or ""
    if not cmd:
        output("allow")
        return
    session_cwd = payload.get("cwd") or os.getcwd()

    try:
        tokens = shlex.split(cmd)
    except ValueError:
        output("allow")  # unbalanced quotes etc.; let the shell report it
        return

    base = os.path.realpath(session_cwd)
    i = 0
    problems = []

    while i < len(tokens):
        t = tokens[i]
        if t == "cd" and i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
            base = resolve(base, tokens[i + 1])
            i += 2
            continue
        if t != "rm":
            i += 1
            continue

        recursive = False
        opts_done = False
        targets = []
        j = i + 1
        while j < len(tokens):
            tj = tokens[j]
            if tj in SEPARATORS:
                break
            if opts_done or not tj.startswith("-") or tj == "-":
                targets.append(tj)
            else:
                if tj == "--":
                    opts_done = True
                elif tj.startswith("--"):
                    if tj == "--recursive" or tj.startswith("--recursive="):
                        recursive = True
                else:
                    body = tj[1:]
                    if "r" in body or "R" in body:
                        recursive = True
            j += 1

        if recursive:
            for tgt in targets:
                tgt2, ok = expand_target(tgt)
                if not ok:
                    continue
                resolved = resolve(base, tgt2)
                if has_git_segment(resolved):
                    problems.append(f"`{tgt}` touches .git (resolved: {resolved})")
                    continue
                if resolved == base and os.path.isdir(os.path.join(base, ".git")):
                    problems.append(
                        f"`{tgt}` would delete the current repo root (contains .git, resolved: {resolved})"
                    )
                    continue
                if os.path.isdir(resolved) and os.path.isdir(os.path.join(resolved, ".git")):
                    problems.append(
                        f"`{tgt}` is a git repo directory (contains .git, resolved: {resolved})"
                    )
                    continue
                if not inside(resolved, base):
                    problems.append(
                        f"`{tgt}` is outside the working directory {base} (resolved: {resolved})"
                    )
        i = j

    if problems:
        uniq = list(dict.fromkeys(problems))
        output("deny", "Blocked rm -rf scope violation:\n- " + "\n- ".join(uniq))
        return
    output("allow")


if __name__ == "__main__":
    main()
