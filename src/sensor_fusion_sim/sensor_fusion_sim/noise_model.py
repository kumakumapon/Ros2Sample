"""Noise generation utilities for simulated sensors."""

import random
from typing import Optional, Tuple

from sample_utils.noise import add_gaussian_noise  # noqa: F401


def add_gaussian_noise_3d(
    x: float,
    y: float,
    z: float,
    stddev_xy: float,
    stddev_z: float,
    rng: Optional[random.Random] = None,
) -> Tuple[float, float, float]:
    """Return (x, y, z) with independent Gaussian noise per axis."""
    return (
        add_gaussian_noise(x, stddev_xy, rng),
        add_gaussian_noise(y, stddev_xy, rng),
        add_gaussian_noise(z, stddev_z, rng),
    )


def drift_walk(
    current: float,
    stddev: float,
    limit: float,
    rng: Optional[random.Random] = None,
) -> float:
    """Random-walk drift step, clamped to [-limit, limit]."""
    if stddev <= 0.0:
        return max(-limit, min(limit, current))
    generator = rng if rng is not None else random
    updated = current + generator.gauss(0.0, stddev)
    return max(-limit, min(limit, updated))


def generate_imu_noise(
    ax: float,
    ay: float,
    az: float,
    gyro_z: float,
    accel_stddev: float,
    gyro_stddev: float,
    accel_bias: float = 0.0,
    gyro_bias: float = 0.0,
    rng: Optional[random.Random] = None,
) -> Tuple[float, float, float, float]:
    """Add noise and bias to IMU readings, return (ax, ay, az, gyro_z)."""
    return (
        add_gaussian_noise(ax + accel_bias, accel_stddev, rng),
        add_gaussian_noise(ay + accel_bias, accel_stddev, rng),
        add_gaussian_noise(az + accel_bias, accel_stddev, rng),
        add_gaussian_noise(gyro_z + gyro_bias, gyro_stddev, rng),
    )
