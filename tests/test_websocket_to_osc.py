"""Tests for Studio v1, legacy metrics, and reconnect behavior."""

import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import pythonosc.udp_client
except ImportError:
    package = types.ModuleType("pythonosc")
    package.__path__ = []
    udp_client = types.ModuleType("pythonosc.udp_client")
    udp_client.SimpleUDPClient = object
    sys.modules["pythonosc"] = package
    sys.modules["pythonosc.udp_client"] = udp_client

SCRIPT = Path(__file__).resolve().parents[1] / "sender" / "websocket_to_osc.py"
spec = importlib.util.spec_from_file_location("router_sender_test", SCRIPT)
sender = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sender)


class OSC:
    def __init__(self):
        self.messages = []

    def send_message(self, address, value):
        self.messages.append((address, value))


class RouterTests(unittest.TestCase):
    def test_studio_first_person(self):
        frame = {"type": "frame", "people": [
            {"id": 7, "metrics": {"energy": 2.5, "height": None}},
            {"id": 8, "metrics": {"energy": 9.5}},
        ]}
        self.assertEqual(sender.extract_metrics(frame), {"energy": 2.5, "height": None})

    def test_hello_pong_and_missing_person(self):
        for payload in (
            {"type": "hello", "metrics": []},
            {"type": "pong", "t": 1},
            {"type": "frame", "people": []},
            {"type": "frame", "people": [{"id": 1}]},
            {"type": "frame", "people": "invalid"},
            ["invalid"],
        ):
            with self.subTest(payload=payload):
                self.assertIsNone(sender.extract_metrics(payload))

    def test_original_flat_metrics(self):
        legacy = {"energy": 4.0, "jerk": 0.7}
        self.assertIs(sender.extract_metrics(legacy), legacy)

    def test_invalid_values_are_skipped_and_fanout_preserved(self):
        first, second = OSC(), OSC()
        metrics = {
            "energy": "2.25", "sync_correlation": -0.75,
            "height": None, "expansion": float("nan"),
            "sway": float("inf"), "jerk": True, "torque": "bad",
        }
        sent = sender.send_metrics(metrics, [{"client": first}, {"client": second}])
        expected = [("/motion/energy", 2.25), ("/motion/sync_correlation", -0.75)]
        self.assertEqual(first.messages, expected)
        self.assertEqual(second.messages, expected)
        self.assertEqual(sent, {"energy": 2.25, "sync_correlation": -0.75})

    def test_all_nine_metrics(self):
        client = OSC()
        sender.send_metrics(
            {name: i for i, name in enumerate(sender.METRIC_NAMES)},
            [{"client": client}],
        )
        self.assertEqual(len(client.messages), 9)
        self.assertEqual(client.messages[-1], ("/motion/jerk", 8.0))

    def test_reconnect_after_connection_failure(self):
        class FailedConnection:
            async def __aenter__(self):
                raise OSError("temporary outage")

            async def __aexit__(self, exc_type, exc, tb):
                return False

        async def stop_after_delay(seconds):
            self.assertEqual(seconds, sender.RECONNECT_DELAY_SECONDS)
            raise asyncio.CancelledError

        with patch.object(sender, "create_osc_outputs", return_value=[]), \
             patch.object(sender.websockets, "connect", return_value=FailedConnection()) as connect, \
             patch.object(sender.asyncio, "sleep", side_effect=stop_after_delay):
            with self.assertRaises(asyncio.CancelledError):
                asyncio.run(sender.forward_metrics("ws://127.0.0.1:8765", []))
            connect.assert_called_once()


if __name__ == "__main__":
    unittest.main()
