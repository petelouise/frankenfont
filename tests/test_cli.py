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
