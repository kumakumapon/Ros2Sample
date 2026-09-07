# manipulator_sim

[日本語](README.md) | [English](README.en.md)

A two-link planar manipulator for forward/inverse kinematics and trajectory playback.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to manipulator_sim
source install/setup.bash
ros2 launch manipulator_sim planar_reach_demo.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `manipulator_simulator` | Integrate joint targets and publish joint states, tool pose and TF. |
| `target_commander` | Cycle through configured reachable planar targets. |
| `ik_target_commander` | Convert Cartesian target_pose into joint_target. |
| `moveit_trajectory_bridge` | Sample incoming planned joint trajectories for the simulator. |

Individual nodes use `ros2 run manipulator_sim <executable>`.

## Interfaces and parameters

joint_states and joint_target (sensor_msgs/JointState), tool_pose and target_pose (geometry_msgs/PoseStamped). planned_joint_trajectory accepts trajectory_msgs/JointTrajectory.

link_lengths sets the two link lengths. elbow_up selects the IK branch; clamp_to_workspace controls unreachable targets. The MoveIt bridge consumes an external planned trajectory; it does not start MoveIt or generate a motion plan.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch manipulator_sim ik_demo.launch.py`
- `ros2 launch manipulator_sim moveit_bridge_demo.launch.py`
- `ros2 launch manipulator_sim planar_reach_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select manipulator_sim
colcon test-result --verbose
```


See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
