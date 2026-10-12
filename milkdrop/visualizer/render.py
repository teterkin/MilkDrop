import numpy as np


def _bilinear(frame, x, y):
    h, w = frame.shape[:2]
    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    x1 = x0 + 1
    y1 = y0 + 1
    wx = (x - x0.astype(np.float32))[..., None]
    wy = (y - y0.astype(np.float32))[..., None]

    x0c = np.clip(x0, 0, w - 1)
    x1c = np.clip(x1, 0, w - 1)
    y0c = np.clip(y0, 0, h - 1)
    y1c = np.clip(y1, 0, h - 1)

    top = frame[y0c, x0c] * (1.0 - wx) + frame[y0c, x1c] * wx
    bottom = frame[y1c, x0c] * (1.0 - wx) + frame[y1c, x1c] * wx
    return top * (1.0 - wy) + bottom * wy


def warp(frame, zoom=1.0, rotate=0.0):
    frame = frame.astype(np.float32)
    h, w = frame.shape[:2]
    cy = (h - 1) / 2.0
    cx = (w - 1) / 2.0

    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    dy = ys - cy
    dx = xs - cx

    cos = np.float32(np.cos(rotate))
    sin = np.float32(np.sin(rotate))
    sx = (dx * cos - dy * sin) / zoom + cx
    sy = (dx * sin + dy * cos) / zoom + cy

    return _bilinear(frame, sx, sy)


def decay(frame, factor):
    return frame * np.float32(factor)


def overlay_spectrum(frame, bands, color=(255, 255, 255)):
    h, w = frame.shape[:2]
    count = len(bands)
    if count == 0:
        return frame

    band_width = max(1, w // count)
    bar_color = np.array(color, dtype=np.float32)

    for i, value in enumerate(bands):
        bar_height = int(np.clip(value, 0.0, 1.0) * h * 0.5)
        if bar_height <= 0:
            continue
        x0 = i * band_width
        x1 = min(w, x0 + band_width)
        frame[h - bar_height : h, x0:x1] += bar_color
    return frame


class Visualizer:
    def __init__(
        self,
        width,
        height,
        num_bands=32,
        decay_factor=0.90,
        beat_zoom=0.015,
        rotation=0.003,
    ):
        self.width = width
        self.height = height
        self.num_bands = num_bands
        self.decay_factor = decay_factor
        self.beat_zoom = beat_zoom
        self.rotation = rotation
        self.buffer = np.zeros((height, width, 3), dtype=np.float32)

    def render(self, bands, beat):
        self.buffer = decay(self.buffer, self.decay_factor)
        zoom = 1.0 + (self.beat_zoom if beat else 0.0)
        self.buffer = warp(self.buffer, zoom=zoom, rotate=self.rotation)
        overlay_spectrum(self.buffer, bands)
        np.clip(self.buffer, 0.0, 255.0, out=self.buffer)
        return self.buffer.astype(np.uint8)
