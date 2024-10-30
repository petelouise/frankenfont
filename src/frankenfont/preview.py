import json
import random
import string
import toml

import fontforge
from rich.console import Console
from rich.text import Text

def load_config(config_path: str) -> dict:
    """Load and parse the config file"""
    if config_path.endswith('.toml'):
        return toml.load(config_path)
    elif config_path.endswith('.json'):
        with open(config_path) as f:
            return json.load(f)
    raise ValueError("Config file must be .toml or .json")

def build_glyph_map(config: dict) -> dict[str, tuple[str, str]]:
    """Build mapping of glyphs to their source fonts and names"""
    glyph_map = {}
    for replacement in config["replacements"]:
        font_path = replacement["font"]
        font = fontforge.open(font_path)
        font_name = font.fontname
        for glyph in replacement["glyphs"]:
            glyph_map[glyph] = (font_path, font_name)
        font.close()
    return glyph_map

def get_sample_text() -> str:
    """Generate sample text with a good mix of characters"""
    # Include uppercase, lowercase, numbers, and basic punctuation
    chars = (
        string.ascii_uppercase[:6] +  # Some uppercase
        string.ascii_lowercase[:6] +  # Some lowercase
        string.digits[:4] +          # Some numbers
        ",.!?-"                      # Basic punctuation
    )
    return ' '.join([''.join(random.sample(chars, 5)) for _ in range(4)])

def preview_config(config_path: str) -> None:
    """Display a preview of the font configuration"""
    console = Console()
    config = load_config(config_path)
    
    # Load base font info
    base_font = fontforge.open(config["fonts"]["base"])
    base_name = base_font.fontname
    base_font.close()
    
    # Build glyph mapping
    glyph_map = build_glyph_map(config)
    
    # Create header
    preview = Text()
    preview.append("\n🔤 Font Preview\n\n", style="bold magenta")
    preview.append(f"Base Font: {base_name}\n\n", style="blue")
    
    # Show replacements grouped by source font
    preview.append("Replacement Glyphs:\n", style="bold green")
    current_font = None
    for replacement in config["replacements"]:
        font = fontforge.open(replacement["font"])
        if font.fontname != current_font:
            preview.append(f"\nFrom {font.fontname}:\n", style="cyan")
            current_font = font.fontname
        preview.append(' '.join(replacement["glyphs"]) + "\n", style="yellow")
        font.close()
    
    # Generate and show sample text
    preview.append("\nSample Text:\n", style="bold red")
    
    # Create sample with base text and replacements
    sample_base = get_sample_text()
    sample = Text()
    
    # Add some replacement glyphs at regular intervals
    replacement_glyphs = list(glyph_map.keys())
    for i, char in enumerate(sample_base):
        if i > 0 and i % 7 == 0 and replacement_glyphs:  # Every 7th position
            glyph = replacement_glyphs.pop(0)
            _, font_name = glyph_map[glyph]
            sample.append(glyph, style="bold yellow")
        else:
            sample.append(char, style="blue")
    
    preview.append(sample)
    preview.append("\n")
    
    # Print the complete preview
    console.print(preview)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        print("Please provide a config file path")
