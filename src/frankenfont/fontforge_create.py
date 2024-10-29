#!/usr/bin/fontforge
import json
import os

import fontforge


def load_config(config_path):
    with open(config_path) as f:
        return json.load(f)


def merge_glyphs(base_font, symbol_font_path, glyphs):
    symbol_font = fontforge.open(symbol_font_path)

    for glyph in glyphs:
        try:
            # Handle both literal symbols and glyph names
            if len(glyph) == 1:  # Literal symbol
                code_point = ord(glyph)
                symbol_font.selection.select(code_point)
            else:  # Glyph name
                if glyph not in symbol_font:
                    print(f"Warning: Glyph '{glyph}' not found in font")
                    continue
                symbol_font.selection.select(glyph)
                code_point = symbol_font[glyph].unicode
                if code_point is None:
                    print(f"Warning: No unicode mapping for glyph '{glyph}'")
                    continue
            
            symbol_font.copy()
            
            # Create glyph slot if needed
            if code_point not in base_font:
                base_font.createChar(code_point)
            
            # Select and paste into target font
            base_font.selection.select(code_point)
            base_font.paste()
        except Exception as e:
            print(f"Warning: Could not copy glyph '{glyph}': {e}")

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
        glyphs = replacement["glyphs"]
        font_path = replacement["font"]
        merge_glyphs(base_font, font_path, glyphs)

    # Generate the output font
    base_font.generate(output_path)
    base_font.close()

    print(f"Custom font saved to {output_path}")
    return output_path


CONFIG_PATH = "tests/test_config.json"
create_custom_font(CONFIG_PATH)
