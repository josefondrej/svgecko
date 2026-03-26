# 🦎 SVGecko

[![PyPI version](https://badge.fury.io/py/svgecko.svg)](https://badge.fury.io/py/svgecko)
[![Python Support](https://img.shields.io/pypi/pyversions/svgecko.svg)](https://pypi.org/project/svgecko/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python library for **arbitrary** geometric SVG transformations. SVGecko enables you to apply any mathematical transformation function to SVG files, going beyond simple affine transformations to support complex geometric operations.

## ✨ Features

- **Arbitrary Transformations**: Apply any mathematical function `(x, y) → (x', y')` to SVG coordinates
- **Comprehensive SVG Support**: Handles path commands, coordinate attributes, and CSS transforms
- **Multiple Command Types**: Supports absolute, relative, and arc path commands
- **Style Transform Support**: Transforms CSS `translate()` functions in style attributes
- **Easy Integration**: Simple API with PIL Image conversion
- **Type Safety**: Full type annotations for better development experience

## 🚀 Installation

```bash
pip install svgecko
```

## 📖 Quick Start

### Basic Transformation

```python
import matplotlib.pyplot as plt
from svgecko import SVG

# Load an SVG file
svg = SVG.from_file('example.svg')

# Apply a transformation (shift by 1 unit in both directions)
transformation = lambda point: (point[0] + 1, point[1] + 1)
transformed_svg = svg.transform(transformation)

# Convert to PIL Image and display
image = transformed_svg.to_pil_image()
plt.imshow(image)
plt.show()
```

### Advanced Transformations

```python
import math
from svgecko import SVG

svg = SVG.from_file('logo.svg')

# Rotate around origin by 45 degrees
def rotate_45(point):
    x, y = point
    angle = math.radians(45)
    new_x = x * math.cos(angle) - y * math.sin(angle)
    new_y = x * math.sin(angle) + y * math.cos(angle)
    return (new_x, new_y)

# Scale by factor of 2
def scale_2x(point):
    return (point[0] * 2, point[1] * 2)

# Apply transformations
rotated_svg = svg.transform(rotate_45)
scaled_svg = svg.transform(scale_2x)

# Save results
rotated_svg.to_file('rotated_logo.svg')
scaled_svg.to_file('scaled_logo.svg')
```

### Working with Different SVG Elements

```python
from svgecko import SVG

# SVG with various elements
svg_content = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <!-- Path with absolute commands -->
    <path d="M10 10 L20 20 L30 10 Z" fill="blue"/>
    
    <!-- Path with relative commands -->
    <path d="M50 50 l10 10 l10 -10 z" fill="red"/>
    
    <!-- Path with arc commands -->
    <path d="M70 70 A10 10 0 0 1 90 70" fill="green"/>
    
    <!-- Element with CSS transform -->
    <rect x="10" y="80" width="20" height="10" 
          style="transform: translate(5, 5)" fill="orange"/>
</svg>
"""

svg = SVG.from_string(svg_content)

# Apply transformation to all elements
def complex_transform(point):
    x, y = point
    # Apply a wave-like transformation
    new_x = x + math.sin(y * 0.1) * 5
    new_y = y + math.cos(x * 0.1) * 5
    return (new_x, new_y)

transformed_svg = svg.transform(complex_transform)
```

## 📚 API Reference

### SVG Class

The main class for working with SVG files.

#### Methods

- `from_file(file_path: str, encoding: str = 'utf-8') -> SVG`
  - Load SVG from a file
  
- `from_string(svg_string: str, encoding: str = 'utf-8') -> SVG`
  - Load SVG from a string
  
- `transform(transformation: Callable[[Tuple[float, float]], Tuple[float, float]], inplace: bool = False) -> SVG`
  - Apply a transformation function to all coordinates
  - `transformation`: Function that takes (x, y) and returns (x', y')
  - `inplace`: If True, modify the current SVG; if False, return a new SVG
  
- `to_file(file_path: str, encoding: str = 'utf-8') -> None`
  - Save SVG to a file
  
- `to_string(encoding: str = 'utf-8') -> str`
  - Convert SVG to XML string
  
- `to_pil_image(**kwargs) -> Image.Image`
  - Convert SVG to PIL Image
  - Supports all cairosvg.svg2png parameters (scale, width, height, etc.)

#### Properties

- `xml`: Access to the underlying XML element tree
- `shape`: Tuple of (width, height) as floats

### Path and PathCommand Classes

For working with SVG path data directly.

```python
from svgecko import Path, PathCommand

# Parse a path string
path = Path.from_command_string('M10 10 L20 20 Z')

# Transform the path
transformed_path = path.transform(lambda p: (p[0] + 5, p[1] + 5))

# Get the command string
print(transformed_path.command_string)  # "M 15.0 15.0 L 25.0 25.0 Z"
```

## 🎯 Supported SVG Features

### ✅ Fully Supported
- **Absolute path commands**: M, L, C, S, Q, T, H, V, Z
- **Relative path commands**: m, l, c, s, q, t, h, v (converted to absolute)
- **Arc commands**: A, a (approximated as line segments)
- **Coordinate attributes**: x, y, x1, y1, x2, y2, cx, cy, fx, fy
- **Points attributes**: polyline/polygon points
- **CSS transforms**: translate(), translateX(), translateY() in style and transform attributes
- **File I/O**: Load from/save to files and strings
- **Image conversion**: Convert to PIL Image objects

### 🔄 Automatic Conversions
- Relative commands (`l`, `m`, etc.) → Absolute commands (`L`, `M`, etc.)
- Horizontal/Vertical commands (`H`, `V`) → Line commands (`L`)
- Arc commands (`A`, `a`) → Line segments (approximation)

## 🧪 Examples

### Mathematical Transformations

```python
# Spiral transformation
def spiral(point, turns=2):
    x, y = point
    r = math.sqrt(x*x + y*y)
    angle = math.atan2(y, x) + r * turns * 2 * math.pi / 100
    return (r * math.cos(angle), r * math.sin(angle))

# Wave distortion
def wave_distort(point):
    x, y = point
    return (x + math.sin(y * 0.1) * 10, y + math.cos(x * 0.1) * 10)

# Perspective projection
def perspective(point, focal_length=100):
    x, y = point
    z = 50  # Assume z-coordinate
    scale = focal_length / (focal_length + z)
    return (x * scale, y * scale)
```

### Visualization Scripts

Install `matplotlib` and run:

```bash
python examples/visualize_transformations.py
python examples/visualize_points.py
```

The scripts save PNGs into `examples/output/` and also display them.

### Batch Processing

```python
import os
from pathlib import Path

def process_svg_directory(input_dir, output_dir, transformation):
    """Apply transformation to all SVG files in a directory."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    for svg_file in input_path.glob('*.svg'):
        svg = SVG.from_file(str(svg_file))
        transformed_svg = svg.transform(transformation)
        
        output_file = output_path / f'transformed_{svg_file.name}'
        transformed_svg.to_file(str(output_file))
        print(f'Processed: {svg_file.name}')

# Usage
process_svg_directory('input/', 'output/', lambda p: (p[0] * 1.5, p[1] * 1.5))
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/josef-ondrej/svgecko.git
cd svgecko
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black svgecko tests

# Sort imports
isort svgecko tests

# Type checking
mypy svgecko

# Linting
flake8 svgecko tests
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 Changelog

### v0.3.4
- ✅ Added support for relative path commands
- ✅ Added support for arc path commands (approximated as line segments)
- ✅ Added support for CSS translate() functions in style attributes
- ✅ Improved type annotations throughout the codebase
- ✅ Added comprehensive Google-style documentation
- ✅ Enhanced test coverage
- ✅ Modernized project structure with pyproject.toml
