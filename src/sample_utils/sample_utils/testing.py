"""Optional ROS integration-test helpers; runtime math has no ROS dependency."""

import time
import unittest

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.qos import qos_profile_sensor_data


class RosTestCase(unittest.TestCase):
    """Own a test node and use wall-clock deadlines even with stopped ROS time."""

    namespace = ''

    def setUp(self):
        """Initialize an isolated ROS context and node for each scenario."""
        self.context = rclpy.context.Context()
        rclpy.init(context=self.context)
        self.addCleanup(self.context.shutdown)
        self.node = rclpy.create_node(
            'integration_client', namespace=self.namespace, context=self.context)
        self.addCleanup(self.node.destroy_node)
        self.executor = SingleThreadedExecutor(context=self.context)
        self.addCleanup(self.executor.shutdown)
        self.executor.add_node(self.node)

    def wait_until(self, predicate, timeout=10.0):
        """Spin until the condition holds, failing on a bounded wall-clock timeout."""
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.05)
        self.assertTrue(predicate(), 'Condition not met before wall-clock timeout')

    def spin_for(self, seconds):
        """Process callbacks for a fixed wall-clock observation window."""
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.executor.spin_once(timeout_sec=0.05)

    def receive(self, message_type, topic):
        """Collect messages with sensor QoS compatible with both reliability modes."""
        messages = []
        self.node.create_subscription(
            message_type, topic, messages.append, qos_profile_sensor_data)
        return messages

    def result(self, future, timeout=10.0):
        """Wait for a future and propagate its exception or return its result."""
        self.wait_until(future.done, timeout)
        return future.result()
