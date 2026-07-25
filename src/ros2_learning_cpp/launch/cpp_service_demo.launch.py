"""C++ 版のサービスサーバーとクライアントを同時に起動するランチファイル."""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """minimal_service_server と minimal_service_client (C++) を起動する."""
    return LaunchDescription([
        Node(
            package='ros2_learning_cpp',
            executable='minimal_service_server',
            name='minimal_service_server',
            output='screen',
        ),
        Node(
            package='ros2_learning_cpp',
            executable='minimal_service_client',
            name='minimal_service_client',
            output='screen',
        ),
    ])
