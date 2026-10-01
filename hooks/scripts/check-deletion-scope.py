#!/usr/bin/env python3
"""PreToolUse hook: require trash on macOS and scope-check rm/trash targets.

Reject paths outside the working directory and paths touching .git or a repo
root. A literal `cd X` changes the working directory for subsequent commands.
Dynamic targets are rejected because their scope cannot be checked statically.
On macOS, direct the caller to install missing trash with `brew install trash`;
this hook only returns a recommendation and never installs anything.
"""
import json
import os
import re
import shlex
import shutil
import sys

SEPARATORS = {"&&", "||", ";", "|", "|&", "&", ">", ">>", "<", "(", ")"}


def expand_target(tgt: str):
    """Return (resolvable_path, statically_resolvable); globs/vars/subst => not resolvable."""
    if any(ch in tgt for ch in "*?[") or "`" in tgt:
        return tgt, False
    tgt = re.sub(r"\$\{HOME\}|\$HOME(?![A-Za-z0-9_])",
                 lambda _: os.environ.get("HOME", ""), tgt)
    if "$" in tgt:
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
    return rel != ".." and not rel.startswith(".." + os.sep)


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
    cmd = tool_input.get("command") or tool_input.get("cmd") or ""
    if not cmd:
        output("allow")
        return
    session_cwd = payload.get("cwd") or os.getcwd()

    try:
        lexer = shlex.shlex(cmd, posix=True, punctuation_chars=";&|<>()")
        lexer.whitespace_split = True
        lexer.commenters = "#"
        tokens = list(lexer)
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
        if os.path.basename(t) not in {"rm", "trash"}:
            i += 1
            continue

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
            j += 1

        for tgt in targets:
            tgt2, ok = expand_target(tgt)
            if not ok:
                problems.append(f"`{tgt}` has dynamic scope; pass explicit file/directory paths")
                continue
            resolved = resolve(base, tgt2)
            if has_git_segment(tgt2) or has_git_segment(resolved):
                problems.append(f"`{tgt}` touches .git (resolved: {resolved})")
                continue
            if os.path.lexists(os.path.join(resolved, ".git")):
                problems.append(
                    f"`{tgt}` is a git repo directory (contains .git, resolved: {resolved})"
                )
                continue
            if not inside(resolved, base):
                problems.append(
                    f"`{tgt}` is outside the working directory {base} (resolved: {resolved})"
                )

        if sys.platform == "darwin":
            if os.path.basename(t) == "rm":
                problems.append("On macOS, use `trash` instead of `rm` (pass paths without rm flags)")
            if shutil.which("trash") is None:
                problems.append("Install `trash` with `brew install trash`, then retry using `trash`")
        i = j

    if problems:
        uniq = list(dict.fromkeys(problems))
        output("deny", "Blocked deletion:\n- " + "\n- ".join(uniq))
        return
    output("allow")


if __name__ == "__main__":
    main()
