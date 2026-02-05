#!/usr/bin/env python3
"""
Configuration Builder - Advanced Example

Demonstrates creating a complex device configuration with:
- Multiple channels
- Strip and matrix zones
- Animation sequences
- Bitmaps/images
- Sensor modules
- Zone groups

Usage:
    python examples/config_builder_advanced.py
    python examples/config_builder_advanced.py --apply COM3
"""

import argparse
import sys
from lumyn_sdk import ConfigBuilder, NetworkType, SerializeConfigToJson, ConnectorX


def create_full_config():
    """Create a full-featured configuration matching example_device_config.json."""
    print("Creating full-featured configuration...")

    config = ConfigBuilder() \
        .ForTeam("9999") \
        .SetNetworkType(NetworkType.USB) \
        \
        .AddChannel(1, "1", 120) \
            .Brightness(100) \
            .AddStripZone("front_left", 60, False, 100) \
            .AddStripZone("front_right", 60, False, 100) \
            .EndChannel() \
        \
        .AddChannel(2, "2", 120) \
            .Brightness(100) \
            .AddStripZone("rear_left", 60, False, 100) \
            .AddStripZone("rear_right", 60, False, 100) \
            .EndChannel() \
        \
        .AddChannel(3, "3", 72) \
            .Brightness(80) \
            .AddStripZone("underglow", 72, True, 80) \
            .EndChannel() \
        \
        .AddChannel(4, "4", 40) \
            .Brightness(100) \
            .AddMatrixZone("matrix_display", 32, 8, 100, 0) \
            .EndChannel() \
        \
        .AddSequence("startup") \
            .AddStep("FadeIn") \
                .WithColor(0, 255, 0) \
                .WithDelay(30) \
                .Reverse(False) \
                .WithRepeat(1) \
                .EndStep() \
            .AddStep("Pulse") \
                .WithColor(0, 255, 0) \
                .WithDelay(50) \
                .Reverse(False) \
                .WithRepeat(2) \
                .EndStep() \
            .AddStep("Fill") \
                .WithColor(0, 255, 0) \
                .WithDelay(-1) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddSequence("error_flash") \
            .AddStep("Blink") \
                .WithColor(255, 0, 0) \
                .WithDelay(100) \
                .Reverse(False) \
                .WithRepeat(4) \
                .EndStep() \
            .AddStep("Breathe") \
                .WithColor(255, 50, 0) \
                .WithDelay(40) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddSequence("alliance_red") \
            .AddStep("Fill") \
                .WithColor(255, 0, 0) \
                .WithDelay(-1) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddSequence("alliance_blue") \
            .AddStep("Fill") \
                .WithColor(0, 0, 255) \
                .WithDelay(-1) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddSequence("auto_mode") \
            .AddStep("Chase") \
                .WithColor(255, 255, 0) \
                .WithDelay(30) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddSequence("disabled") \
            .AddStep("Breathe") \
                .WithColor(50, 50, 50) \
                .WithDelay(10) \
                .Reverse(False) \
                .WithRepeat(0) \
                .EndStep() \
            .EndSequence() \
        \
        .AddBitmap("team_logo") \
            .Static("team_logo.bmp") \
            .EndBitmap() \
        \
        .AddBitmap("happy_eyes") \
            .Animated("happy_eyes", 250) \
            .EndBitmap() \
        \
        .AddModule("distance_sensor", "VL53L1X", 50, "I2C") \
            .WithConfig("address", "0x29") \
            .EndModule() \
        \
        .AddGroup("all_leds") \
            .AddZone("front_left") \
            .AddZone("front_right") \
            .AddZone("rear_left") \
            .AddZone("rear_right") \
            .AddZone("underglow") \
            .EndGroup() \
        \
        .AddGroup("front_leds") \
            .AddZone("front_left") \
            .AddZone("front_right") \
            .EndGroup() \
        \
        .AddGroup("rear_leds") \
            .AddZone("rear_left") \
            .AddZone("rear_right") \
            .EndGroup() \
        \
        .AddGroup("left_side") \
            .AddZone("front_left") \
            .AddZone("rear_left") \
            .EndGroup() \
        \
        .AddGroup("right_side") \
            .AddZone("front_right") \
            .AddZone("rear_right") \
            .EndGroup() \
        \
        .Build()

    print("Full configuration created successfully!")
    return config


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configuration Builder - Advanced Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This example demonstrates creating a complex device configuration with:
- Multiple channels (4 channels)
- Strip and matrix zones
- Animation sequences (6 sequences)
- Bitmaps (static and animated)
- Sensor modules
- Zone groups (5 groups)

Examples:
    python examples/config_builder_advanced.py
    python examples/config_builder_advanced.py --apply COM3
    python examples/config_builder_advanced.py --save full_config.json
        """
    )
    parser.add_argument(
        "--apply",
        help="Apply configuration to device (requires port, e.g., COM3)"
    )
    parser.add_argument(
        "--save",
        help="Save configuration to JSON file"
    )

    args = parser.parse_args()

    # Create configuration
    config = create_full_config()

    # Save to file if requested
    if args.save:
        print(f"\nSaving configuration to {args.save}...")
        with open(args.save, 'w') as f:
            f.write(SerializeConfigToJson(config))
        print(f"Configuration saved to {args.save}")

    # Apply to device if requested
    if args.apply:
        print(f"\nApplying configuration to device at {args.apply}...")
        cx = ConnectorX()
        try:
            if not cx.connect(args.apply):
                print("Failed to connect to device!", file=sys.stderr)
                return 1

            if cx.apply_configuration(config):
                print("Configuration applied successfully!")
            else:
                print("Failed to apply configuration", file=sys.stderr)
                return 1

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
        finally:
            cx.close()
    else:
        # Just print summary
        print("\nConfiguration Summary:")
        print(f"  Channels: {len(config.channels) if config.channels else 0}")
        print(f"  Sequences: {len(config.sequences) if config.sequences else 0}")
        print(f"  Bitmaps: {len(config.bitmaps) if config.bitmaps else 0}")
        print(f"  Modules: {len(config.sensors) if config.sensors else 0}")
        print(f"  Groups: {len(config.animationGroups) if config.animationGroups else 0}")
        print("\nUse --save to write JSON or --apply to send to device")

    return 0


if __name__ == "__main__":
    sys.exit(main())
