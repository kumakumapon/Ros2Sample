# openusd_bridge

[日本語](README.md) | [English](README.en.md)

Record Odometry poses as time-sampled OpenUSD Xforms in a Z-up, meter-scale stage.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as sample_interfaces and sample_utils.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to openusd_bridge
source install/setup.bash
ros2 launch openusd_bridge ground_robot_openusd.launch.py
```

Run one demo at a time and stop it with Ctrl+C before starting another controller.

## Executables

| Executable | Purpose |
| --- | --- |
| `odom_to_usd` | Record timestamped position and orientation into an OpenUSD stage. |

Individual nodes use `ros2 run openusd_bridge <executable>`.

## Interfaces and parameters

input_topic defaults to odom (nav_msgs/Odometry). Output is a .usd, .usda or .usdc file; this is a one-way recorder, not a full TF/mesh or playback bridge.

output_path=/tmp/ros2_openusd/robot_motion.usda, robot_prim_path=/World/Robot, time_codes_per_second=30.0, save_every_n_samples=30, overwrite=true. Set overwrite=false to protect an existing file. OpenUSD pxr bindings are optional and must be importable by the same Python interpreter used to build/run the node.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to inspect the active configuration.
Relative topics follow the node namespace; check resolved names with `ros2 node info /<node>`.

## Launch files

- `ros2 launch openusd_bridge ground_robot_openusd.launch.py`

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select openusd_bridge
colcon test-result --verbose
```

Before launching, verify `python3 -c "from pxr import Usd; print(Usd.GetVersion())"`. Build the workspace using a ROS-compatible Python environment that provides pxr. After recording, open the stage in usdview and play its timeline. Existing output is overwritten by default; use `overwrite:=false` as a launch argument to protect it.

See the [English learning path](../../docs/tutorials/en/00_learning_path.md) and the [Japanese package reference](README.md) for extended examples.
