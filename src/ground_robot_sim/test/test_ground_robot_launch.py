"""Integration test using launch_testing for ground_robot_sim nodes."""

import os
import unittest

import pytest

try:
    from ament_index_python.packages import get_package_share_directory
    from launch import LaunchDescription
    from launch_ros.actions import Node
    import launch_testing
    import launch_testing.actions
    import rclpy
    from rclpy.node import Node as RclpyNode
    from sensor_msgs.msg import LaserScan
    HAVE_LAUNCH_TESTING = True
except ImportError:
    HAVE_LAUNCH_TESTING = False


@pytest.mark.launch_test
def generate_test_description():
    """Generate launch description for integration testing."""
    if not HAVE_LAUNCH_TESTING:
        return LaunchDescription()

    ground_robot_node = Node(
        package='ground_robot_sim',
        executable='ground_robot_node',
        name='ground_robot',
        parameters=[{'publish_rate': 30.0, 'scan_rate': 10.0}],
    )

    return LaunchDescription([
        ground_robot_node,
        launch_testing.actions.ReadyToTest(),
    ])


class TestGroundRobotLaunch(unittest.TestCase):
    """Integration test checking node startup and topic publishing."""

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
        self.node = RclpyNode('test_ground_robot_client')

    def tearDown(self):
        if hasattr(self, 'node'):
            self.node.destroy_node()

    def test_scan_topic_published(self):
        """Verify that ground_robot publishes valid LaserScan messages."""
        received_msgs = []

        sub = self.node.create_subscription(
            LaserScan,
            'scan',
            lambda msg: received_msgs.append(msg),
            10,
        )

        # Spin briefly to receive messages
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
            'Failed to receive scan messages within timeout',
        )
        first_scan = received_msgs[0]
        self.assertGreater(len(first_scan.ranges), 0)
