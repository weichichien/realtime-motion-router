"""OSC receiver for Realtime Motion Router.

Milestone v0.3:
- Read receiver listen host and port from config/config.json.
- Listen for the nine current motion metrics over OSC/UDP.
- Print one complete metric snapshot after each received jerk value.
"""

import argparse
import json
from pathlib import Path

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


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
latest_metrics = {}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Receive and print Realtime Motion Router OSC metrics."
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
        host = config["receiver"]["listen_host"]
        port = int(config["receiver"]["listen_port"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Invalid configuration. Required fields: "
            "receiver.listen_host, receiver.listen_port"
        ) from error

    return host, port


def receive_metric(address, *values):
    if not values:
        return

    metric_name = address.rsplit("/", 1)[-1]
    if metric_name not in METRIC_NAMES:
        return

    try:
        value = float(values[0])
    except (TypeError, ValueError):
        return

    latest_metrics[metric_name] = value

    if metric_name == "jerk" and all(name in latest_metrics for name in METRIC_NAMES):
        summary = " | ".join(
            f"{name}={latest_metrics[name]:.3f}" for name in METRIC_NAMES
        )
        print(summary)


def main():
    args = parse_args()
    host, port = load_config(args.config)

    dispatcher = Dispatcher()
    for metric_name in METRIC_NAMES:
        dispatcher.map(f"/motion/{metric_name}", receive_metric)

    server = ThreadingOSCUDPServer((host, port), dispatcher)

    print(f"Listening for OSC on {host}:{port}")
    print("Expected addresses:")
    for metric_name in METRIC_NAMES:
        print(f"  /motion/{metric_name}")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReceiver stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"Configuration error: {error}")
