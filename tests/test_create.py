import os

import pytest
from fontTools.ttLib import TTFont

from frankenfont.create import create_custom_font, load_config

CONFIG_PATH = "tests/test_config.toml"
config = load_config(CONFIG_PATH)
output_dir = config["fonts"]["output_directory"]
output_path = os.path.join(output_dir, config["fonts"]["output_name"])


@pytest.fixture(scope="module")
def setup_test_environment():
    # Clean up output directory before tests
    if os.path.exists(output_path):
        os.remove(output_path)

    # Run the font creation function
    yield create_custom_font(CONFIG_PATH)

    # Clean up after tests
    if os.path.exists(output_path):
        os.remove(output_path)


# Core Function Tests
def test_config_loading():
    assert config["fonts"]["base"] == "tests/fonts/Brush Script.ttf"
    assert config["fonts"]["output_name"] == "test_custom_font.ttf"
    assert len(config["replacements"]) > 0
    assert config["replacements"][0]["symbols"] == ["!", "™"]


def test_output_font_creation(setup_test_environment):
    assert os.path.exists(output_path)


def test_glyph_replacement(setup_test_environment):
    output_font = TTFont(output_path)
    cmap = output_font["cmap"].getBestCmap()

    for symbol in config["replacements"][0]["symbols"]:
        assert ord(symbol) in cmap

    for symbol in config["replacements"][1]["symbols"]:
        assert ord(symbol) in cmap

    output_font.close()


def test_no_extra_symbols(setup_test_environment):
    output_font = TTFont(output_path)
    cmap = output_font["cmap"].getBestCmap()
    expected_symbols = {ord(s) for r in config["replacements"] for s in r["symbols"]}
    assert set(cmap.keys()).issuperset(expected_symbols)
    output_font.close()
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
