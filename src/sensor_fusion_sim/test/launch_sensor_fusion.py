"""Launch integration scenario; execute with launch_test after building."""

from launch import LaunchDescription
from launch_ros.actions import Node
import launch_testing.actions
from sample_utils.testing import RosTestCase

import math
import re

from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from std_msgs.msg import String


def generate_test_description():
    """Launch the real noisy-sensor to complementary-filter pipeline."""
    return LaunchDescription([
        Node(package='sensor_fusion_sim', executable='noisy_sensor_node',
             namespace='test_fusion', parameters=[{
                 'gps_noise_stddev': 0.0, 'odom_noise_stddev': 0.0,
                 'imu_accel_stddev': 0.0, 'imu_gyro_stddev': 0.0}]),
        Node(package='sensor_fusion_sim', executable='complementary_filter_node',
             namespace='test_fusion'),
        launch_testing.actions.ReadyToTest(),
    ])


class TestFusion(RosTestCase):
    """Check input consumption rather than merely receiving timer output."""

    namespace = 'test_fusion'

    def test_pipeline(self):
        """Require all three sensors, finite moving output and body-frame IMU."""
        fused = self.receive(Odometry, 'fused_odom')
        diagnostics = self.receive(String, 'filter_diagnostics')
        imu = self.receive(Imu, 'imu')
        wheel = self.receive(Odometry, 'wheel_odom')

        def consumed():
            if not diagnostics:
                return False
            counts = dict(re.findall(r'(gps|imu|odom)=(\d+)', diagnostics[-1].data))
            return all(int(counts.get(key, 0)) >= 2 for key in ('gps', 'imu', 'odom'))

        self.wait_until(lambda: consumed() and len(fused) > 5 and imu and wheel)
        self.assertEqual(fused[-1].header.frame_id, 'world')
        self.assertEqual(fused[-1].child_frame_id, 'base_link_fused')
        point = fused[-1].pose.pose.position
        self.assertTrue(math.isfinite(point.x) and math.isfinite(point.y))
        self.assertGreater(math.hypot(point.x, point.y), 2.0)
        self.assertEqual(imu[-1].header.frame_id, 'base_link')
        # Bias remains bounded by 0.05; positive body Y points left.
        self.assertAlmostEqual(imu[-1].linear_acceleration.x, 0.0, delta=0.051)
        self.assertAlmostEqual(imu[-1].linear_acceleration.y, 0.45, delta=0.051)
        self.assertAlmostEqual(wheel[-1].twist.twist.linear.x, 1.5, places=6)
        self.assertAlmostEqual(wheel[-1].twist.twist.linear.y, 0.0, places=6)
        first = (point.x, point.y)
        self.spin_for(1.0)
        point = fused[-1].pose.pose.position
        self.assertGreater(math.hypot(point.x - first[0], point.y - first[1]), 0.2)
