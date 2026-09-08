# Ros2Sample

[![CI](https://github.com/kumakumapon/Ros2Sample/actions/workflows/ci.yml/badge.svg)](https://github.com/kumakumapon/Ros2Sample/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[日本語版 README はこちら (Japanese README)](README.md)

> [!WARNING]
> **This repository is under active development and verification.** Samples and documentation are experimental and provided as-is without guarantee for every platform/configuration. If you encounter any issues, please report them via GitHub Issues.

**Ros2Sample** is a lightweight ROS 2 learning and verification workspace for ground robots, quadrotors, planar manipulators, and sensor fusion.

The primary language of this repository is **Japanese**, but this English document provides a complete guide for international developers to acquire dependencies, build, run demos, and run CI tests on Ubuntu 20.04 / 24.04 / 26.04 with ROS 2 Foxy / Jazzy / Lyrical / Rolling.

![Ros2Sample Overview Concept](docs/assets/ros2-sample-overview.png)

---

## Target Environments

| OS | ROS 2 | Purpose | Notes |
| --- | --- | --- | --- |
| Ubuntu 26.04 LTS | Lyrical Luth | Recommended | May 2026 LTS release. Supported until May 2031. |
| Ubuntu 24.04 LTS | Jazzy Jalisco | Stable / CI Verified | Currently verified in GitHub Actions CI. Noble is supported until 2029. |
| Ubuntu 20.04 LTS | Foxy Fitzroy | Compatibility Target | EOL distribution maintained for legacy compatibility. Python pure-function samples build and run. |
| Ubuntu 24.04 LTS | Kilted Kaiju | Development Candidate | Verify package compatibility as needed. |
| Ubuntu 24.04 / 26.04 | Rolling Ridley | Rolling API Verification | API changes occur frequently; check changelogs if CI fails. |

---

## Repository Structure

```text
.
├── .github/workflows/ci.yml   # GitHub Actions CI workflow (Ubuntu 24.04 / Jazzy)
├── docker/                    # Docker development container setups
├── docs/                      # Specification and tutorial documentation
│   ├── tutorials/             # Step-by-step learning guides (00 to 23)
│   ├── simulation_spec.md     # User-facing simulation and demo specifications
│   └── implementation_spec.md # Technical implementation specifications
├── scripts/                   # Helper scripts for build, lint, rosdep, consistency
├── ros2.repos                 # vcs import template for external dependencies
└── src/                       # ROS 2 packages
```

---

## Packages Overview

The workspace contains 10 ROS 2 packages:

| Package | Description | Key Executables |
| --- | --- | --- |
| `ground_robot_sim` | 2D differential-drive ground robot simulation, synthetic LiDAR obstacle stop/avoidance, closed-loop PID waypoint follower, Action server, teleoperation, emergency stop service, and multi-robot namespaces. | `ground_robot_node`, `diff_drive_patrol`, `lidar_obstacle_stop`, `lidar_obstacle_avoid`, `waypoint_follower`, `navigate_waypoints_server`, `teleop_keyboard`, `diagnostics_publisher` |
| `drone_sim` | 3D kinematic quadrotor simulation, 3D waypoint follower, PID altitude hold, wind disturbance, geofence monitor, leader-follower formation, collision avoidance, telemetry logging, battery consumption model, emergency landing, and FSM / Behavior Tree mission nodes. | `sim_drone`, `altitude_hold`, `waypoint_commander`, `wind_disturbance`, `geofence_monitor`, `formation_controller`, `collision_avoidance`, `telemetry_logger`, `battery_monitor`, `emergency_land`, `mission_state_machine`, `mission_behavior_tree`, `diagnostics_publisher`, `visualization_markers` |
| `manipulator_sim` | 2-DOF planar manipulator simulation, JointState / TF / tool pose tracking, forward & inverse kinematics (IK), and MoveIt2 planned trajectory bridge. | `manipulator_simulator`, `target_commander`, `ik_target_commander`, `moveit_trajectory_bridge` |
| `sensor_fusion_sim` | Sensor fusion with noisy GPS, IMU, and wheel odometry using a complementary filter and Extended Kalman Filter (EKF). Features lifecycle nodes, QoS profiles, callback groups, dynamic parameter tuning, and pure math/transform utilities. | `noisy_sensor_node`, `complementary_filter_node`, `ekf_node`, `lifecycle_data_recorder` |
| `nav2_learning` | Nav2 concepts implemented from scratch without Nav2 dependencies: OccupancyGrid map publishing, A* path planning with line-of-sight shortcutting & smoothing, Pure Pursuit path tracking, dynamic obstacle replanning, and online log-odds occupancy mapping (SLAM fundamentals). | `simple_map_publisher`, `simple_path_planner`, `simple_path_follower`, `nav2_waypoint_client`, `costmap_monitor`, `simple_occupancy_mapper` |
| `openusd_bridge` | Records ROS 2 `Odometry` messages as time-sampled OpenUSD animation stages (`.usd`, `.usda`, `.usdc`) for scene visualization and exchange. | `odom_to_usd` |
| `ros2_learning` | Progressive ROS 2 tutorial package (Python/rclpy) covering Pub/Sub, Service, Action, Parameters, TF2, and Lifecycle nodes. | `minimal_publisher`, `minimal_subscriber`, `minimal_service_server`, `minimal_service_client`, `minimal_action_server`, `minimal_action_client`, `parameter_demo`, `tf_broadcaster_demo`, `tf_listener_demo`, `lifecycle_demo` |
| `ros2_learning_cpp` | C++ (rclcpp) counterpart to `ros2_learning`, demonstrating the same patterns side by side with a rclpy ↔ rclcpp mapping guide. | `minimal_publisher`, `minimal_subscriber`, `minimal_service_server`, `minimal_service_client`, `minimal_action_server`, `minimal_action_client`, `custom_interface_demo` |
| `sample_utils` | Shared PID, Gaussian noise and angle helpers | Library (no executables) |
| `sample_interfaces` | Custom message, service, and action definitions (`RobotStatus.msg`, `GetRobotStatus.srv`, `NavigateWaypoints.action`). | _(Interface-only library package)_ |

---

## Setup and Installation

### 1. Prerequisites

On Ubuntu (e.g. Ubuntu 24.04 / 26.04):

```bash
sudo apt update
sudo apt install -y \
  curl \
  git \
  python3-colcon-common-extensions \
  python3-pip \
  python3-rosdep \
  python3-vcstool
```

### 2. Workspace Setup

```bash
# Clone the repository
git clone https://github.com/kumakumapon/Ros2Sample.git
cd Ros2Sample

# Source your ROS 2 distribution (e.g. jazzy or lyrical)
source /opt/ros/jazzy/setup.bash

# Initialize and update rosdep
sudo rosdep init || true
rosdep update

# Install workspace dependencies
./scripts/rosdep-install.sh jazzy
```

### 3. Build

```bash
./scripts/build.sh
source install/setup.bash
```

### 4. Lint and Test

```bash
./scripts/lint.sh
colcon test --event-handlers console_direct+
colcon test-result --verbose
```

---

## Running Simulation Demos

After sourcing `install/setup.bash`, launch any of the integrated demo launch files:

### Ground Robot Demos (`ground_robot_sim`)

```bash
# Open-loop square patrol
ros2 launch ground_robot_sim diff_drive_patrol.launch.py

# Synthetic LiDAR obstacle stop demo
ros2 launch ground_robot_sim lidar_obstacle_stop.launch.py

# Closed-loop PID waypoint following
ros2 launch ground_robot_sim waypoint_follower.launch.py

# Action-based waypoint navigation server
ros2 launch ground_robot_sim navigate_waypoints.launch.py

# Obstacle avoidance demo (steering away from nearest obstacle)
ros2 launch ground_robot_sim lidar_obstacle_avoid.launch.py

# Noisy sensors vs ground truth demo
ros2 launch ground_robot_sim noisy_sensors_demo.launch.py

# 3 robots in separate namespaces (/robot1, /robot2, /robot3)
ros2 launch ground_robot_sim multi_robot.launch.py

# Optional GZ Sim integration demo
ros2 launch ground_robot_sim gazebo.launch.py use_gui:=false
```

### Drone Demos (`drone_sim`)

```bash
# 3D waypoint following
ros2 launch drone_sim single_quad_waypoint.launch.py

# PID altitude hold
ros2 launch drone_sim altitude_hold.launch.py target_altitude_m:=2.0

# Battery consumption & automatic emergency landing
ros2 launch drone_sim battery_demo.launch.py

# Wind disturbance, geofence monitor & telemetry logging
ros2 launch drone_sim wind_demo.launch.py

# Leader-follower formation flight
ros2 launch drone_sim formation_demo.launch.py

# Artificial potential field collision avoidance
ros2 launch drone_sim collision_avoidance_demo.launch.py

# Finite State Machine (FSM) mission demo (Takeoff -> Cruise -> RTL -> Land)
ros2 launch drone_sim mission_demo.launch.py

# Behavior Tree (BT) mission demo with live /bt_trace logging
ros2 launch drone_sim mission_bt_demo.launch.py

# Multi-drone swarm in separate namespaces
ros2 launch drone_sim swarm.launch.py drone_count:=5
```

### Manipulator Demos (`manipulator_sim`)

```bash
# Planar reach demo (forward kinematics & joint state tracking)
ros2 launch manipulator_sim planar_reach_demo.launch.py

# Inverse kinematics target follower demo
ros2 launch manipulator_sim ik_demo.launch.py

# MoveIt2 planned trajectory bridge demo
ros2 launch manipulator_sim moveit_bridge_demo.launch.py
```

### Sensor Fusion Demos (`sensor_fusion_sim`)

```bash
# Runs noisy sensors, complementary filter, EKF node, and lifecycle recorder
ros2 launch sensor_fusion_sim sensor_fusion_demo.launch.py
```

Compare estimated states against ground truth:

```bash
ros2 topic echo /ground_truth
ros2 topic echo /fused_odom
ros2 topic echo /ekf_odom
ros2 topic echo /ekf_diagnostics
```

Dynamic parameter reconfiguration:

```bash
ros2 param set /complementary_filter gps_alpha 0.3
ros2 param set /ekf_node gps_pos_stddev 0.2
```

### Navigation2 Concepts Demos (`nav2_learning`)

```bash
# OccupancyGrid map publisher demo
ros2 launch nav2_learning simple_map_demo.launch.py

# A* path planning with Pure Pursuit path following & dynamic replanning
ros2 launch nav2_learning simple_planning_demo.launch.py

# Online SLAM log-odds occupancy grid mapping demo
ros2 launch nav2_learning occupancy_mapping_demo.launch.py
```

### OpenUSD Stage Recording (`openusd_bridge`)

```bash
# Records ground robot odometry into /tmp/ros2_openusd/robot_motion.usda (requires pxr)
ros2 launch openusd_bridge ground_robot_openusd.launch.py
```

---

## Learning Tutorials

Chapters 00–06 are available in English; later links lead to Japanese originals. Step-by-step learning tutorials are located in [`docs/tutorials/`](docs/tutorials/):

| Tutorial | Estimated Time | Topic |
| --- | --- | --- |
| [`00_learning_path.md`](docs/tutorials/en/00_learning_path.md) | 5 min | Learning path overview & environment setup |
| [`01_publisher_subscriber.md`](docs/tutorials/en/01_publisher_subscriber.md) | 30 min | Topic communication basics |
| [`02_service_action.md`](docs/tutorials/en/02_service_action.md) | 45 min | Services & Actions |
| [`03_launch_params.md`](docs/tutorials/en/03_launch_params.md) | 30 min | Launch files and parameters |
| [`04_tf_transforms.md`](docs/tutorials/en/04_tf_transforms.md) | 45 min | TF2 and coordinate transformations |
| [`05_custom_interfaces.md`](docs/tutorials/en/05_custom_interfaces.md) | 30 min | Custom message, service, and action definitions |
| [`06_lifecycle_qos.md`](docs/tutorials/en/06_lifecycle_qos.md) | 45 min | Lifecycle nodes & QoS profiles |
| [`07_nav2_overview.md`](docs/tutorials/07_nav2_overview.md) | 45 min | Navigation2 architecture overview |
| [`08_costmap_and_map.md`](docs/tutorials/08_costmap_and_map.md) | 45 min | Maps, costmaps, and inflation layers |
| [`09_path_planning.md`](docs/tutorials/09_path_planning.md) | 60 min | A* path planning, shortcutting, and dynamic replanning |
| [`10_nav2_controller.md`](docs/tutorials/10_nav2_controller.md) | 45 min | Pure Pursuit path tracking controller |
| [`11_behavior_tree.md`](docs/tutorials/11_behavior_tree.md) | 45 min | Behavior Trees vs Finite State Machines |
| [`12_rviz_visualization.md`](docs/tutorials/12_rviz_visualization.md) | 45 min | Visualizing TF, sensors, maps, and paths in RViz2 |
| [`13_debugging_ros2_systems.md`](docs/tutorials/13_debugging_ros2_systems.md) | 45 min | CLI debugging tools and `rqt_graph` |
| [`14_reading_existing_packages.md`](docs/tutorials/14_reading_existing_packages.md) | 60 min | Reading and analyzing existing ROS 2 codebases |
| [`15_mini_projects.md`](docs/tutorials/15_mini_projects.md) | 90 min | Practical capstone mini-projects |
| [`16_troubleshooting.md`](docs/tutorials/16_troubleshooting.md) | — | Common pitfalls and error solutions |
| [`17_gazebo_integration.md`](docs/tutorials/17_gazebo_integration.md) | 60 min | Gazebo / GZ Sim & `ros_gz_bridge` integration |
| [`18_testing_ros2.md`](docs/tutorials/18_testing_ros2.md) | 60 min | Unit testing with pytest & integration tests with `launch_testing` |
| [`19_rosbag2.md`](docs/tutorials/19_rosbag2.md) | 45 min | Recording, replaying, and analyzing data with `rosbag2` |
| [`20_composition.md`](docs/tutorials/20_composition.md) | 45 min | Components and intra-process Composition |
| [`21_multi_robot_communication.md`](docs/tutorials/21_multi_robot_communication.md) | 45 min | Multi-robot DDS discovery and domain isolation (`ROS_DOMAIN_ID`) |
| [`22_moveit2_manipulator_planning.md`](docs/tutorials/22_moveit2_manipulator_planning.md) | 60 min | MoveIt2 manipulator kinematics & trajectory planning |
| [`23_openusd_recording.md`](docs/tutorials/23_openusd_recording.md) | 30 min | Bridging ROS 2 odometry into OpenUSD time-sampled stages |

---

## Visualization with Foxglove Studio

Visualizing TF, 3D poses, synthetic LiDAR point clouds, odometry velocity plots, and diagnostics in [Foxglove Studio](https://foxglove.dev/) is supported via `foxglove_bridge`.

1. Install `ros-${ROS_DISTRO}-foxglove-bridge` and run `ros2 run foxglove_bridge foxglove_bridge`.
2. Connect Foxglove Studio to `ws://localhost:8765`.
3. Import [`config/foxglove/ros2_sample_layout.json`](config/foxglove/ros2_sample_layout.json).
4. See [`docs/foxglove_guide.md`](docs/foxglove_guide.md) for full details.

---

## Docker & Dev Container Environment

A turnkey development container environment is configured via VS Code Dev Containers and Docker Compose:

### VS Code Dev Container
Open the repository in VS Code and select **"Reopen in Container"** to start development in a container with ROS 2, C++/Python tools, and workspace extensions pre-configured (defined in `.devcontainer/devcontainer.json`).

### Docker Compose CLI

```bash
# Build and run default container (Ubuntu 26.04 / Lyrical or Ubuntu 24.04 / Jazzy)
docker compose -f docker/compose.yml build
docker compose -f docker/compose.yml run --rm ros2sample

# Or specify ROS 2 distribution:
ROS_DISTRO=jazzy UBUNTU_CODENAME=noble docker compose -f docker/compose.yml build
ROS_DISTRO=jazzy UBUNTU_CODENAME=noble docker compose -f docker/compose.yml run --rm ros2sample
```

---

## Contributing

Contributions, bug reports, and suggestions are welcome! Please refer to [`CONTRIBUTING.md`](CONTRIBUTING.md) for development workflows, testing requirements, and conventions.

## License

This project is licensed under the [MIT License](LICENSE).

## English package guides

- [ground_robot_sim](src/ground_robot_sim/README.en.md)
- [drone_sim](src/drone_sim/README.en.md)
- [manipulator_sim](src/manipulator_sim/README.en.md)
- [sensor_fusion_sim](src/sensor_fusion_sim/README.en.md)
- [nav2_learning](src/nav2_learning/README.en.md)
- [ros2_learning](src/ros2_learning/README.en.md)
- [ros2_learning_cpp](src/ros2_learning_cpp/README.en.md)
- [openusd_bridge](src/openusd_bridge/README.en.md)
- [sample_utils](src/sample_utils/README.en.md)

Run `bash scripts/test-integration.sh` after building the workspace for the four real-node scenarios.
See [Foxglove and markers](docs/tutorials/24_foxglove_visualization.md) and [container GUI setup](docs/development.md) (Japanese).
