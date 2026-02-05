#!/usr/bin/env python3
"""
Screen Mirror to ConnectorX Matrix

Captures a portion of the screen and displays it on an LED matrix in real-time.
Demonstrates high-speed direct buffer updates with DirectLED and delta compression.

Usage:
    python examples/screen_mirror.py --port COM3 --zone 1616 --fps 60 --select-region
    python examples/screen_mirror.py --port COM3 --zone 88 --region center --brightness 0.3
    
Requirements:
    pip install pillow mss
    
Optional (for better performance):
    pip install numpy

Note:
    This example will only work on Windows
"""

import argparse
import time
import json
import sys
from PIL import Image, ImageDraw, ImageFont
import mss
import lumyn_sdk
from lumyn_sdk import ConnectorX, list_available_ports

try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

_sct = None


def get_screen_capture():
    """Get or create reusable mss screen capture context."""
    global _sct
    if _sct is None:
        _sct = mss.mss()
    return _sct


def capture_and_downsample(sct, monitor, target_width=8, target_height=8, resample_filter=Image.Resampling.BOX):
    """Capture screen region and downsample to target resolution.

    Args:
        sct: MSS screen capture context (reusable)
        monitor: MSS monitor definition with capture region
        target_width: Target width in pixels
        target_height: Target height in pixels
        resample_filter: PIL resampling filter

    Returns:
        PIL Image downsampled to target size
    """
    # Grab the screen region
    screenshot = sct.grab(monitor)

    # Convert to PIL Image
    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

    # Resize with specified filter
    img_small = img.resize((target_width, target_height), resample_filter)

    return img_small


def image_to_buffer_fast(img, brightness=1.0, contrast=1.0, orientation=None):
    """Convert PIL Image to LED buffer bytes (optimized).

    Args:
        img: PIL Image (RGB)
        brightness: Brightness multiplier (0.0-1.0)
        contrast: Contrast multiplier (1.0 = normal, >1.0 = more contrast)
        orientation: Dict with matrix orientation settings:
            - cornerTopBottom: 'top' or 'bottom'
            - cornerLeftRight: 'left' or 'right'  
            - axisLayout: 'rows' or 'cols'
            - sequenceLayout: 'zigzag' or 'progressive'

    Returns:
        bytes: Raw RGB buffer (3 bytes per pixel)
    """
    width, height = img.size

    # Default orientation
    if orientation is None:
        orientation = {}

    corner_tb = orientation.get('cornerTopBottom', 'top')
    corner_lr = orientation.get('cornerLeftRight', 'left')
    axis_layout = orientation.get('axisLayout', 'rows')
    is_zigzag = orientation.get('sequenceLayout', 'progressive') == 'zigzag'

    # Apply contrast and brightness
    try:
        import numpy as np
        arr = np.array(img, dtype=np.float32)

        # Apply contrast: shift to center, scale, shift back
        if contrast != 1.0:
            arr = (arr - 128) * contrast + 128

        # Apply brightness
        if brightness != 1.0:
            arr = arr * brightness

        arr = arr.clip(0, 255).astype(np.uint8)
        img = Image.fromarray(arr)
    except ImportError:
        # Fallback without numpy
        if contrast != 1.0 or brightness != 1.0:
            img = img.point(lambda p: int(
                min(255, max(0, ((p - 128) * contrast + 128) * brightness))))

    try:
        import numpy as np
        arr = np.array(img, dtype=np.uint8)  # Shape: (height, width, 3)

        if axis_layout == 'cols':
            if corner_lr == 'right':
                # Flip horizontally - column 0 is on right
                arr = arr[:, ::-1, :]
            if corner_tb == 'top':
                # Flip vertically - pixel 0 at top means we need to invert
                arr = arr[::-1, :, :]
        else:
            if corner_tb == 'bottom':
                arr = arr[::-1, :, :]  # Flip vertically - row 0 is at bottom
            if corner_lr == 'right':
                # Flip horizontally - each row starts from right
                arr = arr[:, ::-1, :]

        # Step 2: Handle axis layout and zigzag
        if axis_layout == 'cols':
            arr = arr.transpose(1, 0, 2)

            if is_zigzag:
                # Reverse every other column
                for col in range(1, arr.shape[0], 2):
                    arr[col, :, :] = arr[col, ::-1, :]
        else:
            # LED strip runs in rows (left-to-right or right-to-left per row)
            if is_zigzag:
                # Reverse every other row
                for row in range(1, height, 2):
                    arr[row, :, :] = arr[row, ::-1, :]

        return arr.tobytes()

    except ImportError:
        pixels = list(img.getdata())

        grid = []
        for row in range(height):
            grid.append(pixels[row * width:(row + 1) * width])

        # Flip based on corner
        if corner_tb == 'bottom':
            grid = grid[::-1]
        if corner_lr == 'right':
            grid = [row[::-1] for row in grid]

        buffer = bytearray()

        if axis_layout == 'cols':
            # Column-major order
            for col in range(width):
                col_pixels = [grid[row][col] for row in range(height)]
                if is_zigzag and col % 2 == 1:
                    col_pixels = col_pixels[::-1]
                for r, g, b in col_pixels:
                    buffer.extend([r, g, b])
        else:
            # Row-major order
            for row_idx, row_pixels in enumerate(grid):
                if is_zigzag and row_idx % 2 == 1:
                    row_pixels = row_pixels[::-1]
                for r, g, b in row_pixels:
                    buffer.extend([r, g, b])

        return bytes(buffer)


class RegionSelector:
    """Interactive region selector using tkinter."""

    def __init__(self):
        self.region = None
        self.start_x = None
        self.start_y = None
        self.rect_id = None

    def select_region(self):
        """Show interactive region selector overlay.

        Returns:
            dict: Selected region with 'top', 'left', 'width', 'height' or None if cancelled
        """
        if not HAS_TKINTER:
            print("Error: tkinter not available for interactive selection")
            print("Install tkinter or use --region parameter")
            return None

        # Capture full screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

        # Create fullscreen transparent window
        root = tk.Tk()
        root.attributes('-fullscreen', True)
        root.attributes('-alpha', 0.3)
        root.configure(bg='black')

        # Create canvas
        canvas = tk.Canvas(root, highlightthickness=0, bg='black')
        canvas.pack(fill=tk.BOTH, expand=True)

        # Instructions
        instructions = canvas.create_text(
            monitor['width'] // 2, 50,
            text="Click and drag to select region. Press ESC to cancel.",
            fill='white', font=('Arial', 20, 'bold')
        )

        def on_mouse_down(event):
            self.start_x = event.x
            self.start_y = event.y
            if self.rect_id:
                canvas.delete(self.rect_id)

        def on_mouse_move(event):
            if self.start_x is not None and self.start_y is not None:
                if self.rect_id:
                    canvas.delete(self.rect_id)
                self.rect_id = canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    outline='red', width=3
                )
                # Show dimensions
                w = abs(event.x - self.start_x)
                h = abs(event.y - self.start_y)
                canvas.itemconfig(instructions,
                                  text=f"Region: {w}x{h} pixels. Release to confirm, ESC to cancel.")

        def on_mouse_up(event):
            if self.start_x is not None and self.start_y is not None:
                x1, x2 = sorted([self.start_x, event.x])
                y1, y2 = sorted([self.start_y, event.y])

                self.region = {
                    'left': x1,
                    'top': y1,
                    'width': x2 - x1,
                    'height': y2 - y1
                }
                root.quit()

        def on_escape(event):
            self.region = None
            root.quit()

        canvas.bind('<Button-1>', on_mouse_down)
        canvas.bind('<B1-Motion>', on_mouse_move)
        canvas.bind('<ButtonRelease-1>', on_mouse_up)
        root.bind('<Escape>', on_escape)

        root.mainloop()
        root.destroy()

        return self.region


def main():
    parser = argparse.ArgumentParser(description="Screen Mirror to LED Matrix")
    parser.add_argument("--port", required=False,
                        help="Serial port (e.g., COM3)")
    parser.add_argument("--zone", default="88",
                        help="Matrix zone ID (default: 88 for 8x8)")
    parser.add_argument("--duration", type=int, default=20,
                        help="Duration in seconds (default: 20)")
    parser.add_argument("--brightness", type=float, default=0.5,
                        help="Brightness 0.0-1.0 (default: 0.5)")
    parser.add_argument("--contrast", type=float, default=1.0,
                        help="Contrast multiplier (default: 1.0, try 1.5-2.0 for bright scenes)")
    parser.add_argument("--fps", type=int, default=30,
                        help="Target FPS (default: 30)")
    parser.add_argument("--region", type=str, default="center",
                        help="Screen region: 'center', 'top-left', 'top-right', 'bottom-left', 'bottom-right', or 'x,y,width,height'")
    parser.add_argument("--select-region", action="store_true",
                        help="Interactively select screen region with mouse")
    parser.add_argument("--quality", type=str, default="fast", choices=["fast", "balanced", "quality"],
                        help="Resampling quality: fast (BOX), balanced (BILINEAR), quality (LANCZOS)")
    parser.add_argument("--list-ports", action="store_true",
                        help="List available serial ports and exit")
    args = parser.parse_args()

    # Interactive region selection
    if args.select_region:
        print("Interactive region selection mode")
        print("Click and drag to select the region, then release.")
        print("Press ESC to cancel.\n")
        time.sleep(1)  # Give user time to read

        selector = RegionSelector()
        selected = selector.select_region()

        if selected is None:
            print("Region selection cancelled")
            return

        print(
            f"Selected region: {selected['left']},{selected['top']},{selected['width']},{selected['height']}")
        print(
            f"To reuse this region, add: --region {selected['left']},{selected['top']},{selected['width']},{selected['height']}")

        # Ask if user wants to continue
        if HAS_TKINTER:
            root = tk.Tk()
            root.withdraw()
            proceed = messagebox.askyesno("Continue?",
                                          f"Start mirroring with selected region?\n"
                                          f"Size: {selected['width']}x{selected['height']}\n"
                                          f"Position: ({selected['left']}, {selected['top']})")
            root.destroy()

            if not proceed:
                return

        # Override region argument
        custom_region = selected
    else:
        custom_region = None

    # List ports if requested
    if args.list_ports:
        print("Available serial ports:")
        ports = list_available_ports()
        for port in ports:
            print(f"  {port}")
        return

    # Require port if not listing or selecting region
    if not args.port:
        print("Error: --port is required (use --list-ports to see available ports)")
        return

    # Create and connect
    cx = ConnectorX()
    print(f"Connecting to {args.port}...")
    if not cx.connect(args.port):
        print("Failed to connect!")
        return

    print("Connected to ConnectorX!")

    # Get LED handler
    leds = cx.leds
    zone = args.zone

    # Get zone dimensions from config
    config = cx.request_config()
    matrix_width = 8
    matrix_height = 8
    matrix_orientation = None

    if config:
        channels = config.channels or []
        for channel_data in channels:
            for z in channel_data.zones:
                if z.id == zone:
                    # Check if it's a matrix zone (compare enum value name)
                    zone_type_name = str(z.type).split('.')[-1].upper()
                    if zone_type_name == 'MATRIX':
                        matrix_width = getattr(z, 'matrix_cols', 8) or 8
                        matrix_height = getattr(z, 'matrix_rows', 8) or 8
                        matrix_orientation = getattr(
                            z, 'matrix_orientation', None)
                    break

    # Extract orientation values (handle both object and dict)
    if matrix_orientation:
        if hasattr(matrix_orientation, 'corner_top_bottom'):
            # Object-style access
            corner_tb = getattr(matrix_orientation, 'corner_top_bottom', 'top')
            corner_lr = getattr(matrix_orientation,
                                'corner_left_right', 'left')
            axis_layout = getattr(matrix_orientation, 'axis_layout', 'rows')
            seq_layout = getattr(matrix_orientation,
                                 'sequence_layout', 'progressive')
        else:
            # Dict-style access (fallback)
            corner_tb = matrix_orientation.get('cornerTopBottom', 'top')
            corner_lr = matrix_orientation.get('cornerLeftRight', 'left')
            axis_layout = matrix_orientation.get('axisLayout', 'rows')
            seq_layout = matrix_orientation.get(
                'sequenceLayout', 'progressive')
    else:
        corner_tb, corner_lr, axis_layout, seq_layout = 'top', 'left', 'rows', 'progressive'

    print(f"Matrix zone '{zone}': {matrix_width}x{matrix_height} LEDs")
    print(
        f"  Orientation: corner={corner_tb}-{corner_lr}, axis={axis_layout}, sequence={seq_layout}")

    # Determine screen capture region
    if custom_region:
        # Use interactively selected region
        monitor = custom_region
        x = monitor['left']
        y = monitor['top']
        capture_size = monitor['width']
    else:
        with mss.mss() as sct:
            primary_monitor = sct.monitors[1]  # Primary monitor
            screen_width = primary_monitor['width']
            screen_height = primary_monitor['height']

            # Calculate capture region (square region)
            capture_size = min(screen_width, screen_height) // 2

            if args.region == "center":
                x = (screen_width - capture_size) // 2
                y = (screen_height - capture_size) // 2
            elif args.region == "top-left":
                x, y = 0, 0
            elif args.region == "top-right":
                x = screen_width - capture_size
                y = 0
            elif args.region == "bottom-left":
                x = 0
                y = screen_height - capture_size
            elif args.region == "bottom-right":
                x = screen_width - capture_size
                y = screen_height - capture_size
            else:
                # Custom region: x,y,width,height
                try:
                    parts = args.region.split(',')
                    x, y, w, h = map(int, parts)
                    capture_size = w  # For display purposes
                except:
                    print(f"Invalid region format: {args.region}")
                    print("Use: x,y,width,height or predefined region name")
                    cx.disconnect()
                    return

            monitor = {
                "top": y,
                "left": x,
                "width": capture_size,
                "height": capture_size
            }

    print(f"Capturing {capture_size}x{capture_size} region at ({x}, {y})")
    print(
        f"Target: {args.fps} FPS, Brightness: {args.brightness}, Duration: {args.duration}s")
    print(f"Quality: {args.quality}")
    print("Starting screen mirror...\n")

    # Select resampling filter based on quality setting
    resample_filters = {
        "fast": Image.Resampling.BOX,
        "balanced": Image.Resampling.BILINEAR,
        "quality": Image.Resampling.LANCZOS,
    }
    resample_filter = resample_filters[args.quality]

    # Create DirectLED for efficient buffer updates with delta compression
    num_leds = matrix_width * matrix_height
    direct_led = leds.create_direct_led(
        zone, num_leds=num_leds, full_refresh_interval=30)

    frame_time = 1.0 / args.fps
    start_time = time.time()
    frame_count = 0

    # Get reusable screen capture context
    sct = get_screen_capture()

    try:
        while (time.time() - start_time) < args.duration:
            frame_start = time.time()

            # Capture and process screen
            img = capture_and_downsample(
                sct, monitor, matrix_width, matrix_height, resample_filter)
            buffer = image_to_buffer_fast(
                img, args.brightness, args.contrast, matrix_orientation)

            # Send to LED matrix with automatic delta compression
            direct_led.update(buffer)

            frame_count += 1

            # Frame rate limiting
            elapsed = time.time() - frame_start
            if elapsed < frame_time:
                time.sleep(frame_time - elapsed)

            # Stats every second
            if frame_count % args.fps == 0:
                actual_fps = frame_count / (time.time() - start_time)
                print(f"Frame {frame_count}: {actual_fps:.1f} FPS")

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    # Final stats
    total_time = time.time() - start_time
    actual_fps = frame_count / total_time
    print(
        f"\nCompleted: {frame_count} frames in {total_time:.1f}s ({actual_fps:.1f} FPS)")

    # Turn off matrix
    print("Clearing matrix...")
    buffer = bytes([0, 0, 0] * num_leds)
    direct_led.force_full_update(buffer)

    cx.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()
