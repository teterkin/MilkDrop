import shutil
import subprocess
from pathlib import Path

import numpy as np


class AudioPlayer:
    def __init__(self, music, decoder=None, sample_rate=44100):
        self.music = music
        self.decoder = decoder or decode_to_mono
        self.sample_rate = sample_rate
        self.track = None
        self.samples = None
        self.seek_offset = 0.0
        self.paused = False
        self.volume = 1.0

    def load(self, path):
        self.track = Path(path)
        self.music.load(str(self.track))
        self.samples = self.decoder(self.track, sample_rate=self.sample_rate)
        self.seek_offset = 0.0
        self.paused = False

    def play(self):
        self.music.play()
        self.paused = False

    def toggle_pause(self):
        if self.paused:
            self.music.unpause()
        else:
            self.music.pause()
        self.paused = not self.paused
        return self.paused

    def seek(self, seconds):
        target = max(0.0, self.position() + seconds)
        self.music.play(start=target)
        self.seek_offset = target
        self.paused = False
        return target

    def position(self):
        return resolve_position(self.music.get_pos(), self.seek_offset)

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, value))
        self.music.set_volume(self.volume)

    def analysis_window(self, window_size):
        if self.samples is None:
            return np.zeros(window_size, dtype=np.float32)
        return slice_for_analysis(
            self.samples, self.position(), self.sample_rate, window_size
        )


def decode_to_mono(path, sample_rate=44100):
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError("ffmpeg not found on PATH; install ffmpeg to decode mp3")

    command = [
        ffmpeg,
        "-nostdin",
        "-loglevel",
        "error",
        "-i",
        str(path),
        "-f",
        "s16le",
        "-ac",
        "1",
        "-ar",
        str(sample_rate),
        "-",
    ]
    result = subprocess.run(command, capture_output=True, check=True)
    return np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0


def resolve_position(raw_ms, seek_offset=0.0):
    return seek_offset + max(0, raw_ms) / 1000.0


def slice_for_analysis(samples, position, sample_rate, window_size):
    end = int(position * sample_rate)
    start = end - window_size
    window = np.zeros(window_size, dtype=np.float32)

    src_start = max(0, start)
    src_end = min(end, len(samples))
    if src_end > src_start:
        window[src_start - start : src_end - start] = samples[src_start:src_end]
    return window
