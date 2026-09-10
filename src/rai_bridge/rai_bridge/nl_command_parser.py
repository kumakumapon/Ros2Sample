"""Rule-based natural-language command parser (no ROS or LLM dependency).

This is the offline fallback that ``nl_command_node`` uses by default, and
that CI exercises deterministically. It recognizes a small set of Japanese
and English phrases for driving a differential-drive robot and extracts an
optional distance (meters) or angle (degrees) from the text.
"""

import re
from typing import NamedTuple, Optional

DEFAULT_DISTANCE_M = 1.0
DEFAULT_ANGLE_DEG = 90.0

STOP_KEYWORDS = ('止まれ', '止まって', 'ストップ', '停止', 'stop', 'halt')
LEFT_KEYWORDS = ('左', 'left')
RIGHT_KEYWORDS = ('右', 'right')
BACKWARD_KEYWORDS = ('後退', '下がって', '下がれ', 'backward', 'back up')
FORWARD_KEYWORDS = ('前進', '進んで', '進め', 'forward', 'advance')

DISTANCE_PATTERN = re.compile(
    r'(\d+(?:\.\d+)?)\s*(?:メートル|メーター|meters?|m\b)', re.IGNORECASE,
)
ANGLE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*(?:度|deg(?:rees?)?)', re.IGNORECASE)


class ParsedCommand(NamedTuple):
    """A recognized action plus its numeric argument (meters or degrees)."""

    action: str
    value: float
    raw_text: str


def _matches(normalized_text: str, keywords) -> bool:
    """Return whether any keyword occurs in normalized_text."""
    return any(keyword in normalized_text for keyword in keywords)


def _extract_number(text: str, pattern: 're.Pattern') -> Optional[float]:
    """Return the first number captured by pattern in text, if any."""
    match = pattern.search(text)
    return float(match.group(1)) if match else None


def parse_command(text: str) -> ParsedCommand:
    """Parse free-form text into a ParsedCommand.

    Recognized actions are ``move_forward``, ``move_backward``,
    ``rotate_left``, ``rotate_right`` and ``stop``. Text that matches none
    of these keywords returns action ``unknown`` with value ``0.0``.
    """
    normalized = text.strip().lower()

    if _matches(normalized, STOP_KEYWORDS):
        return ParsedCommand('stop', 0.0, text)
    if _matches(normalized, LEFT_KEYWORDS):
        angle = _extract_number(text, ANGLE_PATTERN)
        return ParsedCommand('rotate_left', angle or DEFAULT_ANGLE_DEG, text)
    if _matches(normalized, RIGHT_KEYWORDS):
        angle = _extract_number(text, ANGLE_PATTERN)
        return ParsedCommand('rotate_right', angle or DEFAULT_ANGLE_DEG, text)
    if _matches(normalized, BACKWARD_KEYWORDS):
        distance = _extract_number(text, DISTANCE_PATTERN)
        return ParsedCommand('move_backward', distance or DEFAULT_DISTANCE_M, text)
    if _matches(normalized, FORWARD_KEYWORDS):
        distance = _extract_number(text, DISTANCE_PATTERN)
        return ParsedCommand('move_forward', distance or DEFAULT_DISTANCE_M, text)
    return ParsedCommand('unknown', 0.0, text)
