# ground_robot_sim

[日本語](README.md) | [English](README.en.md)

A lightweight differential-drive simulator with synthetic LiDAR, PID waypoint tracking and namespace support.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to ground_robot_sim
source install/setup.bash
ros2 launch ground_robot_sim waypoint_follower.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `diagnostics_publisher` | Publish diagnostic_msgs/DiagnosticArray health summaries. |
| `diff_drive_patrol` | Issue an open-loop square patrol. |
| `ground_robot_node` | Integrate differential-drive motion and publish odometry/LiDAR. |
| `lidar_obstacle_avoid` | Steer around nearby obstacles. |
| `lidar_obstacle_stop` | Stop when an obstacle is too close. |
| `navigate_waypoints_server` | Navigate waypoint action goals using robot feedback. |
| `teleop_keyboard` | Publish velocity commands from an interactive terminal. |
| `waypoint_follower` | Track XY waypoints with closed-loop PID. |

Individual nodes use `ros2 run ground_robot_sim <executable>`.

## Interfaces and parameters

odom (nav_msgs/Odometry), scan (sensor_msgs/LaserScan), cmd_vel (geometry_msgs/Twist). emergency_stop and reset_emergency are std_srvs/Trigger services.

publish_rate=30.0 and scan_rate=10.0 configure ground_robot_node. max_linear_speed=0.8 limits forward speed. Stop latches until reset_emergency; further commands cannot override it.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch ground_robot_sim diff_drive_patrol.launch.py`
- `ros2 launch ground_robot_sim gazebo.launch.py`
- `ros2 launch ground_robot_sim lidar_obstacle_avoid.launch.py`
- `ros2 launch ground_robot_sim lidar_obstacle_stop.launch.py`
- `ros2 launch ground_robot_sim multi_robot.launch.py`
- `ros2 launch ground_robot_sim navigate_waypoints.launch.py`
- `ros2 launch ground_robot_sim noisy_sensors_demo.launch.py`
- `ros2 launch ground_robot_sim waypoint_follower.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select ground_robot_sim
colcon test-result --verbose
```

After building the full workspace, run `bash scripts/test-integration.sh` for the four real-node integration scenarios.

Inspect `ros2 topic echo /scan` and `ros2 topic echo /odom`. Call `ros2 service call /emergency_stop std_srvs/srv/Trigger "{}"` to latch a stop, then use the same type with `/reset_emergency` to release it. For keyboard control, run ground_robot_node and teleop_keyboard in separate terminals without another controller.

See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
