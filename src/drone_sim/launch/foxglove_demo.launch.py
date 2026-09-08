"""Launch the formation demo and reference markers; start the bridge separately."""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    """Use the same four waypoint triples as formation_demo.launch.py."""
    share = get_package_share_directory('drone_sim')
    return LaunchDescription([
        IncludeLaunchDescription(PythonLaunchDescriptionSource(
            share + '/launch/formation_demo.launch.py')),
        Node(package='drone_sim', executable='visualization_markers', output='screen'),
    ])
