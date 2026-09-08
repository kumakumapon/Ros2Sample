# drone_sim

[日本語](README.md) | [English](README.en.md)

A kinematic 3D quadrotor simulator with missions, formation flight, wind and sensor noise.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to drone_sim
source install/setup.bash
ros2 launch drone_sim single_quad_waypoint.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `altitude_hold` | Hold target altitude with PID. |
| `battery_monitor` | Estimate battery consumption from activity. |
| `collision_avoidance` | Compute repulsive collision-avoidance corrections. |
| `diagnostics_publisher` | Publish diagnostic_msgs/DiagnosticArray health summaries. |
| `emergency_land` | Command descent in response to a low battery. |
| `formation_controller` | Follow leader odometry with an offset. |
| `geofence_monitor` | Detect boundary breaches and publish corrective setpoints. |
| `mission_behavior_tree` | Execute a behavior-tree mission with trace output. |
| `mission_state_machine` | Execute a finite-state takeoff/cruise/return/land mission. |
| `sim_drone` | Simulate bounded 3D velocities and position setpoints. |
| `telemetry_logger` | Write flight telemetry to CSV. |
| `waypoint_commander` | Cycle through XYZ position setpoints. |
| `visualization_markers` | Display reference bounds, waypoints and live formation poses. |
| `wind_disturbance` | Publish simulated wind disturbance. |

Individual nodes use `ros2 run drone_sim <executable>`.

## Interfaces and parameters

odom (nav_msgs/Odometry), pose and setpoint_pose (geometry_msgs/PoseStamped), imu (sensor_msgs/Imu), cmd_vel (geometry_msgs/Twist).

sim_drone publishes at publish_rate_hz=50.0; cmd_timeout_sec=0.6 expires stale commands. waypoint_commander uses flat XYZ waypoints and tolerance_m=0.25. Use one motion controller at a time.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch drone_sim altitude_hold.launch.py`
- `ros2 launch drone_sim battery_demo.launch.py`
- `ros2 launch drone_sim collision_avoidance_demo.launch.py`
- `ros2 launch drone_sim formation_demo.launch.py`
- `ros2 launch drone_sim foxglove_demo.launch.py`
- `ros2 launch drone_sim mission_bt_demo.launch.py`
- `ros2 launch drone_sim mission_demo.launch.py`
- `ros2 launch drone_sim noisy_sensors_demo.launch.py`
- `ros2 launch drone_sim single_quad_waypoint.launch.py`
- `ros2 launch drone_sim swarm.launch.py`
- `ros2 launch drone_sim wind_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select drone_sim
colcon test-result --verbose
```

After building the full workspace, run `bash scripts/test-integration.sh` for the four real-node integration scenarios.

Inspect `ros2 topic echo /pose` and `ros2 topic hz /imu`. The Foxglove demo launches leader/follower motion plus visualization_markers. Markers are display-only: their bounds do not enforce a geofence. Match them to geofence_monitor parameters when using that controller.

See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
