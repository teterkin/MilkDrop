from pathlib import Path

import pygame
import pytest

from milkdrop.controls import apply_key
from milkdrop.playlist import Playlist


class FakePlayer:
    def __init__(self):
        self.volume = 0.8
        self.log = []

    def toggle_pause(self):
        self.log.append(("pause",))

    def seek(self, delta):
        self.log.append(("seek", delta))

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, value))
        self.log.append(("volume", value))


def test_space_toggles_pause_and_escape_quits():
    player = FakePlayer()
    playlist = Playlist([])

    assert apply_key(pygame.K_SPACE, player, playlist) == "pause"
    assert player.log == [("pause",)]
    assert apply_key(pygame.K_ESCAPE, player, playlist) == "quit"


def test_v_requests_visualization_switch():
    player = FakePlayer()
    playlist = Playlist([])

    assert apply_key(pygame.K_v, player, playlist) == "visualize"


def test_arrows_seek_and_change_volume():
    player = FakePlayer()
    playlist = Playlist([])

    assert apply_key(pygame.K_LEFT, player, playlist) == "seek"
    assert apply_key(pygame.K_RIGHT, player, playlist) == "seek"
    assert player.log == [("seek", -5.0), ("seek", 5.0)]

    apply_key(pygame.K_UP, player, playlist)
    assert player.volume == pytest.approx(0.85)
    apply_key(pygame.K_DOWN, player, playlist)
    assert player.volume == pytest.approx(0.80)


def test_n_and_p_navigate_playlist():
    player = FakePlayer()
    playlist = Playlist([Path("a.mp3"), Path("b.mp3")])

    assert apply_key(pygame.K_n, player, playlist) == "next"
    assert playlist.index == 1
    assert apply_key(pygame.K_p, player, playlist) == "prev"
    assert playlist.index == 0


def test_r_cycles_repeat_modes():
    player = FakePlayer()
    playlist = Playlist([Path("a.mp3")], repeat="off")

    apply_key(pygame.K_r, player, playlist)
    assert playlist.repeat == "all"
    apply_key(pygame.K_r, player, playlist)
    assert playlist.repeat == "one"
    apply_key(pygame.K_r, player, playlist)
    assert playlist.repeat == "off"


def test_s_toggles_shuffle():
    player = FakePlayer()
    playlist = Playlist([Path("a.mp3"), Path("b.mp3")], shuffle=False)

    assert apply_key(pygame.K_s, player, playlist) == "shuffle"
    assert playlist.shuffle is True
    apply_key(pygame.K_s, player, playlist)
    assert playlist.shuffle is False

