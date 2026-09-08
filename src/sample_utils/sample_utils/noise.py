"""Common Gaussian noise policy with injectable random generators."""

import random
from typing import Optional


def add_gaussian_noise(
    value: float,
    stddev: float,
    rng: Optional[random.Random] = None,
) -> float:
    """
    Return value with additive Gaussian noise.

    No random call is made and the value is returned unchanged when
    stddev is less than or equal to 0.0.
    """
    if stddev <= 0.0:
        return value
    generator = rng if rng is not None else random
    return value + generator.gauss(0.0, stddev)
