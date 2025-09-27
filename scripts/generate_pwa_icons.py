#!/usr/bin/env python3
"""
Script to generate PWA icons from existing logo
Requires Pillow: pip install Pillow
"""

import os
import sys

from PIL import Image, ImageDraw


def create_pwa_icons():
    """Generate PWA icons in various sizes"""

    # Icon sizes needed for PWA
    icon_sizes = [
        (48, 48, "logo-48.png"),
        (72, 72, "logo-72.png"),
        (96, 96, "logo-96.png"),
        (144, 144, "logo-144.png"),
        (192, 192, "logo-192.png"),
        (512, 512, "logo-512.png"),
    ]

    # Check if logo exists
    logo_path = "static/logo.svg"
    if not os.path.exists(logo_path):
        print(f"Logo not found at {logo_path}")
        return False

    try:
        # Try to open SVG (requires cairosvg or convert to PNG first)
        # For now, we'll create a simple colored square with text
        print("Creating PWA icons...")

        for width, height, filename in icon_sizes:
            # Create a new image with the specified size
            img = Image.new(
                "RGBA", (width, height), (102, 126, 234, 255)
            )  # #667eea color

            # Create a drawing context
            draw = ImageDraw.Draw(img)

            # Add text "NOV" in the center
            try:
                # Try to use a font, fallback to default if not available
                from PIL import ImageFont

                font_size = max(12, width // 8)
                try:
                    font = ImageFont.truetype(
                        "/System/Library/Fonts/Arial.ttf", font_size
                    )
                except:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()

            # Calculate text position
            text = "NOV"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (width - text_width) // 2
            y = (height - text_height) // 2

            # Draw white text
            draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

            # Save the image
            output_path = f"static/{filename}"
            img.save(output_path, "PNG")
            print(f"Created {output_path} ({width}x{height})")

        # Create additional icons for shortcuts
        shortcut_icons = [
            (96, 96, "icon-checkin.png"),
            (96, 96, "icon-dashboard.png"),
            (96, 96, "icon-view.png"),
            (96, 96, "icon-close.png"),
        ]

        for width, height, filename in shortcut_icons:
            img = Image.new("RGBA", (width, height), (102, 126, 234, 255))
            draw = ImageDraw.Draw(img)

            # Add different symbols for different icons
            if "checkin" in filename:
                symbol = "✓"
            elif "dashboard" in filename:
                symbol = "📊"
            elif "view" in filename:
                symbol = "👁"
            elif "close" in filename:
                symbol = "✕"
            else:
                symbol = "?"

            try:
                font_size = max(20, width // 4)
                try:
                    font = ImageFont.truetype(
                        "/System/Library/Fonts/Arial.ttf", font_size
                    )
                except:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), symbol, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (width - text_width) // 2
            y = (height - text_height) // 2

            draw.text((x, y), symbol, fill=(255, 255, 255, 255), font=font)

            output_path = f"static/{filename}"
            img.save(output_path, "PNG")
            print(f"Created {output_path} ({width}x{height})")

        print("✅ All PWA icons generated successfully!")
        return True

    except Exception as e:
        print(f"Error generating icons: {e}")
        return False


if __name__ == "__main__":
    success = create_pwa_icons()
    sys.exit(0 if success else 1)
