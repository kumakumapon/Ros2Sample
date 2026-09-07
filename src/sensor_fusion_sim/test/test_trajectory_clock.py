"""Regression coverage for epoch, simulated-clock startup, pause and rewind."""

from sensor_fusion_sim.trajectory_clock import TrajectoryClock


def test_epoch_origin():
    """Large epoch times must not change the initial trajectory phase."""
    clock = TrajectoryClock(1_700_000_000_000_000_000)
    assert clock.elapsed(1_700_000_000_000_000_000) == 0.0
    assert clock.elapsed(1_700_000_001_000_000_000) == 1.0


def test_simulated_clock():
    """An uninitialized clock starts on the first nonzero tick and can rewind."""
    clock = TrajectoryClock(0)
    assert clock.elapsed(0) == 0.0
    assert clock.elapsed(100_000_000_000) == 0.0
    assert clock.elapsed(101_000_000_000) == 1.0
    assert clock.elapsed(101_000_000_000) == 1.0
    assert clock.elapsed(50_000_000_000) == 0.0
    assert clock.elapsed(51_000_000_000) == 1.0
    assert clock.elapsed(0) == 0.0
    assert clock.elapsed(200_000_000_000) == 0.0
