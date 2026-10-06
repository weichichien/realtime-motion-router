"""WebSocket -> OSC sender for Realtime Motion Router.

Milestone v0.3:
- Read WebSocket source and OSC target from config/config.json.
- Forward all nine current motion metrics as OSC messages.
"""

import argparse
import asyncio
import json
from pathlib import Path

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

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "config.json"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Forward motion metrics from a WebSocket source to an OSC receiver."
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to JSON configuration file. Default: config/config.json",
    )
    return parser.parse_args()


def load_config(config_path):
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            f"Copy {path.parent / 'config.example.json'} to {path} and edit it first."
        )

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    try:
        source = config["source"]["websocket_url"]
        target = config["sender"]["target_ip"]
        port = int(config["sender"]["target_port"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Invalid configuration. Required fields: "
            "source.websocket_url, sender.target_ip, sender.target_port"
        ) from error

    return source, target, port


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
    source, target, port = load_config(args.config)
    await forward_metrics(source, target, port)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSender stopped.")
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}")
