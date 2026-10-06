"""WebSocket -> OSC sender for Realtime Motion Router.

Milestone v0.4:
- Read motion source and OSC output settings from config/config.json.
- Forward all nine current motion metrics as OSC messages.
- Fan out every metric frame to every configured OSC output.
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
        description="Forward motion metrics from a WebSocket source to OSC receivers."
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
        source = str(config["motion_source"]["websocket_url"])
        raw_outputs = config["osc_outputs"]

        if not isinstance(raw_outputs, list) or not raw_outputs:
            raise ValueError("osc_outputs must contain at least one destination.")

        outputs = []
        for index, output in enumerate(raw_outputs):
            if not isinstance(output, dict):
                raise ValueError(f"osc_outputs[{index}] must be an object.")

            output_name = str(output.get("name", f"OSC receiver {index + 1}"))
            destination_ip = str(output["destination_ip"])
            destination_port = int(output["destination_port"])

            if not destination_ip:
                raise ValueError(
                    f"osc_outputs[{index}].destination_ip must not be empty."
                )
            if not 1 <= destination_port <= 65535:
                raise ValueError(
                    f"osc_outputs[{index}].destination_port must be between 1 and 65535."
                )

            outputs.append(
                {
                    "name": output_name,
                    "destination_ip": destination_ip,
                    "destination_port": destination_port,
                }
            )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Invalid configuration. Required fields: "
            "motion_source.websocket_url and at least one osc_outputs item with "
            "destination_ip and destination_port. "
            "If your config still uses source/sender/receiver, recreate it from "
            "config/config.example.json."
        ) from error

    return source, outputs


def create_osc_outputs(outputs):
    configured_outputs = []

    for output in outputs:
        configured_outputs.append(
            {
                **output,
                "client": SimpleUDPClient(
                    output["destination_ip"],
                    output["destination_port"],
                ),
            }
        )

    return configured_outputs


async def forward_metrics(source, outputs):
    configured_outputs = create_osc_outputs(outputs)

    print(f"Motion source:     {source}")
    print(f"OSC outputs:       {len(configured_outputs)}")
    for index, output in enumerate(configured_outputs, start=1):
        print(
            f"  {index}. {output['name']} -> "
            f"{output['destination_ip']}:{output['destination_port']}"
        )

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

                address = f"/motion/{metric_name}"
                for output in configured_outputs:
                    output["client"].send_message(address, value)

                sent_values[metric_name] = value

            if sent_values:
                summary = " | ".join(
                    f"{name}={sent_values[name]:.3f}"
                    for name in METRIC_NAMES
                    if name in sent_values
                )
                print(
                    f"\rSent to {len(configured_outputs)} output(s): {summary}",
                    end="",
                    flush=True,
                )


async def main():
    args = parse_args()
    source, outputs = load_config(args.config)
    await forward_metrics(source, outputs)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSender stopped.")
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}")
