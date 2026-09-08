# ros2_learning_cpp

[日本語](README.md) | [English](README.en.md)

C++/rclcpp counterparts to the Python pub/sub, service, action and custom-interface examples.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to ros2_learning_cpp
source install/setup.bash
ros2 launch ros2_learning_cpp cpp_pubsub_demo.launch.py
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
| `custom_interface_demo` | Publish RobotStatus and serve GetRobotStatus. |

Individual nodes use `ros2 run ros2_learning_cpp <executable>`.

## Interfaces and parameters

chatter (std_msgs/String), set_flag (std_srvs/SetBool), navigate_waypoints (sample_interfaces/NavigateWaypoints), robot_status (sample_interfaces/RobotStatus), get_robot_status (sample_interfaces/GetRobotStatus).

custom_interface_demo uses robot_name=cpp_robot and publish_rate_hz=2.0. This package uses ament_cmake and C++17; Python examples use ament_python. rclpy.create_publisher maps to create_publisher<T>(); rclpy.spin maps to rclcpp::spin; ActionServer maps to rclcpp_action::create_server<T>().

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch ros2_learning_cpp cpp_action_demo.launch.py`
- `ros2 launch ros2_learning_cpp cpp_custom_interface_demo.launch.py`
- `ros2 launch ros2_learning_cpp cpp_pubsub_demo.launch.py`
- `ros2 launch ros2_learning_cpp cpp_service_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select ros2_learning_cpp
colcon test-result --verbose
```


See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
