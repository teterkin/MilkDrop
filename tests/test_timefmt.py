from milkdrop.timefmt import format_time


def test_formats_seconds_as_minutes_and_seconds():
    assert format_time(0) == "0:00"
    assert format_time(5) == "0:05"
    assert format_time(65) == "1:05"
    assert format_time(3599) == "59:59"


def test_clamps_negative_and_truncates_fraction():
    assert format_time(-3) == "0:00"
    assert format_time(65.9) == "1:05"
