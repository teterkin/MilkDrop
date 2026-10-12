import pytest

from milkdrop.__main__ import main
from milkdrop.config import Config
from milkdrop.playlist import PlaylistError


def test_main_help_exits_zero():
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0


def test_main_reports_unreadable_folder_without_traceback(tmp_path, monkeypatch, capsys):
    def boom(path):
        raise PlaylistError(f"cannot read folder '{path}'")

    monkeypatch.setattr("milkdrop.app.scan_folder", boom)

    code = main([str(tmp_path)])

    assert code == 1
    err = capsys.readouterr().err
    assert "cannot read folder" in err


def test_main_saves_selected_visualizer_on_exit(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr("milkdrop.__main__.CONFIG_PATH", config_path)

    class FakeApp:
        def __init__(self, path, config):
            self.config = config

        def run(self):
            self.config.visualizer = "fractal"

    monkeypatch.setattr("milkdrop.__main__.MilkDropApp", FakeApp)

    code = main(["song.mp3"])

    assert code == 0
    assert Config.load(config_path).visualizer == "fractal"

