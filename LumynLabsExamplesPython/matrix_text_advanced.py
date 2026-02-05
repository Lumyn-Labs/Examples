#!/usr/bin/env python3
"""
Matrix Text (Advanced)

Demonstrates the improved matrix text features added in SDK 4.2/4.3:
  - Font selection
  - Alignment for static text
  - Smooth scrolling, ping-pong, no-scroll
  - Background color
  - Vertical offset

Usage:
    python examples/matrix_text_advanced.py --port COM3 --zone matrix_display
"""

import argparse
import time

import lumyn_sdk
from lumyn_sdk import ConnectorX


def main() -> None:
    parser = argparse.ArgumentParser(description="Matrix Text (Advanced)")
    parser.add_argument("--port", required=False,
                        help="Serial port (e.g., COM3)")
    parser.add_argument("--zone", default="matrix_display",
                        help="Matrix zone id (default: matrix_display)")
    parser.add_argument("--list-ports", action="store_true",
                        help="List available serial ports and exit")
    args = parser.parse_args()

    if args.list_ports:
        print("Available serial ports:")
        for port in lumyn_sdk.list_available_ports():
            print(f"  {port}")
        return

    if not args.port:
        print("Error: --port is required (use --list-ports to see available ports)")
        return

    cx = ConnectorX()
    print(f"Connecting to {args.port}...")
    if not cx.connect(args.port):
        print("Failed to connect!")
        return

    print("Connected.")
    leds = cx.leds

    zone = args.zone
    print(f"Using matrix zone: {zone}")

    # Example 1: Smooth scrolling with background, font, and ping-pong
    print("Example 1: smooth scrolling, ping-pong, background")
    try:
        (leds.set_text("HELLO LUMYN")
             .for_zone(zone)
             .with_color((255, 200, 0))
             .with_background_color((10, 10, 40))
             .with_font(lumyn_sdk.MatrixTextFont.FREE_SANS_BOLD_12)
             .with_direction(lumyn_sdk.MatrixTextScrollDirection.LEFT)
             .with_delay(30)
             .smooth_scroll(True)
             .ping_pong(True)
             .run_once(False))
    except Exception as exc:
        print(f"Matrix text advanced features not available: {exc}")
        return

    time.sleep(6)

    # Example 2: Static centered text with alignment + y offset
    print("Example 2: static centered text with offset")
    (leds.set_text("STATIC")
         .for_zone(zone)
         .with_color((0, 255, 120))
         .with_background_color((0, 0, 0))
         .with_font(lumyn_sdk.MatrixTextFont.TOM_THUMB)
         .with_align(lumyn_sdk.MatrixTextAlign.CENTER)
         .no_scroll(True)
         .with_y_offset(-2)
         .run_once(False))

    time.sleep(4)

    # Example 3: Classic scrolling without background
    print("Example 3: classic scrolling")
    (leds.set_text("GOOD LUCK!")
         .for_zone(zone)
         .with_color((255, 0, 0))
         .with_font(lumyn_sdk.MatrixTextFont.BUILTIN)
         .with_direction(lumyn_sdk.MatrixTextScrollDirection.RIGHT)
         .with_delay(60)
         .smooth_scroll(False)
         .ping_pong(False)
         .run_once(False))

    time.sleep(6)

    print("Done.")


if __name__ == "__main__":
    main()
