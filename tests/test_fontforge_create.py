import pytest
from unittest import mock
from pathlib import Path
import sys

# Adjust the import path if necessary
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.frankenfont.fontforge_create import create_custom_font

@pytest.fixture
def mock_fontforge():
    with mock.patch("src.frankenfont.fontforge_create.some_fontforge_function") as mocked_ff:
        yield mocked_ff

def test_create_custom_font_fontforge(mock_fontforge):
    """Smoke test for create_custom_font in fontforge_create.py using the FontForge backend."""
    config_path = Path(__file__).parent / "test_config.json"  # Ensure this config is valid for FontForge
    try:
        create_custom_font(str(config_path))
    except Exception as e:
        pytest.fail(f"create_custom_font raised an exception: {e}")
    # Optionally, verify that FontForge functions were called
    mock_fontforge.assert_called()
