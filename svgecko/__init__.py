"""SVGecko: Lightweight library for arbitrary geometric SVG transformations.

This library provides tools for applying arbitrary geometric transformations to SVG files,
supporting both path commands and coordinate attributes.
"""

from svgecko.svg import SVG
from svgecko.svg_path import Path, PathCommand
from svgecko.utils import load_python_logo

__version__ = "0.4.0"
__author__ = "Josef Ondrej"
__email__ = "josef.ondrej@outlook.com"

__all__ = [
    "SVG",
    "Path", 
    "PathCommand",
    "load_python_logo",
]