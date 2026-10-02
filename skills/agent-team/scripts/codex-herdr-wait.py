#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["websockets==15.0.1"]
# ///
"""One-shot Codex interrupt / independent Herdr wait / same-thread continuation."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

from websockets.sync.client import unix_connect


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def event(job, name, **data):
    with (job / "events.jsonl").open("a") as stream:
        stream.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                                 "event": name, **data}, ensure_ascii=False) + "\n")


class RPC:
    def __init__(self, socket):
        self.ws = unix_connect(socket, max_size=None)
        self.sequence = 0
        try:
            self.call("initialize", {"clientInfo": {
                "name": "situ2001_herdr_wait", "version": "1.0"}})
            self.ws.send(json.dumps({"method": "initialized"}))
        except Exception:
            self.close()
            raise

    def call(self, method, params):
        self.sequence += 1
        request_id = self.sequence
        self.ws.send(json.dumps({"id": request_id, "method": method, "params": params}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    raise RuntimeError(f"{method}: {message['error']}")
                return message["result"]
            if "method" in message and "id" in message:
                raise RuntimeError(f"Unexpected server request {message['method']}; controller cannot answer it")

    def thread(self, thread_id):
        thread = self.call("thread/read", {"threadId": thread_id, "includeTurns": True})["thread"]
        if thread["id"] != thread_id:
            raise RuntimeError("thread/read returned a different thread")
        return thread

    def close(self):
        self.ws.close()


def herdr(*args):
    process = subprocess.run(["herdr", "agent", *args], capture_output=True, text=True)
    evidence = {"args": list(args), "returncode": process.returncode,
                "stdout": process.stdout, "stderr": process.stderr}
    return evidence


def agent_from(evidence):
    if evidence["returncode"]:
        raise RuntimeError(f"herdr agent {evidence['args']}: {evidence['stderr'].strip()}")
    return json.loads(evidence["stdout"])["result"]["agent"]


def identity(agent, require_session=True):
    # A live name follows a pane occupant; bind the registered session as well.
    session = agent.get("agent_session")
    if require_session and not session:
        raise RuntimeError("Herdr did not expose agent_session; cannot bind this wait to an agent")
    return {"pane_id": agent["pane_id"], "terminal_id": agent["terminal_id"],
            "agent": agent["agent"], "agent_session": session}


def get_bound(expected):
    evidence = herdr("get", expected["pane_id"])
    agent = agent_from(evidence)
    if identity(agent, require_session=expected["agent_session"] is not None) != expected:
        raise RuntimeError(f"Registered agent changed in {expected['pane_id']}")
    return agent, evidence


def latest(thread):
    return thread["turns"][-1] if thread["turns"] else None


def turn_summary(thread):
    turn = latest(thread)
    return {"id": turn["id"], "status": turn["status"]} if turn else None


def is_turn(thread, turn_id, status):
    turn = latest(thread)
    return turn is not None and turn["id"] == turn_id and turn["status"] == status


def prepare(args):
    thread_id = args.thread_id or os.environ.get("CODEX_THREAD_ID")
    if not thread_id:
        raise RuntimeError("Supply --thread-id or run prepare in the director's CODEX_THREAD_ID environment")
    resume = args.resume_file.resolve().read_text()
    if not resume.strip():
        raise RuntimeError("The saved continuation must contain task context and acceptance instructions")
    director = identity(agent_from(herdr("get", args.director)), require_session=False)
    session = director["agent_session"]
    if director["agent"] != "codex" or (session is not None and (
            session["kind"] != "id" or session["value"] != thread_id)):
        raise RuntimeError("--director is not the Codex session identified by --thread-id/CODEX_THREAD_ID")
    target = identity(agent_from(herdr("get", args.target)))
    if director["pane_id"] == target["pane_id"]:
        raise RuntimeError("The delegated target must be separate from the director")
    rpc = RPC(str(args.socket.expanduser().resolve()))
    try:
        thread = rpc.thread(thread_id)
        active = [turn for turn in thread["turns"] if turn["status"] == "inProgress"]
        if len(active) != 1 or latest(thread)["id"] != active[0]["id"]:
            raise RuntimeError("Expected exactly one current inProgress director turn")
        turn_id = active[0]["id"]
        if args.turn_id and args.turn_id != turn_id:
            raise RuntimeError("--turn-id does not match the current inProgress turn")
    finally:
        rpc.close()
    job = args.job.resolve()
    job.mkdir()  # A registration is immutable; use a fresh directory for a new wait.
    plan = {"threadId": thread_id, "turnId": turn_id,
            "socket": str(args.socket.expanduser().resolve()),
            "director": director, "target": target, "resume": resume,
            "resumeSource": str(args.resume_file.resolve()), "cwd": str(Path.cwd())}
    write_json(job / "plan.json", plan)
    event(job, "prepared", threadId=thread_id, turnId=turn_id)
    print(json.dumps({"job": str(job), "threadId": thread_id, "turnId": turn_id}))
    return 0


def run(args):
    job = args.job.resolve()
    plan = json.loads((job / "plan.json").read_text())
    try:
        with (job / "run.claim").open("x") as claim:
            claim.write(f"pid={os.getpid()}\n")
            claim.flush()
            os.fsync(claim.fileno())
    except FileExistsError:
        print(f"Already claimed; inspect {job / 'result.json'} and events.jsonl. No RPC repeated.", file=sys.stderr)
        return 3
    result = {"threadId": plan["threadId"], "turnId": plan["turnId"], "phase": "claimed"}

    def save(phase, **data):
        result.update(phase=phase, **data)
        write_json(job / "result.json", result)
        event(job, phase, **data)

    def cancelled():
        return (job / "cancelled").exists()

    rpc = None
    try:
        save("claimed")
        if cancelled():
            save("cancelled")
            return 4
        rpc = RPC(plan["socket"])
        get_bound(plan["director"])
        get_bound(plan["target"])
        thread = rpc.thread(plan["threadId"])
        if not is_turn(thread, plan["turnId"], "inProgress"):
            save("superseded", observedTurn=turn_summary(thread))
            return 4
        if cancelled():
            save("cancelled")
            return 4
        # Persist before each mutation. A lost response must never cause a retry.
        save("interrupt_requested")
        rpc.call("turn/interrupt", {"threadId": plan["threadId"], "turnId": plan["turnId"]})
        save("interrupt_acknowledged")

        try:
            # Interrupt acknowledges cancellation, not completion. Wait for the
            # registered director UI to settle, then verify the exact turn.
            evidence = herdr("wait", plan["director"]["pane_id"])
            save("director_settled", directorWait=evidence)
            agent_from(evidence)
            get_bound(plan["director"])
            thread = rpc.thread(plan["threadId"])
            if not is_turn(thread, plan["turnId"], "interrupted"):
                if is_turn(thread, plan["turnId"], "inProgress"):
                    raise RuntimeError("Director UI settled before the interrupted turn; cancellation is not confirmed")
                save("superseded", observedTurn=turn_summary(thread))
                return 4
            if cancelled():
                save("cancelled")
                return 4
            get_bound(plan["target"])
            save("waiting")
            evidence = herdr("wait", plan["target"]["pane_id"])
            save("wait_returned", targetWait=evidence)
            waited = agent_from(evidence)
            if identity(waited) != plan["target"]:
                raise RuntimeError("Delegated agent changed while waiting")
            current, evidence = get_bound(plan["target"])
            save("target_checked", targetGet=evidence)
            status = current["agent_status"]
            if status not in ("idle", "done", "blocked"):
                raise RuntimeError(f"Delegated agent is {status} after wait; inspect its current UI")
            reason = "blocked" if status == "blocked" else "ready"
        except Exception as error:
            reason = "wait_failed"
            save("wait_failed", waitError=str(error))

        save("wake_ready", wakeReason=reason)
        # A user-created later turn (even a completed/interrupted one) takes
        # precedence. Never interrupt that turn or steer it with old results.
        thread = rpc.thread(plan["threadId"])
        if cancelled():
            save("cancelled")
            return 4
        if not is_turn(thread, plan["turnId"], "interrupted"):
            if is_turn(thread, plan["turnId"], "inProgress"):
                raise RuntimeError("Interrupted turn is still inProgress; continuation cannot start")
            save("superseded", observedTurn=turn_summary(thread))
            return 4
        if thread["status"]["type"] != "idle":
            raise RuntimeError(f"Director thread is not idle: {thread['status']}")
        message = (
            f"[situ2001 Herdr wait: {reason}] Independent controller evidence: {job / 'result.json'}; "
            f"registration: {job / 'plan.json'}; events: {job / 'events.jsonl'}. "
            "Read these files before continuing. This is a new turn on the same thread. "
            "For ready, retrieve the actual delegated response using Herdr's official procedure and "
            "accept against the saved criteria; idle/done only establishes readiness. "
            "For blocked or wait_failed, inspect agent get and its visible UI and handle the blocker/failure; "
            "read application history only once settled.\n\nSaved continuation:\n" + plan["resume"])
        save("start_requested")
        started = rpc.call("turn/start", {"threadId": plan["threadId"],
                                          "input": [{"type": "text", "text": message}]})
        save("resumed", resumedTurnId=started["turn"]["id"])
        print(json.dumps({"phase": "resumed", "wakeReason": reason, "job": str(job)}))
        return 0
    except Exception as error:
        save("failed", error=str(error), failedPhase=result["phase"])
        print(f"Controller failed: {error}. Inspect {job / 'result.json'}; no automatic retry/server restart.",
              file=sys.stderr)
        return 1
    finally:
        if rpc is not None:
            rpc.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("prepare", help="Register an exact active turn; performs no interruption")
    command.add_argument("--job", type=Path, required=True, help="New persistent evidence directory")
    command.add_argument("--director", required=True, help="Explicit live director Herdr name/pane; session cross-checked when exposed")
    command.add_argument("--target", required=True, help="One already-delegated live Herdr name/pane")
    command.add_argument("--resume-file", type=Path, required=True, help="Saved task context, result paths and acceptance criteria")
    command.add_argument("--thread-id", help="Defaults to CODEX_THREAD_ID; never inferred from HERDR_PANE_ID")
    command.add_argument("--turn-id", help="Optional expected turn; otherwise read the current inProgress turn")
    command.add_argument("--socket", type=Path, default=Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) /
                         "app-server-control/app-server-control.sock", help="Existing daemon Unix WebSocket")
    for name, help_text in [("run", "Run once from an independent Herdr shell pane"),
                            ("cancel", "Leave evidence and suppress continuation when the wait returns")]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--job", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "cancel":
            (args.job / "cancelled").touch()
            print("Cancellation recorded; an active Herdr wait still runs until it settles.")
            return 0
        if os.environ.get("HERDR_ENV") != "1":
            raise RuntimeError("Run inside the same Herdr session as the registered agents (HERDR_ENV=1)")
        return prepare(args) if args.command == "prepare" else run(args)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
