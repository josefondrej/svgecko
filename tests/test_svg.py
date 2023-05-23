import numpy as np
import pytest

from svg_transform.svg import SVG


@pytest.fixture
def cross():
    """
    SVG with a cross in the middle
    """
    svg_string = """
    <svg class="icon  icon--plus" viewBox="0 0 5 5" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 1 h1 v1 h1 v1 h-1 v1 h-1 v-1 h-1 v-1 h1 z" />
    </svg>
    """
    return SVG.from_string(svg_string)


def test_transform(cross: SVG):
    no_transform = lambda x: x
    cross.transform(
        transformation=no_transform,
        inplace=True
    )
    transformed_array = np.array(cross.to_pil_image(scale=1))
    expected_transformed_array = [
        [0, 0, 0, 0, 0],
        [0, 0, 255, 0, 0],
        [0, 255, 255, 255, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    transformed_array.T[-1].tolist() == expected_transformed_array
