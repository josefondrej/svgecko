from pathlib import Path

from svgecko.svg import SVG

PYTHON_LOGO_PATH = Path(__file__).parent / 'resources' / 'python-logo.svg'
CROSS_PATH = Path(__file__).parent / 'resources' / 'cross.svg'


def load_python_logo() -> SVG:
    python_logo_path = PYTHON_LOGO_PATH
    with open(python_logo_path, 'r') as f:
        python_logo_string = f.read()
    return SVG.from_string(python_logo_string)
