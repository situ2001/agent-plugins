"""Accounting regressions; uses in-memory rollout fixtures only."""
import json
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

from extract_sessions import extract


def event(kind, **values):
    return {"type": "event_msg", "timestamp": "2026-01-01T00:00:00Z",
            "payload": {"type": kind, **values}}


def token(value, last=None):
    usage = {"input_tokens": value, "cached_input_tokens": 0,
             "output_tokens": 10, "total_tokens": value + 10}
    return event("token_count", info={"total_token_usage": usage,
                                     "last_token_usage": usage if last is None else last})


def prompt(text):
    return {"type": "response_item", "payload": {"type": "message", "role": "user",
            "content": [{"type": "input_text", "text": text}]}}


class AccountingTests(unittest.TestCase):
    def parse(self, records, **kwargs):
        raw = "\n".join(json.dumps(r) for r in records)
        with patch.object(Path, "open", mock_open(read_data=raw)):
            return extract(Path("fixture.jsonl"), **kwargs)

    def test_multiturn_delta_and_duplicate_snapshots(self):
        rows = [event("task_started", turn_id="a"), prompt("first"), token(100), token(100),
                event("task_complete", turn_id="a"), event("task_started", turn_id="b"),
                prompt("second"), token(250), event("task_complete", turn_id="b")]
        turns = self.parse(rows)["turns"]
        self.assertEqual([t["usage_delta"]["input_tokens"] for t in turns], [100, 150])
        self.assertIsNone(turns[0]["usage_delta"]["cache_write_input_tokens"])

    def test_unknown_baseline_and_reset(self):
        rows = [event("task_started"), prompt("question"), token(100, {"input_tokens": 20}),
                event("task_complete")]
        self.assertIsNone(self.parse(rows)["turns"][0]["usage_delta"])
        rows = [event("task_started"), token(100), token(50), event("task_complete")]
        self.assertIsNone(self.parse(rows)["turns"][0]["usage_delta"])

    def test_aborted_and_prompt_filter(self):
        rows = [event("task_started"), prompt("# AGENTS.md instructions target"),
                prompt("actual question"), token(100), event("turn_aborted")]
        self.assertEqual(self.parse(rows, keyword="target")["turns"], [])
        self.assertEqual(self.parse(rows, keyword="actual")["turns"][0]["status"], "aborted")

    def test_tool_overlap(self):
        def tool(kind, cid, second):
            return {"type": "response_item", "timestamp": f"2026-01-01T00:00:0{second}Z",
                    "payload": {"type": kind, "call_id": cid}}
        rows = [event("task_started"), tool("function_call", "a", 1),
                tool("custom_tool_call", "b", 2), tool("function_call_output", "a", 4),
                tool("custom_tool_call_output", "b", 5), event("task_complete")]
        result = self.parse(rows)["turns"][0]
        self.assertEqual(result["tool_response_sum_s"], 6)
        self.assertEqual(result["tool_response_union_s"], 4)


if __name__ == "__main__":
    unittest.main()
