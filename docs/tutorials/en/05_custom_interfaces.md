# 05. Custom messages, services and actions

[日本語](../05_custom_interfaces.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

The sample_interfaces package defines contracts shared by Python and C++ nodes. A .msg is a record; a .srv separates request and response with ---; an .action has goal, result and feedback sections separated by two --- lines.

```bash
colcon build --symlink-install --packages-up-to sample_interfaces ros2_learning_cpp
source install/setup.bash
ros2 interface show sample_interfaces/msg/RobotStatus
ros2 interface show sample_interfaces/srv/GetRobotStatus
ros2 interface show sample_interfaces/action/NavigateWaypoints
```

RobotStatus contains a header, robot_name, state, battery_percentage, position and linear_velocity. GetRobotStatus has an empty request and returns status, success and message. NavigateWaypoints accepts PoseStamped waypoints, loop and tolerance_m; it returns success, waypoints_completed and message, and publishes current_index, total_waypoints, distance_to_current and current_position as feedback.

```bash
ros2 launch ros2_learning_cpp cpp_custom_interface_demo.launch.py
# Another terminal
ros2 topic echo /robot_status
ros2 service call /get_robot_status sample_interfaces/srv/GetRobotStatus '{}'
```

Expect a typed status message and a successful service response. Compare these with the same contracts in the ground robot simulator.

Read sample_interfaces/CMakeLists.txt for rosidl_generate_interfaces and the declared dependencies. package.xml declares rosidl generators/runtime and membership in rosidl_interface_packages. Keep interface generation separate from implementation packages so several nodes can share it without depending on each other's code.

Exercise: on a development branch, add a field to a message, rebuild both interfaces and consumers, and source the new overlay in every terminal. A stale generated Python module or C++ build can make two apparently identical topic names use incompatible contracts. Avoid changing units silently; document units and valid ranges in the interface comments.
