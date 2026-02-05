#!/usr/bin/env python3
"""
ConnectorX Usage Examples

This example demonstrates the fundamental operations of the Lumyn ConnectorX SDK
for the ConnectorX device (1 channel).

For multi-channel/matrix support, see connectorx_animate.py

Device Configuration:
    See example_device_config_basic.json for the config used by this example.
    ConnectorX has 1 channel with a single zone named "main".

Usage:
    python examples/connectorx_basic.py --port COM3
    python examples/connectorx_basic.py --port /dev/ttyACM0
"""

import argparse
import time
import sys
from typing import Any

import lumyn_sdk
from lumyn_sdk import ConnectorX, Animation
from lumyn_sdk.interfaces.i_event_callback import IEventCallback
from lumyn_sdk.interfaces.i_module_data_callback import IModuleDataCallback
from lumyn_sdk.domain.event import Event
from lumyn_sdk.domain.module.new_data_info import NewDataInfo


# =============================================================================
# Configuration - Matches example_device_config_basic.json
# =============================================================================

# ConnectorX has 1 channel with these zones:
ZONE_MAIN = "main"          # The LED strip (144 LEDs)

# Groups defined in config:
GROUP_ALL = "all_leds"      # Contains: main

# Sequences defined in config:
SEQ_STARTUP = "startup"
SEQ_ALLIANCE_RED = "alliance_red"
SEQ_ALLIANCE_BLUE = "alliance_blue"


# =============================================================================
# Event Handler - Receives device events
# =============================================================================

class MyEventHandler(IEventCallback):
    """Handle events from the ConnectorX device."""

    def handle_event(self, event: Event) -> None:
        """Called when an event is received from the device."""
        event_type = event.type if hasattr(event, 'type') else 'unknown'
        print(f"[Event] Type: {event_type}")

        # Handle specific event types
        if event_type == lumyn_sdk.EventType.Connected:
            print("  -> Device connected!")
        elif event_type == lumyn_sdk.EventType.Disconnected:
            print("  -> Device disconnected!")
        elif event_type == lumyn_sdk.EventType.Error:
            print("  -> Error event received")


# =============================================================================
# Module Data Handler - Receives sensor/module data
# =============================================================================

class MyModuleHandler(IModuleDataCallback):
    """Handle module data from sensors (potentiometers, buttons, TOF, etc.)."""

    def handle_data(self, info: NewDataInfo) -> None:
        """Called when new module data is available."""
        print(f"[Module Data] New data received")
        # Process sensor data here
        # info contains module_id, data_type, and the actual data


# =============================================================================
# Example 1: Basic Connection and Color Setting
# =============================================================================

def example_basic_colors(cx: ConnectorX) -> None:
    """
    Demonstrate setting solid colors on the main LED zone.

    This is the simplest way to control LEDs - just set a color.
    """
    print("\n=== Example 1: Basic Colors ===")

    # Get LED handler (public API)
    leds = cx.leds

    # Set main zone to red
    print(f"Setting '{ZONE_MAIN}' to RED...")
    leds.set_color(ZONE_MAIN, (255, 0, 0))
    time.sleep(1.0)

    # Set main zone to green
    print(f"Setting '{ZONE_MAIN}' to GREEN...")
    leds.set_color(ZONE_MAIN, (0, 255, 0))
    time.sleep(1.0)

    # Set main zone to blue
    print(f"Setting '{ZONE_MAIN}' to BLUE...")
    leds.set_color(ZONE_MAIN, (0, 0, 255))
    time.sleep(1.0)

    # Set a custom color (orange)
    print(f"Setting '{ZONE_MAIN}' to ORANGE...")
    leds.set_color(ZONE_MAIN, (255, 165, 0))
    time.sleep(1.0)


# =============================================================================
# Example 2: Built-in Animations
# =============================================================================

def example_animations(cx: ConnectorX) -> None:
    """
    Demonstrate running built-in animations.

    The SDK provides 27 built-in animations that run on the device.
    """
    print("\n=== Example 2: Built-in Animations ===")

    # Get LED handler (public API)
    leds = cx.leds

    # Rainbow animation - cycles through all colors
    print("Running RAINBOW ROLL animation...")
    leds.set_animation(
        ZONE_MAIN,
        Animation.RainbowRoll,
        (0, 0, 0),  # Color not used for rainbow
        50  # Delay in ms between frames
    )
    time.sleep(3.0)

    # Breathing animation - fades in and out
    print("Running BREATHE animation (blue)...")
    leds.set_animation(
        ZONE_MAIN,
        Animation.Breathe,
        (0, 0, 255),  # Blue
        30  # Faster breathing
    )
    time.sleep(3.0)

    # Blink animation
    print("Running BLINK animation (red)...")
    leds.set_animation(
        ZONE_MAIN,
        Animation.Blink,
        (255, 0, 0),  # Red
        500  # 500ms on/off
    )
    time.sleep(3.0)

    # Chase animation - LEDs light up in sequence
    print("Running CHASE animation (green)...")
    leds.set_animation(
        ZONE_MAIN,
        Animation.Chase,
        (0, 255, 0),  # Green
        50
    )
    time.sleep(3.0)

    # Fire animation - simulates fire effect
    print("Running FIRE animation...")
    leds.set_animation(
        ZONE_MAIN,
        Animation.Fire,
        (255, 100, 0),  # Orange base
        30
    )
    time.sleep(3.0)


# =============================================================================
# Example 3: Using Animation Sequences
# =============================================================================

def example_sequences(cx: ConnectorX) -> None:
    """
    Demonstrate running pre-configured animation sequences.

    Sequences are defined in the device config and run multiple
    animation steps automatically.
    """
    print("\n=== Example 3: Animation Sequences ===")

    # Get LED handler (public API)
    leds = cx.leds

    # Run the startup sequence
    print(f"Running '{SEQ_STARTUP}' sequence...")
    leds.set_animation_sequence(ZONE_MAIN, SEQ_STARTUP)
    time.sleep(4.0)

    # Set alliance colors using sequences
    print(f"Running '{SEQ_ALLIANCE_RED}' sequence...")
    leds.set_animation_sequence(ZONE_MAIN, SEQ_ALLIANCE_RED)
    time.sleep(2.0)

    print(f"Running '{SEQ_ALLIANCE_BLUE}' sequence...")
    leds.set_animation_sequence(ZONE_MAIN, SEQ_ALLIANCE_BLUE)
    time.sleep(2.0)


# =============================================================================
# Example 4: All Available Animations Demo
# =============================================================================

def example_all_animations(cx: ConnectorX) -> None:
    """
    Cycle through all 27 available animations.
    """
    print("\n=== Example 4: All Animations Demo ===")

    # Get LED handler (public API)
    leds = cx.leds

    animations = [
        (Animation.Fill, "Fill", (255, 255, 255)),
        (Animation.Blink, "Blink", (255, 0, 0)),
        (Animation.Breathe, "Breathe", (0, 255, 0)),
        (Animation.RainbowRoll, "Rainbow Roll", (0, 0, 0)),
        (Animation.SineRoll, "Sine Roll", (0, 0, 255)),
        (Animation.Chase, "Chase", (255, 255, 0)),
        (Animation.FadeIn, "Fade In", (255, 0, 255)),
        (Animation.FadeOut, "Fade Out", (0, 255, 255)),
        (Animation.RainbowCycle, "Rainbow Cycle", (0, 0, 0)),
        (Animation.AlternateBreathe, "Alternate Breathe", (255, 100, 0)),
        (Animation.GrowingBreathe, "Growing Breathe", (100, 0, 255)),
        (Animation.Comet, "Comet", (255, 255, 255)),
        (Animation.Sparkle, "Sparkle", (255, 255, 255)),
        (Animation.Fire, "Fire", (255, 100, 0)),
        (Animation.Scanner, "Scanner", (255, 0, 0)),
        (Animation.TheaterChase, "Theater Chase", (255, 255, 0)),
        (Animation.Twinkle, "Twinkle", (255, 255, 255)),
        (Animation.Meteor, "Meteor", (100, 100, 255)),
        (Animation.Wave, "Wave", (0, 255, 100)),
        (Animation.Pulse, "Pulse", (255, 0, 100)),
        (Animation.Larson, "Larson Scanner", (255, 0, 0)),
        (Animation.Ripple, "Ripple", (0, 100, 255)),
        (Animation.Confetti, "Confetti", (255, 255, 255)),
        (Animation.Lava, "Lava", (255, 50, 0)),
        (Animation.Plasma, "Plasma", (100, 0, 255)),
        (Animation.Heartbeat, "Heartbeat", (255, 0, 50)),
    ]

    for animation, name, color in animations:
        print(f"  Playing: {name}")
        leds.set_animation(
            ZONE_MAIN,
            animation,
            color,
            40
        )
        time.sleep(2.0)

    print("Animation demo complete!")


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="ConnectorX Usage Examples (1 channel)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Device Configuration:
    This example uses example_device_config_basic.json which defines:
    - 1 channel with 144 LEDs
    - 1 zone: "main"
    - 1 group: "all_leds"
    - Sequences: startup, alliance_red, alliance_blue

Examples:
    python examples/connectorx_basic.py --port COM3
    python examples/connectorx_basic.py --port /dev/ttyACM0 --example colors
    python examples/connectorx_basic.py --port COM3 --example all-animations
        """
    )
    parser.add_argument("--port", required=True,
                        help="Serial port (e.g., COM3 or /dev/ttyACM0)")
    parser.add_argument(
        "--example",
        choices=["colors", "animations",
                 "sequences", "all-animations", "all"],
        default="all",
        help="Which example to run (default: all)"
    )

    args = parser.parse_args()

    print(f"Lumyn SDK v{lumyn_sdk.__version__}")
    print(f"Connecting to {args.port}...")
    print("Device: ConnectorX (1 channel)")

    # Create ConnectorX instance with callbacks
    event_handler = MyEventHandler()
    module_handler = MyModuleHandler()

    cx = ConnectorX()
    cx.add_event_callback(event_handler)
    cx.modules.register_module("test", module_handler)

    try:
        # Connect to the device
        if not cx.connect(args.port):
            print("Failed to connect to device!", file=sys.stderr)
            return 1

        print("Connected successfully!")

        # Run requested examples
        if args.example in ("colors", "all"):
            example_basic_colors(cx)

        if args.example in ("animations", "all"):
            example_animations(cx)

        if args.example in ("sequences", "all"):
            example_sequences(cx)

        if args.example == "all-animations":
            example_all_animations(cx)

        print("\nExamples complete!")
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    finally:
        cx.disconnect()


if __name__ == "__main__":
    sys.exit(main())
