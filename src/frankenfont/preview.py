import json
import os
import random
import string
import toml
from pathlib import Path
from typing import List, Dict

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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
    console = Console()
    config = load_config(config_path)
    
    # Create header
    preview = Text()
    preview.append("\n🔤 Font Preview\n\n", style="bold magenta")
    
    # Show base font
    base_name = get_font_name(config["fonts"]["base"])
    preview.append("Base Font: ", style="bold blue")
    preview.append(f"{base_name}\n\n")
    
    # Show replacements grouped by source font
    preview.append("Replacement Glyphs:\n", style="bold green")
    for replacement in config["replacements"]:
        font_name = get_font_name(replacement["font"])
        preview.append(f"\nFrom {font_name}:\n", style="cyan")
        
        # Show glyphs with visual indicators
        glyphs_text = Text()
        for glyph in replacement["glyphs"]:
            if len(glyph) == 1:  # Literal symbol
                glyphs_text.append(f"{glyph} ", style="yellow")
            else:  # Named glyph
                glyphs_text.append(f"[{glyph}] ", style="yellow")
        preview.append(glyphs_text)
        preview.append("\n")
    
    # Generate and show sample text
    preview.append("\nSample Text Preview:\n", style="bold red")
    sample_text = get_sample_text()
    
    # Create sample with markers for replacements
    sample = Text()
    replacement_glyphs = []
    for rep in config["replacements"]:
        replacement_glyphs.extend(rep["glyphs"])
    
    # Insert replacement markers in sample text
    for i, char in enumerate(sample_text):
        if i > 0 and i % 7 == 0 and replacement_glyphs:  # Every 7th position
            glyph = replacement_glyphs.pop(0)
            marker = glyph if len(glyph) == 1 else f"[{glyph}]"
            sample.append(marker, style="bold yellow")
        else:
            sample.append(char, style="blue")
    
    # Add the sample in a panel
    preview.append(Panel(sample, title="Sample", border_style="bright_black"))
    preview.append("\n")
    
    # Print the complete preview
    console.print(preview)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        print("Please provide a config file path")
