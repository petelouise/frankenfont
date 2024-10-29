import subprocess

from frankenfont.cli import main


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

    monkeypatch.setattr("frankenfont.font_creator.install_font", mock_install_font)
    main()
    captured = capsys.readouterr()
    assert "Custom font saved to" in captured.out
    assert "Mock installation successful" in captured.out
