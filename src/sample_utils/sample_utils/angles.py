"""Common planar angle convention."""

import math


def normalize_angle(angle: float) -> float:
    """Wrap a finite angle to [-pi, pi] using trigonometric reduction."""
    return math.atan2(math.sin(angle), math.cos(angle))
