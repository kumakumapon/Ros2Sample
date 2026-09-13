"""Launch the RAI agent node for TurtleBot3 natural-language control."""

from os.path import join

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Return the RAI agent node configured for TurtleBot3."""
    share_dir = get_package_share_directory('rai_bridge')
    config_file = join(share_dir, 'config', 'tb3_rai_agent.yaml')

    ns_arg = DeclareLaunchArgument(
        'robot_namespace',
        default_value='',
        description='Robot namespace — empty for a single robot, '
                    '/tb3_0 etc. for multi-robot setups.',
    )

    return LaunchDescription([
        ns_arg,
        Node(
            package='rai_bridge',
            executable='rai_agent_node',
            name='rai_agent_node',
            namespace=LaunchConfiguration('robot_namespace'),
            output='screen',
            parameters=[config_file],
        ),
    ])
