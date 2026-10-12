from milkdrop.visualizer.fractal import FractalVisualizer
from milkdrop.visualizer.mesh import SphereMeshVisualizer, WireframeMeshVisualizer
from milkdrop.visualizer.render import Visualizer

VISUALIZERS = {
    "milkdrop": Visualizer,
    "fractal": FractalVisualizer,
    "whitecap": WireframeMeshVisualizer,
    "sphere": SphereMeshVisualizer,
}


def cycle(index, total):
    if total <= 0:
        return 0
    return (index + 1) % total
