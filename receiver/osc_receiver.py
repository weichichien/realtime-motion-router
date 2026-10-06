"""OSC receiver for Realtime Motion Router.

Milestone v0.2:
- Listen for the nine current motion metrics over OSC/UDP.
- Print one complete metric snapshot after each received jerk value.
"""

import argparse

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

latest_metrics = {}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Receive and print the current Realtime Motion Router OSC metrics."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Local interface to listen on. Default: 0.0.0.0 (all interfaces).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="UDP port to listen on. Default: 9000.",
    )
    return parser.parse_args()


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

    # The sender transmits metrics in METRIC_NAMES order, with jerk last.
    # Print a complete snapshot once all metrics have been received.
    if metric_name == "jerk" and all(name in latest_metrics for name in METRIC_NAMES):
        summary = " | ".join(
            f"{name}={latest_metrics[name]:.3f}" for name in METRIC_NAMES
        )
        print(summary)


def main():
    args = parse_args()

    dispatcher = Dispatcher()
    for metric_name in METRIC_NAMES:
        dispatcher.map(f"/motion/{metric_name}", receive_metric)

    server = ThreadingOSCUDPServer((args.host, args.port), dispatcher)

    print(f"Listening for OSC on {args.host}:{args.port}")
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
    main()
