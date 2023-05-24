from __future__ import annotations

from copy import deepcopy
from io import BytesIO
from typing import Callable, Tuple

from PIL import Image
from cairosvg import svg2png
from lxml import etree
from lxml.etree import ElementBase

from svgecko.svg_path import transform_path_command_string


class SVG:
    """
    Representation of an SVG file.
    """

    def __init__(self, xml: ElementBase):
        self._xml = xml

    @property
    def xml(self) -> ElementBase:
        return self._xml

    @classmethod
    def from_string(cls, svg_string: str, encoding: str = 'utf-8') -> SVG:
        """
        Parses an SVG string in XML format and returns an SVG object.
        :param svg_string: SVG string in XML format
        :param encoding: encoding of the SVG string
        :return: SVG object
        """
        svg_tree = etree.fromstring(bytes(svg_string, encoding=encoding))
        return SVG(svg_tree)

    @classmethod
    def from_file(cls, file_path: str, encoding: str = 'utf-8') -> SVG:
        """
        Parses an SVG file and returns an SVG object.
        :param file_path: path to SVG file
        :return: SVG object
        """
        with open(file_path, 'r', encoding=encoding) as file:
            svg_string = file.read()
        return SVG.from_string(svg_string, encoding=encoding)

    def to_string(self, encoding: str = 'utf-8') -> str:
        """
        Returns the SVG object as a string in XML format.
        :param encoding: encoding of the SVG string
        :return: SVG string in XML format
        """
        return etree.tostring(self._xml, encoding=encoding).decode(encoding=encoding)

    def to_file(self, file_path: str, encoding: str = 'utf-8') -> None:
        """
        Writes the SVG object to a file.
        :param file_path: path to SVG file
        :param encoding: encoding of the SVG string
        """
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(self.to_string(encoding=encoding))

    def __copy__(self):
        return SVG(self._xml)

    def __deepcopy__(self, memodict={}):
        return SVG(deepcopy(self._xml))

    @property
    def shape(self):
        raw_width, raw_height = self.xml.attrib['width'], self.xml.attrib['height']
        width = float(''.join([c for c in raw_width if c.isdigit() or c == '.']))
        height = float(''.join([c for c in raw_height if c.isdigit() or c == '.']))
        return width, height

    def transform(self, transformation: Callable[[Tuple[float, float]], Tuple[float, float]],
                  inplace: bool = False) -> SVG:
        """
        Applies a transformation from R2 -> R2 to every point in the SVG object.
        Keeps everything else the same.
        :param transformation: function representing transformation from R2 -> R2
        :return: transformed SVG object
        """
        if inplace:
            svg = self
        else:
            svg = deepcopy(self)

        self._transform_paths(svg, transformation)
        self._transform_xy_attributes(svg, transformation)

        return svg

    @staticmethod
    def _transform_xy_attributes(svg: SVG, transformation: Callable[[Tuple[float, float]], Tuple[float, float]]):
        for attribute_pairs in [('x', 'y'), ('x1', 'y1'), ('x2', 'y2')]:
            elements_with_both_attributes_selector = f'//*[@{attribute_pairs[0]} and @{attribute_pairs[1]}]'
            elements_with_both_attributes = svg.xml.xpath(elements_with_both_attributes_selector)
            for element in elements_with_both_attributes:
                x_name, y_name = attribute_pairs
                x, y = float(element.attrib[x_name]), float(element.attrib[y_name])
                transformed_x, transformed_y = transformation((x, y))
                element.attrib[x_name], element.attrib[y_name] = str(transformed_x), str(transformed_y)

    @staticmethod
    def _transform_paths(svg: SVG, transformation: Callable[[Tuple[float, float]], Tuple[float, float]]):
        elements_with_attribute_d_selector = '//*[@d]'
        paths = svg.xml.xpath(elements_with_attribute_d_selector)
        for path in paths:
            path_command_string = path.attrib['d']
            transformed_path_command_string = transform_path_command_string(
                path_command_string=path_command_string,
                transformation=transformation
            )
            path.attrib['d'] = transformed_path_command_string

    def to_pil_image(self, **kwargs) -> Image:
        buffer = BytesIO()
        svg2png(bytestring=bytes(self.to_string(encoding='utf-8'), encoding='utf-8'), write_to=buffer, **kwargs)
        buffer.seek(0)
        image = Image.open(buffer)
        return image

    def add(self, other: SVG):
        for child in other._xml:
            self._xml.append(child)
