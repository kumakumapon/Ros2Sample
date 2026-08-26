"""Pure coordinate transform and quaternion helpers for sensor fusion."""

import math
from typing import Tuple


def normalize_angle(angle: float) -> float:
    """Wrap angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def yaw_to_quaternion(yaw: float) -> Tuple[float, float, float, float]:
    """Return an x, y, z, w normalized quaternion for a pure planar yaw rotation."""
    half_yaw = yaw * 0.5
    return 0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw)


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    """Return the planar yaw angle in radians from an x, y, z, w quaternion."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def euler_to_quaternion(
    roll: float,
    pitch: float,
    yaw: float,
) -> Tuple[float, float, float, float]:
    """Convert roll, pitch, and yaw angles (ZYX convention) to an x, y, z, w quaternion."""
    half_roll = roll * 0.5
    half_pitch = pitch * 0.5
    half_yaw = yaw * 0.5

    cr = math.cos(half_roll)
    sr = math.sin(half_roll)
    cp = math.cos(half_pitch)
    sp = math.sin(half_pitch)
    cy = math.cos(half_yaw)
    sy = math.sin(half_yaw)

    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    qw = cr * cp * cy + sr * sp * sy
    return qx, qy, qz, qw


def quaternion_to_euler(
    x: float,
    y: float,
    z: float,
    w: float,
) -> Tuple[float, float, float]:
    """Convert an x, y, z, w quaternion to roll, pitch, and yaw angles in radians."""
    # Roll (x-axis rotation)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw


def transform_point_2d(
    x: float,
    y: float,
    tx: float,
    ty: float,
    yaw: float,
) -> Tuple[float, float]:
    """
    Apply a 2D rigid transform (rotation by yaw followed by translation (tx, ty)).

    Computes: p_world = R(yaw) * p_local + t.
    """
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    x_out = x * cos_yaw - y * sin_yaw + tx
    y_out = x * sin_yaw + y * cos_yaw + ty
    return x_out, y_out


def inverse_transform_point_2d(
    x: float,
    y: float,
    tx: float,
    ty: float,
    yaw: float,
) -> Tuple[float, float]:
    """
    Apply inverse 2D rigid transform (world point to frame at (tx, ty, yaw)).

    Computes: p_local = R(-yaw) * (p_world - t).
    """
    dx = x - tx
    dy = y - ty
    cos_yaw = math.cos(yaw)
    sin_yaw = math.sin(yaw)
    x_out = dx * cos_yaw + dy * sin_yaw
    y_out = -dx * sin_yaw + dy * cos_yaw
    return x_out, y_out
