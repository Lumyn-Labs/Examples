#!/usr/bin/env python3
"""
Basic handshake example using the Lumyn SDK Python package.

Usage:
  python -m lumyn_sdk.examples.handshake_basic --port /dev/ttyACM0
or
  python examples/handshake_basic.py --port /dev/ttyACM0
"""

import argparse
import sys
from typing import Optional

import lumyn_sdk
from lumyn_sdk.serial_adapter.pyserialio import PySerialIO


class _Handler(lumyn_sdk.transmission.ILumynTransmissionHandler):
    def HandleEvent(self, event):
        print(f"[event] {getattr(event, 'type', 'unknown')}")

    def HandleTransmission(self, transmission):
        pass


def _do_handshake(port: str, timeout_ms: int) -> Optional[object]:
    handler = _Handler()
    listener = lumyn_sdk.transmission.TransmissionPortListener(handler)

    serial_io = PySerialIO(port)

    def handle_serial_data(data, length):
        try:
            listener.ingressBytes(data)
        except Exception as e:  # noqa: BLE001
            print(f"serial handler error: {e}", file=sys.stderr)

    serial_io.setReadCallback(handle_serial_data)
    listener.setWriteCallback(lambda data: serial_io.writeBytes(data))

    listener.Init()
    serial_io.start_reading()

    try:
        request = lumyn_sdk.request.Request()
        request.type = lumyn_sdk.request.RequestType.Handshake
        request.handshake.hostSource = lumyn_sdk.request.HostConnectionSource.Roborio

        response = listener.SendRequest(request, timeout_ms)
        return response
    finally:
        if hasattr(serial_io, "stop_reading"):
            serial_io.stop_reading()
        serial_io.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Lumyn SDK handshake example")
    parser.add_argument("--port", required=True, help="Serial port path (e.g., /dev/ttyACM0)")
    parser.add_argument("--timeout", type=int, default=5000, help="Request timeout in ms")
    args = parser.parse_args()

    try:
        resp = _do_handshake(args.port, args.timeout)
    except Exception as e:  # noqa: BLE001
        print(f"handshake error: {e}", file=sys.stderr)
        return 2

    if resp is None:
        print("handshake: no response (timeout)")
        return 1

    print("handshake: response received")
    if hasattr(resp, "type"):
        print(f"  type: {resp.type}")
    if hasattr(resp, "success"):
        print(f"  success: {resp.success}")
    if hasattr(resp, "data") and getattr(resp, "data"):
        try:
            print(f"  data: {resp.data.hex()}")
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


