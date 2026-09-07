# 00. Learning path

[日本語](../00_learning_path.md) | [Repository overview](../../../README.en.md)

This workspace teaches ROS 2 through small Python/C++ nodes, then ground robots, drones,
manipulators and sensor fusion. Use the English guides for chapters 01–06 first; advanced
chapters currently link to Japanese originals. Japanese remains the specification baseline.

## Prepare the workspace

Install ROS 2 for your Ubuntu release first. CI uses Ubuntu 24.04 with Jazzy.
From a clone of this repository:

```bash
source /opt/ros/jazzy/setup.bash
bash scripts/rosdep-install.sh jazzy
bash scripts/build.sh
source install/setup.bash
ros2 launch ros2_learning pubsub_demo.launch.py
```

Run a second terminal with the same ROS environment and overlay. Choose one demo at a time.
The [development guide](../../development.md) covers Docker and GUI forwarding.

## Choose a route

Start with topics → services/actions → launch/parameters → TF → custom interfaces → lifecycle/QoS.
For ground navigation continue through 07–10; for mission logic use 11; for visualization and
debugging use 12–13. Read source with 14, then combine concepts in 15. Chapters 17–24 cover
optional integrations and tooling. No physical robot is required for the lightweight demos.

| Chapter | Topic | Language |
| --- | --- | --- |
| [00](00_learning_path.md) | Learning path | English |
| [01](01_publisher_subscriber.md) | Publisher and subscriber | English |
| [02](02_service_action.md) | Services and actions | English |
| [03](03_launch_params.md) | Launch and parameters | English |
| [04](04_tf_transforms.md) | TF2 transforms | English |
| [05](05_custom_interfaces.md) | Custom interfaces | English |
| [06](06_lifecycle_qos.md) | Lifecycle and QoS | English |
| [07](../07_nav2_overview.md) | Navigation2 architecture | Japanese |
| [08](../08_costmap_and_map.md) | Maps and costmaps | Japanese |
| [09](../09_path_planning.md) | Path planning | Japanese |
| [10](../10_nav2_controller.md) | Path tracking | Japanese |
| [11](../11_behavior_tree.md) | Behavior trees | Japanese |
| [12](../12_rviz_visualization.md) | RViz visualization | Japanese |
| [13](../13_debugging_ros2_systems.md) | Debugging ROS systems | Japanese |
| [14](../14_reading_existing_packages.md) | Reading packages | Japanese |
| [15](../15_mini_projects.md) | Mini projects | Japanese |
| [16](../16_troubleshooting.md) | Troubleshooting | Japanese |
| [17](../17_gazebo_integration.md) | Gazebo integration | Japanese |
| [18](../18_testing_ros2.md) | Testing ROS 2 | Japanese |
| [19](../19_rosbag2.md) | rosbag2 recording | Japanese |
| [20](../20_composition.md) | Composition | Japanese |
| [21](../21_multi_robot_communication.md) | Multi-robot communication | Japanese |
| [22](../22_moveit2_manipulator_planning.md) | MoveIt2 planning | Japanese |
| [23](../23_openusd_recording.md) | OpenUSD recording | Japanese |
| [24](../24_foxglove_visualization.md) | Foxglove and markers | Japanese |

## Check your understanding

After chapter 06, explain when to use a topic, service or action, diagnose a QoS mismatch,
inspect a frame transform, and activate a lifecycle node. Then run a simulation and identify
its sensor, controller and actuator interfaces before modifying code.
