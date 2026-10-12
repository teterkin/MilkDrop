import pytest

from milkdrop.__main__ import main
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
