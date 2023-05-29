from __future__ import annotations

import re
from typing import Callable, Tuple, List, Optional, Any

COMMAND_TYPES = 'MmLlCcSsQqTtAaZzHhVv'


class Path:
    def __init__(self, commands: List[PathCommand]):
        self._commands = commands

    @classmethod
    def from_command_string(cls, command_string: str) -> Path:
        commands = parse_commands(command_string)
        return Path(commands=commands)

    @property
    def command_string(self):
        return ''.join([str(command) for command in self._commands])

    def transform(self, transformation: Callable[[Tuple[float, float]], Tuple[float, float]]) -> Path:
        path_start_coordinates = None  # Coordinates of the start of the path in the untransformed coordinate system
        current_coordinates = (0, 0)  # Current coordinates in the untransformed coordinate system
        transformed_commands = list()

        for command in self._commands:
            if command.type in ['M', 'L', 'C', 'S', 'Q', 'T']:
                transformed_coordinates = flatten([
                    transformation((command.coordinates[i], command.coordinates[i + 1])) for i in
                    range(0, len(command.coordinates), 2)])
                transformed_command = PathCommand(command.type, transformed_coordinates)
                current_coordinates = tuple(command.coordinates[-2:])
            elif command.type in ['H']:
                transformed_coordinates = flatten(
                    [transformation((x, current_coordinates[1])) for x in command.coordinates])
                transformed_command = PathCommand('L', transformed_coordinates)
                current_coordinates = (command.coordinates[-1], current_coordinates[1])
            elif command.type in ['V']:
                transformed_coordinates = flatten(
                    [transformation((current_coordinates[0], y)) for y in command.coordinates])
                transformed_command = PathCommand('L', transformed_coordinates)
                current_coordinates = (current_coordinates[0], command.coordinates[-1])
            elif command.type in ['A', 'a']:
                raise NotImplementedError('Arcs are not implemented yet')
            elif command.type in ['m', 'l', 'c', 's', 'q', 't']:
                raise NotImplementedError('Relative commands are not implemented yet')
            elif command.type in ['Z', 'z']:
                transformed_command = PathCommand('Z')
                current_coordinates = path_start_coordinates
                path_start_coordinates = None

            if path_start_coordinates is None:
                path_start_coordinates = current_coordinates

            transformed_commands.append(transformed_command)

        return Path(transformed_commands)


class PathCommand:
    def __init__(self, command_type: str, coordinates: Optional[List[float]] = None):
        if command_type not in COMMAND_TYPES and len(command_type) != 1:
            raise ValueError(f'Invalid command type: {command_type}')

        self._command_type = command_type
        self._coordinates = coordinates if coordinates is not None else list()

    @property
    def type(self) -> str:
        return self._command_type

    @property
    def coordinates(self) -> Tuple[float, float]:
        return self._coordinates

    def __str__(self):
        return self._command_type + ' '.join([str(coordinate) for coordinate in self._coordinates])

    def __repr__(self):
        return f'PathCommand({self._command_type}, {self._coordinates})'


def flatten(nested_list: List[Tuple[Any]]) -> List[Any]:
    """
    Flattens a nested list of tuples into a list of elements.
    :param nested_list: Nested list of tuples
    :return: List of elements
    """
    return [element for nested_tuple in nested_list for element in nested_tuple]


def parse_coordinates(coordinates: str) -> List[float]:
    """
    Parses a string of coordinates into a list of floats.
    :param coordinates: String of coordinates
    :return: List of floats
    """
    if coordinates.strip() == '':
        return list()

    return [float(coordinate.strip()) for coordinate in re.split(r'[, ]+', coordinates.strip())]


def parse_commands(path_command_string: str) -> List[PathCommand]:
    """
    Parses a path command string into a list of PathCommands.
    :param path_command_string: Raw SVG path command string
    :return: List of PathCommands
    """
    commands = list()
    current_command = ''
    current_coordinates = ''
    for char in path_command_string:
        if char in COMMAND_TYPES:
            if current_command:
                command = PathCommand(current_command, parse_coordinates(current_coordinates))
                commands.append(command)
            current_command = char
            current_coordinates = ''
        else:
            current_coordinates += char
    command = PathCommand(current_command, parse_coordinates(current_coordinates))
    commands.append(command)
    return commands


def transform_path_command_string(path_command_string: str,
                                  transformation: Callable[[Tuple[float, float]], Tuple[float, float]]) -> str:
    """
    Transforms a path command string by applying a transformation to every point.
    :param path_command_string: SVG path command string
    :param transformation: Transformation that maps points from R2 to R2
    :return: Transformed path command string
    """
    path = Path.from_command_string(path_command_string)
    transformed_path = path.transform(transformation)
    return transformed_path.command_string
