"""Tests for the SVG module."""

import os
import re

import numpy as np
import pytest

from svgecko.svg import SVG
from svgecko.utils import load_python_logo, CROSS_PATH


def _replace_whitespaces_with_space(string: str) -> str:
    return re.sub(r'\s+', ' ', string)


def _require_cairosvg() -> None:
    try:
        import cairosvg  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("cairosvg is required for rasterization tests")


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
    _require_cairosvg()
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
    _require_cairosvg()
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


def test_shape_from_viewbox():
    svg_string = """
    <svg viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg"></svg>
    """
    svg = SVG.from_string(svg_string)
    width, height = svg.shape
    assert width == 120.0
    assert height == 80.0


def test_shape_from_viewbox_when_percent():
    svg_string = """
    <svg width="100%" height="100%" viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg"></svg>
    """
    svg = SVG.from_string(svg_string)
    width, height = svg.shape
    assert width == 200.0
    assert height == 100.0


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


def test_relative_commands():
    """Test transformation of relative path commands."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 5 l2 0 l0 2 l-2 0 l0 -2 z" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    
    # Apply transformation
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)
    
    # Check that the path was transformed
    path_elements = transformed_svg.xml.xpath('//*[@d]')
    assert len(path_elements) > 0, "No path elements found"
    path_element = path_elements[0]
    path_d = path_element.attrib['d']
    
    # Should contain absolute coordinates after transformation
    assert 'L' in path_d  # Relative 'l' should become absolute 'L'


def test_arc_commands():
    """Test transformation of arc path commands."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 5 A2 2 0 0 1 7 5" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    
    # Apply transformation
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)
    
    # Check that the arc was converted to line segment
    path_elements = transformed_svg.xml.xpath('//*[@d]')
    assert len(path_elements) > 0, "No path elements found"
    path_element = path_elements[0]
    path_d = path_element.attrib['d']
    
    # Should contain 'L' command (arc converted to line)
    assert 'L' in path_d


def test_style_translate():
    """Test transformation of CSS translate functions in style attributes."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="2" height="2" style="transform: translate(1, 1)" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    
    # Apply transformation
    transformation = lambda point: (point[0] + 2, point[1] + 2)
    transformed_svg = svg.transform(transformation)
    
    # Check that translate was transformed
    rect_elements = transformed_svg.xml.xpath('//*[@style]')
    assert len(rect_elements) > 0, "No rect elements found"
    rect_element = rect_elements[0]
    style_attr = rect_element.attrib.get('style', '')
    
    # Should contain transformed translate values
    assert 'translate(3.0, 3.0)' in style_attr


def test_style_translate_single_value():
    """Test transformation of CSS translate with single value."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="2" height="2" style="transform: translate(5)" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    
    # Apply transformation
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)
    
    # Check that translate was transformed
    rect_elements = transformed_svg.xml.xpath('//*[@style]')
    assert len(rect_elements) > 0, "No rect elements found"
    rect_element = rect_elements[0]
    style_attr = rect_element.attrib.get('style', '')
    
    # Should contain transformed translate values
    assert 'translate(6.0, 1.0)' in style_attr


def test_style_translate_space_separated_and_units():
    """Test translate() parsing with spaces and units."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="2" height="2" style="transform: translate(5px 10px)" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    transformation = lambda point: (point[0] + 1, point[1] + 2)
    transformed_svg = svg.transform(transformation)

    rect_element = transformed_svg.xml.xpath('//*[@style]')[0]
    style_attr = rect_element.attrib.get('style', '')
    assert 'translate(6.0, 12.0)' in style_attr


def test_style_translate_axis_functions():
    """Test translateX/translateY parsing."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="2" height="2" style="transform: translateX(5) translateY(2)" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)

    rect_element = transformed_svg.xml.xpath('//*[@style]')[0]
    style_attr = rect_element.attrib.get('style', '')
    assert 'translate(6.0, 1.0)' in style_attr
    assert 'translate(1.0, 3.0)' in style_attr


def test_translate_transform_attribute():
    """Test translate() in transform attributes."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
    <g transform="translate(1 2) rotate(15)">
        <rect x="0" y="0" width="2" height="2" />
    </g>
    </svg>
    """
    svg = SVG.from_string(svg_string)
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)

    group = transformed_svg.xml.xpath('//*[@transform]')[0]
    assert 'translate(2.0, 3.0)' in group.attrib.get('transform', '')


def test_points_attribute_transformation():
    """Test transformation of polygon/polyline points."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
        <polygon points="0,0 2,0 2,2" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)

    polygon = transformed_svg.xml.xpath('//*[@points]')[0]
    assert polygon.attrib['points'] == '1.0,1.0 3.0,1.0 3.0,3.0'


def test_cx_cy_attributes_transformation():
    """Test transformation of cx/cy attributes."""
    svg_string = """
    <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">
        <circle cx="2" cy="3" r="1" />
    </svg>
    """
    svg = SVG.from_string(svg_string)
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation)

    circle = transformed_svg.xml.xpath('//*[@cx and @cy]')[0]
    assert circle.attrib['cx'] == '3.0'
    assert circle.attrib['cy'] == '4.0'


def test_copy_and_deepcopy():
    """Test copy and deepcopy functionality."""
    svg = SVG.from_file(CROSS_PATH)
    
    # Test shallow copy
    svg_copy = svg.__copy__()
    assert svg_copy is not svg
    assert svg_copy.to_string() == svg.to_string()
    
    # Test deep copy
    svg_deepcopy = svg.__deepcopy__()
    assert svg_deepcopy is not svg
    assert svg_deepcopy.to_string() == svg.to_string()


def test_pickle_support():
    """Test pickle support."""
    import pickle
    
    svg = SVG.from_file(CROSS_PATH)
    
    # Pickle and unpickle
    pickled = pickle.dumps(svg)
    unpickled_svg = pickle.loads(pickled)
    
    assert unpickled_svg.to_string() == svg.to_string()


def test_add_method():
    """Test adding elements from another SVG."""
    svg1_string = """
    <svg viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg">
    <rect x="0" y="0" width="2" height="2" />
    </svg>
    """
    svg2_string = """
    <svg viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg">
    <circle cx="3" cy="3" r="1" />
    </svg>
    """
    
    svg1 = SVG.from_string(svg1_string)
    svg2 = SVG.from_string(svg2_string)
    
    svg1.add(svg2)
    
    # Check that both elements are present
    svg_string = svg1.to_string()
    assert 'rect' in svg_string
    assert 'circle' in svg_string


def test_inplace_transform():
    """Test inplace transformation."""
    svg = SVG.from_file(CROSS_PATH)
    original_id = id(svg)
    
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation, inplace=True)
    
    # Should be the same object
    assert id(transformed_svg) == original_id
    assert transformed_svg is svg


def test_non_inplace_transform():
    """Test non-inplace transformation."""
    svg = SVG.from_file(CROSS_PATH)
    
    transformation = lambda point: (point[0] + 1, point[1] + 1)
    transformed_svg = svg.transform(transformation, inplace=False)
    
    # Should be different objects
    assert id(transformed_svg) != id(svg)
    assert transformed_svg is not svg
