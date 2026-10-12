from milkdrop.visualizer.fractal import FractalVisualizer
from milkdrop.visualizer.render import Visualizer

VISUALIZERS = {
    "milkdrop": Visualizer,
    "fractal": FractalVisualizer,
}


def cycle(index, total):
    if total <= 0:
        return 0
    return (index + 1) % total
