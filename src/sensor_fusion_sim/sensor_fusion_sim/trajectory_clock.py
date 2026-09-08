"""Elapsed ROS time with a deterministic origin and backwards-jump reset."""


class TrajectoryClock:
    """Wait for initialized ROS time and reset the trajectory after clock rewind."""

    def __init__(self, now_ns: int) -> None:
        """Capture startup time, deferring an uninitialized simulated clock."""
        self._origin = now_ns if now_ns != 0 else None
        self._previous = now_ns

    def elapsed(self, now_ns: int) -> float:
        """Return elapsed seconds, starting at zero after initialization or rewind."""
        if self._origin is None or now_ns < self._previous:
            self._origin = now_ns if now_ns != 0 else None
        self._previous = now_ns
        return 0.0 if self._origin is None else (now_ns - self._origin) * 1e-9
