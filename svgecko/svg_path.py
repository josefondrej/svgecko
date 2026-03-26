"""SVG path parsing and transformation module."""

from __future__ import annotations

import math
import re
from typing import Any, Callable, List, Optional, Tuple

COMMAND_TYPES: str = 'MmLlCcSsQqTtAaZzHhVv'

_NUMBER_RE = re.compile(r'[+-]?(?:\d*\.\d+|\d+\.?)(?:[eE][+-]?\d+)?')
_TOKEN_RE = re.compile(r'[MmLlCcSsQqTtAaZzHhVv]|[+-]?(?:\d*\.\d+|\d+\.?)(?:[eE][+-]?\d+)?')
_PARAMS_PER_COMMAND = {
    'M': 2,
    'L': 2,
    'C': 6,
    'S': 4,
    'Q': 4,
    'T': 2,
    'A': 7,
    'H': 1,
    'V': 1,
    'Z': 0,
}

# Type alias for transformation functions
TransformationFunction = Callable[[Tuple[float, float]], Tuple[float, float]]


class Path:
    """Represents an SVG path as a collection of path commands.
    
    This class provides methods to parse SVG path strings and apply
    transformations to the path commands.
    
    Attributes:
        _commands: List of PathCommand objects representing the path.
    """
    
    def __init__(self, commands: List[PathCommand]) -> None:
        """Initialize a Path with a list of commands.
        
        Args:
            commands: List of PathCommand objects.
        """
        self._commands = commands

    @classmethod
    def from_command_string(cls, command_string: str) -> Path:
        """Create a Path from an SVG path command string.
        
        Args:
            command_string: SVG path command string (e.g., "M10 10 L20 20").
            
        Returns:
            A Path object representing the parsed commands.
            
        Raises:
            ValueError: If the command string contains invalid commands.
        """
        commands = parse_commands(command_string)
        return Path(commands=commands)

    @property
    def command_string(self) -> str:
        """Get the SVG path command string representation.
        
        Returns:
            The SVG path command string.
        """
        return ' '.join([str(command) for command in self._commands])

    def transform(self, transformation: TransformationFunction) -> Path:
        """Apply a transformation to all coordinates in the path.
        
        Args:
            transformation: Function that transforms (x, y) coordinates.
            
        Returns:
            A new Path object with transformed coordinates.
        """
        current: Tuple[float, float] = (0.0, 0.0)
        subpath_start: Optional[Tuple[float, float]] = None
        transformed_commands: List[PathCommand] = []

        for command in self._commands:
            command_type = command.type
            coords = command.coordinates

            if command_type in ['M', 'm']:
                if command_type == 'm':
                    current = (current[0] + coords[0], current[1] + coords[1])
                else:
                    current = (coords[0], coords[1])
                subpath_start = current
                transformed = transformation(current)
                transformed_commands.append(PathCommand('M', [transformed[0], transformed[1]]))
                continue

            if command_type in ['L', 'l']:
                if command_type == 'l':
                    current = (current[0] + coords[0], current[1] + coords[1])
                else:
                    current = (coords[0], coords[1])
                transformed = transformation(current)
                transformed_commands.append(PathCommand('L', [transformed[0], transformed[1]]))
                continue

            if command_type in ['H', 'h']:
                x_value = coords[0] + current[0] if command_type == 'h' else coords[0]
                current = (x_value, current[1])
                transformed = transformation(current)
                transformed_commands.append(PathCommand('L', [transformed[0], transformed[1]]))
                continue

            if command_type in ['V', 'v']:
                y_value = coords[0] + current[1] if command_type == 'v' else coords[0]
                current = (current[0], y_value)
                transformed = transformation(current)
                transformed_commands.append(PathCommand('L', [transformed[0], transformed[1]]))
                continue

            if command_type in ['C', 'c', 'S', 's', 'Q', 'q', 'T', 't']:
                absolute_coords: List[float] = []
                if command_type.islower():
                    for i in range(0, len(coords), 2):
                        absolute_coords.extend([current[0] + coords[i], current[1] + coords[i + 1]])
                    current = (current[0] + coords[-2], current[1] + coords[-1])
                else:
                    absolute_coords = coords
                    current = (coords[-2], coords[-1])

                transformed_coords = flatten([
                    transformation((absolute_coords[i], absolute_coords[i + 1]))
                    for i in range(0, len(absolute_coords), 2)
                ])
                transformed_commands.append(PathCommand(command_type.upper(), transformed_coords))
                continue

            if command_type in ['A', 'a']:
                if len(coords) != 7:
                    raise ValueError(f'Invalid arc command length: {coords}')
                rx, ry, rotation, large_arc_flag, sweep_flag, end_x, end_y = coords
                if command_type == 'a':
                    end = (current[0] + end_x, current[1] + end_y)
                else:
                    end = (end_x, end_y)

                arc_points = self._arc_to_points(
                    start=current,
                    end=end,
                    rx=rx,
                    ry=ry,
                    rotation=rotation,
                    large_arc=bool(int(large_arc_flag)),
                    sweep=bool(int(sweep_flag)),
                )
                if not arc_points:
                    arc_points = [end]

                for point in arc_points:
                    transformed = transformation(point)
                    transformed_commands.append(PathCommand('L', [transformed[0], transformed[1]]))

                current = end
                continue

            if command_type in ['Z', 'z']:
                transformed_commands.append(PathCommand('Z'))
                if subpath_start is not None:
                    current = subpath_start
                subpath_start = None
                continue

            raise ValueError(f'Unsupported command type: {command_type}')

        return Path(transformed_commands)

    @staticmethod
    def _arc_to_points(
        start: Tuple[float, float],
        end: Tuple[float, float],
        rx: float,
        ry: float,
        rotation: float,
        large_arc: bool,
        sweep: bool,
    ) -> List[Tuple[float, float]]:
        """Approximate an SVG arc with line segment points."""
        if rx == 0 or ry == 0 or start == end:
            return [end]

        rx = abs(rx)
        ry = abs(ry)

        phi = math.radians(rotation % 360.0)
        cos_phi = math.cos(phi)
        sin_phi = math.sin(phi)

        dx = (start[0] - end[0]) / 2.0
        dy = (start[1] - end[1]) / 2.0
        x1p = cos_phi * dx + sin_phi * dy
        y1p = -sin_phi * dx + cos_phi * dy

        rx2 = rx * rx
        ry2 = ry * ry
        x1p2 = x1p * x1p
        y1p2 = y1p * y1p

        radius_check = x1p2 / rx2 + y1p2 / ry2
        if radius_check > 1:
            scale = math.sqrt(radius_check)
            rx *= scale
            ry *= scale
            rx2 = rx * rx
            ry2 = ry * ry

        numerator = rx2 * ry2 - rx2 * y1p2 - ry2 * x1p2
        denominator = rx2 * y1p2 + ry2 * x1p2
        if denominator == 0:
            return [end]

        factor = math.sqrt(max(0.0, numerator / denominator))
        if large_arc == sweep:
            factor = -factor

        cxp = factor * (rx * y1p) / ry
        cyp = factor * (-ry * x1p) / rx

        cx = cos_phi * cxp - sin_phi * cyp + (start[0] + end[0]) / 2.0
        cy = sin_phi * cxp + cos_phi * cyp + (start[1] + end[1]) / 2.0

        def _angle(u: Tuple[float, float], v: Tuple[float, float]) -> float:
            dot = u[0] * v[0] + u[1] * v[1]
            det = u[0] * v[1] - u[1] * v[0]
            return math.atan2(det, dot)

        v1 = ((x1p - cxp) / rx, (y1p - cyp) / ry)
        v2 = ((-x1p - cxp) / rx, (-y1p - cyp) / ry)
        theta1 = _angle((1.0, 0.0), v1)
        delta = _angle(v1, v2)

        if not sweep and delta > 0:
            delta -= 2.0 * math.pi
        elif sweep and delta < 0:
            delta += 2.0 * math.pi

        segments = max(1, int(math.ceil(abs(delta) / (math.pi / 8.0))))
        points: List[Tuple[float, float]] = []
        for i in range(1, segments + 1):
            angle = theta1 + delta * (i / segments)
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            x = cx + rx * cos_phi * cos_angle - ry * sin_phi * sin_angle
            y = cy + rx * sin_phi * cos_angle + ry * cos_phi * sin_angle
            points.append((x, y))

        return points


class PathCommand:
    """Represents a single SVG path command.
    
    This class represents commands like 'M', 'L', 'C', etc. along with
    their associated coordinates.
    
    Attributes:
        _command_type: The command type (e.g., 'M', 'L', 'C').
        _coordinates: List of coordinate values for the command.
    """
    
    def __init__(self, command_type: str, coordinates: Optional[List[float]] = None) -> None:
        """Initialize a PathCommand.
        
        Args:
            command_type: The command type (e.g., 'M', 'L', 'C').
            coordinates: List of coordinate values. Defaults to empty list.
            
        Raises:
            ValueError: If command_type is not a valid SVG command.
        """
        if command_type not in COMMAND_TYPES:
            raise ValueError(f'Invalid command type: {command_type}')

        self._command_type = command_type
        self._coordinates = coordinates if coordinates is not None else []

    @property
    def type(self) -> str:
        """Get the command type.
        
        Returns:
            The command type string.
        """
        return self._command_type

    @property
    def coordinates(self) -> List[float]:
        """Get the command coordinates.
        
        Returns:
            List of coordinate values.
        """
        return self._coordinates

    def __str__(self) -> str:
        """Get string representation of the command.
        
        Returns:
            SVG path command string (e.g., "M 10 20").
        """
        if not self._coordinates:
            return self._command_type
        return self._command_type + ' ' + ' '.join([str(coordinate) for coordinate in self._coordinates])

    def __repr__(self) -> str:
        """Get detailed string representation of the command.
        
        Returns:
            Detailed string representation.
        """
        return f'PathCommand({self._command_type}, {self._coordinates})'


def flatten(nested_list: List[Tuple[Any, ...]]) -> List[Any]:
    """Flatten a nested list of tuples into a list of elements.
    
    Args:
        nested_list: List of tuples to flatten.
        
    Returns:
        Flattened list of elements.
    """
    return [element for nested_tuple in nested_list for element in nested_tuple]


def parse_numbers(value: str) -> List[float]:
    """Parse all numbers from a string into a list of floats."""
    if not value:
        return []
    return [float(token) for token in _NUMBER_RE.findall(value)]


def parse_coordinates(coordinates: str) -> List[float]:
    """Parse a string of coordinates into a list of floats.
    
    Args:
        coordinates: String containing coordinate values separated by
            commas or spaces (e.g., "10,20 30,40" or "10 20 30 40").
            
    Returns:
        List of parsed coordinate values as floats.
        
    Raises:
        ValueError: If coordinates cannot be parsed as floats.
    """
    return parse_numbers(coordinates.strip())


def parse_commands(path_command_string: str) -> List[PathCommand]:
    """Parse an SVG path command string into a list of PathCommand objects.
    
    Args:
        path_command_string: Raw SVG path command string (e.g., "M10 10 L20 20").
        
    Returns:
        List of PathCommand objects representing the parsed commands.
        
    Raises:
        ValueError: If the command string contains invalid commands.
    """
    commands: List[PathCommand] = []
    tokens = _TOKEN_RE.findall(path_command_string)
    if not tokens:
        return commands

    current_command: Optional[str] = None
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in COMMAND_TYPES:
            current_command = token
            index += 1
            if current_command in ['Z', 'z']:
                commands.append(PathCommand(current_command))
                current_command = None
                continue

            numbers: List[float] = []
            while index < len(tokens) and tokens[index] not in COMMAND_TYPES:
                numbers.append(float(tokens[index]))
                index += 1

            if not numbers:
                raise ValueError(f'Path command missing coordinates: {current_command}')

        else:
            if current_command is None:
                raise ValueError('Path data missing command')

            numbers = []
            while index < len(tokens) and tokens[index] not in COMMAND_TYPES:
                numbers.append(float(tokens[index]))
                index += 1

        if current_command in ['M', 'm']:
            if len(numbers) < 2 or len(numbers) % 2 != 0:
                raise ValueError(f'Invalid coordinate count for {current_command}: {numbers}')
            commands.append(PathCommand(current_command, numbers[:2]))
            follow_command = 'L' if current_command == 'M' else 'l'
            for i in range(2, len(numbers), 2):
                commands.append(PathCommand(follow_command, numbers[i:i + 2]))
            continue

        param_count = _PARAMS_PER_COMMAND[current_command.upper()]
        if param_count == 0:
            if numbers:
                raise ValueError(f'Invalid coordinates for {current_command}: {numbers}')
            continue
        if len(numbers) % param_count != 0:
            raise ValueError(f'Invalid coordinate count for {current_command}: {numbers}')

        for i in range(0, len(numbers), param_count):
            commands.append(PathCommand(current_command, numbers[i:i + param_count]))

    return commands


def transform_path_command_string(
    path_command_string: str,
    transformation: TransformationFunction
) -> str:
    """Transform an SVG path command string by applying a transformation to every point.
    
    Args:
        path_command_string: SVG path command string to transform.
        transformation: Function that transforms (x, y) coordinates.
        
    Returns:
        Transformed SVG path command string.
        
    Raises:
        ValueError: If the command string contains invalid commands.
    """
    path = Path.from_command_string(path_command_string)
    transformed_path = path.transform(transformation)
    return transformed_path.command_string
