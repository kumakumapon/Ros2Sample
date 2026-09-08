"""Publish geofence, waypoint and live formation markers for RViz or Foxglove."""

from functools import partial

from drone_sim.marker_geometry import box_edges
from drone_sim.waypoint_utils import parse_waypoints
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray


class VisualizationMarkers(Node):
    """Display reference geometry and live odometry without commanding a robot."""

    def __init__(self):
        """Declare a common fixed frame, bounds, waypoint triples and odom topics."""
        super().__init__('visualization_markers')
        self.declare_parameter('frame_id', 'odom')
        self.declare_parameter('bounds_min', [-2.0, -2.0, 0.0])
        self.declare_parameter('bounds_max', [8.0, 8.0, 4.0])
        self.declare_parameter(
            'waypoints', [0.0, 0.0, 2.0, 4.0, 0.0, 2.0,
                          4.0, 4.0, 2.0, 0.0, 4.0, 2.0])
        self.declare_parameter(
            'odom_topics', ['leader/odom', 'follower_1/odom', 'follower_2/odom'])
        self.frame = str(self.get_parameter('frame_id').value)
        self.lower = list(self.get_parameter('bounds_min').value)
        self.upper = list(self.get_parameter('bounds_max').value)
        if len(self.lower) != 3 or len(self.upper) != 3:
            raise ValueError('bounds_min and bounds_max require three coordinates')
        if not all(a < b for a, b in zip(self.lower, self.upper)):
            raise ValueError('Each minimum bound must be less than its maximum')
        self.waypoints = parse_waypoints(self.get_parameter('waypoints').value)
        self.publisher = self.create_publisher(MarkerArray, 'visualization_markers', 10)
        for index, topic in enumerate(self.get_parameter('odom_topics').value):
            self.create_subscription(Odometry, topic, partial(self._on_odom, index), 10)
        self.create_timer(0.5, self._publish_reference)

    def _marker(self, namespace, marker_id, marker_type):
        marker = Marker()
        marker.header.frame_id = self.frame
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = namespace
        marker.id = marker_id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.color.a = 1.0
        marker.lifetime.sec = 2
        return marker

    def _publish_reference(self):
        fence = self._marker('geofence', 0, Marker.LINE_LIST)
        fence.scale.x = 0.04
        fence.color.r = 1.0
        fence.color.g = 0.6
        fence.points = [Point(x=x, y=y, z=z)
                        for edge in box_edges(self.lower, self.upper) for x, y, z in edge]
        path = self._marker('waypoints', 0, Marker.LINE_STRIP)
        path.scale.x = 0.06
        path.color.g = 1.0
        path.points = [Point(x=x, y=y, z=z) for x, y, z in self.waypoints]
        self.publisher.publish(MarkerArray(markers=[fence, path]))

    def _on_odom(self, index, msg):
        marker = self._marker('formation', index, Marker.SPHERE)
        # Retain the odometry frame; a viewer must have TF to its fixed frame.
        marker.header = msg.header
        marker.pose = msg.pose.pose
        marker.scale.x = marker.scale.y = marker.scale.z = 0.3
        marker.color.r = 0.2
        marker.color.g = 0.4 + 0.2 * (index % 3)
        marker.color.b = 1.0
        self.publisher.publish(MarkerArray(markers=[marker]))


def main(args=None):
    """Run the visualization-only publisher."""
    rclpy.init(args=args)
    node = VisualizationMarkers()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
