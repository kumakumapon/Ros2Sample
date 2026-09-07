# sample_utils

[日本語](README.md) | [English](README.en.md)

A ROS-independent Python library shared by the simulation packages. It has no executables.
The package demonstrates library reuse through ament_python and package.xml dependencies.

| Module | API | Contract |
| --- | --- | --- |
| `pid` | `PIDController.compute(error, dt)`, `reset()` | Integral and output clamping; nonpositive dt returns zero |
| `noise` | `add_gaussian_noise(value, stddev, rng=None)` | Nonpositive noise consumes no random numbers; inject random.Random for reproducibility |
| `angles` | `normalize_angle(angle)` | Radians normalized to [-pi, pi] |
| `testing` | `RosTestCase` | Optional ROS test support: monotonic deadlines, sensor QoS and cleanup |

```bash
colcon build --symlink-install --packages-up-to sample_utils
source install/setup.bash
colcon test --packages-select sample_utils
```

Consumers declare `<exec_depend>sample_utils</exec_depend>` and import from `sample_utils.pid`
or `sample_utils.noise`. Existing imports through drone_sim and ground_robot_sim remain compatible.
PID regression tests live here. Only the optional `testing` module imports rclpy.
The unused dead_reckoning_step, innovation and euclidean_distance helpers were removed from
sensor_fusion_sim; the complementary-filter helpers remain exercised by the real node.
