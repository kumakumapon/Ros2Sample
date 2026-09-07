"""Pure noise-injection helpers for simulated ground-robot sensors (no ROS imports)."""

import math
import random
from typing import List, Optional, Sequence, Tuple

from sample_utils.noise import add_gaussian_noise  # noqa: F401


def noisy_pose_2d(
    x: float,
    y: float,
    yaw: float,
    pos_stddev: float,
    yaw_stddev: float,
    rng: Optional[random.Random] = None,
) -> Tuple[float, float, float]:
    """Return (x, y, yaw) with independent Gaussian noise on position and heading."""
    generator = rng if rng is not None else random
    return (
        add_gaussian_noise(x, pos_stddev, generator),
        add_gaussian_noise(y, pos_stddev, generator),
        add_gaussian_noise(yaw, yaw_stddev, generator),
    )


def noisy_scan(
    ranges: Sequence[float],
    stddev: float,
    range_min: float,
    range_max: float,
    rng: Optional[random.Random] = None,
) -> List[float]:
    """
    Return ranges with per-sample Gaussian noise clamped to [range_min, range_max].

    Non-finite readings (inf/nan) pass through unchanged, and the list is
    returned unmodified in value when stddev <= 0.
    """
    if stddev <= 0.0:
        return list(ranges)
    generator = rng if rng is not None else random
    noisy = []
    for value in ranges:
        if not math.isfinite(value):
            noisy.append(value)
            continue
        noisy.append(max(range_min, min(range_max, add_gaussian_noise(value, stddev, generator))))
    return noisy
