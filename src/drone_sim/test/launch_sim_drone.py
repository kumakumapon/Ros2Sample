"""Integration test using launch_testing for drone_sim nodes."""

import unittest

import pytest

try:
    from launch import LaunchDescription
    from launch_ros.actions import Node
    import launch_testing
    import launch_testing.actions
    from nav_msgs.msg import Odometry
    import rclpy
    from rclpy.node import Node as RclpyNode
    HAVE_LAUNCH_TESTING = True
except ImportError:
    HAVE_LAUNCH_TESTING = False


@pytest.mark.launch_test
def generate_test_description():
    """Generate launch description for drone integration testing."""
    if not HAVE_LAUNCH_TESTING:
        return LaunchDescription()

    drone_node = Node(
        package='drone_sim',
        executable='sim_drone',
        name='sim_drone',
        parameters=[{'publish_rate_hz': 50.0}],
    )

    return LaunchDescription([
        drone_node,
        launch_testing.actions.ReadyToTest(),
    ])


class TestSimDroneLaunch(unittest.TestCase):
    """Integration test checking drone simulation startup and odometry publishing."""

    @classmethod
    def setUpClass(cls):
        if not HAVE_LAUNCH_TESTING:
            return
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        if not HAVE_LAUNCH_TESTING:
            return
        rclpy.shutdown()

    def setUp(self):
        if not HAVE_LAUNCH_TESTING:
            self.skipTest('launch_testing or ROS 2 dependencies not available')
        self.node = RclpyNode('test_drone_client')

    def tearDown(self):
        if hasattr(self, 'node'):
            self.node.destroy_node()

    def test_odom_topic_published(self):
        """Verify that sim_drone publishes valid Odometry messages."""
        received_msgs = []

        sub = self.node.create_subscription(
            Odometry,
            'odom',
            lambda msg: received_msgs.append(msg),
            10,
        )

        start_time = self.node.get_clock().now()
        while len(received_msgs) < 3:
            rclpy.spin_once(self.node, timeout_sec=0.1)
            elapsed = (self.node.get_clock().now() - start_time).nanoseconds * 1e-9
            if elapsed > 5.0:
                break

        self.node.destroy_subscription(sub)
        self.assertGreaterEqual(
            len(received_msgs),
            1,
            'Failed to receive odom messages within timeout',
        )
