"""Launch integration scenario; execute with launch_test after building."""

from geometry_msgs.msg import Twist
from launch import LaunchDescription
from launch_ros.actions import Node
import launch_testing.actions
from nav_msgs.msg import Odometry
from sample_utils.testing import RosTestCase
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Trigger


def generate_test_description():
    """Start the ground robot without a competing controller."""
    return LaunchDescription([
        Node(package='ground_robot_sim', executable='ground_robot_node',
             namespace='test_ground', parameters=[{'publish_rate': 30.0, 'scan_rate': 10.0}]),
        launch_testing.actions.ReadyToTest(),
    ])


class TestGroundRobot(RosTestCase):
    """Validate scans and the stop/reset service behavior under continued commands."""

    namespace = 'test_ground'

    def test_scan_and_emergency_stop(self):
        """Stop must latch, ignore commands, and allow movement after reset."""
        scans = self.receive(LaserScan, 'scan')
        odom = self.receive(Odometry, 'odom')
        self.wait_until(lambda: len(scans) >= 3 and len(odom) >= 3)
        self.assertEqual(len(scans[-1].ranges), 181)
        self.assertEqual(scans[-1].header.frame_id, 'base_scan')
        self.assertGreater(scans[-1].range_max, scans[-1].range_min)
        publisher = self.node.create_publisher(Twist, 'cmd_vel', 10)
        self.wait_until(lambda: publisher.get_subscription_count() > 0)
        command = Twist()
        command.linear.x = 0.3
        timer = self.node.create_timer(0.05, lambda: publisher.publish(command))
        self.addCleanup(self.node.destroy_timer, timer)
        start_x = odom[-1].pose.pose.position.x
        self.wait_until(lambda: odom[-1].pose.pose.position.x > start_x + 0.1)
        stop = self.node.create_client(Trigger, 'emergency_stop')
        reset = self.node.create_client(Trigger, 'reset_emergency')
        self.assertTrue(stop.wait_for_service(timeout_sec=10.0))
        self.assertTrue(reset.wait_for_service(timeout_sec=10.0))
        self.assertTrue(self.result(stop.call_async(Trigger.Request())).success)
        self.spin_for(0.3)
        stopped_x = odom[-1].pose.pose.position.x
        odom.clear()
        self.spin_for(0.5)
        self.assertGreater(len(odom), 3)
        for msg in odom:
            self.assertAlmostEqual(msg.pose.pose.position.x, stopped_x, places=5)
            self.assertAlmostEqual(msg.twist.twist.linear.x, 0.0, places=5)
        self.assertTrue(self.result(reset.call_async(Trigger.Request())).success)
        self.wait_until(lambda: odom[-1].pose.pose.position.x > stopped_x + 0.1)
