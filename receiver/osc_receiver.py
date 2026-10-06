"""Minimal OSC receiver for Realtime Motion Router.

Milestone v0.1:
- Listen for OSC/UDP messages.
- Print /motion/energy values for cross-computer testing.
"""

import argparse

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer


def parse_args():
    parser = argparse.ArgumentParser(
        description="Receive and print the /motion/energy OSC message."
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


def print_energy(address, *values):
    if not values:
        return

    try:
        energy = float(values[0])
        print(f"{address} {energy:.6f}")
    except (TypeError, ValueError):
        print(f"{address} {values[0]}")


def main():
    args = parse_args()

    dispatcher = Dispatcher()
    dispatcher.map("/motion/energy", print_energy)

    server = ThreadingOSCUDPServer((args.host, args.port), dispatcher)

    print(f"Listening for OSC on {args.host}:{args.port}")
    print("Expected address: /motion/energy")
    print("Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nReceiver stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
