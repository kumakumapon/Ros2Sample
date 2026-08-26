"""Tests for the drone_sim.math_utils module."""

import math

from drone_sim.math_utils import (
    clamp,
    euler_from_quat,
    normalize_angle,
    quat_from_euler,
    yaw_from_quat,
)
import pytest


def test_clamp_inside_range():
    """Value inside bounds is returned unchanged."""
    assert clamp(0.5, 0.0, 1.0) == pytest.approx(0.5)


def test_clamp_below_range():
    """Value below lower bound is clamped to lower bound."""
    assert clamp(-1.0, 0.0, 1.0) == pytest.approx(0.0)


def test_clamp_above_range():
    """Value above upper bound is clamped to upper bound."""
    assert clamp(2.0, 0.0, 1.0) == pytest.approx(1.0)


def test_normalize_angle_zero():
    """Zero stays zero."""
    assert normalize_angle(0.0) == pytest.approx(0.0)


def test_normalize_angle_three_pi():
    """3*pi wraps to approximately +/-pi (magnitude pi)."""
    assert abs(normalize_angle(3.0 * math.pi)) == pytest.approx(math.pi)


def test_normalize_angle_minus_three_halves_pi():
    """Negative 3*pi/2 wraps to pi/2."""
    assert normalize_angle(-3.0 * math.pi / 2.0) == pytest.approx(math.pi / 2.0)


def test_normalize_angle_already_in_range():
    """Value already in [-pi, pi] is returned unchanged."""
    assert normalize_angle(1.0) == pytest.approx(1.0)
    assert normalize_angle(-1.0) == pytest.approx(-1.0)


def test_quat_from_euler_yaw_only():
    """Yaw-only quaternion matches (0, 0, sin(yaw/2), cos(yaw/2))."""
    yaw = math.pi / 4.0
    x, y, z, w = quat_from_euler(0.0, 0.0, yaw)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)
    assert z == pytest.approx(math.sin(yaw / 2.0))
    assert w == pytest.approx(math.cos(yaw / 2.0))


def test_quat_from_euler_zero_angles_identity():
    """Zero roll/pitch/yaw gives the identity quaternion (0, 0, 0, 1)."""
    x, y, z, w = quat_from_euler(0.0, 0.0, 0.0)
    assert x == pytest.approx(0.0)
    assert y == pytest.approx(0.0)
    assert z == pytest.approx(0.0)
    assert w == pytest.approx(1.0)


def test_quat_from_euler_unit_norm():
    """An arbitrary roll/pitch/yaw quaternion has unit norm."""
    roll, pitch, yaw = 0.3, 0.5, 1.2
    x, y, z, w = quat_from_euler(roll, pitch, yaw)
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    assert norm == pytest.approx(1.0)


def test_euler_from_quat_roundtrip():
    """Euler angles convert to quaternion and back accurately."""
    test_cases = [
        (0.0, 0.0, 0.0),
        (0.2, -0.3, 0.7),
        (-0.5, 0.4, -1.1),
    ]
    for roll, pitch, yaw in test_cases:
        qx, qy, qz, qw = quat_from_euler(roll, pitch, yaw)
        r_rec, p_rec, y_rec = euler_from_quat(qx, qy, qz, qw)
        assert r_rec == pytest.approx(roll, abs=1e-6)
        assert p_rec == pytest.approx(pitch, abs=1e-6)
        assert y_rec == pytest.approx(yaw, abs=1e-6)


def test_yaw_from_quat_yaw_only():
    """Planar yaw extraction from a yaw-only quaternion."""
    for yaw in [0.0, 0.5, -1.2, math.pi / 2.0]:
        qx, qy, qz, qw = quat_from_euler(0.0, 0.0, yaw)
        extracted_yaw = yaw_from_quat(qx, qy, qz, qw)
        assert extracted_yaw == pytest.approx(yaw, abs=1e-6)
