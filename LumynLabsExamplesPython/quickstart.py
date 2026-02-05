#!/usr/bin/env python3
"""
ConnectorX Quick Start

The simplest example to get started with ConnectorX LEDs.

Usage:
    python examples/quickstart.py --port COM3
"""

import argparse
import time
import lumyn_sdk
from lumyn_sdk import ConnectorX, Animation, list_available_ports, SerializeConfigToJson
from lumyn_sdk.interfaces.i_event_callback import IEventCallback
from lumyn_sdk.domain.event.event import Event


# =============================================================================
# Event Handler - Receives device events
# =============================================================================

class QuickstartEventHandler(IEventCallback):
    """Handle events from the ConnectorX device."""

    def handle_event(self, event: Event) -> None:
        """Called when an event is received from the device."""
        event_type = event.type if hasattr(event, 'type') else 'unknown'
        extra_msg = getattr(event, 'extra_message', None)

        # Get human-readable event type name
        try:
            type_name = lumyn_sdk.EventType(event_type).name
        except (ValueError, TypeError):
            type_name = str(event_type)

        # Format the base message
        msg_suffix = f" - '{extra_msg}'" if extra_msg else ""
        print(f"[Event] {type_name}{msg_suffix}")

        # Handle specific event types
        if event_type == lumyn_sdk.EventType.Connected:
            print("  -> Device connected!")
        elif event_type == lumyn_sdk.EventType.Disconnected:
            print("  -> Device disconnected!")
        elif event_type == lumyn_sdk.EventType.Error:
            error_info = getattr(event, 'custom_data', None)
            error_type = getattr(event, 'custom_type', 0)
            print(f"  -> Error event: type={error_type}, data={error_info}")
        elif event_type == lumyn_sdk.EventType.HeartBeat:
            # Heartbeat events are periodic status updates
            pass  # Silently ignore heartbeats
        else:
            print(f"  -> Event data: {event}")


def main():
    parser = argparse.ArgumentParser(description="ConnectorX Quick Start")
    parser.add_argument("--port", required=False,
                        help="Serial port (e.g., COM3)")
    parser.add_argument("--zone", default="strip",
                        help="Zone name (default: strip)")
    parser.add_argument("--list-ports", action="store_true",
                        help="List available serial ports and exit")
    args = parser.parse_args()

    # List ports if requested
    if args.list_ports:
        print("Available serial ports:")
        ports = list_available_ports()
        for port in ports:
            print(f"  {port}")
        return

    # Require port if not listing
    if not args.port:
        print("Error: --port is required (use --list-ports to see available ports)")
        return

    # Create and connect
    cx = ConnectorX()

    # Add event handler to see device events
    event_handler = QuickstartEventHandler()
    cx.add_event_callback(event_handler)

    print(f"Connecting to {args.port}...")
    if not cx.connect(args.port):
        print("Failed to connect!")
        print("Use --list-ports to see available serial ports")
        return

    print("Connected to ConnectorX!")

    # Get and display config
    config_obj = cx.request_config()
    if config_obj:
        config_json = SerializeConfigToJson(config_obj)
        print(f'Config on device: {config_json}')
    else:
        print('Config on device: None')

    # Get LED handler (public API)
    leds = cx.leds
    zone = args.zone

    # Run animations with different colors
    print("Red breathe animation...")
    leds.set_animation(zone, Animation.Breathe, (255, 0, 0), 10)
    time.sleep(6)

    print("Green plasma animation...")
    leds.set_animation(zone, Animation.Plasma, (0, 150, 0), 100)
    time.sleep(3)

    print("Blue chase animation...")
    leds.set_animation(zone, Animation.Chase, (0, 0, 255), 50)
    time.sleep(5)

    print("Purple comet animation...")
    leds.set_animation(zone, Animation.Comet, (128, 0, 255), 20)
    time.sleep(3)

    print("Orange sparkle animation...")
    leds.set_animation(zone, Animation.Sparkle, (255, 128, 0), 100)
    time.sleep(3)

    # Rainbow animation (color doesn't matter)
    print("Rainbow roll animation...")
    leds.set_animation(zone, Animation.RainbowCycle, (0, 0, 0), 50)
    time.sleep(3)

    # Direct LED buffer control with delta compression
    print("\nDirect LED buffer test with DirectLED...")

    # Get zone length from config
    import json
    config_obj = cx.request_config()
    num_leds = None
    if config_obj:
        config_str = SerializeConfigToJson(config_obj)
        config = json.loads(config_str)
        channels = config.get('channels', {})
        for channel_key, channel_data in channels.items():
            if isinstance(channel_data, dict):
                for z in channel_data.get('zones', []):
                    if isinstance(z, dict) and z.get('id') == zone:
                        if z.get('type') == 'matrix':
                            num_leds = z.get('rows', 0) * z.get('cols', 0)
                        else:
                            num_leds = z.get('length', 0)
                        print(f"Found zone: {z}")
                        break
            if num_leds:
                break

    if num_leds:
        print(f"Zone '{zone}' has {num_leds} LEDs")

        # Create a DirectLED instance for efficient buffer updates
        # Automatically sends full buffer every 10 frames (for demo purposes)
        direct_led = leds.create_direct_led(
            zone, num_leds=num_leds, full_refresh_interval=10)

        # Frame 0: all red (will be full buffer - first frame)
        buffer = bytearray()
        for i in range(num_leds):
            buffer.extend([255, 0, 0])  # R, G, B
        print("Frame 0: Setting all LEDs to RED (auto: full buffer)...")
        direct_led.force_full_update(bytes(buffer))
        time.sleep(1)

        # Frame 1: all green (will use delta)
        buffer = bytearray()
        for i in range(num_leds):
            buffer.extend([0, 255, 0])  # R, G, B
        print("Frame 1: Setting all LEDs to GREEN (auto: delta)...")
        direct_led.update(bytes(buffer))
        time.sleep(1)

        # Frame 2: alternate red/blue (will use delta)
        buffer = bytearray()
        for i in range(num_leds):
            if i % 2 == 0:
                buffer.extend([255, 0, 0])  # Red
            else:
                buffer.extend([0, 0, 255])  # Blue
        print("Frame 2: Setting alternating RED/BLUE (auto: delta)...")
        direct_led.update(bytes(buffer))
        time.sleep(1)

        # Frames 3-12: animate a moving white pixel
        print("Frames 3-12: Moving white pixel (auto: delta for frames 3-9, full at frame 10)...")
        for frame in range(3, 13):
            buffer = bytearray()
            for i in range(num_leds):
                if i == (frame - 3) % num_leds:
                    buffer.extend([255, 255, 255])  # White pixel
                else:
                    buffer.extend([0, 0, 0])  # Off
            direct_led.update(bytes(buffer))
            time.sleep(0.1)

        print("Filling with black")
        buffer = bytearray()
        for i in range(num_leds):
            buffer.extend([0, 0, 0])  # Off
        direct_led.update(bytes(buffer))
        time.sleep(1)
    else:
        print(f"Could not find zone '{zone}' in config")

    # Turn off with Fill animation (solid color)
    print("\nOff")
    leds.set_animation(zone, Animation.Fill, (0, 0, 0), 0, one_shot=True)
    time.sleep(1)

    cx.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()
