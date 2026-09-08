"""Launch integration scenario; execute with launch_test after building."""

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from launch import LaunchDescription
from launch_ros.actions import Node
import launch_testing.actions
from rclpy.action import ActionClient
from sample_interfaces.action import NavigateWaypoints
from sample_utils.testing import RosTestCase


def generate_test_description():
    """Start the action server; the test supplies its client."""
    return LaunchDescription([
        Node(package='ros2_learning', executable='minimal_action_server',
             namespace='test_action', parameters=[{'speed': 1.0, 'control_rate_hz': 20.0}]),
        launch_testing.actions.ReadyToTest(),
    ])


class TestAction(RosTestCase):
    """Exercise goal rejection, feedback and a successful result."""

    namespace = 'test_action'

    def test_goal_result(self):
        """Navigate two short waypoints and assert the exact completion count."""
        client = ActionClient(self.node, NavigateWaypoints, 'navigate_waypoints')
        self.addCleanup(client.destroy)
        self.assertTrue(client.wait_for_server(timeout_sec=10.0))
        rejected = self.result(client.send_goal_async(NavigateWaypoints.Goal()))
        self.assertFalse(rejected.accepted)
        goal = NavigateWaypoints.Goal()
        goal.tolerance_m = 0.05
        for x in (0.2, 0.4):
            waypoint = PoseStamped()
            waypoint.header.frame_id = 'odom'
            waypoint.pose.orientation.w = 1.0
            waypoint.pose.position.x = x
            goal.waypoints.append(waypoint)
        feedback = []
        handle = self.result(client.send_goal_async(goal, feedback_callback=feedback.append))
        self.assertTrue(handle.accepted)
        result = self.result(handle.get_result_async())
        self.assertEqual(result.status, GoalStatus.STATUS_SUCCEEDED)
        self.assertTrue(result.result.success)
        self.assertEqual(result.result.waypoints_completed, 2)
        self.assertGreater(len(feedback), 0)
        self.assertEqual(feedback[-1].feedback.total_waypoints, 2)
