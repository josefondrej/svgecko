import numpy as np
import pytest

from svgtransform.svg import SVG
from svgtransform.utils import load_python_logo


@pytest.fixture
def python_logo() -> SVG:
    return load_python_logo()


@pytest.fixture
def cross() -> SVG:
    """
    SVG with a cross in the middle
    """
    svg_string = """
    <svg class="icon  icon--plus" viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 1 h1 v1 h1 v1 h-1 v1 h-1 v-1 h-1 v-1 h1 z" />
    </svg>
    """
    return SVG.from_string(svg_string)


@pytest.fixture
def cross_abs() -> SVG:
    """
    SVG with a cross in the middle, absolute coordinates
    """
    svg_string = """
    <svg class="icon  icon--plus" viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 1 H3 V2 H4 V3 H3 V4 H2 V3 H1 V2 H2 Z" />
    </svg>
    """
    return SVG.from_string(svg_string)


def test_empty_transform(cross_abs: SVG):
    no_transform = lambda x: (x[0], x[1])
    cross_abs.transform(
        transformation=no_transform,
        inplace=True
    )
    transformed_array = np.array(cross_abs.to_pil_image(scale=1)).T[-1].tolist()
    expected_transformed_array = [
        [0, 0, 0, 0, 0],
        [0, 0, 255, 0, 0],
        [0, 255, 255, 255, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    assert transformed_array == expected_transformed_array


def test_shift_right_down(cross_abs: SVG):
    shift_right_down = lambda x: (
        x[0] + 1,
        x[1] + 1
    )
    cross_abs.transform(
        transformation=shift_right_down,
        inplace=True
    )
    transformed_array = np.array(cross_abs.to_pil_image(scale=1)).T[-1].tolist()
    expected_transformed_array = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 255, 0],
        [0, 0, 255, 255, 255],
        [0, 0, 0, 255, 0]
    ]

    assert transformed_array == expected_transformed_array


def test_shape(python_logo: SVG):
    width, height = python_logo.shape
    assert abs(width - 92.070236) < 1e-6
    assert abs(height - 101.00108) < 1e-6
