import os

import pytest

from frankenfont.cli import main

CONFIG_PATH = "tests/test_config.toml"
output_path = "tests/fonts/output/test_custom_font.ttf"


@pytest.fixture(scope="module")
def setup_test_environment():
    # Clean up output directory before tests
    if os.path.exists(output_path):
        os.remove(output_path)

    yield

    # Clean up after tests
    if os.path.exists(output_path):
        os.remove(output_path)


def test_cli_create_command(monkeypatch, capsys):
    test_args = ["create", CONFIG_PATH]
    monkeypatch.setattr("sys.argv", ["frankenfont"] + test_args)
    main()
    captured = capsys.readouterr()
    assert "Custom font saved to" in captured.out
    assert os.path.exists(output_path)


def test_cli_create_with_install(monkeypatch, capsys):
    test_args = ["create", CONFIG_PATH, "--install"]
    monkeypatch.setattr("sys.argv", ["frankenfont"] + test_args)

    def mock_install_font(font_path):
        assert font_path == output_path
        print("Mock installation successful for:", font_path)

    monkeypatch.setattr("frankenfont.create.install_font", mock_install_font)
    main()
    captured = capsys.readouterr()
    assert "Custom font saved to" in captured.out
    assert "Mock installation successful" in captured.out
import pytest
from unittest import mock
from pathlib import Path
import sys

# Adjust the import path if necessary
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.frankenfont.cli import main

@pytest.fixture
def mock_preview_config():
    with mock.patch("src.frankenfont.preview.preview_config") as mocked_preview:
        yield mocked_preview

def test_cli_main_with_valid_config(mock_preview_config):
    """Smoke test for CLI with a valid configuration file."""
    config_path = Path(__file__).parent / "test_config.json"
    sys.argv = ["frankenfont", str(config_path)]
    try:
        main()
    except SystemExit as e:
        assert e.code == 0
    mock_preview_config.assert_called_with(str(config_path))

def test_cli_main_without_arguments():
    """Test CLI behavior when no arguments are provided."""
    sys.argv = ["frankenfont"]
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == "Error: Please provide a config file path"
