from pathlib import Path

from svg_transform.svg import SVG


def load_python_logo() -> SVG:
    python_logo_path = Path(__file__).parent / 'resources' / 'python-logo.svg'
    with open(python_logo_path, 'r') as f:
        python_logo_string = f.read()
    return SVG.from_string(python_logo_string)
