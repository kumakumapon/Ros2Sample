# 06. Lifecycle nodes and QoS

[日本語](../06_lifecycle_qos.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

A lifecycle node separates construction, resource configuration and active work. Starting its process does not automatically activate publication.

```bash
ros2 launch ros2_learning lifecycle_demo.launch.py
# Another terminal
ros2 lifecycle get /lifecycle_demo
ros2 lifecycle set /lifecycle_demo configure
ros2 lifecycle get /lifecycle_demo
ros2 lifecycle set /lifecycle_demo activate
ros2 topic echo /lifecycle_output
```

Expect Unconfigured → Inactive → Active, and String output only after activation. Stop echo, then run:

```bash
ros2 lifecycle set /lifecycle_demo deactivate
ros2 lifecycle set /lifecycle_demo cleanup
ros2 lifecycle get /lifecycle_demo
```

Deactivation stops the timer; cleanup releases configured resources. Inspect on_configure, on_activate, on_deactivate and on_cleanup in lifecycle_demo.py. The publish_rate_hz and message_prefix parameters configure this example.

QoS controls reliability, durability, history and depth. Reliable delivery retries lost messages; best effort favors fresh measurements. A reliable subscriber cannot match a best-effort publisher. A best-effort subscriber can receive from either. Transient-local durability supports late subscribers to retained data; volatile subscribers do not request historical data.

Inspect a live sensor stream:

```bash
ros2 launch sensor_fusion_sim sensor_fusion_demo.launch.py
# Another terminal
ros2 topic info /imu -v
ros2 topic echo /imu --qos-reliability best_effort
```

Stop the lifecycle demo before this experiment if you want a simpler graph. The sensor IMU uses best effort while GPS and wheel odometry use reliable QoS. The filter's subscriber settings match these choices. A topic appearing in ros2 topic list does not prove that endpoints are compatible or receiving data.

Exercise: deliberately request reliable IMU reception and compare it with best effort. Diagnose the result through endpoint QoS rather than changing topic names. Use a wall-clock timeout in tests so a stopped simulation clock cannot make a failed test hang forever.
