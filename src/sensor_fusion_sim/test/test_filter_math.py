"""Unit tests for sensor_fusion_sim.filter_math."""

import math

import pytest
from sensor_fusion_sim.filter_math import (
    blend_angle,
    complementary_filter_1d,
    complementary_filter_3d,
    normalize_angle,
)


def test_complementary_filter_1d_alpha_zero():
    """alpha=0 returns predicted value unchanged."""
    assert complementary_filter_1d(5.0, 10.0, 0.0) == pytest.approx(5.0)


def test_complementary_filter_1d_alpha_one():
    """alpha=1 returns measured value."""
    assert complementary_filter_1d(5.0, 10.0, 1.0) == pytest.approx(10.0)


def test_complementary_filter_1d_half():
    """alpha=0.5 returns average of predicted and measured."""
    assert complementary_filter_1d(4.0, 6.0, 0.5) == pytest.approx(5.0)


def test_complementary_filter_3d_alpha_one():
    """alpha=1 returns measured values in all three axes."""
    result = complementary_filter_3d(
        0.0, 0.0, 0.0,
        1.0, 2.0, 3.0,
        1.0,
    )
    assert result == pytest.approx((1.0, 2.0, 3.0))


def test_blend_angle():
    """Test angular blending across standard values and phase wrap boundaries."""
    # Simple interpolation
    assert blend_angle(0.0, 1.0, 0.5) == pytest.approx(0.5)
    assert blend_angle(0.0, 1.0, 0.0) == pytest.approx(0.0)
    assert blend_angle(0.0, 1.0, 1.0) == pytest.approx(1.0)

    # Wrap around +/- pi: from 3.0 to -3.0 (difference is ~0.28 rad across pi boundary)
    current = 3.1
    target = -3.1
    blended = blend_angle(current, target, 0.5)
    # The midpoint across pi is pi or -pi
    assert abs(abs(blended) - math.pi) < 0.1


def test_normalize_angle_within_range():
    """Angle already in [-pi, pi] is returned unchanged."""
    assert normalize_angle(1.0) == pytest.approx(1.0)
    assert normalize_angle(-1.0) == pytest.approx(-1.0)


def test_normalize_angle_wraps_positive():
    """3*pi wraps to pi (magnitude)."""
    result = normalize_angle(3.0 * math.pi)
    assert abs(result) == pytest.approx(math.pi)


def test_normalize_angle_wraps_negative():
    """-3*pi wraps to -pi (magnitude)."""
    result = normalize_angle(-3.0 * math.pi)
    assert abs(result) == pytest.approx(math.pi)
