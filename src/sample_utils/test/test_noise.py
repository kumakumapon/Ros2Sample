"""Deterministic noise policy tests shared by every simulator."""

import random

from sample_utils.noise import add_gaussian_noise


def test_zero_noise_does_not_consume_rng():
    """Disabled noise must preserve both the value and RNG sequence."""
    rng = random.Random(4)
    before = rng.getstate()
    assert add_gaussian_noise(2.0, 0.0, rng) == 2.0
    assert add_gaussian_noise(2.0, -1.0, rng) == 2.0
    assert rng.getstate() == before


def test_injected_rng_is_repeatable():
    """Equal seeds must produce equal independent streams."""
    a, b = random.Random(9), random.Random(9)
    assert [add_gaussian_noise(1.0, 0.2, a) for _ in range(10)] == [
        add_gaussian_noise(1.0, 0.2, b) for _ in range(10)]
