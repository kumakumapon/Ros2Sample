"""カスタム msg / srv を C++ から使うデモを起動するランチファイル."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """custom_interface_demo (C++) をパラメータ付きで起動する."""
    return LaunchDescription([
        Node(
            package='ros2_learning_cpp',
            executable='custom_interface_demo',
            name='custom_interface_demo',
            output='screen',
            parameters=[{
                'robot_name': 'cpp_robot',
                'publish_rate_hz': 2.0,
            }],
        ),
    ])
