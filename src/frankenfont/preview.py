import json
import os
import sys
import tempfile
import contextlib
import logging
from pathlib import Path

import toml
from PIL import Image, ImageDraw, ImageFont


def load_config(config_path: str) -> dict:
    """Load and parse the config file"""
    if config_path.endswith(".toml"):
        return toml.load(config_path)
    elif config_path.endswith(".json"):
        with open(config_path) as f:
            return json.load(f)
    raise ValueError("Config file must be .toml or .json")


def get_font_name(font_path: str) -> str:
    """Extract font name from path"""
    return Path(font_path).stem.replace(".", " ")



def preview_config(config_path: str) -> None:
    """Display a preview of the font configuration"""
    config = load_config(config_path)

    # Load base font
    base_font_path = config["fonts"]["base"]
    try:
        base_font = ImageFont.truetype(base_font_path, size=40)
    except OSError:
        print(f"Error loading base font from {base_font_path}")
        sys.exit(1)

    # Prepare replacements
    replacements = config.get("replacements", [])
    replacement_fonts = []
    for replacement in replacements:
        font_path = replacement["font"]
        # If the font path is relative, make it absolute based on config file location
        config_dir = Path(config_path).parent
        font_path = str(config_dir / font_path)
        try:
            font = ImageFont.truetype(font_path, size=40)
            replacement_fonts.append((font, replacement["glyphs"], font_path))
            logging.info(f"Loaded replacement font from {font_path}")
        except OSError:
            logging.error(f"Error loading replacement font from {font_path}")
            sys.exit(1)

    # Create an image with white background
    image_width = 1200
    image_height = 800
    image = Image.new("RGBA", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(image)

    # Initialize starting position
    x, y = 50, 50
    line_height = 60

    # Draw base font sample
    draw.text((x, y), "Base Font Sample:", font=base_font, fill="black")
    y += line_height
    sample_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,!.-?"
    draw.text((x, y), sample_text, font=base_font, fill="black")
    y += line_height * 2

    # Draw replacement fonts samples
    for font, glyphs, font_path in replacement_fonts:
        draw.text((x, y), f"Replacement Font: {Path(font_path).name}", font=base_font, fill="black")
        y += line_height
        valid_glyphs = []
        for glyph in glyphs:
            bbox = font.getbbox(glyph)
            if bbox is not None:
                valid_glyphs.append(glyph)
            else:
                valid_glyphs.append(f"[Missing: {glyph}]")
        glyphs_text = " ".join(valid_glyphs)
        draw.text((x, y), glyphs_text, font=font, fill="black")
        y += line_height * 2

        # Check if y exceeds image height and adjust if necessary
        if y + line_height > image_height - 50:
            image_height += 200
            new_image = Image.new("RGBA", (image_width, image_height), color="white")
            new_image.paste(image, (0, 0))
            image = new_image
            draw = ImageDraw.Draw(image)

    # Save image to a temporary file and display
    with contextlib.ExitStack() as stack:
        tmp = stack.enter_context(tempfile.NamedTemporaryFile(suffix=".png", delete=False))
        image.save(tmp.name)
        image.show()
        os.unlink(tmp.name)

    print("Font preview image has been displayed.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        sys.exit("Error: Please provide a config file path")
