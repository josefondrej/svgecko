import os
import re

import numpy as np
import pytest

from svgecko.svg import SVG
from svgecko.utils import load_python_logo, CROSS_PATH


def _replace_whitespaces_with_space(string: str) -> str:
    return re.sub(r'\s+', ' ', string)


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


def test_from_file():
    svg = SVG.from_file(CROSS_PATH)
    svg_string = svg.to_string()
    expected_svg_string = """<svg xmlns="http://www.w3.org/2000/svg" class="icon  icon--plus" width="5" height="5" viewBox="0 0 5 5"> <path d="M2 1 H3 V2 H4 V3 H3 V4 H2 V3 H1 V2 H2 Z"/> </svg>"""
    assert _replace_whitespaces_with_space(svg_string) == _replace_whitespaces_with_space(expected_svg_string)


@pytest.fixture
def temp_svg_file_path() -> str:
    yield 'temp.svg'
    os.remove('temp.svg')


def test_to_file(temp_svg_file_path):
    svg = SVG.from_file(CROSS_PATH)
    svg.to_file(temp_svg_file_path)
    svg_retrieved = SVG.from_file(temp_svg_file_path)
    assert svg_retrieved.to_string() == svg.to_string()
