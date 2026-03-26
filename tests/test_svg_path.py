"""Tests for the SVG path module."""

import pytest

from svgecko.svg_path import (
    Path,
    PathCommand,
    flatten,
    parse_coordinates,
    parse_commands,
    transform_path_command_string,
)


def test_path_command_creation():
    """Test PathCommand creation and properties."""
    # Test valid command
    cmd = PathCommand('M', [10.0, 20.0])
    assert cmd.type == 'M'
    assert cmd.coordinates == [10.0, 20.0]
    
    # Test command without coordinates
    cmd = PathCommand('Z')
    assert cmd.type == 'Z'
    assert cmd.coordinates == []
    
    # Test invalid command
    with pytest.raises(ValueError):
        PathCommand('X')


def test_path_command_string_representation():
    """Test string representation of PathCommand."""
    cmd = PathCommand('M', [10.0, 20.0])
    assert str(cmd) == 'M 10.0 20.0'
    
    cmd = PathCommand('Z')
    assert str(cmd) == 'Z'


def test_path_command_repr():
    """Test repr representation of PathCommand."""
    cmd = PathCommand('M', [10.0, 20.0])
    assert repr(cmd) == "PathCommand(M, [10.0, 20.0])"


def test_parse_coordinates():
    """Test coordinate parsing."""
    # Test comma-separated coordinates
    coords = parse_coordinates('10,20,30,40')
    assert coords == [10.0, 20.0, 30.0, 40.0]
    
    # Test space-separated coordinates
    coords = parse_coordinates('10 20 30 40')
    assert coords == [10.0, 20.0, 30.0, 40.0]
    
    # Test mixed separators
    coords = parse_coordinates('10, 20 30, 40')
    assert coords == [10.0, 20.0, 30.0, 40.0]
    
    # Test empty string
    coords = parse_coordinates('')
    assert coords == []
    
    # Test single coordinate
    coords = parse_coordinates('10')
    assert coords == [10.0]


def test_parse_coordinates_negative_and_exponent():
    """Test parsing of negative and exponent numbers."""
    coords = parse_coordinates('10-5 2.5e1 -3.5E-1')
    assert coords == [10.0, -5.0, 25.0, -0.35]


def test_parse_commands():
    """Test command parsing."""
    # Test simple path
    commands = parse_commands('M10 20 L30 40 Z')
    assert len(commands) == 3
    assert commands[0].type == 'M'
    assert commands[0].coordinates == [10.0, 20.0]
    assert commands[1].type == 'L'
    assert commands[1].coordinates == [30.0, 40.0]
    assert commands[2].type == 'Z'
    assert commands[2].coordinates == []


def test_parse_commands_implicit_moveto():
    """Test implicit lineto after moveto with multiple pairs."""
    commands = parse_commands('M10 10 20 20 30 30')
    assert [cmd.type for cmd in commands] == ['M', 'L', 'L']
    assert commands[0].coordinates == [10.0, 10.0]
    assert commands[1].coordinates == [20.0, 20.0]
    assert commands[2].coordinates == [30.0, 30.0]


def test_parse_commands_repeated_lineto():
    """Test repeated lineto coordinates without repeating the command."""
    commands = parse_commands('L10 10 20 20')
    assert [cmd.type for cmd in commands] == ['L', 'L']
    assert commands[0].coordinates == [10.0, 10.0]
    assert commands[1].coordinates == [20.0, 20.0]


def test_parse_commands_negative_without_separator():
    """Test parsing numbers without explicit separators."""
    commands = parse_commands('M10-10 L5-5')
    assert commands[0].coordinates == [10.0, -10.0]
    assert commands[1].coordinates == [5.0, -5.0]


def test_parse_commands_invalid_counts():
    """Ensure invalid coordinate counts raise errors."""
    with pytest.raises(ValueError):
        parse_commands('M10')
    with pytest.raises(ValueError):
        parse_commands('L10')


def test_path_from_command_string():
    """Test Path creation from command string."""
    path = Path.from_command_string('M10 20 L30 40 Z')
    assert len(path._commands) == 3
    assert path.command_string == 'M 10.0 20.0 L 30.0 40.0 Z'


def test_path_transform():
    """Test path transformation."""
    path = Path.from_command_string('M10 20 L30 40')
    
    # Test identity transformation
    identity = lambda point: (point[0], point[1])
    transformed = path.transform(identity)
    assert transformed.command_string == 'M 10.0 20.0 L 30.0 40.0'
    
    # Test translation
    translate = lambda point: (point[0] + 5, point[1] + 5)
    transformed = path.transform(translate)
    assert transformed.command_string == 'M 15.0 25.0 L 35.0 45.0'


def test_path_transform_relative_commands():
    """Test transformation of relative commands."""
    path = Path.from_command_string('M10 10 l5 5 l5 -5')
    
    # Transform relative commands
    translate = lambda point: (point[0] + 1, point[1] + 1)
    transformed = path.transform(translate)
    
    # Should convert relative to absolute
    assert 'L' in transformed.command_string  # 'l' becomes 'L'


def test_relative_command_chain_updates_current():
    """Ensure relative commands accumulate correctly."""
    path = Path.from_command_string('M10 10 l5 0 l5 0')
    identity = lambda point: (point[0], point[1])
    transformed = path.transform(identity)
    assert transformed.command_string == 'M 10.0 10.0 L 15.0 10.0 L 20.0 10.0'


def test_relative_moveto_with_implicit_lineto():
    """Relative moveto with multiple pairs should create implicit lineto."""
    path = Path.from_command_string('m5 5 5 0')
    identity = lambda point: (point[0], point[1])
    transformed = path.transform(identity)
    assert transformed.command_string == 'M 5.0 5.0 L 10.0 5.0'


def test_path_transform_arc_commands():
    """Test transformation of arc commands."""
    path = Path.from_command_string('M10 10 A5 5 0 0 1 20 10')
    
    # Transform arc commands
    translate = lambda point: (point[0] + 1, point[1] + 1)
    transformed = path.transform(translate)
    
    # Should convert arc to line
    assert 'L' in transformed.command_string  # 'A' becomes 'L'


def test_path_transform_horizontal_vertical():
    """Test transformation of horizontal and vertical commands."""
    path = Path.from_command_string('M10 10 H20 V30')
    
    # Transform H and V commands
    translate = lambda point: (point[0] + 1, point[1] + 1)
    transformed = path.transform(translate)
    
    # Should convert H and V to L
    assert 'L' in transformed.command_string


def test_path_transform_relative_horizontal_vertical():
    """Test transformation of relative horizontal/vertical commands."""
    path = Path.from_command_string('M10 10 h5 v-5')
    identity = lambda point: (point[0], point[1])
    transformed = path.transform(identity)
    assert transformed.command_string == 'M 10.0 10.0 L 15.0 10.0 L 15.0 5.0'


def test_flatten():
    """Test flatten function."""
    nested = [(1, 2), (3, 4), (5, 6)]
    flattened = flatten(nested)
    assert flattened == [1, 2, 3, 4, 5, 6]


def test_transform_path_command_string():
    """Test transform_path_command_string function."""
    command_string = 'M10 20 L30 40'
    
    # Test identity transformation
    identity = lambda point: (point[0], point[1])
    result = transform_path_command_string(command_string, identity)
    assert result == 'M 10.0 20.0 L 30.0 40.0'
    
    # Test translation
    translate = lambda point: (point[0] + 5, point[1] + 5)
    result = transform_path_command_string(command_string, translate)
    assert result == 'M 15.0 25.0 L 35.0 45.0'


def test_complex_path_transformation():
    """Test transformation of complex path with multiple command types."""
    command_string = 'M10 10 L20 20 H30 V40 C50 50 60 60 70 70 Z'
    path = Path.from_command_string(command_string)
    
    # Apply scaling transformation
    scale = lambda point: (point[0] * 2, point[1] * 2)
    transformed = path.transform(scale)
    
    # Check that all commands were transformed
    assert 'M 20.0 20.0' in transformed.command_string
    assert 'L 40.0 40.0' in transformed.command_string
    assert 'L 60.0 40.0' in transformed.command_string  # H30 -> L
    assert 'L 60.0 80.0' in transformed.command_string  # V40 -> L
    assert 'C 100.0 100.0 120.0 120.0 140.0 140.0' in transformed.command_string
    assert 'Z' in transformed.command_string
