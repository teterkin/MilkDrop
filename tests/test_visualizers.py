import numpy as np

from milkdrop.visualizer import VISUALIZERS, cycle
from milkdrop.visualizer.fractal import FractalVisualizer
from milkdrop.visualizer.render import palette


def test_palette_returns_valid_rgb_and_varies_with_t():
    c0 = palette(0.0)
    c1 = palette(0.5)

    arr = np.asarray(c0)
    assert arr.shape == (3,)
    assert arr.dtype == np.uint8
    assert ((arr >= 0) & (arr <= 255)).all()
    assert not np.array_equal(np.asarray(c0), np.asarray(c1))


def test_palette_is_vectorized_over_arrays():
    result = palette(np.array([0.0, 0.25, 0.5, 0.75]))

    assert result.shape == (4, 3)
    assert result.dtype == np.uint8


def test_cycle_wraps_around_and_handles_empty():
    assert cycle(0, 3) == 1
    assert cycle(2, 3) == 0
    assert cycle(0, 0) == 0


def test_fractal_visualizer_renders_uint8_and_reacts_to_audio():
    viz = FractalVisualizer(width=48, height=32, num_bands=8)

    silence = viz.render(np.zeros(8), beat=False)
    assert silence.shape == (32, 48, 3)
    assert silence.dtype == np.uint8

    loud = None
    for _ in range(3):
        loud = viz.render(np.linspace(0.0, 1.0, 8), beat=True)

    assert loud.shape == (32, 48, 3)
    assert not np.array_equal(silence, loud)


def test_registry_exposes_all_visualizers():
    assert set(VISUALIZERS) == {"milkdrop", "fractal", "whitecap", "sphere"}

    for factory in VISUALIZERS.values():
        viz = factory(width=8, height=8, num_bands=4)
        assert hasattr(viz, "render")



