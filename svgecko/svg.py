"""SVG module for handling SVG file operations and transformations."""

from __future__ import annotations

from copy import deepcopy
from io import BytesIO
import re
from typing import Callable, Dict, Optional, Tuple

from PIL import Image
from lxml import etree
from lxml.etree import ElementBase

from svgecko.svg_path import parse_numbers, transform_path_command_string


class SVG:
    """Representation of an SVG file with transformation capabilities.
    
    This class provides methods to load, manipulate, and save SVG files.
    It supports arbitrary geometric transformations on SVG path commands,
    coordinate attributes, points attributes, and translate() transforms.
    
    Attributes:
        xml: The underlying XML element tree representation of the SVG.
    
    Example:
        >>> svg = SVG.from_file('example.svg')
        >>> transformation = lambda point: (point[0] + 1, point[1] + 1)
        >>> transformed_svg = svg.transform(transformation)
        >>> transformed_svg.to_file('transformed.svg')
    """

    def __init__(self, xml: ElementBase) -> None:
        """Initialize SVG from XML element.
        
        Args:
            xml: The XML element tree representing the SVG.
        """
        self._xml = xml

    @property
    def xml(self) -> ElementBase:
        """Get the underlying XML element tree.
        
        Returns:
            The XML element tree representation of the SVG.
        """
        return self._xml

    @classmethod
    def from_string(cls, svg_string: str, encoding: str = 'utf-8') -> SVG:
        """Parse an SVG string and return an SVG object.
        
        Args:
            svg_string: SVG string in XML format.
            encoding: Character encoding of the SVG string. Defaults to 'utf-8'.
            
        Returns:
            An SVG object representing the parsed SVG.
            
        Raises:
            etree.XMLSyntaxError: If the SVG string is not valid XML.
        """
        svg_tree = etree.fromstring(bytes(svg_string, encoding=encoding))
        return SVG(svg_tree)

    @classmethod
    def from_file(cls, file_path: str, encoding: str = 'utf-8') -> SVG:
        """Parse an SVG file and return an SVG object.
        
        Args:
            file_path: Path to the SVG file.
            encoding: Character encoding of the file. Defaults to 'utf-8'.
            
        Returns:
            An SVG object representing the parsed SVG file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            etree.XMLSyntaxError: If the file contains invalid XML.
        """
        with open(file_path, 'r', encoding=encoding) as file:
            svg_string = file.read()
        return SVG.from_string(svg_string, encoding=encoding)

    def to_string(self, encoding: str = 'utf-8') -> str:
        """Convert the SVG object to an XML string.
        
        Args:
            encoding: Character encoding for the output string. Defaults to 'utf-8'.
            
        Returns:
            The SVG as an XML string.
        """
        return etree.tostring(self._xml, encoding=encoding).decode(encoding=encoding)

    def to_file(self, file_path: str, encoding: str = 'utf-8') -> None:
        """Write the SVG object to a file.
        
        Args:
            file_path: Path where the SVG file should be written.
            encoding: Character encoding for the file. Defaults to 'utf-8'.
        """
        with open(file_path, 'w', encoding=encoding) as file:
            file.write(self.to_string(encoding=encoding))

    def __copy__(self) -> SVG:
        """Create a shallow copy of the SVG object."""
        return SVG(self._xml)

    def __deepcopy__(self, memodict: Optional[Dict] = None) -> SVG:
        """Create a deep copy of the SVG object."""
        if memodict is None:
            memodict = {}
        return SVG(deepcopy(self._xml, memodict))

    def __getstate__(self) -> Dict[str, str]:
        """Get state for pickling."""
        return {'xml': self.to_string()}

    def __setstate__(self, state: Dict[str, str]) -> None:
        """Set state from unpickling."""
        self._xml = self.from_string(state['xml']).xml

    @property
    def shape(self) -> Tuple[float, float]:
        """Get the width and height of the SVG.
        
        Returns:
            A tuple containing (width, height) as floats.
            
        Raises:
            ValueError: If width/height cannot be resolved from attributes
                or viewBox.
        """
        raw_width = self.xml.attrib.get('width')
        raw_height = self.xml.attrib.get('height')
        width = self._parse_length(raw_width)
        height = self._parse_length(raw_height)

        if width is None or height is None:
            view_box = self.xml.attrib.get('viewBox')
            if view_box:
                values = parse_numbers(view_box)
                if len(values) == 4:
                    width = width if width is not None else values[2]
                    height = height if height is not None else values[3]

        if width is None or height is None:
            raise ValueError('SVG width/height could not be resolved from attributes or viewBox.')

        return width, height

    def transform(
        self, 
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]],
        inplace: bool = False
    ) -> SVG:
        """Apply a geometric transformation to all points in the SVG.
        
        This method applies a transformation function to all coordinate points
        in the SVG, including path commands, coordinate attributes, points
        attributes, and translate() transforms.
        
        Args:
            transformation: A function that takes a (x, y) tuple and returns
                a transformed (x, y) tuple.
            inplace: If True, modify this SVG object. If False, return a new
                transformed copy. Defaults to False.
                
        Returns:
            The transformed SVG object. If inplace=True, returns self.
            Otherwise, returns a new SVG object.
        """
        if inplace:
            svg = self
        else:
            svg = deepcopy(self)

        self._transform_paths(svg, transformation)
        self._transform_xy_attributes(svg, transformation)
        self._transform_points_attributes(svg, transformation)
        self._transform_transform_attributes(svg, transformation)
        self._transform_style_attributes(svg, transformation)

        return svg

    @staticmethod
    def _transform_xy_attributes(
        svg: SVG, 
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> None:
        """Transform coordinate attributes in SVG elements.
        
        Args:
            svg: The SVG object to transform.
            transformation: The transformation function to apply.
        """
        for attribute_pairs in [('x', 'y'), ('x1', 'y1'), ('x2', 'y2'), ('cx', 'cy'), ('fx', 'fy')]:
            elements_with_both_attributes_selector = f'//*[@{attribute_pairs[0]} and @{attribute_pairs[1]}]'
            elements_with_both_attributes = svg.xml.xpath(elements_with_both_attributes_selector)
            for element in elements_with_both_attributes:
                x_name, y_name = attribute_pairs
                x_values = parse_numbers(element.attrib[x_name])
                y_values = parse_numbers(element.attrib[y_name])
                if not x_values or not y_values:
                    continue
                x, y = x_values[0], y_values[0]
                transformed_x, transformed_y = transformation((x, y))
                element.attrib[x_name], element.attrib[y_name] = str(transformed_x), str(transformed_y)

    @staticmethod
    def _transform_paths(
        svg: SVG, 
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> None:
        """Transform path commands in SVG elements.
        
        Args:
            svg: The SVG object to transform.
            transformation: The transformation function to apply.
        """
        elements_with_attribute_d_selector = '//*[@d]'
        paths = svg.xml.xpath(elements_with_attribute_d_selector)
        for path in paths:
            path_command_string = path.attrib['d']
            transformed_path_command_string = transform_path_command_string(
                path_command_string=path_command_string,
                transformation=transformation
            )
            path.attrib['d'] = transformed_path_command_string

    @staticmethod
    def _transform_points_attributes(
        svg: SVG,
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> None:
        """Transform points attributes in polygon/polyline elements."""
        elements_with_points = svg.xml.xpath('//*[@points]')
        for element in elements_with_points:
            points_attr = element.attrib.get('points', '')
            numbers = parse_numbers(points_attr)
            if len(numbers) < 2 or len(numbers) % 2 != 0:
                continue

            transformed_pairs = []
            for i in range(0, len(numbers), 2):
                transformed = transformation((numbers[i], numbers[i + 1]))
                transformed_pairs.append(f'{transformed[0]},{transformed[1]}')

            element.attrib['points'] = ' '.join(transformed_pairs)
    
    @staticmethod
    def _transform_style_attributes(
        svg: SVG, 
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> None:
        """Transform style positioning commands like translate in SVG elements.
        
        Args:
            svg: The SVG object to transform.
            transformation: The transformation function to apply.
        """
        import re
        
        # Find all elements with style attributes
        elements_with_style = svg.xml.xpath('//*[@style]')
        
        for element in elements_with_style:
            style_attr = element.attrib.get('style', '')
            if not style_attr:
                continue
                
            # Transform translate() functions in style
            transformed_style = SVG._transform_translate_functions(style_attr, transformation)
            if transformed_style != style_attr:
                element.attrib['style'] = transformed_style

    @staticmethod
    def _transform_transform_attributes(
        svg: SVG,
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> None:
        """Transform translate() functions in transform attributes."""
        elements_with_transform = svg.xml.xpath('//*[@transform]')
        for element in elements_with_transform:
            transform_attr = element.attrib.get('transform', '')
            if not transform_attr:
                continue

            transformed_transform = SVG._transform_translate_functions(transform_attr, transformation)
            if transformed_transform != transform_attr:
                element.attrib['transform'] = transformed_transform
    
    @staticmethod
    def _transform_translate_functions(
        style_string: str,
        transformation: Callable[[Tuple[float, float]], Tuple[float, float]]
    ) -> str:
        """Transform translate() functions in CSS style strings.
        
        Args:
            style_string: CSS style string that may contain translate() functions.
            transformation: The transformation function to apply.
            
        Returns:
            Transformed style string.
        """
        import re
        
        def transform_translate(match: re.Match[str]) -> str:
            translate_values = match.group('values')
            function_name = match.group('func')
            values = parse_numbers(translate_values)

            if not values:
                return match.group(0)

            if function_name == 'translate':
                x = values[0]
                y = values[1] if len(values) > 1 else 0.0
            elif function_name == 'translateX':
                x = values[0]
                y = 0.0
            else:  # translateY
                x = 0.0
                y = values[0]

            transformed_x, transformed_y = transformation((x, y))
            return f'translate({transformed_x}, {transformed_y})'

        pattern = r'(?P<func>translate|translateX|translateY)\((?P<values>[^)]+)\)'
        return re.sub(pattern, transform_translate, style_string)

    @staticmethod
    def _parse_length(value: Optional[str]) -> Optional[float]:
        """Parse a length attribute, ignoring percent values."""
        if not value:
            return None
        if '%' in value:
            return None
        match = re.search(r'[+-]?(?:\d*\.\d+|\d+\.?)(?:[eE][+-]?\d+)?', value)
        if not match:
            return None
        return float(match.group(0))

    def to_pil_image(self, **kwargs) -> Image.Image:
        """Convert the SVG to a PIL Image.
        
        Args:
            **kwargs: Additional arguments passed to cairosvg.svg2png.
                Common options include:
                - scale: Scale factor for the output image (default: 1.0)
                - width: Output width in pixels
                - height: Output height in pixels
                
        Returns:
            A PIL Image object representing the SVG.
        """
        try:
            from cairosvg import svg2png
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "cairosvg is required for SVG.to_pil_image(). Install it via pip."
            ) from exc
        buffer = BytesIO()
        svg2png(bytestring=bytes(self.to_string(encoding='utf-8'), encoding='utf-8'), write_to=buffer, **kwargs)
        buffer.seek(0)
        image = Image.open(buffer)
        return image

    def add(self, other: SVG) -> None:
        """Add elements from another SVG to this SVG.
        
        Args:
            other: The SVG object whose elements should be added to this SVG.
        """
        for child in other._xml:
            self._xml.append(child)
