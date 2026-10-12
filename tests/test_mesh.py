import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import numpy as np
import pytest

pygame = pytest.importorskip("pygame")

from milkdrop.visualizer.mesh import (
    WireframeMeshVisualizer,
    make_grid,
    project,
    rotate,
)


def test_make_grid_returns_flat_xy_plane():
    grid = make_grid(4)

    assert grid.shape == (16, 3)
    assert (grid[:, 2] == 0).all()
    assert grid[:, 0].min() == -1.0
    assert grid[:, 0].max() == 1.0
    assert grid[:, 1].min() == -1.0
    assert grid[:, 1].max() == 1.0


def test_rotate_is_identity_at_zero_and_preserves_length():
    pts = make_grid(3)

    same = rotate(pts, 0.0, 0.0)
    assert np.allclose(same, pts)

    rotated = rotate(pts, 0.5, 1.1)
    assert rotated.shape == pts.shape
    assert np.allclose(
        np.linalg.norm(rotated, axis=1), np.linalg.norm(pts, axis=1)
    )


def test_project_centers_origin_and_foreshortens_with_depth():
    center = np.array([[0.0, 0.0, 0.0]], dtype=np.float32)
    xs, ys = project(center, width=100, height=50, focal=2.0)
    assert xs.shape == (1,)
    assert ys.shape == (1,)
    assert np.allclose(xs, 50.0)
    assert np.allclose(ys, 25.0)

    near = np.array([[1.0, 0.0, -0.5]], dtype=np.float32)
    far = np.array([[1.0, 0.0, 0.5]], dtype=np.float32)
    xs_near, _ = project(near, width=100, height=50, focal=2.0)
    xs_far, _ = project(far, width=100, height=50, focal=2.0)
    assert (xs_near[0] - 50.0) > (xs_far[0] - 50.0)


def test_wireframe_visualizer_renders_uint8_and_reacts_to_audio():
    pygame.init()
    try:
        viz = WireframeMeshVisualizer(width=64, height=40, num_bands=8)

        silence = viz.render(np.zeros(8), beat=False)
        assert silence.shape == (40, 64, 3)
        assert silence.dtype == np.uint8

        loud = None
        for _ in range(3):
            loud = viz.render(np.linspace(0.0, 1.0, 8), beat=True)

        assert loud.shape == (40, 64, 3)
        assert not np.array_equal(silence, loud)
    finally:
        pygame.quit()
