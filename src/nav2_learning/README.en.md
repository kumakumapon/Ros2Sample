# nav2_learning

[日本語](README.md) | [English](README.en.md)

Learn occupancy grids, A* planning, path smoothing, Pure Pursuit and log-odds mapping.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to nav2_learning
source install/setup.bash
ros2 launch nav2_learning simple_planning_demo.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `simple_map_publisher` | Publish a synthetic occupancy grid. |
| `simple_path_planner` | Plan and replan paths with A*. |
| `simple_path_follower` | Track a path with Pure Pursuit. |
| `nav2_waypoint_client` | Send NavigateToPose goals to an external Nav2 stack. |
| `costmap_monitor` | Inspect occupancy/costmap data. |
| `simple_occupancy_mapper` | Update a log-odds map from scan and odometry. |

Individual nodes use `ros2 run nav2_learning <executable>`.

## Interfaces and parameters

map (nav_msgs/OccupancyGrid) is shared globally. plan and plan_raw (nav_msgs/Path), odom and cmd_vel are robot-relative names. clicked_point adds obstacles.

resolution sets meters per cell and must be positive. shortcut_enabled, smoothing_window and replan_on_map_change control path post-processing. Mapping uses hit_log_odds and miss_log_odds. nav2_waypoint_client requires a separately running Nav2 NavigateToPose server; the pure planning demo does not.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch nav2_learning nav2_waypoint_demo.launch.py`
- `ros2 launch nav2_learning occupancy_mapping_demo.launch.py`
- `ros2 launch nav2_learning simple_map_demo.launch.py`
- `ros2 launch nav2_learning simple_planning_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select nav2_learning
colcon test-result --verbose
```


See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
