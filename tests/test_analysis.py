import numpy as np
import pytest

from milkdrop.analysis import BeatDetector, SpectrumAnalyzer


def test_sine_energy_lands_in_expected_band_and_normalizes():
    sr = 44100
    t = np.arange(sr) / sr
    tone = 0.5 * np.sin(2 * np.pi * 1000 * t)

    analyzer = SpectrumAnalyzer(sr, num_bands=64)
    bands = analyzer.analyze(tone[: analyzer.fft_size])

    peak = int(np.argmax(bands))
    center = analyzer.band_centers[peak]

    assert abs(center - 1000) / 1000 < 0.5
    assert bands.max() == pytest.approx(1.0)


def test_beat_detector_triggers_on_onset_after_steady_state():
    detector = BeatDetector()

    steady = [detector.update(0.2) for _ in range(60)]
    assert steady[-5:] == [False] * 5

    assert detector.update(1.0) is True

