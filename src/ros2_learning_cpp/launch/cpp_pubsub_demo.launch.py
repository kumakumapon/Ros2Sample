"""C++ 版のパブリッシャーとサブスクライバーを同時に起動するランチファイル."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """minimal_publisher と minimal_subscriber (C++) を起動する."""
    return LaunchDescription([
        Node(
            package='ros2_learning_cpp',
            executable='minimal_publisher',
            name='minimal_publisher',
            output='screen',
        ),
        Node(
            package='ros2_learning_cpp',
            executable='minimal_subscriber',
            name='minimal_subscriber',
            output='screen',
        ),
    ])
