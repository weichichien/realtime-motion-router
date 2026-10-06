"""Minimal WebSocket -> OSC sender for Realtime Motion Router.

Milestone v0.1:
- Read /ws/metrics JSON from realtime-dance-analysis.
- Extract only the "energy" metric.
- Send it as OSC address /motion/energy.
"""

import argparse
import asyncio
import json

import websockets
from pythonosc.udp_client import SimpleUDPClient


def parse_args():
    parser = argparse.ArgumentParser(
        description="Forward the energy metric from a WebSocket source to an OSC receiver."
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


async def forward_energy(source, target, port):
    osc_client = SimpleUDPClient(target, port)

    print(f"WebSocket source: {source}")
    print(f"OSC target:       {target}:{port}")
    print("OSC address:      /motion/energy")
    print("Connecting...")

    async with websockets.connect(source) as websocket:
        print("Connected. Press Ctrl+C to stop.")

        async for message in websocket:
            try:
                metrics = json.loads(message)
            except json.JSONDecodeError:
                continue

            energy = metrics.get("energy")
            if energy is None:
                continue

            try:
                energy = float(energy)
            except (TypeError, ValueError):
                continue

            osc_client.send_message("/motion/energy", energy)
            print(f"\rSent /motion/energy {energy:.6f}", end="", flush=True)


async def main():
    args = parse_args()
    await forward_energy(args.source, args.target, args.port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSender stopped.")
