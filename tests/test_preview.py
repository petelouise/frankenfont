import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
from PIL import Image, ImageFont

from src.frankenfont.preview import preview_config, load_config, get_font_name

@pytest.fixture
def mock_image():
    with patch('PIL.Image.new') as mock_new:
        mock_img = MagicMock()
        mock_new.return_value = mock_img
        mock_img.show = MagicMock()
        yield mock_img

@pytest.fixture
def mock_imagefont():
    with patch('PIL.ImageFont.truetype') as mock_font:
        mock_font.return_value = MagicMock()
        yield mock_font

@pytest.mark.parametrize("config_path,expected_ext", [
    ("test_config.json", "json"),
    ("test_config.toml", "toml")
])
def test_load_config_file_types(config_path, expected_ext):
    """Test loading different config file types"""
    with patch(f"{'json' if expected_ext == 'json' else 'toml'}.load") as mock_load:
        mock_load.return_value = {"fonts": {"base": "test.ttf"}}
        load_config(config_path)
        mock_load.assert_called_once()

def test_load_config_invalid_extension():
    """Test handling of invalid config file extension"""
    with pytest.raises(ValueError, match="Config file must be .toml or .json"):
        load_config("config.invalid")

def test_get_font_name():
    """Test font name extraction from path"""
    assert get_font_name("/path/to/Arial.Bold.ttf") == "Arial Bold"
    assert get_font_name("ComicSans.ttf") == "ComicSans"

@pytest.mark.parametrize("config_path", [
    Path(__file__).parent / "test_config.json",
    Path(__file__).parent / "test_config.toml"
])
def test_preview_with_configs(config_path, mock_image, mock_imagefont):
    """Test preview generation with different config files"""
    preview_config(str(config_path))
    mock_image.show.assert_called_once()
    mock_imagefont.assert_called()

def test_preview_config_missing_font():
    """Test handling of missing font file"""
    with patch('PIL.ImageFont.truetype', side_effect=OSError):
        with pytest.raises(SystemExit):
            preview_config("test_config.toml")

@patch('tempfile.NamedTemporaryFile')
@patch('os.unlink')
def test_preview_cleanup(mock_unlink, mock_tempfile, mock_image):
    """Test temporary file cleanup"""
    mock_temp = MagicMock()
    mock_temp.name = "temp.png"
    mock_tempfile.return_value.__enter__.return_value = mock_temp
    
    preview_config("test_config.toml")
    
    mock_unlink.assert_called_once_with("temp.png")
