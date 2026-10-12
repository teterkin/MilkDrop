import numpy as np
import pygame

from milkdrop.visualizer.render import palette


def make_grid(n):
    xs = np.linspace(-1.0, 1.0, n, dtype=np.float32)
    ys = np.linspace(-1.0, 1.0, n, dtype=np.float32)
    xx, yy = np.meshgrid(xs, ys, indexing="ij")
    return np.stack([xx, yy, np.zeros_like(xx)], axis=-1).reshape(-1, 3)


def rotate(points, ax, ay):
    points = np.asarray(points, dtype=np.float32)
    cos_y, sin_y = np.cos(ay), np.sin(ay)
    cos_x, sin_x = np.cos(ax), np.sin(ax)

    x, y, z = points[:, 0], points[:, 1], points[:, 2]

    x1 = x * cos_y + z * sin_y
    z1 = -x * sin_y + z * cos_y

    y2 = y * cos_x - z1 * sin_x
    z2 = y * sin_x + z1 * cos_x

    return np.stack([x1, y2, z2], axis=-1).astype(np.float32)


def project(points, width, height, focal):
    points = np.asarray(points, dtype=np.float32)
    depth = focal + points[:, 2]
    scale = focal / depth

    xs = width * 0.5 + points[:, 0] * scale * (width * 0.5)
    ys = height * 0.5 - points[:, 1] * scale * (height * 0.5)
    return xs.astype(np.float32), ys.astype(np.float32)


class WireframeMeshVisualizer:
    def __init__(self, width, height, num_bands=64, n=20, focal=2.2):
        self.width = width
        self.height = height
        self.num_bands = num_bands
        self.n = n
        self.focal = focal
        self._base = make_grid(n).reshape(n, n, 3)
        self._surface = None
        self.angle = 0.0
        self.tilt = -0.95

    def render(self, bands, beat):
        bands = np.asarray(bands, dtype=np.float32)
        n = self.n
        if bands.size:
            edge = max(1, len(bands) // 8)
            bass = float(bands[:edge].mean())
            treble = float(bands[-edge:].mean())
            profile = np.interp(
                np.linspace(0.0, 1.0, n),
                np.linspace(0.0, 1.0, len(bands)),
                bands,
            )
        else:
            bass = treble = 0.0
            profile = np.zeros(n, dtype=np.float32)

        amp = 0.25 + 0.9 * bass + (0.35 if beat else 0.0)
        wave = np.sin(np.linspace(0.0, 3.0 * np.pi, n) + self.angle * 2.0)
        heights = (profile + 0.15 * wave)[None, :] * amp

        pts = self._base.copy()
        pts[:, :, 2] = heights
        rotated = rotate(pts.reshape(-1, 3), self.tilt, self.angle)
        xs, ys = project(rotated, self.width, self.height, self.focal)
        depth = self.focal + rotated[:, 2]

        span = np.ptp(depth) if np.ptp(depth) else 1.0
        t = (depth - depth.min()) / span
        colors = palette(t, phase=self.angle)
        bright = (0.35 + 0.65 * (1.0 - t))[:, None]
        colors = np.clip(colors.astype(np.float32) * bright, 0, 255).astype(np.uint8)

        xs = xs.reshape(n, n)
        ys = ys.reshape(n, n)
        colors = colors.reshape(n, n, 3)

        if self._surface is None:
            self._surface = pygame.Surface((self.width, self.height))
        surface = self._surface
        surface.fill((0, 0, 0))
        for i in range(n):
            for j in range(n):
                color = tuple(int(v) for v in colors[i, j])
                here = (int(xs[i, j]), int(ys[i, j]))
                if j + 1 < n:
                    pygame.draw.line(
                        surface, color, here, (int(xs[i, j + 1]), int(ys[i, j + 1]))
                    )
                if i + 1 < n:
                    pygame.draw.line(
                        surface, color, here, (int(xs[i + 1, j]), int(ys[i + 1, j]))
                    )

        self.angle += 0.008 + 0.25 * treble + (0.02 if beat else 0.0)
        frame = pygame.surfarray.array3d(surface)
        return frame.swapaxes(0, 1).copy()
