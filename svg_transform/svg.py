from __future__ import annotations

from io import BytesIO
from typing import Callable, Tuple

from PIL import Image
from cairosvg import svg2png
from lxml import etree
from lxml.etree import ElementBase

from svg_transform.svg_path import transform_path_command_string


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

    def to_string(self, encoding: str = 'utf-8') -> str:
        """
        Returns the SVG object as a string in XML format.
        :param encoding: encoding of the SVG string
        :return: SVG string in XML format
        """
        return etree.tostring(self._xml, encoding=encoding).decode(encoding=encoding)

    def copy(self) -> SVG:
        """
        Returns a copy of the SVG object.
        :return: copy of the SVG object
        """
        return SVG(self._xml.copy())

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
            svg = self.copy()

        elements_with_attribute_d_selector = '//*[@d]'
        paths = svg.xml.xpath(elements_with_attribute_d_selector)
        for path in paths:
            path_command_string = path.attrib['d']
            transformed_path_command_string = transform_path_command_string(
                path_command_string=path_command_string,
                transformation=transformation
            )
            path.attrib['d'] = transformed_path_command_string

        return svg

    def to_pil_image(self, **kwargs) -> Image:
        buffer = BytesIO()
        svg2png(bytestring=bytes(self.to_string(encoding='utf-8'), encoding='utf-8'), write_to=buffer, **kwargs)
        buffer.seek(0)
        image = Image.open(buffer)
        return image
