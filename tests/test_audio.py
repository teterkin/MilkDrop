import math
import struct
import wave

import numpy as np

from milkdrop.audio import (
    AudioPlayer,
    decode_to_mono,
    resolve_position,
    slice_for_analysis,
)


def make_wav(path, freq=440.0, secs=0.1, sample_rate=44100):
    frames = bytearray()
    for i in range(int(sample_rate * secs)):
        value = int(0.5 * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
        frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(bytes(frames))


def test_decode_to_mono_returns_expected_signal(tmp_path):
    wav = tmp_path / "tone.wav"
    make_wav(wav, freq=440.0, secs=0.1, sample_rate=44100)

    samples = decode_to_mono(wav, sample_rate=44100)

    assert samples.ndim == 1
    assert samples.dtype == np.float32
    assert abs(len(samples) - 4410) < 100

    spectrum = np.abs(np.fft.rfft(samples))
    freqs = np.fft.rfftfreq(len(samples), 1 / 44100)
    assert abs(freqs[int(np.argmax(spectrum))] - 440.0) < 5.0


def test_slice_for_analysis_returns_window_ending_at_position():
    samples = np.arange(1000, dtype=np.float32)

    window = slice_for_analysis(samples, position=2.0, sample_rate=100, window_size=50)

    assert len(window) == 50
    assert window[0] == 150
    assert window[-1] == 199


def test_slice_for_analysis_zero_pads_before_track_start():
    samples = np.ones(100, dtype=np.float32)

    window = slice_for_analysis(samples, position=0.2, sample_rate=100, window_size=50)

    assert len(window) == 50
    assert window[0] == 0.0
    assert window[-1] == 1.0
    assert int(np.count_nonzero(window)) == 20


def test_resolve_position_combines_seek_offset_and_clamps_negative():
    assert resolve_position(raw_ms=500, seek_offset=10.0) == 10.5
    assert resolve_position(raw_ms=-1, seek_offset=10.0) == 10.0


class FakeMusic:
    def __init__(self):
        self.loaded = None
        self.played_start = None
        self.raw_ms = 0
        self.volume = None

    def load(self, path):
        self.loaded = path

    def play(self, start=0.0):
        self.played_start = start

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def get_pos(self):
        return self.raw_ms

    def set_volume(self, value):
        self.volume = value


def test_audio_player_loads_seeks_and_tracks_position():
    fake = FakeMusic()
    player = AudioPlayer(fake, decoder=lambda path, sample_rate: np.zeros(10, np.float32))

    player.load("x.mp3")
    assert fake.loaded == "x.mp3"

    player.seek(30)
    assert fake.played_start == 30

    fake.raw_ms = 1000
    assert player.position() == 31.0


def test_audio_player_clamps_volume_to_unit_range():
    fake = FakeMusic()
    player = AudioPlayer(fake, decoder=lambda path, sample_rate: np.zeros(10, np.float32))

    player.set_volume(2.0)
    assert fake.volume == 1.0
    player.set_volume(-1.0)
    assert fake.volume == 0.0




