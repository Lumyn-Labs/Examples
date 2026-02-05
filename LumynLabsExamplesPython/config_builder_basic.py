#!/usr/bin/env python3
"""
Configuration Builder - Basic Example

Demonstrates creating a device configuration programmatically using the
fluent builder API, matching the Java vendordep style.

Usage:
    python examples/config_builder_basic.py
    python examples/config_builder_basic.py --apply COM3
"""

import argparse
import sys
from lumyn_sdk import ConfigBuilder, NetworkType, SerializeConfigToJson, ConnectorX


def create_basic_config():
    """Create a basic configuration with one channel and one group."""
    print("Creating basic configuration...")

    config = ConfigBuilder() \
        .ForTeam("9999") \
        .SetNetworkType(NetworkType.USB) \
        .AddChannel(0, "channel_0", 144) \
            .Brightness(255) \
            .AddStripZone("main", 144, False) \
            .EndChannel() \
        .AddGroup("all_leds") \
            .AddZone("main") \
            .EndGroup() \
        .Build()

    print("Configuration created successfully!")
    return config


def create_advanced_config():
    """Create a more advanced configuration with sequences."""
    print("Creating advanced configuration...")

    config = ConfigBuilder() \
        .ForTeam("9999") \
        .SetNetworkType(NetworkType.USB) \
        .AddChannel(0, "channel_0", 144) \
            .Brightness(255) \
            .AddStripZone("main", 144, False) \
            .EndChannel() \
        .AddSequence("startup") \
            .AddStep("FadeIn") \
                .WithColor(0, 255, 0) \
                .WithDelay(30) \
                .EndStep() \
            .AddStep("Fill") \
                .WithColor(0, 255, 0) \
                .WithDelay(-1) \
                .EndStep() \
            .EndSequence() \
        .AddSequence("alliance_red") \
            .AddStep("Fill") \
                .WithColor(255, 0, 0) \
                .WithDelay(-1) \
                .EndStep() \
            .EndSequence() \
        .AddGroup("all_leds") \
            .AddZone("main") \
            .EndGroup() \
        .Build()

    print("Advanced configuration created successfully!")
    return config


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configuration Builder - Basic Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This example demonstrates creating device configurations programmatically.

Examples:
    python examples/config_builder_basic.py
    python examples/config_builder_basic.py --apply COM3
    python examples/config_builder_basic.py --save my_config.json
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
    parser.add_argument(
        "--advanced",
        action="store_true",
        help="Create advanced configuration with sequences"
    )

    args = parser.parse_args()

    # Create configuration
    if args.advanced:
        config = create_advanced_config()
    else:
        config = create_basic_config()

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
        # Just print the JSON
        print("\nConfiguration JSON:")
        print(SerializeConfigToJson(config))

    return 0


if __name__ == "__main__":
    sys.exit(main())
