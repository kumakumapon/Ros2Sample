"""Launch integration scenario; execute with launch_test after building."""

from launch import LaunchDescription
from launch_ros.actions import Node
import launch_testing.actions
from sample_utils.testing import RosTestCase

from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu


def generate_test_description():
    """Start only the drone under test in its own namespace."""
    return LaunchDescription([
        Node(package='drone_sim', executable='sim_drone', namespace='test_drone',
             parameters=[{'publish_rate_hz': 50.0}]),
        launch_testing.actions.ReadyToTest(),
    ])


class TestDrone(RosTestCase):
    """Validate all sensor streams, publication rates and commanded motion."""

    namespace = 'test_drone'

    def test_sensors_and_motion(self):
        """Receive 50 Hz sensor data and move forward on repeated cmd_vel input."""
        odom = self.receive(Odometry, 'odom')
        pose = self.receive(PoseStamped, 'pose')
        imu = self.receive(Imu, 'imu')
        self.wait_until(lambda: all(len(m) >= 3 for m in (odom, pose, imu)))
        start_x = odom[-1].pose.pose.position.x
        for stream in (odom, pose, imu):
            stream.clear()
        self.spin_for(2.0)
        for stream in (odom, pose, imu):
            self.assertGreaterEqual(len(stream), 30)
            stamps = [m.header.stamp.sec + m.header.stamp.nanosec * 1e-9 for m in stream]
            self.assertTrue(all(b > a for a, b in zip(stamps, stamps[1:])))
            rate = (len(stamps) - 1) / (stamps[-1] - stamps[0])
            self.assertGreater(rate, 20.0)
            self.assertLess(rate, 80.0)
        publisher = self.node.create_publisher(Twist, 'cmd_vel', 10)
        self.wait_until(lambda: publisher.get_subscription_count() > 0)
        command = Twist()
        command.linear.x = 0.5
        timer = self.node.create_timer(0.05, lambda: publisher.publish(command))
        self.addCleanup(self.node.destroy_timer, timer)
        self.wait_until(lambda: odom[-1].pose.pose.position.x > start_x + 0.3)
        self.assertEqual(odom[-1].header.frame_id, 'odom')
        self.assertEqual(imu[-1].header.frame_id, 'base_link')
