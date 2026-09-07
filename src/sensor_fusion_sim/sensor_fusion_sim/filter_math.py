"""Mathematical utilities for complementary filtering and state estimation."""

from typing import Tuple

from sample_utils.angles import normalize_angle  # noqa: F401


def complementary_filter_1d(
    predicted: float,
    measured: float,
    alpha: float,
) -> float:
    """Blend predicted and measured: alpha*measured + (1-alpha)*predicted."""
    return alpha * measured + (1.0 - alpha) * predicted


def complementary_filter_3d(
    pred_x: float,
    pred_y: float,
    pred_z: float,
    meas_x: float,
    meas_y: float,
    meas_z: float,
    alpha: float,
) -> Tuple[float, float, float]:
    """Blend 3D predicted and measured positions."""
    return (
        complementary_filter_1d(pred_x, meas_x, alpha),
        complementary_filter_1d(pred_y, meas_y, alpha),
        complementary_filter_1d(pred_z, meas_z, alpha),
    )


def blend_angle(
    current_yaw: float,
    measured_yaw: float,
    weight: float,
) -> float:
    """Blend current and measured headings, wrapping across the +/- pi phase boundary."""
    diff = normalize_angle(measured_yaw - current_yaw)
    return normalize_angle(current_yaw + weight * diff)
