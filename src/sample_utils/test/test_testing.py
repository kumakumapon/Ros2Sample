"""Exercise the integration helper with a real non-default ROS context."""

import pytest

pytest.importorskip('rclpy')
testing = pytest.importorskip('sample_utils.testing')


class TestRosExecutor(testing.RosTestCase):
    """Check that timers and futures run on the helper's initialized context."""

    def test_timer_and_future(self):
        """Spin timer callbacks and complete a future without a global executor."""
        ticks = []
        timer = self.node.create_timer(0.01, lambda: ticks.append(True))
        self.addCleanup(self.node.destroy_timer, timer)
        self.wait_until(lambda: len(ticks) >= 2, timeout=2.0)
        before = len(ticks)
        self.spin_for(0.05)
        self.assertGreater(len(ticks), before)
        future = self.executor.create_task(lambda: 42)
        self.assertEqual(self.result(future), 42)
