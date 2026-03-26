from pathlib import Path

import matplotlib.pyplot as plt

from svgecko import SVG

OUTPUT_DIR = Path(__file__).parent / "output"

SVG_STRING = """
<svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
    <polygon points="20,20 100,20 100,100 20,100" fill="#2f5f8f"/>
    <polyline points="20,60 60,20 100,60 60,100 20,60" fill="none" stroke="#d94f4f" stroke-width="4"/>
</svg>
"""


def _render(svg: SVG, target_width: float = 220.0):
    width, _height = svg.shape
    scale = target_width / width if width else 1.0
    return svg.to_pil_image(scale=scale)


def _shear(point):
    x, y = point
    return (x + y * 0.25, y)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    svg = SVG.from_string(SVG_STRING)
    transformed = svg.transform(_shear)

    fig, axes = plt.subplots(1, 2, figsize=(7, 3))

    axes[0].imshow(_render(svg))
    axes[0].set_title("Points: original")
    axes[0].set_axis_off()

    axes[1].imshow(_render(transformed))
    axes[1].set_title("Points: sheared")
    axes[1].set_axis_off()

    fig.tight_layout()
    output_path = OUTPUT_DIR / "points_shear.png"
    fig.savefig(output_path, dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
