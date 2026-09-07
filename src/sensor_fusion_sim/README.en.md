# sensor_fusion_sim

[日本語](README.md) | [English](README.en.md)

Compare complementary filtering and an extended Kalman filter on a circular trajectory.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to sensor_fusion_sim
source install/setup.bash
ros2 launch sensor_fusion_sim sensor_fusion_demo.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `noisy_sensor_node` | Publish noisy GPS, body-frame IMU and wheel odometry. |
| `complementary_filter_node` | Blend sensor measurements with adjustable weights. |
| `lifecycle_data_recorder` | Record data while the lifecycle node is active. |
| `ekf_node` | Estimate planar pose, speed and yaw rate with an EKF. |

Individual nodes use `ros2 run sensor_fusion_sim <executable>`.

## Interfaces and parameters

gps (geometry_msgs/PointStamped), imu (sensor_msgs/Imu, best effort), wheel_odom, ground_truth, fused_odom and ekf_odom (nav_msgs/Odometry). filter_diagnostics and ekf_diagnostics carry std_msgs/String.

circle_radius=5.0 and circle_omega=0.3 define the trajectory. gps_noise_stddev=0.5 and odom_noise_stddev=0.05 set measurement noise. gps_alpha=0.15 and odom_alpha=0.30 weight complementary-filter measurements.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch sensor_fusion_sim sensor_fusion_demo.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select sensor_fusion_sim
colcon test-result --verbose
```

After building the full workspace, run `bash scripts/test-integration.sh` for the four real-node integration scenarios.

Inspect `ros2 topic echo /filter_diagnostics` for nonzero GPS, IMU and odometry counters. The circle starts at elapsed time zero; an uninitialized simulated clock waits for its first nonzero tick, and a rewind resets the trajectory. Pose is in world coordinates, but IMU acceleration and odometry twist are in body coordinates (+X forward, +Y left, +Z up). Default centripetal acceleration is (0, +0.45, 0) m/s² before noise/bias. Gravity is removed in this teaching model. Default forward velocity is 1.5 m/s.

See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
