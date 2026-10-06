"""OSC receiver for Realtime Motion Router.

Milestone v0.3:
- Read OSC receiver settings from config/config.json.
- Hide socket-specific 0.0.0.0 behind listen_interface = "all".
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
        listen_interface = str(config["osc_receiver"]["listen_interface"])
        listen_port = int(config["osc_receiver"]["listen_port"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(
            "Invalid configuration. Required fields: "
            "osc_receiver.listen_interface and osc_receiver.listen_port. "
            "If your config still uses source/sender/receiver, recreate it from "
            "config/config.example.json."
        ) from error

    if listen_interface.lower() == "all":
        bind_host = "0.0.0.0"
        display_interface = "all interfaces"
    else:
        bind_host = listen_interface
        display_interface = listen_interface

    return bind_host, display_interface, listen_port


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
    bind_host, display_interface, listen_port = load_config(args.config)

    dispatcher = Dispatcher()
    for metric_name in METRIC_NAMES:
        dispatcher.map(f"/motion/{metric_name}", receive_metric)

    server = ThreadingOSCUDPServer((bind_host, listen_port), dispatcher)

    print(f"Listening for OSC on {display_interface}, port {listen_port}")
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
