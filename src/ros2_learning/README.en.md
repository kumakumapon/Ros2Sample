# ros2_learning

[日本語](README.md) | [English](README.en.md)

Small Python/rclpy examples for chapters 01–06, paired with the C++ package.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to ros2_learning
source install/setup.bash
ros2 launch ros2_learning pubsub_demo.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `minimal_publisher` | Publish numbered String messages on chatter. |
| `minimal_subscriber` | Log incoming chatter messages. |
| `minimal_service_server` | Provide the SetBool set_flag service. |
| `minimal_service_client` | Toggle set_flag asynchronously every two seconds. |
| `minimal_action_server` | Accept NavigateWaypoints goals and publish feedback/results. |
| `minimal_action_client` | Send waypoint goals and display progress. |
| `parameter_demo` | Validate parameter updates and publish robot_info. |
| `tf_broadcaster_demo` | Broadcast dynamic and static transforms. |
| `tf_listener_demo` | Look up the configured TF transform. |
| `lifecycle_demo` | Publish only while active. |

Individual nodes use `ros2 run ros2_learning <executable>`.

## Interfaces and parameters

chatter and robot_info (std_msgs/String), set_flag (std_srvs/SetBool), navigate_waypoints (sample_interfaces/NavigateWaypoints), /tf and /tf_static, lifecycle_output (std_msgs/String).

minimal_publisher: publish_rate_hz=1.0. minimal_action_server: speed=0.5, control_rate_hz=10.0. parameter_demo: robot_name=learning_bot, max_speed=1.0, update_rate_hz=2.0, enable_logging=true. TF broadcaster: parent_frame=world, child_frame=learning_robot, orbit_radius=2.0, orbit_speed=0.5. TF listener: target_frame=sensor_frame, source_frame=world. lifecycle_demo: publish_rate_hz=1.0, message_prefix controls output text.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch ros2_learning action_demo.launch.py`
- `ros2 launch ros2_learning lifecycle_demo.launch.py`
- `ros2 launch ros2_learning parameter_demo.launch.py`
- `ros2 launch ros2_learning pubsub_demo.launch.py`
- `ros2 launch ros2_learning service_demo.launch.py`
- `ros2 launch ros2_learning tf_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select ros2_learning
colcon test-result --verbose
```

After building the full workspace, run `bash scripts/test-integration.sh` for the four real-node integration scenarios.

The service is SetBool, and the action is NavigateWaypoints. Use `ros2 service call /set_flag std_srvs/srv/SetBool "{data: true}"`. Start lifecycle_demo, then run `ros2 lifecycle set /lifecycle_demo configure` and `ros2 lifecycle set /lifecycle_demo activate`; only then does lifecycle_output publish. For TF run `ros2 run tf2_ros tf2_echo world sensor_frame`. See the English chapters below for complete action and parameter exercises.

See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
