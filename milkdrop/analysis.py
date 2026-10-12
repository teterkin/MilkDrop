import numpy as np


class SpectrumAnalyzer:
    def __init__(
        self,
        sample_rate,
        num_bands=32,
        fmin=20.0,
        fmax=16000.0,
        fft_size=2048,
        smoothing=0.0,
    ):
        self.sample_rate = sample_rate
        self.num_bands = num_bands
        self.fft_size = fft_size
        self.fmin = fmin
        self.fmax = min(fmax, sample_rate / 2.0)
        self.smoothing = smoothing

        edges = np.geomspace(self.fmin, self.fmax, num_bands + 1)
        self.band_centers = np.sqrt(edges[:-1] * edges[1:])
        self._edges = edges

        self._window = np.hanning(fft_size)
        freqs = np.fft.rfftfreq(fft_size, 1.0 / sample_rate)
        self._bin_index = [
            np.where((freqs >= edges[i]) & (freqs < edges[i + 1]))[0]
            for i in range(num_bands)
        ]
        self._prev = np.zeros(num_bands)

    def analyze(self, samples):
        buf = np.zeros(self.fft_size)
        n = min(len(samples), self.fft_size)
        buf[:n] = samples[:n]

        spectrum = np.abs(np.fft.rfft(buf * self._window))
        bands = np.array(
            [
                spectrum[idx].mean() if len(idx) else 0.0
                for idx in self._bin_index
            ]
        )
        peak = bands.max()
        if peak > 0:
            bands = bands / peak
        if self.smoothing:
            bands = self.smoothing * self._prev + (1.0 - self.smoothing) * bands
        self._prev = bands
        return bands


class BeatDetector:
    def __init__(self, history=43, threshold=1.3, min_level=0.01):
        self.history = history
        self.threshold = threshold
        self.min_level = min_level
        self._samples = []

    def update(self, energy):
        average = sum(self._samples) / len(self._samples) if self._samples else 0.0
        self._samples.append(energy)
        if len(self._samples) > self.history:
            self._samples.pop(0)

        if average <= self.min_level:
            return False
        return energy > average * self.threshold
