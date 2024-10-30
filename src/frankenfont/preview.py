import json
import os
import sys
import tempfile
from pathlib import Path
from typing import List, Dict
import toml

from PIL import Image, ImageDraw, ImageFont

def load_config(config_path: str) -> dict:
    """Load and parse the config file"""
    if config_path.endswith('.toml'):
        return toml.load(config_path)
    elif config_path.endswith('.json'):
        with open(config_path) as f:
            return json.load(f)
    raise ValueError("Config file must be .toml or .json")

def get_font_name(font_path: str) -> str:
    """Extract font name from path"""
    return Path(font_path).stem.replace('.', ' ')

def get_sample_text() -> str:
    """Generate sample text with a good mix of characters"""
    chars = (
        string.ascii_uppercase[:6] +  # Some uppercase
        string.ascii_lowercase[:6] +  # Some lowercase
        string.digits[:4] +          # Some numbers
        ",.!?-"                      # Basic punctuation
    )
    return ' '.join([''.join(random.sample(chars, 5)) for _ in range(4)])

def preview_config(config_path: str) -> None:
    """Display a preview of the font configuration"""
    config = load_config(config_path)
    
    # Load base font
    base_font_path = config["fonts"]["base"]
    try:
        base_font = ImageFont.truetype(base_font_path, size=40)
    except IOError:
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
            replacement_fonts.append((font, replacement["glyphs"]))
        except IOError:
            print(f"Error loading replacement font from {font_path}")
            sys.exit(1)
    
    # Create an image with white background
    image_width = 800
    image_height = 600
    image = Image.new("RGB", (image_width, image_height), color="white")
    draw = ImageDraw.Draw(image)
    
    # Starting position
    x, y = 50, 50
    
    # Draw base font sample
    draw.text((x, y), "Base Font Sample:", font=base_font, fill="black")
    y += 50
    sample_text = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,!.-?"
    draw.text((x, y), sample_text, font=base_font, fill="black")
    y += 100
    
    # Draw replacement fonts samples
    for font, glyphs in replacement_fonts:
        draw.text((x, y), f"Replacement Font: {font.path}", font=base_font, fill="black")
        y += 50
        glyphs_text = " ".join([glyph if len(glyph) == 1 else f"[{glyph}]" for glyph in glyphs])
        draw.text((x, y), glyphs_text, font=font, fill="black")
        y += 100
    
    # Save image to a temporary file and display
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        image.save(tmp.name)
        image.show()
        # Delete the temporary file after displaying
        os.unlink(tmp.name)
    
    print("Font preview image has been displayed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        sys.exit("Error: Please provide a config file path")
