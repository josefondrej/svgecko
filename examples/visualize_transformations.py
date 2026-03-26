import math
from pathlib import Path

import matplotlib.pyplot as plt

from svgecko import SVG
from svgecko.utils import load_python_logo, CROSS_PATH

OUTPUT_DIR = Path(__file__).parent / "output"


def _render(svg: SVG, target_width: float = 220.0):
    width, _height = svg.shape
    scale = target_width / width if width else 1.0
    return svg.to_pil_image(scale=scale)


def _rotate(angle_degrees: float):
    angle = math.radians(angle_degrees)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    def _apply(point):
        x, y = point
        return (x * cos_angle - y * sin_angle, x * sin_angle + y * cos_angle)

    return _apply


def _wave(point):
    x, y = point
    return (x + math.sin(y * 0.12) * 6.0, y + math.cos(x * 0.12) * 6.0)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cross = SVG.from_file(str(CROSS_PATH))
    logo = load_python_logo()

    translated_cross = cross.transform(lambda p: (p[0] + 1.5, p[1] + 1.0))
    rotated_cross = cross.transform(_rotate(45))
    waved_logo = logo.transform(_wave)

    fig, axes = plt.subplots(2, 2, figsize=(8, 6))

    axes[0, 0].imshow(_render(cross))
    axes[0, 0].set_title("Cross: original")
    axes[0, 0].set_axis_off()

    axes[0, 1].imshow(_render(translated_cross))
    axes[0, 1].set_title("Cross: translated")
    axes[0, 1].set_axis_off()

    axes[1, 0].imshow(_render(rotated_cross))
    axes[1, 0].set_title("Cross: rotated")
    axes[1, 0].set_axis_off()

    axes[1, 1].imshow(_render(waved_logo, target_width=260.0))
    axes[1, 1].set_title("Logo: wave")
    axes[1, 1].set_axis_off()

    fig.tight_layout()
    output_path = OUTPUT_DIR / "transformations.png"
    fig.savefig(output_path, dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
