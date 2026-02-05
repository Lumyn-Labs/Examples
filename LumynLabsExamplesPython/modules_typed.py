"""
Example usage of typed module helpers that mirror the Java vendordep API.
"""

import argparse
import time

from lumyn_sdk import (
    AnalogInputModule,
    ConnectorX,
    DigitalInputModule,
    VL53L1XModule,
    list_available_ports,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Modules typed example")
    parser.add_argument("--port", required=False, help="Serial port (e.g., /dev/ttyUSB0 or COM3)")
    parser.add_argument("--list-ports", action="store_true", help="List available serial ports and exit")
    args = parser.parse_args()

    if args.list_ports:
        print("Available serial ports:")
        for p in list_available_ports():
            print(f"  {p}")
        return 0

    if not args.port:
        print("Error: --port is required (use --list-ports to see available ports)")
        return 1

    cx = ConnectorX()
    if not cx.connect(args.port):
        print("Failed to connect to device")
        print("Use --list-ports to see available serial ports")
        return 1

    dio = DigitalInputModule(cx, "digital-1")
    dio.on_update(lambda payload: print(f"DIO state: {'HIGH' if payload.state else 'LOW'}"))
    dio.start()

    tof = VL53L1XModule(cx, "tof-1")
    tof.on_update(lambda payload: print(f"Distance: {payload.dist} mm") if payload.valid else None)
    tof.start()

    analog = AnalogInputModule(cx, "analog-1")
    analog.on_update(lambda payload: print(f"Analog raw={payload.raw_value} scaled={payload.scaled_value}"))
    analog.start()

    try:
        print("Press Ctrl+C to exit...")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        dio.stop()
        tof.stop()
        analog.stop()
        cx.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
