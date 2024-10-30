import pytest
from unittest import mock
from pathlib import Path
import sys

# Adjust the import path if necessary
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.frankenfont.preview import preview_config

@pytest.fixture
def mock_image_show():
    with mock.patch("src.frankenfont.preview.Image.show") as mocked_show:
        yield mocked_show

@pytest.mark.parametrize("config_path", [
    Path(__file__).parent / "test_config.json",
    Path(__file__).parent / "test_config.toml"
])
def test_preview_with_configs(config_path, mock_image_show):
    """Parameterized test using a fixture to mock Image.show."""
    try:
        preview_config(str(config_path))
    except Exception as e:
        pytest.fail(f"preview_config raised an exception with config {config_path}: {e}")
    mock_image_show.assert_called()
