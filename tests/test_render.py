import numpy as np

from milkdrop.visualizer.render import Visualizer, decay, overlay_spectrum, warp


def test_warp_identity_keeps_frame():
    rng = np.random.default_rng(0)
    frame = rng.integers(0, 255, size=(32, 32, 3)).astype(np.float32)

    out = warp(frame, zoom=1.0, rotate=0.0)

    assert out.shape == frame.shape
    assert out.dtype == np.float32
    np.testing.assert_allclose(out[1:-1, 1:-1], frame[1:-1, 1:-1], atol=1.0)


def test_warp_zoom_moves_content_outward():
    frame = np.zeros((64, 64, 3), dtype=np.float32)
    frame[32, 40] = 255.0

    out = warp(frame, zoom=2.0, rotate=0.0)

    center_offset_x = 40 - 31.5
    expected_x = int(round(31.5 + center_offset_x * 2.0))
    assert out[32, expected_x, 0] > 100.0


def test_decay_scales_values_and_returns_float():
    frame = np.full((4, 4, 3), 100.0, dtype=np.float32)

    out = decay(frame, factor=0.5)

    assert out.dtype == np.float32
    np.testing.assert_allclose(out, 50.0)


def test_overlay_spectrum_keeps_shape_and_brightens_pixels():
    frame = np.zeros((40, 40, 3), dtype=np.float32)
    bands = np.linspace(0.0, 1.0, 8)

    out = overlay_spectrum(frame, bands, color=(255, 0, 0))

    assert out.shape == frame.shape
    assert out.max() > 0.0


def test_visualizer_silence_is_black_and_music_brightens():
    viz = Visualizer(width=32, height=32, num_bands=8)

    silence = viz.render(bands=np.zeros(8), beat=False)
    assert silence.shape == (32, 32, 3)
    assert silence.dtype == np.uint8
    assert np.count_nonzero(silence) == 0

    loud = None
    for _ in range(5):
        loud = viz.render(bands=np.linspace(0.0, 1.0, 8), beat=True)

    assert np.count_nonzero(loud) > 0

