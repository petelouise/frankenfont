#!/usr/bin/fontforge
import json
import os

import fontforge


def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)


def merge_glyphs(base_font, symbol_font_path, symbols):
    symbol_font = fontforge.open(symbol_font_path)

    for symbol in symbols:
        try:
            code_point = ord(symbol)
            # Get the glyph from symbol font
            symbol_glyph = symbol_font[code_point]
            # Create or get the glyph slot in base font
            if code_point not in base_font:
                base_font.createChar(code_point)
            # Copy the glyph data
            target_glyph = base_font[code_point]
            target_glyph.clear()
            target_glyph.width = symbol_glyph.width
            target_glyph.importOutlines(symbol_glyph)
        except Exception as e:
            print(f"Warning: Could not copy symbol {symbol}: {e}")

    symbol_font.close()


def create_custom_font(config_path):
    config = load_config(config_path)
    base_font_path = config["fonts"]["base"]
    output_dir = config["fonts"].get("output_directory", "output")
    output_name = config["fonts"].get("output_name", "custom_font.ttf")
    output_path = os.path.join(output_dir, output_name)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open base font
    base_font = fontforge.open(base_font_path)

    # Process each replacement set
    for replacement in config["replacements"]:
        symbols = replacement["symbols"]
        font_path = replacement["font"]
        merge_glyphs(base_font, font_path, symbols)

    # Generate the output font
    base_font.generate(output_path)
    base_font.close()

    print(f"Custom font saved to {output_path}")
    return output_path


CONFIG_PATH = "tests/test_config.json"
create_custom_font(CONFIG_PATH)
