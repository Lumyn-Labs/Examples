#!/usr/bin/env python3
"""
ConnectorX Animate - Advanced Animation and Multi-Channel Control

This example demonstrates advanced features of the ConnectorX Animate device.
Note: ConnectorXAnimate is for LED-only devices (USB-only, no module support).
For devices with module/sensor support, use ConnectorX instead.

Features demonstrated:
- 4-channel LED control
- Multiple zones per channel
- Zone groups
- Animation sequences
- LED matrix display
- Robot state-based patterns

Device Configuration:
    See example_device_config.json for the config used by this example.
    ConnectorX Animate has 4 channels supporting:
    - Multiple LED strips across channels
    - LED matrix displays
    - Sensor integration

Usage:
    python examples/connectorx_animate.py --port COM3
    python examples/connectorx_animate.py --port /dev/ttyACM0 --demo robot-states
"""

import argparse
import time
import sys
from enum import Enum, auto
from typing import Callable, List, Tuple

import lumyn_sdk
from lumyn_sdk import ConnectorXAnimate, Animation


# =============================================================================
# Configuration - Matches example_device_config.json (4-channel Animate)
# =============================================================================

# Channel 1: Front strips (120 LEDs total)
ZONE_FRONT_LEFT = "front_left"      # 60 LEDs
ZONE_FRONT_RIGHT = "front_right"    # 60 LEDs

# Channel 2: Rear strips (120 LEDs total)
ZONE_REAR_LEFT = "rear_left"        # 60 LEDs
ZONE_REAR_RIGHT = "rear_right"      # 60 LEDs

# Channel 3: Underglow (72 LEDs)
ZONE_UNDERGLOW = "underglow"        # 72 LEDs, reversed

# Channel 4: Matrix display (8x5 = 40 LEDs)
ZONE_MATRIX = "matrix_display"      # 8 rows x 5 cols

# Groups defined in config:
GROUP_ALL = "all_leds"              # All strip zones (not matrix)
GROUP_FRONT = "front_leds"          # front_left + front_right
GROUP_REAR = "rear_leds"            # rear_left + rear_right
GROUP_LEFT = "left_side"            # front_left + rear_left
GROUP_RIGHT = "right_side"          # front_right + rear_right

# Sequences defined in config:
SEQ_STARTUP = "startup"
SEQ_ERROR_FLASH = "error_flash"
SEQ_ALLIANCE_RED = "alliance_red"
SEQ_ALLIANCE_BLUE = "alliance_blue"
SEQ_AUTO_MODE = "auto_mode"
SEQ_DISABLED = "disabled"

# All strip zones for iteration
ALL_STRIP_ZONES = [
    ZONE_FRONT_LEFT, ZONE_FRONT_RIGHT,
    ZONE_REAR_LEFT, ZONE_REAR_RIGHT,
    ZONE_UNDERGLOW
]

# Corner zones for sequential patterns
CORNER_ZONES = [
    ZONE_FRONT_LEFT, ZONE_FRONT_RIGHT,
    ZONE_REAR_RIGHT, ZONE_REAR_LEFT  # Clockwise order
]


# =============================================================================
# Robot State Definitions (FRC-style)
# =============================================================================

class RobotState(Enum):
    """Robot operational states for LED indication."""
    DISABLED = auto()
    AUTONOMOUS = auto()
    TELEOP = auto()
    TEST = auto()
    ESTOPPED = auto()
    CONNECTED = auto()
    DISCONNECTED = auto()
    ERROR = auto()


# =============================================================================
# Animation Presets
# =============================================================================

class AnimationPresets:
    """Pre-configured animation settings for common use cases."""

    @staticmethod
    def alliance_red() -> tuple[int, int, int]:
        """Red alliance colors."""
        return (255, 0, 0)

    @staticmethod
    def alliance_blue() -> tuple[int, int, int]:
        """Blue alliance colors."""
        return (0, 0, 255)

    @staticmethod
    def warning_orange() -> tuple[int, int, int]:
        """Warning/caution color."""
        return (255, 165, 0)

    @staticmethod
    def success_green() -> tuple[int, int, int]:
        """Success/ready color."""
        return (0, 255, 0)

    @staticmethod
    def error_red() -> tuple[int, int, int]:
        """Error indication."""
        return (255, 0, 0)

    @staticmethod
    def neutral_white() -> tuple[int, int, int]:
        """Neutral/default color."""
        return (255, 255, 255)

    @staticmethod
    def disabled_dim() -> tuple[int, int, int]:
        """Dim color for disabled state."""
        return (50, 50, 50)


# =============================================================================
# State-Based LED Controller
# =============================================================================

class RobotLEDController:
    """
    Controls LEDs based on robot state.

    This class provides a high-level interface for setting LED patterns
    based on robot operational states, designed for FRC robots using
    the ConnectorX Animate with 4 channels.
    """

    def __init__(self, cx: ConnectorXAnimate, group: str = GROUP_ALL) -> None:
        self.cx: ConnectorXAnimate = cx
        self.group: str = group
        self.leds = cx.leds
        self.current_state: RobotState | None = None
        self.alliance_color: tuple[int, int,
                                   int] = AnimationPresets.neutral_white()

    def set_alliance(self, is_red: bool) -> None:
        """Set the alliance color for state-aware animations."""
        self.alliance_color = (
            AnimationPresets.alliance_red() if is_red
            else AnimationPresets.alliance_blue()
        )

    def set_state(self, state: RobotState) -> None:
        """
        Update LEDs based on robot state.

        This is the main method to call from your robot code.
        Uses group control to update all zones at once.
        """
        if state == self.current_state:
            return  # No change needed

        self.current_state = state

        if state == RobotState.DISABLED:
            self._show_disabled()
        elif state == RobotState.AUTONOMOUS:
            self._show_autonomous()
        elif state == RobotState.TELEOP:
            self._show_teleop()
        elif state == RobotState.TEST:
            self._show_test()
        elif state == RobotState.ESTOPPED:
            self._show_estopped()
        elif state == RobotState.CONNECTED:
            self._show_connected()
        elif state == RobotState.DISCONNECTED:
            self._show_disconnected()
        elif state == RobotState.ERROR:
            self._show_error()

    def _show_disabled(self) -> None:
        """Disabled: Use the pre-configured disabled sequence."""
        print(f"  LED State: DISABLED")
        self.leds.set_group_animation_sequence(self.group, SEQ_DISABLED)

    def _show_autonomous(self) -> None:
        """Autonomous: Use the auto_mode sequence."""
        print(f"  LED State: AUTONOMOUS")
        self.leds.set_group_animation_sequence(self.group, SEQ_AUTO_MODE)

    def _show_teleop(self) -> None:
        """Teleop: Solid alliance color on all zones."""
        print(f"  LED State: TELEOP")
        self.leds.set_group_color(self.group, self.alliance_color)

    def _show_test(self) -> None:
        """Test: Rainbow pattern."""
        print(f"  LED State: TEST")
        self.leds.set_group_animation(
            self.group,
            Animation.RainbowCycle,
            AnimationPresets.neutral_white(),
            40
        )

    def _show_estopped(self) -> None:
        """E-Stopped: Fast red blink."""
        print(f"  LED State: E-STOPPED")
        self.leds.set_group_animation(
            self.group,
            Animation.Blink,
            AnimationPresets.error_red(),
            100  # Fast blink
        )

    def _show_connected(self) -> None:
        """Connected: Run startup sequence."""
        print(f"  LED State: CONNECTED")
        self.leds.set_group_animation_sequence(self.group, SEQ_STARTUP)

    def _show_disconnected(self) -> None:
        """Disconnected: Slow orange pulse."""
        print(f"  LED State: DISCONNECTED")
        self.leds.set_group_animation(
            self.group,
            Animation.Pulse,
            AnimationPresets.warning_orange(),
            80
        )

    def _show_error(self) -> None:
        """Error: Run error sequence."""
        print(f"  LED State: ERROR")
        self.leds.set_group_animation_sequence(self.group, SEQ_ERROR_FLASH)


# =============================================================================
# Demo: Robot State Simulation
# =============================================================================

def demo_robot_states(cx: ConnectorXAnimate) -> None:
    """
    Simulate a robot going through different states.

    This demonstrates how LEDs would look during a typical FRC match
    using the 4-channel ConnectorX Animate configuration.
    """
    print("\n=== Robot State Simulation ===")
    print("Using group control to update all 4 channels at once")

    controller = RobotLEDController(cx, GROUP_ALL)
    controller.set_alliance(is_red=True)  # Set to red alliance

    states = [
        (RobotState.DISCONNECTED, "Waiting for connection...", 2),
        (RobotState.CONNECTED, "Driver Station connected!", 2),
        (RobotState.DISABLED, "Robot disabled, waiting for match...", 3),
        (RobotState.AUTONOMOUS, "AUTO MODE - Robot running autonomous!", 4),
        (RobotState.TELEOP, "TELEOP - Driver control active!", 4),
        (RobotState.DISABLED, "Match ended, robot disabled", 2),
        (RobotState.TEST, "Entering test mode...", 3),
        (RobotState.ERROR, "Simulating error condition!", 2),
        (RobotState.ESTOPPED, "E-STOP ACTIVATED!", 3),
        (RobotState.DISABLED, "Resetting...", 2),
    ]

    for state, message, duration in states:
        print(f"\n{message}")
        controller.set_state(state)
        time.sleep(duration)

    print("\nState simulation complete!")


# =============================================================================
# Demo: Multi-Channel Zone Control
# =============================================================================

def demo_zone_control(cx: ConnectorXAnimate) -> None:
    """
    Demonstrate independent control of zones across all 4 channels.
    """
    print("\n=== Multi-Channel Zone Control ===")
    print("ConnectorX Animate: 4 channels, 6 zones")

    leds = cx.leds

    # Show zone configuration
    print("\nZone configuration:")
    print("  Channel 1: front_left (60 LEDs), front_right (60 LEDs)")
    print("  Channel 2: rear_left (60 LEDs), rear_right (60 LEDs)")
    print("  Channel 3: underglow (72 LEDs)")
    print("  Channel 4: matrix_display (8x8)")

    # Pattern 1: Sequential channel activation
    print("\nPattern 1: Sequential zone activation...")
    for zone in ALL_STRIP_ZONES:
        print(f"  Activating: {zone}")
        leds.set_animation(
            zone, Animation.FadeIn,
            (0, 255, 0), 30
        )
        time.sleep(0.5)
    time.sleep(1.0)

    # Pattern 2: Left vs Right
    print("\nPattern 2: Left (red) vs Right (blue)...")
    leds.set_group_color(GROUP_LEFT, AnimationPresets.alliance_red())
    leds.set_group_color(GROUP_RIGHT, AnimationPresets.alliance_blue())
    time.sleep(2.0)

    # Pattern 3: Front vs Rear
    print("\nPattern 3: Front (green) vs Rear (purple)...")
    leds.set_group_color(
        GROUP_FRONT, (0, 255, 0))
    leds.set_group_color(
        GROUP_REAR, (128, 0, 255))
    leds.set_color(ZONE_UNDERGLOW,
                   (255, 255, 0))
    time.sleep(2.0)

    # Pattern 4: Clockwise chase around robot
    print("\nPattern 4: Clockwise chase effect...")
    for _ in range(3):
        for zone in CORNER_ZONES:
            leds.set_animation(
                zone, Animation.Pulse,
                (255, 255, 255), 50
            )
            time.sleep(0.3)
    time.sleep(1.0)

    # Pattern 5: Synchronized all channels
    print("\nPattern 5: All zones synchronized rainbow...")
    for zone in ALL_STRIP_ZONES:
        leds.set_animation(
            zone, Animation.RainbowCycle,
            (0, 0, 0), 40
        )
    time.sleep(4.0)


# =============================================================================
# Demo: Animation Sequences
# =============================================================================

def demo_sequences(cx: ConnectorXAnimate) -> None:
    """
    Demonstrate using pre-configured animation sequences.
    """
    print("\n=== Animation Sequences ===")
    print("Running sequences defined in device config")

    leds = cx.leds

    sequences = [
        (SEQ_STARTUP, "Startup sequence", 4),
        (SEQ_ALLIANCE_RED, "Red alliance", 2),
        (SEQ_ALLIANCE_BLUE, "Blue alliance", 2),
        (SEQ_AUTO_MODE, "Autonomous mode", 3),
        (SEQ_DISABLED, "Disabled state", 3),
        (SEQ_ERROR_FLASH, "Error indication", 3),
    ]

    for seq_name, description, duration in sequences:
        print(f"\n  Running: {description} ({seq_name})")
        leds.set_group_animation_sequence(GROUP_ALL, seq_name)
        time.sleep(duration)


# =============================================================================
# Demo: Reactive Effects
# =============================================================================

def demo_reactive_effects(cx: ConnectorXAnimate) -> None:
    """
    Demonstrate reactive LED effects for game events.
    """
    print("\n=== Reactive Effects ===")

    leds = cx.leds

    base_color = (0, 100, 255)
    leds.set_group_color(GROUP_ALL, base_color)
    print("Base state: Blue alliance color")
    time.sleep(1.0)

    # Event: Ball detected by intake
    print("\n[EVENT] Ball detected by intake!")
    leds.set_animation(
        ZONE_FRONT_LEFT, Animation.Pulse,
        (255, 255, 0), 50
    )
    leds.set_animation(
        ZONE_FRONT_RIGHT, Animation.Pulse,
        (255, 255, 0), 50
    )
    time.sleep(1.5)
    leds.set_group_color(GROUP_FRONT, base_color)

    # Event: Ball scored
    print("\n[EVENT] Ball scored!")
    leds.set_group_animation(
        GROUP_ALL, Animation.Comet,
        (0, 255, 0), 30
    )
    time.sleep(2.0)
    leds.set_group_color(GROUP_ALL, base_color)

    # Event: Low battery warning
    print("\n[EVENT] Low battery warning!")
    for _ in range(3):
        leds.set_group_animation(
            GROUP_ALL, Animation.Blink,
            (255, 165, 0), 200
        )
        time.sleep(0.6)
    leds.set_group_color(GROUP_ALL, base_color)

    # Event: Target locked (scanner on front, pulse on rear)
    print("\n[EVENT] Target locked!")
    leds.set_group_animation(
        GROUP_FRONT, Animation.Scanner,
        (255, 0, 0), 40
    )
    leds.set_group_animation(
        GROUP_REAR, Animation.Pulse,
        (255, 0, 0), 60
    )
    time.sleep(2.5)
    leds.set_group_color(GROUP_ALL, base_color)


# =============================================================================
# Demo: Matrix Display
# =============================================================================

def demo_matrix_display(cx: ConnectorXAnimate) -> None:
    """
    Demonstrate LED matrix text display (Channel 4).
    """
    print("\n=== Matrix Display (Channel 4) ===")

    leds = cx.leds

    messages = [
        ("FRC", 2),
        ("2025", 2),
        ("9999", 2),  # Team number from config
        ("GO!", 1),
    ]

    print(f"  Matrix zone: {ZONE_MATRIX} (8 rows x 5 cols)")

    for text, duration in messages:
        print(f"  Displaying: {text}")
        try:
            leds.set_matrix_text(
                ZONE_MATRIX,
                text,
                (0, 255, 0),  # Green text
                lumyn_sdk.MatrixTextScrollDirection.LEFT,
                50  # Scroll speed
            )
        except Exception as e:
            print(f"  Matrix text not supported: {e}")
            return
        time.sleep(duration)


# =============================================================================
# Demo: Underglow Effects
# =============================================================================

def demo_underglow(cx: ConnectorXAnimate) -> None:
    """
    Demonstrate underglow-specific effects (Channel 3).
    """
    print("\n=== Underglow Effects (Channel 3) ===")

    leds = cx.leds

    print(f"  Zone: {ZONE_UNDERGLOW} (72 LEDs, reversed)")

    # Effect 1: Lava flow
    print("\n  Effect 1: Lava flow")
    leds.set_animation(
        ZONE_UNDERGLOW, Animation.Lava,
        (255, 50, 0), 30
    )
    time.sleep(3.0)

    # Effect 2: Plasma
    print("\n  Effect 2: Plasma")
    leds.set_animation(
        ZONE_UNDERGLOW, Animation.Plasma,
        (100, 0, 255), 40
    )
    time.sleep(3.0)

    # Effect 3: Fire
    print("\n  Effect 3: Fire")
    leds.set_animation(
        ZONE_UNDERGLOW, Animation.Fire,
        (255, 100, 0), 30
    )
    time.sleep(3.0)

    # Effect 4: Rainbow
    print("\n  Effect 4: Rainbow Roll")
    leds.set_animation(
        ZONE_UNDERGLOW, Animation.RainbowRoll,
        (0, 0, 0), 20
    )
    time.sleep(3.0)


# =============================================================================
# Main Entry Point
# =============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="ConnectorX Animate - Advanced 4-Channel Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Device Configuration:
    This example uses example_device_config.json which defines:
    - Channel 1: front_left (60), front_right (60)
    - Channel 2: rear_left (60), rear_right (60)
    - Channel 3: underglow (72, reversed)
    - Channel 4: matrix_display (8x5)
    
    Groups: all_leds, front_leds, rear_leds, left_side, right_side
    Sequences: startup, error_flash, alliance_red/blue, auto_mode, disabled

Demos:
    robot-states    - FRC robot state simulation
    zones           - Multi-channel zone control
    sequences       - Pre-configured animation sequences
    reactive        - Game event reactive effects
    matrix          - Matrix text display
    underglow       - Underglow-specific effects
    all             - Run all demos

Examples:
    python examples/connectorx_animate.py --port COM3
    python examples/connectorx_animate.py --port /dev/ttyACM0 --demo robot-states
        """
    )
    parser.add_argument("--port", required=True, help="Serial port")
    parser.add_argument(
        "--demo",
        choices=["robot-states", "zones", "sequences",
                 "reactive", "matrix", "underglow", "all"],
        default="all",
        help="Which demo to run (default: all)"
    )

    args = parser.parse_args()

    print(f"Lumyn SDK v{lumyn_sdk.__version__}")
    print(f"Connecting to {args.port}...")
    print("Device: ConnectorX Animate (4 channels)")

    # Use ConnectorXAnimate for LED-only devices (no module support needed)
    cx = ConnectorXAnimate()

    try:
        if not cx.connect(args.port):
            print("Failed to connect!", file=sys.stderr)
            return 1

        print("Connected!\n")

        if args.demo in ("robot-states", "all"):
            demo_robot_states(cx)

        if args.demo in ("zones", "all"):
            demo_zone_control(cx)

        if args.demo in ("sequences", "all"):
            demo_sequences(cx)

        if args.demo in ("reactive", "all"):
            demo_reactive_effects(cx)

        if args.demo in ("underglow", "all"):
            demo_underglow(cx)

        if args.demo in ("matrix", "all"):
            demo_matrix_display(cx)

        print("\n=== All demos complete! ===")
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted")
        return 0
    finally:
        cx.disconnect()


if __name__ == "__main__":
    sys.exit(main())
