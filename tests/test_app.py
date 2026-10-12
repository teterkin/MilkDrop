import math
import os
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pytest

pygame = pytest.importorskip("pygame")

from milkdrop.app import INTERNAL_HEIGHT, INTERNAL_WIDTH, MilkDropApp
from milkdrop.config import Config


def _make_wav(path, freq=440.0, secs=0.1, sample_rate=44100):
    frames = bytearray()
    for i in range(int(sample_rate * secs)):
        value = int(0.5 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(bytes(frames))


def test_app_computes_frame_headless(tmp_path):
    wav = tmp_path / "tone.wav"
    _make_wav(wav)

    app = MilkDropApp(str(wav), Config(width=64, height=48))
    try:
        frame = app.compute_frame()
        assert frame.shape == (INTERNAL_HEIGHT, INTERNAL_WIDTH, 3)
        assert frame.dtype == np.uint8
    finally:
        pygame.quit()


def test_run_loop_exits_on_quit_event(tmp_path):
    wav = tmp_path / "tone.wav"
    _make_wav(wav)

    app = MilkDropApp(str(wav), Config(width=64, height=48))
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    app.run()
    assert app.running is False


def test_v_switches_visualizer_mode_and_updates_config(tmp_path):
    wav = tmp_path / "tone.wav"
    _make_wav(wav)

    app = MilkDropApp(str(wav), Config(width=64, height=48, visualizer="milkdrop"))
    try:
        assert app.mode_name == "milkdrop"

        app._handle_action("visualize")
        assert app.mode_name == "fractal"
        assert app.config.visualizer == "fractal"

        app._handle_action("visualize")
        assert app.mode_name == "whitecap"
        assert app.config.visualizer == "whitecap"

        app._handle_action("visualize")
        assert app.mode_name == "milkdrop"

        frame = app.compute_frame()
        assert frame.shape == (INTERNAL_HEIGHT, INTERNAL_WIDTH, 3)
        assert frame.dtype == np.uint8
    finally:
        pygame.quit()


