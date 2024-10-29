import os
import platform
import subprocess
from shutil import copyfile

import toml
from fontTools.ttLib import TTFont


def load_config(config_path):
    return toml.load(config_path)


def merge_glyphs(base_font, symbol_font, symbols):
    symbol_font_glyphs = TTFont(symbol_font)
    cmap = symbol_font_glyphs["cmap"].getBestCmap()
    glyf = symbol_font_glyphs["glyf"]
    hmtx = symbol_font_glyphs["hmtx"]

    for symbol in symbols:
        code_point = ord(symbol)
        if code_point in cmap:
            glyph_name = cmap[code_point]
            if glyph_name in glyf.keys():
                # Copy glyph outline
                base_font["glyf"][glyph_name] = glyf[glyph_name]
                # Copy horizontal metrics
                base_font["hmtx"][glyph_name] = hmtx[glyph_name]
                # Update character mapping
                base_font["cmap"].tables[0].cmap[code_point] = glyph_name
    symbol_font_glyphs.close()


def create_custom_font(config_path):
    config = load_config(config_path)
    base_font_path = config["fonts"]["base"]
    output_dir = config["fonts"].get("output_directory", "output")
    output_name = config["fonts"].get("output_name", "custom_font.ttf")
    output_path = os.path.join(output_dir, output_name)

    os.makedirs(output_dir, exist_ok=True)
    copyfile(base_font_path, output_path)
    base_font = TTFont(output_path)

    for replacement in config["replacements"]:
        symbols = replacement["symbols"]
        font_path = replacement["font"]
        merge_glyphs(base_font, font_path, symbols)

    base_font.save(output_path)
    print(f"Custom font saved to {output_path}")
    return output_path


def install_font(font_path):
    system = platform.system()
    if system == "Windows":
        subprocess.run(f"copy {font_path} %WINDIR%\\Fonts", shell=True)
    elif system == "Darwin":
        subprocess.run(["cp", font_path, "~/Library/Fonts/"])
    elif system == "Linux":
        subprocess.run(["sudo", "cp", font_path, "/usr/local/share/fonts/"])
    print("Font installed. You may need to restart applications to see the changes.")
