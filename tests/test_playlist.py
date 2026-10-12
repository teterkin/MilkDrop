from pathlib import Path
import random

from milkdrop.playlist import Playlist, scan_folder


def test_scan_folder_returns_only_mp3_sorted_case_insensitive(tmp_path):
    (tmp_path / "b.MP3").write_bytes(b"x")
    (tmp_path / "a.mp3").write_bytes(b"x")
    (tmp_path / "notes.txt").write_text("nope")
    (tmp_path / "cover.jpg").write_bytes(b"x")
    (tmp_path / "sub").mkdir()

    result = scan_folder(tmp_path)

    assert result == [tmp_path / "a.mp3", tmp_path / "b.MP3"]
    assert all(isinstance(p, Path) for p in result)


def test_next_advances_and_stops_at_end_when_repeat_off():
    pl = Playlist([Path("a.mp3"), Path("b.mp3")])

    assert pl.current == Path("a.mp3")
    assert pl.next() == Path("b.mp3")
    assert pl.next() == Path("b.mp3")


def test_repeat_all_wraps_next_and_prev():
    pl = Playlist([Path("a.mp3"), Path("b.mp3")], repeat="all")

    assert pl.prev() == Path("b.mp3")
    assert pl.next() == Path("a.mp3")


def test_repeat_one_stays_on_current_track():
    pl = Playlist([Path("a.mp3"), Path("b.mp3")], repeat="one")

    assert pl.next() == Path("a.mp3")
    assert pl.prev() == Path("a.mp3")


def test_empty_playlist_has_no_current_and_steps_return_none():
    pl = Playlist([])

    assert pl.current is None
    assert pl.next() is None
    assert pl.prev() is None


def test_shuffle_next_visits_every_track_once_before_repeating():
    tracks = [Path(f"{i}.mp3") for i in range(4)]
    pl = Playlist(tracks, shuffle=True, rng=random.Random(42))

    seen = {pl.current}
    for _ in range(3):
        seen.add(pl.next())

    assert seen == set(tracks)




