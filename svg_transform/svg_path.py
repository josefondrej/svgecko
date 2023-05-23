from typing import Callable, Tuple, List, Optional

COMMAND_TYPES = 'MmLlCcSsQqTtAaZzHhVv'


class PathCommand:
    def __init__(self, command_type: str, coordinates: Optional[List[float]] = None):
        if command_type not in COMMAND_TYPES and len(command_type) != 1:
            raise ValueError(f'Invalid command type: {command_type}')

        self._command_type = command_type
        self._coordinates = coordinates if coordinates is not None else list()

    def transform(self, transformation: Callable[[Tuple[int, int]], Tuple[int, int]]):
        if self._command_type in ['M', 'L', 'C', 'S', 'Q', 'T']:
            transformed_coordinates = [
                transformation((self._coordinates[i], self._coordinates[i + 1])) for i in
                range(0, len(self._coordinates), 2)]
            self._coordinates = [coordinate for point in transformed_coordinates for coordinate in point]
        elif self._command_type in ['H']:
            self._coordinates = [
                transformation((self._coordinates[i], 0)
                               )[0] for i in range(len(self._coordinates))]
        elif self._command_type in ['V']:
            self._coordinates = [
                transformation((0, self._coordinates[i]))[1] for i in range(len(self._coordinates))]
        elif self._command_type in ['A', 'a']:
            raise NotImplementedError('Arcs are not implemented yet')
        elif self._command_type in ['m', 'l', 'c', 's', 'q', 't', 'h', 'v']:
            raise NotImplementedError('Relative commands are not implemented yet')
        elif self._command_type in ['Z', 'z']:
            pass

    def __str__(self):
        return self._command_type + ' '.join([str(coordinate) for coordinate in self._coordinates])

    def __repr__(self):
        return f'PathCommand({self._command_type}, {self._coordinates})'


def parse_coordinates(coordinates: str) -> List[float]:
    """
    Parses a string of coordinates into a list of floats.
    :param coordinates: String of coordinates
    :return: List of floats
    """
    if coordinates.strip() == '':
        return list()
    return [float(coordinate.strip()) for coordinate in coordinates.strip().split(' ')]


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
    commands = parse_commands(path_command_string)
    for command in commands:
        command.transform(transformation)
    return ''.join([str(command) for command in commands])
