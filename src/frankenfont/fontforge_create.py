#!/usr/bin/fontforge
import os
import fontforge
import toml


def load_config(config_path):
    return toml.load(config_path)


def merge_glyphs(base_font, symbol_font_path, symbols):
    symbol_font = fontforge.open(symbol_font_path)
    
    for symbol in symbols:
        try:
            # Get the glyph from symbol font
            symbol_glyph = symbol_font[ord(symbol)]
            # Create or get the glyph slot in base font
            if ord(symbol) not in base_font:
                base_font.createChar(ord(symbol))
            # Copy the glyph reference
            base_font[ord(symbol)].reference(symbol_glyph)
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
