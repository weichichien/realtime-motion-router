"""WebSocket -> OSC sender for Realtime Motion Router.

Milestone v0.2:
- Read /ws/metrics JSON from realtime-dance-analysis.
- Forward all nine current motion metrics as OSC messages.
"""

import argparse
import asyncio
import json

import websockets
from pythonosc.udp_client import SimpleUDPClient


METRIC_NAMES = (
    "energy",
    "sync_velocity",
    "sync_correlation",
    "expansion",
    "curvature",
    "height",
    "sway",
    "torque",
    "jerk",
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Forward motion metrics from a WebSocket source to an OSC receiver."
    )
    parser.add_argument(
        "--source",
        default="ws://127.0.0.1:8000/ws/metrics",
        help="WebSocket metrics source URL.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Receiver IP address, for example 192.168.50.20.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Receiver UDP port. Default: 9000.",
    )
    return parser.parse_args()


async def forward_metrics(source, target, port):
    osc_client = SimpleUDPClient(target, port)

    print(f"WebSocket source: {source}")
    print(f"OSC target:       {target}:{port}")
    print("OSC addresses:")
    for metric_name in METRIC_NAMES:
        print(f"  /motion/{metric_name}")
    print("Connecting...")

    async with websockets.connect(source) as websocket:
        print("Connected. Press Ctrl+C to stop.")

        async for message in websocket:
            try:
                metrics = json.loads(message)
            except json.JSONDecodeError:
                continue

            sent_values = {}

            for metric_name in METRIC_NAMES:
                value = metrics.get(metric_name)
                if value is None:
                    continue

                try:
                    value = float(value)
                except (TypeError, ValueError):
                    continue

                osc_client.send_message(f"/motion/{metric_name}", value)
                sent_values[metric_name] = value

            if sent_values:
                summary = " | ".join(
                    f"{name}={sent_values[name]:.3f}"
                    for name in METRIC_NAMES
                    if name in sent_values
                )
                print(f"\rSent {summary}", end="", flush=True)


async def main():
    args = parse_args()
    await forward_metrics(args.source, args.target, args.port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSender stopped.")
