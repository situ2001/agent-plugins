# /// script
# requires-python = ">=3.9"
# dependencies = ["websockets==15.0.1"]
# ///
"""Execute the real CLI against an isolated Unix WebSocket and fake Herdr."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest

from websockets.sync.server import unix_serve


CLI = Path(__file__).resolve().parents[1] / "scripts/codex-herdr-wait.py"
THREAD = "test-director-thread"
TURN = "test-director-turn"

FAKE_HERDR = r'''
import json, os, pathlib, sys, time
root = pathlib.Path(os.environ['FAKE_ROOT'])
config = json.loads((root / 'config.json').read_text())
args = sys.argv[1:]
with (root / 'herdr.jsonl').open('a') as f:
    f.write(json.dumps(args) + '\n')
assert args[0] == 'agent'
assert args[1] in ('get', 'wait'), 'Controller must leave response/history retrieval to acceptance'
name = args[2]
role = 'director' if name in ('director', 'w-test:p-director') else 'target'
agent = dict(config[role])
if role == 'target' and (root / 'replace-target').exists():
    agent['agent_session'] = dict(agent['agent_session'], value='replacement-session')
if args[1] == 'wait':
    if role == 'director':
        (root / 'interrupted').touch()
        if config.get('director_wait_error'):
            print('simulated director wait failure after interrupt', file=sys.stderr)
            sys.exit(1)
    else:
        (root / 'target-waiting').touch()
        if config.get('hold'):
            while not (root / 'release').exists():
                time.sleep(0.01)
        if config.get('new_turn'):
            (root / 'new-turn').touch()
        if config.get('cancel'):
            (root / 'job/cancelled').touch()
        if config.get('replace_during_wait'):
            agent['agent_session'] = dict(agent['agent_session'], value='replacement-session')
        if config.get('wait_error'):
            print('simulated Herdr daemon connection failure', file=sys.stderr)
            sys.exit(1)
    agent['agent_status'] = config.get('target_status', 'idle') if role == 'target' else 'idle'
elif role == 'target' and (root / 'target-waiting').exists():
    agent['agent_status'] = config.get('target_status', 'idle')
print(json.dumps({'result': {'agent': agent, 'type': 'agent_info'}}))
'''


def agent(role):
    return {"pane_id": f"w-test:p-{role}", "terminal_id": f"term-{role}",
            "agent": "codex", "agent_status": "working", "agent_session": {
                "kind": "id", "source": "herdr:codex", "value": THREAD if role == "director" else "test-worker-thread"}}


class CLITest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cw-", dir="/tmp")
        self.root = Path(self.temporary.name)
        self.job = self.root / "job"
        self.socket = self.root / "control.sock"
        self.config = {"director": agent("director"), "target": agent("target")}
        self.configure()
        self.resume = self.root / "resume.txt"
        self.resume.write_text("Accept the delegated implementation using /tmp/test-result.txt and its checks.")
        executable = self.root / "herdr"
        executable.write_text(f"#!{sys.executable}\n" + FAKE_HERDR)
        executable.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{self.root}:{os.environ['PATH']}",
                        FAKE_ROOT=str(self.root), HERDR_ENV="1", CODEX_THREAD_ID=THREAD,
                        CODEX_SESSION_ID="wrong-session", HERDR_PANE_ID="stale-pane")
        self.requests = []
        self.errors = []
        self.interrupt_requested = False
        self.lost = None
        self.rpc_error = None
        self.server = unix_serve(self.handle, str(self.socket))
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()

    def tearDown(self):
        (self.root / "release").touch()
        self.server.shutdown()
        self.server_thread.join(timeout=2)
        self.assertEqual(self.errors, [])
        self.temporary.cleanup()

    def configure(self, **data):
        self.config.update(data)
        (self.root / "config.json").write_text(json.dumps(self.config))

    def handle(self, websocket):
        initialized = False
        try:
            for text in websocket:
                message = json.loads(text)
                self.requests.append(message)
                method = message['method']
                if method == 'initialize':
                    self.assertFalse(initialized)
                    value = {}
                elif method == 'initialized':
                    initialized = True
                    continue
                else:
                    self.assertTrue(initialized)
                    self.assertEqual(message['params']['threadId'], THREAD)
                    if method == 'thread/read':
                        self.assertTrue(message['params']['includeTurns'])
                        interrupted = (self.root / 'interrupted').exists()
                        turns = [{'id': TURN, 'status': 'interrupted' if interrupted else 'inProgress'}]
                        if (self.root / 'new-turn').exists():
                            turns.append({'id': 'user-new-turn', 'status': self.config.get('new_status', 'inProgress')})
                        value = {'thread': {'id': THREAD, 'turns': turns,
                                            'status': {'type': 'idle' if interrupted else 'active'}}}
                    elif method == 'turn/interrupt':
                        self.assertEqual(message['params']['turnId'], TURN)
                        self.interrupt_requested = True
                        value = {}
                    elif method == 'turn/start':
                        self.assertTrue(self.interrupt_requested)
                        self.assertTrue((self.root / 'interrupted').exists())
                        self.assertTrue((self.root / 'target-waiting').exists() or self.config.get('director_wait_error'))
                        self.assertFalse((self.root / 'new-turn').exists())
                        value = {'turn': {'id': 'controller-new-turn', 'status': 'inProgress'}}
                    else:
                        self.fail(f'Unexpected method: {method}')
                if method == self.lost:
                    websocket.close()
                    return
                # Exercise asynchronous notifications and unmatched responses.
                websocket.send(json.dumps({'method': 'account/updated', 'params': {}}))
                if method == self.rpc_error:
                    websocket.send(json.dumps({'id': message['id'], 'error': {
                        'code': -32000, 'message': 'thread access denied'}}))
                else:
                    websocket.send(json.dumps({'id': message['id'], 'result': value}))
        except Exception as error:
            self.errors.append(repr(error))

    def cli(self, *args, **options):
        return subprocess.run([sys.executable, str(CLI), *map(str, args)],
                              capture_output=True, text=True, env=options.get('env', self.env), timeout=10)

    def prepare(self, *extra):
        return self.cli('prepare', '--job', self.job, '--director', 'director', '--target', 'worker',
                        '--resume-file', self.resume, '--socket', self.socket, *extra)

    def registered(self):
        response = self.prepare()
        self.assertEqual(response.returncode, 0, response.stderr)

    def result(self):
        return json.loads((self.job / 'result.json').read_text())

    def mutations(self):
        return [request for request in self.requests if request['method'] in ('turn/interrupt', 'turn/start')]

    def herdr_calls(self):
        return [json.loads(line) for line in (self.root / 'herdr.jsonl').read_text().splitlines()]

    def test_prepare_records_exact_turn_without_interrupt_and_freezes_context(self):
        self.registered()
        plan = json.loads((self.job / 'plan.json').read_text())
        self.assertEqual((plan['threadId'], plan['turnId']), (THREAD, TURN))
        self.assertEqual(plan['director']['pane_id'], 'w-test:p-director')
        self.assertIn('Accept', plan['resume'])
        self.assertEqual(self.mutations(), [])
        self.assertNotEqual(self.prepare().returncode, 0)  # Cannot overwrite registration.

    def test_explicit_thread_overrides_environment_and_expected_turn_is_checked(self):
        self.env['CODEX_THREAD_ID'] = 'wrong-thread'
        response = self.prepare('--thread-id', THREAD, '--turn-id', TURN)
        self.assertEqual(response.returncode, 0, response.stderr)

    def test_wrong_expected_turn_rejected(self):
        self.assertEqual(self.prepare('--turn-id', 'wrong-turn').returncode, 1)
        self.assertFalse(self.job.exists())
        self.assertEqual(self.mutations(), [])

    def test_wrong_director_session_rejected(self):
        self.config['director']['agent_session']['value'] = 'other-session'
        self.configure()
        self.assertEqual(self.prepare().returncode, 1)
        self.assertEqual(self.requests, [])

    def test_director_without_session_metadata_uses_explicit_pane(self):
        # The successful live prototype exposed no director agent_session.
        del self.config['director']['agent_session']
        self.configure()
        self.registered()
        response = self.cli('run', '--job', self.job)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(self.result()['phase'], 'resumed')

    def test_missing_executor_session_cannot_bind_registration(self):
        del self.config['target']['agent_session']
        self.configure()
        response = self.prepare()
        self.assertEqual(response.returncode, 1)
        self.assertIn('cannot bind', response.stderr)
        self.assertEqual(self.requests, [])

    def test_ready_wait_resumes_same_thread_and_duplicate_does_not_redeliver(self):
        self.registered()
        self.resume.write_text('Changed context must not replace saved instructions')
        response = self.cli('run', '--job', self.job)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(self.result()['phase'], 'resumed')
        self.assertEqual(self.result()['wakeReason'], 'ready')
        self.assertEqual([m['method'] for m in self.mutations()], ['turn/interrupt', 'turn/start'])
        self.assertEqual([c[2] for c in self.herdr_calls() if c[1] == 'wait'],
                         ['w-test:p-director', 'w-test:p-target'])
        message = self.mutations()[1]['params']['input'][0]['text']
        self.assertIn('Accept the delegated implementation', message)
        self.assertIn('idle/done only establishes readiness', message)
        requests = len(self.requests)
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 3)
        self.assertEqual(len(self.requests), requests)

    def test_blocked_wakes_without_reading_history(self):
        self.configure(target_status='blocked')
        self.registered()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 0)
        self.assertEqual(self.result()['wakeReason'], 'blocked')
        self.assertTrue(all(c[1] in ('get', 'wait') for c in self.herdr_calls()))

    def test_wait_failure_wakes_with_saved_error(self):
        self.configure(wait_error=True)
        self.registered()
        response = self.cli('run', '--job', self.job)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(self.result()['wakeReason'], 'wait_failed')
        self.assertIn('daemon connection failure', self.result()['waitError'])
        self.assertEqual(self.result()['targetWait']['returncode'], 1)

    def test_director_wait_failure_wakes_if_rpc_confirms_interruption(self):
        self.configure(director_wait_error=True)
        self.registered()
        response = self.cli('run', '--job', self.job)
        self.assertEqual(response.returncode, 0, response.stderr)
        self.assertEqual(self.result()['wakeReason'], 'wait_failed')
        self.assertIn('director wait failure', self.result()['waitError'])
        self.assertFalse((self.root / 'target-waiting').exists())

    def test_unsettled_target_after_wait_wakes_for_inspection(self):
        self.configure(target_status='working')
        self.registered()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 0)
        self.assertEqual(self.result()['wakeReason'], 'wait_failed')
        self.assertIn('working after wait', self.result()['waitError'])

    def test_user_new_turn_preserves_result_without_start(self):
        for status in ('inProgress', 'completed', 'interrupted'):
            with self.subTest(status=status):
                if self.job.exists():
                    # Each iteration registers a fresh independent turn/job.
                    self.job = self.root / f'job-{status}'
                (self.root / 'new-turn').unlink(missing_ok=True)
                (self.root / 'interrupted').unlink(missing_ok=True)
                self.configure(new_turn=True, new_status=status)
                self.registered()
                response = self.cli('run', '--job', self.job)
                self.assertEqual(response.returncode, 4, response.stderr)
                self.assertEqual(self.result()['phase'], 'superseded')
                self.assertEqual(self.result()['wakeReason'], 'ready')
        self.assertTrue(all(m['method'] == 'turn/interrupt' for m in self.mutations()))

    def test_turn_changes_before_run_no_interrupt(self):
        self.registered()
        (self.root / 'new-turn').touch()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 4)
        self.assertEqual(self.mutations(), [])

    def test_cancel_before_run_no_interrupt(self):
        self.registered()
        self.assertEqual(self.cli('cancel', '--job', self.job).returncode, 0)
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 4)
        self.assertEqual(self.result()['phase'], 'cancelled')
        self.assertEqual(self.mutations(), [])

    def test_cancel_during_wait_keeps_result_no_start(self):
        self.configure(cancel=True)
        self.registered()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 4)
        self.assertIn('targetWait', self.result())
        self.assertEqual(len(self.mutations()), 1)

    def test_changed_worker_before_interrupt_fails(self):
        self.registered()
        (self.root / 'replace-target').touch()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 1)
        self.assertIn('Registered agent changed', self.result()['error'])
        self.assertEqual(self.mutations(), [])

    def test_changed_worker_during_wait_wakes_as_failure(self):
        self.configure(replace_during_wait=True)
        self.registered()
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 0)
        self.assertEqual(self.result()['wakeReason'], 'wait_failed')
        self.assertIn('changed while waiting', self.result()['waitError'])

    def test_access_error_does_not_create_or_restart_server(self):
        self.rpc_error = 'thread/read'
        response = self.prepare()
        self.assertEqual(response.returncode, 1)
        self.assertIn('thread access denied', response.stderr)
        self.assertEqual(self.mutations(), [])

    def test_socket_connection_failure_is_explicit(self):
        self.socket = self.root / 'absent.sock'
        response = self.prepare()
        self.assertEqual(response.returncode, 1)
        self.assertIn('No such file', response.stderr)
        self.assertEqual(self.requests, [])

    def test_lost_mutation_response_is_not_retried(self):
        self.registered()
        self.lost = 'turn/start'
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 1)
        self.assertEqual(self.result()['failedPhase'], 'start_requested')
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 3)
        self.assertEqual([m['method'] for m in self.mutations()], ['turn/interrupt', 'turn/start'])

    def test_lost_interrupt_response_leaves_evidence_and_consumes_registration(self):
        self.registered()
        self.lost = 'turn/interrupt'
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 1)
        self.assertEqual(self.result()['failedPhase'], 'interrupt_requested')
        self.assertEqual(self.cli('run', '--job', self.job).returncode, 3)
        self.assertEqual([m['method'] for m in self.mutations()], ['turn/interrupt'])

    def test_duplicate_controller_while_waiting_is_rejected(self):
        self.configure(hold=True)
        self.registered()
        process = subprocess.Popen([sys.executable, str(CLI), 'run', '--job', str(self.job)],
                                   env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 5  # Bound a broken test, never a production wait.
            while not (self.root / 'target-waiting').exists():
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)
            self.assertEqual(self.cli('run', '--job', self.job).returncode, 3)
            (self.root / 'release').touch()
            stdout, stderr = process.communicate(timeout=5)
            self.assertEqual(process.returncode, 0, stderr)
            self.assertEqual(len(self.mutations()), 2)
        finally:
            (self.root / 'release').touch()
            if process.poll() is None:
                process.kill()
                process.communicate()


if __name__ == '__main__':
    unittest.main(verbosity=2)
