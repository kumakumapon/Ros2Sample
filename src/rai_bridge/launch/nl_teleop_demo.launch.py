"""Launch the ground robot plus a scripted natural-language command bridge demo."""

from os.path import join

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    """Return the ground robot, NL command bridge, and scripted demo publisher."""
    share_dir = get_package_share_directory('rai_bridge')
    config_file = join(share_dir, 'config', 'nl_command_demo.yaml')

    return LaunchDescription([
        Node(
            package='ground_robot_sim',
            executable='ground_robot_node',
            name='ground_robot',
            output='screen',
        ),
        Node(
            package='rai_bridge',
            executable='nl_command_node',
            name='nl_command_node',
            output='screen',
            parameters=[config_file],
        ),
        Node(
            package='rai_bridge',
            executable='nl_demo_publisher',
            name='nl_demo_publisher',
            output='screen',
            parameters=[config_file],
        ),
    ])
