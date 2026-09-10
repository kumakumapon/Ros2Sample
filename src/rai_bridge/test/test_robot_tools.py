"""Unit tests for the pure Twist-shaping helpers used by nl_command_node."""

import math

from rai_bridge import robot_tools
from rai_bridge.nl_command_parser import parse_command


def test_twist_values_for_forward():
    """Forward commands produce a positive linear_x and no rotation."""
    command = parse_command('前進して')
    linear_x, angular_z = robot_tools.twist_values_for_command(command, 0.5, 1.0)
    assert linear_x == 0.5
    assert angular_z == 0.0


def test_twist_values_for_rotate_right_is_negative():
    """Rotating right yields a negative angular_z and no forward motion."""
    command = parse_command('右に曲がって')
    linear_x, angular_z = robot_tools.twist_values_for_command(command, 0.5, 1.0)
    assert linear_x == 0.0
    assert angular_z == -1.0


def test_twist_values_for_stop_is_zero():
    """A stop command always produces a zero Twist."""
    command = robot_tools.stop()
    assert robot_tools.twist_values_for_command(command, 0.5, 1.0) == (0.0, 0.0)


def test_duration_for_move_uses_distance_over_speed():
    """Move duration is the requested distance divided by the linear speed."""
    command = parse_command('4メートル進んで')
    duration = robot_tools.command_duration_sec(command, 2.0, 1.0)
    assert duration == 2.0


def test_duration_for_rotate_uses_angle_over_rate():
    """Rotate duration is the requested angle in radians divided by the rate."""
    command = robot_tools.rotate_left(90.0)
    duration = robot_tools.command_duration_sec(command, 1.0, math.pi / 2)
    assert math.isclose(duration, 1.0)


def test_tool_functions_build_expected_commands():
    """The plain tool functions build ParsedCommand values with the given args."""
    assert robot_tools.move_backward(1.5).value == 1.5
    assert robot_tools.rotate_right(30.0).action == 'rotate_right'
