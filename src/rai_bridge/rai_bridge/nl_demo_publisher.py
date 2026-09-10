"""Publish a scripted sequence of natural-language commands, for demos without an LLM."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

DEFAULT_SCRIPT = [
    '前進して',
    '2メートル進んで',
    '右に曲がって',
    '1メートル進んで',
    '左に90度回転して',
    '止まって',
]


class NlDemoPublisher(Node):
    """Step through a fixed script of text commands on a timer."""

    def __init__(self) -> None:
        """Declare parameters and set up the scripted command publisher."""
        super().__init__('nl_demo_publisher')
        self.declare_parameter('output_topic', 'nl_command')
        self.declare_parameter('commands', DEFAULT_SCRIPT)
        self.declare_parameter('interval_sec', 4.0)
        self.declare_parameter('loop', True)

        output_topic = str(self.get_parameter('output_topic').value)
        self._commands = list(self.get_parameter('commands').value) or list(DEFAULT_SCRIPT)
        self._loop = bool(self.get_parameter('loop').value)
        interval = max(0.1, float(self.get_parameter('interval_sec').value))

        self._index = 0
        self.publisher = self.create_publisher(String, output_topic, 10)
        self.create_timer(interval, self._on_timer)
        self.get_logger().info(
            f'Publishing {len(self._commands)} demo command(s) to {output_topic}',
        )

    def _on_timer(self) -> None:
        """Publish the next command in the script, looping unless disabled."""
        if self._index >= len(self._commands):
            if not self._loop:
                return
            self._index = 0
        msg = String()
        msg.data = self._commands[self._index]
        self.publisher.publish(msg)
        self._index += 1


def main(args=None) -> None:
    """Run the scripted natural-language command publisher."""
    rclpy.init(args=args)
    node = NlDemoPublisher()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
