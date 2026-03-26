"""Utility functions and resources for SVGecko."""

from pathlib import Path
from typing import Final

from svgecko.svg import SVG

PYTHON_LOGO_PATH: Final[Path] = Path(__file__).parent / 'resources' / 'python-logo.svg'
CROSS_PATH: Final[Path] = Path(__file__).parent / 'resources' / 'cross.svg'


def load_python_logo() -> SVG:
    """Load the Python logo SVG from the resources directory.
    
    Returns:
        An SVG object containing the Python logo.
        
    Raises:
        FileNotFoundError: If the Python logo SVG file is not found.
        etree.XMLSyntaxError: If the SVG file contains invalid XML.
    """
    with open(PYTHON_LOGO_PATH, 'r', encoding='utf-8') as f:
        python_logo_string = f.read()
    return SVG.from_string(python_logo_string)
