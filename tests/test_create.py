import os
import pytest
from unittest.mock import patch, MagicMock
from fontTools.ttLib import TTFont
from frankenfont.create import create_custom_font, load_config, merge_glyphs

CONFIG_PATH = "tests/test_config.toml"
config = load_config(CONFIG_PATH)
output_dir = config["fonts"]["output_directory"]
output_path = os.path.join(output_dir, config["fonts"]["output_name"])

@pytest.fixture(scope="module")
def setup_test_environment():
    if os.path.exists(output_path):
        os.remove(output_path)
    yield create_custom_font(CONFIG_PATH)
    if os.path.exists(output_path):
        os.remove(output_path)

@pytest.fixture
def mock_ttfont():
    with patch('fontTools.ttLib.TTFont') as mock:
        yield mock

def test_config_loading():
    """Test configuration file loading and parsing"""
    assert config["fonts"]["base"] == "tests/fonts/Brush Script.ttf"
    assert config["fonts"]["output_name"] == "test_custom_font.ttf"
    assert len(config["replacements"]) > 0
    assert config["replacements"][0]["symbols"] == ["!", "™"]

def test_config_loading_invalid_path():
    """Test handling of invalid config path"""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.toml")

def test_output_font_creation(setup_test_environment):
    """Test that output font file is created"""
    assert os.path.exists(output_path)

def test_merge_glyphs(mock_ttfont):
    """Test glyph merging functionality"""
    base_font = MagicMock()
    base_font["glyf"] = {}
    base_font["hmtx"] = {}
    base_font["cmap"].tables = [MagicMock()]
    base_font["cmap"].tables[0].cmap = {}
    
    symbols = ["A", "B"]
    merge_glyphs(base_font, "test_font.ttf", symbols)
    
    # Verify that TTFont was called to open symbol font
    mock_ttfont.assert_called_once_with("test_font.ttf")

def test_glyph_replacement(setup_test_environment):
    """Test that glyphs are correctly replaced in output font"""
    output_font = TTFont(output_path)
    cmap = output_font["cmap"].getBestCmap()

    for replacement in config["replacements"]:
        for symbol in replacement["symbols"]:
            assert ord(symbol) in cmap, f"Symbol {symbol} not found in font"

    output_font.close()

def test_no_extra_symbols(setup_test_environment):
    """Test that only specified symbols are added"""
    output_font = TTFont(output_path)
    cmap = output_font["cmap"].getBestCmap()
    expected_symbols = {ord(s) for r in config["replacements"] for s in r["symbols"]}
    assert set(cmap.keys()).issuperset(expected_symbols)
    output_font.close()

def test_create_custom_font_invalid_config():
    """Test handling of invalid configuration"""
    with pytest.raises(KeyError):
        create_custom_font("tests/invalid_config.toml")

@patch('os.makedirs')
def test_output_directory_creation(mock_makedirs):
    """Test that output directory is created if it doesn't exist"""
    create_custom_font(CONFIG_PATH)
    mock_makedirs.assert_called_once_with(output_dir, exist_ok=True)
import pytest
from unittest import mock
from pathlib import Path
import sys

# Adjust the import path if necessary
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.frankenfont.create import create_custom_font

@pytest.fixture
def mock_install_font():
    with mock.patch("src.frankenfont.create.install_font") as mocked_install:
        yield mocked_install

def test_create_custom_font_create_backend(mock_install_font):
    """Smoke test for create_custom_font in create.py using the default backend."""
    config_path = Path(__file__).parent / "test_config.json"  # Ensure this config is valid
    try:
        create_custom_font(str(config_path))
    except Exception as e:
        pytest.fail(f"create_custom_font raised an exception: {e}")
    mock_install_font.assert_called()
