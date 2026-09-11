"""
Pure "tool" functions that turn a command into Twist-shaped values.

Each function here is deliberately small, typed, and documented -- the same
shape RAI and LangChain agents expect a "tool" to have, so
``rai_agent_adapter`` can wrap them for a real LLM agent with no changes.
``nl_command_node`` calls them directly from the rule-based parser output.
"""

import math
from typing import Tuple

from rai_bridge.nl_command_parser import ParsedCommand


def move_forward(distance_m: float, raw_text: str = '') -> ParsedCommand:
    """Return a command that drives the robot forward by distance_m meters."""
    return ParsedCommand('move_forward', distance_m, raw_text or f'move_forward({distance_m})')


def move_backward(distance_m: float, raw_text: str = '') -> ParsedCommand:
    """Return a command that drives the robot backward by distance_m meters."""
    return ParsedCommand('move_backward', distance_m, raw_text or f'move_backward({distance_m})')


def rotate_left(angle_deg: float, raw_text: str = '') -> ParsedCommand:
    """Return a command that rotates the robot left by angle_deg degrees."""
    return ParsedCommand('rotate_left', angle_deg, raw_text or f'rotate_left({angle_deg})')


def rotate_right(angle_deg: float, raw_text: str = '') -> ParsedCommand:
    """Return a command that rotates the robot right by angle_deg degrees."""
    return ParsedCommand('rotate_right', angle_deg, raw_text or f'rotate_right({angle_deg})')


def stop(raw_text: str = '') -> ParsedCommand:
    """Return a command that stops the robot immediately."""
    return ParsedCommand('stop', 0.0, raw_text or 'stop()')


def twist_values_for_command(
    command: ParsedCommand,
    linear_speed: float,
    angular_speed: float,
) -> Tuple[float, float]:
    """Return the (linear_x, angular_z) Twist components for command.action."""
    if command.action == 'move_forward':
        return (abs(linear_speed), 0.0)
    if command.action == 'move_backward':
        return (-abs(linear_speed), 0.0)
    if command.action == 'rotate_left':
        return (0.0, abs(angular_speed))
    if command.action == 'rotate_right':
        return (0.0, -abs(angular_speed))
    return (0.0, 0.0)


def command_duration_sec(
    command: ParsedCommand,
    linear_speed: float,
    angular_speed: float,
) -> float:
    """
    Return how long to hold the Twist to satisfy command.value.

    Distance-based actions divide meters by linear_speed; rotation-based
    actions convert degrees to radians and divide by angular_speed. Unknown
    and stop actions need no holding time.
    """
    if command.action in ('move_forward', 'move_backward'):
        speed = max(abs(linear_speed), 1e-6)
        return abs(command.value) / speed
    if command.action in ('rotate_left', 'rotate_right'):
        rate = max(abs(angular_speed), 1e-6)
        return math.radians(abs(command.value)) / rate
    return 0.0
