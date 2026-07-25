"""C++ 版のアクションサーバーとクライアントを同時に起動するランチファイル."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """minimal_action_server と minimal_action_client (C++) を起動する."""
    return LaunchDescription([
        Node(
            package='ros2_learning_cpp',
            executable='minimal_action_server',
            name='minimal_action_server',
            output='screen',
        ),
        Node(
            package='ros2_learning_cpp',
            executable='minimal_action_client',
            name='minimal_action_client',
            output='screen',
        ),
    ])
