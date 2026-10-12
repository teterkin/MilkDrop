import numpy as np

from milkdrop.visualizer.render import palette


class FractalVisualizer:
    def __init__(self, width, height, num_bands=64, max_iter=32):
        self.width = width
        self.height = height
        self.num_bands = num_bands
        self.max_iter = max_iter
        self.phase = 0.0

        aspect = height / width
        xs = np.linspace(-1.6, 1.6, width, dtype=np.float32)
        ys = np.linspace(-1.6 * aspect, 1.6 * aspect, height, dtype=np.float32)
        xx, yy = np.meshgrid(xs, ys)
        self._grid = (xx + 1j * yy).astype(np.complex64)

    def render(self, bands, beat):
        bands = np.asarray(bands, dtype=np.float32)
        if bands.size:
            edge = max(1, len(bands) // 8)
            bass = float(bands[:edge].mean())
            treble = float(bands[-edge:].mean())
        else:
            bass = treble = 0.0

        radius = 0.7 + 0.2 * bass + (0.08 if beat else 0.0)
        c = np.complex64(
            radius * np.cos(self.phase) + 1j * radius * np.sin(self.phase)
        )

        z = self._grid.copy()
        counts = np.full(z.shape, self.max_iter, dtype=np.float32)
        alive = np.ones(z.shape, dtype=bool)
        for i in range(self.max_iter):
            z[alive] = z[alive] * z[alive] + c
            escaped = alive & (z.real * z.real + z.imag * z.imag > 4.0)
            counts[escaped] = i
            alive &= ~escaped
            if not alive.any():
                break

        rgb = palette(counts / self.max_iter, phase=self.phase * 0.5)
        self.phase += 0.02 + 0.3 * treble + (0.1 if beat else 0.0)
        return rgb
