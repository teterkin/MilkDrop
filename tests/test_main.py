import pytest

from milkdrop.__main__ import main


def test_main_help_exits_zero():
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
