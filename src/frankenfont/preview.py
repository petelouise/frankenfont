import random
import string
from typing import List, Dict

import fontforge
import rich
from rich.console import Console
from rich.text import Text

def get_sample_text(replacements: List[Dict]) -> str:
    """Generate sample text including replacement glyphs and random characters"""
    # Get all replacement symbols
    symbols = []
    for replacement in replacements:
        symbols.extend(replacement["glyphs"])
    
    # Add some random ASCII letters and punctuation
    sample = list(random.sample(string.ascii_letters + string.punctuation, 20))
    
    # Insert replacement symbols at random positions
    for symbol in symbols:
        pos = random.randint(0, len(sample))
        sample.insert(pos, symbol)
    
    return ' '.join([''.join(sample[i:i+5]) for i in range(0, len(sample), 5)])

def preview_config(config_path: str) -> None:
    """Display a preview of the font configuration"""
    console = Console()
    
    # Load fonts
    base_font = fontforge.open(config["fonts"]["base"])
    base_name = base_font.fontname
    base_font.close()
    
    # Create preview text
    preview = Text()
    preview.append("\n🔤 Font Preview\n\n", style="bold magenta")
    preview.append(f"Base Font: {base_name}\n\n", style="blue")
    
    # Show replacements
    preview.append("Replacement Glyphs:\n", style="bold green")
    for replacement in config["replacements"]:
        font_path = replacement["font"]
        font = fontforge.open(font_path)
        preview.append(f"\nFrom {font.fontname}:\n", style="cyan")
        preview.append(' '.join(replacement["glyphs"]) + "\n", style="yellow")
        font.close()
    
    # Show sample text
    preview.append("\nSample Text:\n", style="bold red")
    sample = get_sample_text(config["replacements"])
    preview.append(sample + "\n", style="italic")
    
    # Print the preview
    console.print(preview)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        preview_config(sys.argv[1])
    else:
        print("Please provide a config file path")
