import json

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


def test_main_fullscreen_flag_is_applied_but_not_persisted(tmp_path, monkeypatch):
    config_path = tmp_path / "config.json"
    monkeypatch.setattr("milkdrop.__main__.CONFIG_PATH", config_path)

    seen = {}

    class FakeApp:
        def __init__(self, path, config):
            seen["fullscreen"] = config.fullscreen

        def run(self):
            pass

    monkeypatch.setattr("milkdrop.__main__.MilkDropApp", FakeApp)

    assert main(["--fullscreen", "song.mp3"]) == 0
    assert seen["fullscreen"] is True

    saved = json.loads(config_path.read_text())
    assert saved.get("fullscreen", False) is False

    assert main(["song.mp3"]) == 0
    assert seen["fullscreen"] is False

