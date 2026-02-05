#!/usr/bin/env python3
"""
Device Class Comparison Example

This example demonstrates the three device classes and when to use each:

- ConnectorXBase: Abstract base class (don't instantiate directly)
- ConnectorX: Full-featured device with LEDs, modules, and UART support
- ConnectorXAnimate: Simplified LED-only device (USB only)

Usage:
    python examples/device_comparison.py --port COM3
"""

import argparse
import sys
import lumyn_sdk
from lumyn_sdk import ConnectorX, ConnectorXAnimate, Animation


def demonstrate_connectorx(port: str) -> None:
    """
    Demonstrate ConnectorX - full-featured device.
    
    ConnectorX supports:
    - USB and UART connections
    - LED control
    - Module/sensor data
    - Module handlers
    """
    print("\n" + "=" * 60)
    print("ConnectorX - Full-Featured Device")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ USB connections")
    print("  ✓ UART connections")
    print("  ✓ LED control")
    print("  ✓ Module/sensor data")
    print("  ✓ Module handlers")
    
    cx = ConnectorX()
    
    try:
        print(f"\nConnecting to {port}...")
        if not cx.connect(port):
            print("Failed to connect!")
            return
        
        print("Connected successfully!")
        
        # Demonstrate LED control
        print("\n1. LED Control:")
        print("   Setting zone1 to red...")
        cx.leds.set_color("zone1", (255, 0, 0))
        
        # Demonstrate module access
        print("\n2. Module Access:")
        print(f"   Module handler available: {cx.modules is not None}")
        print("   (Register modules with: cx.modules.register_module(...))")
        
        # Demonstrate UART connection capability
        print("\n3. Connection Types:")
        print("   ✓ USB: cx.connect_usb(port)")
        print("   ✓ UART: cx.connect_uart(port, baud)")
        
        print("\nConnectorX demonstration complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cx.close()


def demonstrate_connectorx_animate(port: str) -> None:
    """
    Demonstrate ConnectorXAnimate - LED-only device.
    
    ConnectorXAnimate supports:
    - USB connections only
    - LED control
    - No module/sensor data
    - No module handlers
    """
    print("\n" + "=" * 60)
    print("ConnectorXAnimate - LED-Only Device")
    print("=" * 60)
    print("\nFeatures:")
    print("  ✓ USB connections")
    print("  ✗ UART connections (not supported)")
    print("  ✓ LED control")
    print("  ✗ Module/sensor data (not supported)")
    print("  ✗ Module handlers (not supported)")
    
    cx_animate = ConnectorXAnimate()
    
    try:
        print(f"\nConnecting to {port}...")
        if not cx_animate.connect_usb(port):
            print("Failed to connect!")
            return
        
        print("Connected successfully!")
        
        # Demonstrate LED control
        print("\n1. LED Control:")
        print("   Setting zone1 to blue...")
        cx_animate.leds.set_color("zone1", (0, 0, 255))
        
        print("   Running animation...")
        cx_animate.leds.set_animation("zone1", Animation.Breathe, (0, 255, 0), 30)
        
        # Demonstrate DirectLED (works for both device types)
        print("\n2. DirectLED Support:")
        print("   DirectLED works with both ConnectorX and ConnectorXAnimate")
        print("   Example: direct_led = cx_animate.leds.create_direct_led('zone1', 60)")
        
        # Show what's NOT available
        print("\n3. Not Available:")
        print("   ✗ No modules property")
        print("   ✗ No connect_uart() method")
        print("   ✗ No get_latest_module_data() method")
        
        print("\nConnectorXAnimate demonstration complete!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cx_animate.close()


def show_comparison_table() -> None:
    """Show a feature comparison table."""
    print("\n" + "=" * 60)
    print("Feature Comparison")
    print("=" * 60)
    print("\n" + " " * 20 + "ConnectorX" + " " * 10 + "ConnectorXAnimate")
    print("-" * 60)
    print("USB Connection" + " " * 12 + "✓" + " " * 19 + "✓")
    print("UART Connection" + " " * 11 + "✓" + " " * 19 + "✗")
    print("LED Control" + " " * 15 + "✓" + " " * 19 + "✓")
    print("DirectLED" + " " * 18 + "✓" + " " * 19 + "✓")
    print("Module Data" + " " * 16 + "✓" + " " * 19 + "✗")
    print("Module Handlers" + " " * 12 + "✓" + " " * 19 + "✗")
    print("Event Handling" + " " * 13 + "✓" + " " * 19 + "✓")
    print("Configuration" + " " * 13 + "✓" + " " * 19 + "✓")
    print("\nWhen to use:")
    print("  ConnectorX: Full-featured devices with sensors/modules")
    print("  ConnectorXAnimate: LED-only devices, simpler API")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Device Class Comparison Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This example demonstrates the differences between ConnectorX and ConnectorXAnimate.

ConnectorXBase: Abstract base class (not meant to be instantiated directly)
ConnectorX: Full-featured device with LEDs, modules, and UART support
ConnectorXAnimate: Simplified LED-only device (USB only)

Examples:
    python examples/device_comparison.py --port COM3
    python examples/device_comparison.py --port COM3 --device connectorx
    python examples/device_comparison.py --port COM3 --device animate
        """
    )
    parser.add_argument("--port", required=True, help="Serial port (e.g., COM3)")
    parser.add_argument(
        "--device",
        choices=["connectorx", "animate", "both"],
        default="both",
        help="Which device to demonstrate (default: both)"
    )
    parser.add_argument(
        "--table-only",
        action="store_true",
        help="Show comparison table only (no connection)"
    )

    args = parser.parse_args()

    print(f"Lumyn SDK v{lumyn_sdk.__version__}")
    print("\nDevice Class Hierarchy Demonstration")
    
    # Always show the comparison table
    show_comparison_table()
    
    if args.table_only:
        return 0
    
    # Demonstrate devices based on selection
    if args.device in ("connectorx", "both"):
        demonstrate_connectorx(args.port)
    
    if args.device in ("animate", "both"):
        if args.device == "both":
            input("\nPress Enter to continue to ConnectorXAnimate demonstration...")
        demonstrate_connectorx_animate(args.port)
    
    print("\n" + "=" * 60)
    print("Demonstration complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
