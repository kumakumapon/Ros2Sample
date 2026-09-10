"""Unit tests for the rule-based natural-language command parser."""

from rai_bridge.nl_command_parser import DEFAULT_ANGLE_DEG, DEFAULT_DISTANCE_M, parse_command


def test_stop_japanese_and_english():
    """Both Japanese and English stop phrases map to the stop action."""
    assert parse_command('止まって').action == 'stop'
    assert parse_command('Please stop now').action == 'stop'


def test_forward_default_distance():
    """A forward phrase without a number uses the default distance."""
    command = parse_command('前進して')
    assert command.action == 'move_forward'
    assert command.value == DEFAULT_DISTANCE_M


def test_forward_with_explicit_distance():
    """A forward phrase with a Japanese unit extracts the given distance."""
    command = parse_command('3メートル進んで')
    assert command.action == 'move_forward'
    assert command.value == 3.0


def test_backward_with_explicit_distance():
    """An English backward phrase with a unit extracts the given distance."""
    command = parse_command('move backward 2.5 m')
    assert command.action == 'move_backward'
    assert command.value == 2.5


def test_rotate_left_default_angle():
    """A left phrase without a number uses the default angle."""
    command = parse_command('左に曲がって')
    assert command.action == 'rotate_left'
    assert command.value == DEFAULT_ANGLE_DEG


def test_rotate_right_with_explicit_angle():
    """A right phrase with a degree suffix extracts the given angle."""
    command = parse_command('右に45度回転して')
    assert command.action == 'rotate_right'
    assert command.value == 45.0


def test_unknown_command():
    """Text with no recognized keyword is reported as unknown."""
    command = parse_command('いい天気ですね')
    assert command.action == 'unknown'
    assert command.value == 0.0
