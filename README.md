# 🦎 SVGecko

Lightweight library for **arbitrary** geometric SVG transformations. Created because existing libraries had a hard time
applying other than [affine transformations](https://en.wikipedia.org/wiki/Affine_transformation) to SVGs.
So far only supports SVGs with absolute [path commands](https://css-tricks.com/svg-path-syntax-illustrated-guide/).

## Installation

In your terminal, run the following command:

```
pip install svgecko
```

## Getting Started

The following code loads your svg file, shifts it by one unit in both the x and y directions, and plots the result.

```python
import matplotlib.pyplot as plt

from svgecko.svg import SVG

# Load the SVG
svg_path = '/path/to/your/svg/file.svg'
svg = SVG.from_file(svg_path)

# Define the transformation and apply it to the SVG
transformation = lambda point: (point[0] + 1, point[1] + 1)
svg.transform(transformation=transformation, inplace=True)

# Plot the transformed SVG
image = svg.to_pil_image()
plt.imshow(image)
plt.show()
```

## Roadmap

- [ ] Support for angular rotation path commands
- [ ] Support for relative path commands
- [ ] Support for style positioning commands (e.g. translate)

