"""Small math helpers used by the drone simulation nodes."""

from math import asin, atan2, copysign, cos, pi, sin
from typing import Tuple


def clamp(value: float, lower: float, upper: float) -> float:
    """Clamp value to the inclusive [lower, upper] range."""
    return max(lower, min(upper, value))


def normalize_angle(angle: float) -> float:
    """Wrap an angle to [-pi, pi]."""
    return atan2(sin(angle), cos(angle))


def quat_from_euler(
    roll: float,
    pitch: float,
    yaw: float,
) -> Tuple[float, float, float, float]:
    """Return an x, y, z, w quaternion from roll, pitch, and yaw radians."""
    half_roll = roll * 0.5
    half_pitch = pitch * 0.5
    half_yaw = yaw * 0.5

    cr = cos(half_roll)
    sr = sin(half_roll)
    cp = cos(half_pitch)
    sp = sin(half_pitch)
    cy = cos(half_yaw)
    sy = sin(half_yaw)

    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def euler_from_quat(
    x: float,
    y: float,
    z: float,
    w: float,
) -> Tuple[float, float, float]:
    """Return roll, pitch, yaw angles in radians from an x, y, z, w quaternion."""
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = copysign(pi / 2.0, sinp)
    else:
        pitch = asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    """Return planar yaw angle in radians from an x, y, z, w quaternion."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return atan2(siny_cosp, cosy_cosp)
