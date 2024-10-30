import contextlib
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

import toml
from PIL import Image, ImageDraw, ImageFont

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


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
    logging.info(f"Loaded configuration from {config_path}")

    # Load base font
    base_font_path = config["fonts"]["base"]
    logging.info(f"Loading base font from {base_font_path}")
    try:
        base_font = ImageFont.truetype(base_font_path, size=40)
        logging.info(f"Successfully loaded base font: {base_font_path}")
    except OSError:
        logging.error(f"Error loading base font from {base_font_path}")
        sys.exit(1)

    # Prepare replacements
    replacements = config.get("replacements", [])
    replacement_fonts = []
    for replacement in replacements:
        font_path = replacement["font"]
        config_dir = Path(config_path).parent
        font_path = str(config_dir / font_path)
        logging.info(
            f"Loading replacement font from {font_path} for glyphs: {replacement['glyphs']}"
        )
        try:
            font = ImageFont.truetype(font_path, size=40)
            replacement_fonts.append((font, replacement["glyphs"], font_path))
            logging.info(f"Successfully loaded replacement font: {font_path}")
        except OSError:
            logging.error(f"Error loading replacement font from {font_path}")
            sys.exit(1)

    # Define colors for replacement fonts
    color_palette = ["red", "green", "blue", "orange", "purple", "cyan"]
    font_colors = {}
    glyph_to_font_color = {}

    # Add base font to colors
    base_font_name = get_font_name(base_font_path)
    font_colors[base_font_name] = default_color

    for i, (font, glyphs, font_path) in enumerate(replacement_fonts):
        assigned_color = color_palette[i % len(color_palette)]
        font_name = get_font_name(font_path)
        font_colors[font_name] = assigned_color
        for glyph in glyphs:
            glyph_to_font_color[glyph] = (font, assigned_color)

    default_color = "black"

    # Create an image with white background
    image_width = 1200
    image_height = 800
    image = Image.new("RGBA", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(image)

    # Initialize starting position
    x_start, y_start = 50, 50
    x, y = x_start, y_start
    line_height = 60
    spacing = 10  # Space between glyphs

    # Define sample text
    sample_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,!.-?"
    replacement_glyphs = ''.join(replacement["glyphs"] for replacement in replacements)
    all_glyphs = sample_text + replacement_glyphs

    # Draw base font sample with mixed glyphs
    for character in all_glyphs:
        if character in glyph_to_font_color:
            font, color = glyph_to_font_color[character]
        else:
            font = base_font
            color = default_color

        draw.text((x, y), character, font=font, fill=color)

        try:
            # Use getbbox to obtain the width of the glyph
            bbox = font.getbbox(character)
            glyph_width = bbox[2] - bbox[0] if bbox else 0
        except AttributeError:
            # Fallback using getlength if getbbox is unavailable
            try:
                glyph_width = font.getlength(character)
            except AttributeError:
                logging.error(f"Unable to determine width for glyph '{character}'.")
                glyph_width = 40  # Default fallback width

        x += glyph_width + spacing

        # Check for line wrap
        if x > image_width - x_start:
            x = x_start
            y += line_height

    # Draw font names in bottom right corner
    small_font_size = 20
    try:
        small_font = ImageFont.truetype(base_font_path, size=small_font_size)
    except OSError:
        logging.error(f"Error loading small font from {base_font_path}")
        small_font = ImageFont.load_default()

    margin = 50
    y_font_names = image_height - margin

    # Calculate total width of font names to align them to the right
    font_names_list = list(font_colors.keys())
    font_names_text = " | ".join(font_names_list)
    total_width = 0
    temp_draw = ImageDraw.Draw(image)
    for font_name in font_names_list:
        font_color = font_colors[font_name]
        bbox = small_font.getbbox(font_name)
        width = bbox[2] - bbox[0] if bbox else 0
        separator_bbox = small_font.getbbox(" | ")
        separator_width = separator_bbox[2] - separator_bbox[0] if separator_bbox else 0
        total_width += width + separator_width
    if font_names_list:
        last_separator_bbox = small_font.getbbox(" | ")
        last_separator_width = last_separator_bbox[2] - last_separator_bbox[0] if last_separator_bbox else 0
        total_width -= last_separator_width  # Remove last separator

    x_font_names = image_width - margin - total_width

    for i, font_name in enumerate(font_names_list):
        font_color = font_colors[font_name]
        if i < len(font_names_list) - 1:
            text = f"{font_name} | "
        else:
            text = f"{font_name}"
        draw.text((x_font_names, y_font_names), text, font=small_font, fill=font_color)
        try:
            bbox = small_font.getbbox(text)
            glyph_width = bbox[2] - bbox[0] if bbox else 0
        except AttributeError:
            # Fallback using getlength if getbbox is unavailable
            try:
                glyph_width = small_font.getlength(text)
            except AttributeError:
                logging.error(f"Unable to determine width for text '{text}'.")
                glyph_width = 100  # Default fallback width
        x_font_names += glyph_width

    # Save image to a temporary file and display
    with contextlib.ExitStack() as stack:
        tmp = stack.enter_context(
            tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        )
        image.save(tmp.name)
        logging.info(f"Saved preview image to temporary file: {tmp.name}")
        image.show()
        os.unlink(tmp.name)
        logging.info("Displayed and deleted temporary preview image.")

    print("Font preview image has been displayed.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        sys.exit("Error: Please provide a config file path")
