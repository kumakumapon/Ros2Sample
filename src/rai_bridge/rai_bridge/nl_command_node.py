"""Bridge free-form natural-language text commands to cmd_vel Twist commands."""

from geometry_msgs.msg import Twist
from rai_bridge import robot_tools
from rai_bridge.nl_command_parser import DEFAULT_ANGLE_DEG, DEFAULT_DISTANCE_M, parse_command
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class NlCommandNode(Node):
    """Subscribe to text commands and drive the robot with open-loop Twist phases."""

    def __init__(self) -> None:
        """Declare parameters and set up the command subscription and publishers."""
        super().__init__('nl_command_node')
        self.declare_parameter('input_topic', 'nl_command')
        self.declare_parameter('linear_speed', 0.3)
        self.declare_parameter('angular_speed', 0.6)
        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('default_distance_m', DEFAULT_DISTANCE_M)
        self.declare_parameter('default_angle_deg', DEFAULT_ANGLE_DEG)

        input_topic = str(self.get_parameter('input_topic').value)
        self._linear_speed = float(self.get_parameter('linear_speed').value)
        self._angular_speed = float(self.get_parameter('angular_speed').value)
        rate = max(1.0, float(self.get_parameter('publish_rate').value))

        self._linear_x = 0.0
        self._angular_z = 0.0
        self._remaining_sec = 0.0
        self._status = 'idle'
        self._period_sec = 1.0 / rate

        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.status_publisher = self.create_publisher(String, 'nl_command_status', 10)
        self.create_subscription(String, input_topic, self._on_command, 10)
        self.create_timer(self._period_sec, self._on_timer)
        self.get_logger().info(f'Listening for natural-language commands on {input_topic}')

    def _on_command(self, msg: String) -> None:
        """Parse an incoming text command and start a new open-loop phase."""
        command = parse_command(msg.data)
        self._linear_x, self._angular_z = robot_tools.twist_values_for_command(
            command, self._linear_speed, self._angular_speed,
        )
        self._remaining_sec = robot_tools.command_duration_sec(
            command, self._linear_speed, self._angular_speed,
        )
        self._status = self._describe(command)
        self.get_logger().info(f'"{msg.data}" -> {self._status}')
        self._publish_status()

    def _on_timer(self) -> None:
        """Publish the active Twist phase and stop once its duration elapses."""
        twist = Twist()
        if self._remaining_sec > 0.0:
            twist.linear.x = self._linear_x
            twist.angular.z = self._angular_z
            self._remaining_sec -= self._period_sec
            if self._remaining_sec <= 0.0:
                self._status = 'idle'
                self._publish_status()
        self.cmd_vel_publisher.publish(twist)

    def _publish_status(self) -> None:
        """Publish the current human-readable status string."""
        status = String()
        status.data = self._status
        self.status_publisher.publish(status)

    @staticmethod
    def _describe(command) -> str:
        """Return a short human-readable label for a parsed command."""
        if command.action == 'unknown':
            return f'unrecognized: {command.raw_text}'
        if command.action == 'stop':
            return 'stop'
        return f'{command.action}({command.value:.2f})'


def main(args=None) -> None:
    """Run the natural-language command bridge node."""
    rclpy.init(args=args)
    node = NlCommandNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
