"""Tests for transform_utils module in sensor_fusion_sim."""

import math

import pytest
from sensor_fusion_sim.transform_utils import (
    euler_to_quaternion,
    inverse_transform_point_2d,
    normalize_angle,
    quaternion_to_euler,
    transform_point_2d,
    yaw_from_quaternion,
    yaw_to_quaternion,
)


def test_normalize_angle():
    """Test angle normalization to [-pi, pi]."""
    assert math.isclose(normalize_angle(0.0), 0.0)
    assert math.isclose(normalize_angle(math.pi), math.pi)
    assert math.isclose(normalize_angle(-math.pi), -math.pi)
    assert math.isclose(normalize_angle(3 * math.pi), math.pi)
    assert math.isclose(normalize_angle(-3 * math.pi), -math.pi)
    assert math.isclose(normalize_angle(2 * math.pi), 0.0, abs_tol=1e-9)
    assert math.isclose(normalize_angle(-2 * math.pi), 0.0, abs_tol=1e-9)
    assert math.isclose(normalize_angle(math.pi / 2.0), math.pi / 2.0)
    assert math.isclose(normalize_angle(5 * math.pi / 2.0), math.pi / 2.0)


def test_yaw_to_quaternion_and_back():
    """Test yaw to quaternion and reverse extraction."""
    for yaw in [0.0, math.pi / 4.0, math.pi / 2.0, -math.pi / 3.0, math.pi, -math.pi]:
        qx, qy, qz, qw = yaw_to_quaternion(yaw)
        assert math.isclose(qx, 0.0)
        assert math.isclose(qy, 0.0)
        # Unit quaternion norm
        norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
        assert math.isclose(norm, 1.0)
        # Recover yaw
        recovered_yaw = yaw_from_quaternion(qx, qy, qz, qw)
        assert math.isclose(normalize_angle(recovered_yaw), normalize_angle(yaw), abs_tol=1e-7)


def test_euler_to_quaternion_and_back():
    """Test 3D Euler to quaternion and inverse conversion."""
    test_cases = [
        (0.0, 0.0, 0.0),
        (0.1, 0.2, 0.3),
        (-0.5, 0.4, -1.2),
        (0.0, math.pi / 2.0 - 0.01, 0.0),
        (math.pi / 3.0, -math.pi / 4.0, math.pi / 6.0),
    ]
    for roll, pitch, yaw in test_cases:
        qx, qy, qz, qw = euler_to_quaternion(roll, pitch, yaw)
        norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
        assert math.isclose(norm, 1.0)

        r_rec, p_rec, y_rec = quaternion_to_euler(qx, qy, qz, qw)
        assert math.isclose(r_rec, roll, abs_tol=1e-7)
        assert math.isclose(p_rec, pitch, abs_tol=1e-7)
        assert math.isclose(y_rec, yaw, abs_tol=1e-7)


def test_transform_point_2d_and_inverse():
    """Test forward and inverse 2D point transformation."""
    px, py = 2.0, 3.0
    tx, ty = 10.0, -5.0
    yaw = math.pi / 3.0

    # Forward transform
    wx, wy = transform_point_2d(px, py, tx, ty, yaw)
    # Inverse transform
    lx, ly = inverse_transform_point_2d(wx, wy, tx, ty, yaw)

    assert math.isclose(lx, px, abs_tol=1e-9)
    assert math.isclose(ly, py, abs_tol=1e-9)


def test_transform_point_2d_identities():
    """Test identity transformation."""
    px, py = 1.5, -2.5
    wx, wy = transform_point_2d(px, py, 0.0, 0.0, 0.0)
    assert math.isclose(wx, px)
    assert math.isclose(wy, py)

    # Pure translation
    wx, wy = transform_point_2d(px, py, 3.0, 4.0, 0.0)
    assert math.isclose(wx, 4.5)
    assert math.isclose(wy, 1.5)

    # Pure 90 deg rotation
    wx, wy = transform_point_2d(1.0, 0.0, 0.0, 0.0, math.pi / 2.0)
    assert math.isclose(wx, 0.0, abs_tol=1e-9)
    assert math.isclose(wy, 1.0, abs_tol=1e-9)
