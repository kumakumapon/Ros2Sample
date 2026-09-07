# 03. Launch files and parameters

[日本語](../03_launch_params.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

Launch descriptions group nodes and initial configuration into a repeatable experiment. A launch argument is evaluated by the launch system; a node parameter is owned by the node. They are only connected when the launch file passes the argument into a parameter.

```bash
ros2 launch ros2_learning parameter_demo.launch.py
# Another terminal
ros2 param list /parameter_demo
ros2 param get /parameter_demo max_speed
ros2 param describe /parameter_demo max_speed
ros2 param set /parameter_demo max_speed 0.8
ros2 topic echo /robot_info
```

Observe the updated robot information and node logs. The node declares robot_name, max_speed, update_rate_hz and enable_logging. Read its parameter callback before assuming every setting is dynamically applied: some nodes read configuration only during construction.

Stop the launch, then provide startup overrides directly:

```bash
ros2 run ros2_learning parameter_demo --ros-args -p robot_name:=lesson_bot -p max_speed:=0.7
```

Save a running configuration with `ros2 param dump /parameter_demo > /tmp/lesson-params.yaml`. After stopping the node, load it with `ros2 run ros2_learning parameter_demo --ros-args --params-file /tmp/lesson-params.yaml`. The YAML node key must match the node name (or use an intentional wildcard).

Inspect pubsub_demo.launch.py: LaunchDescription owns Node actions. Inspect tf_demo.launch.py for DeclareLaunchArgument and LaunchConfiguration. List supported arguments with `ros2 launch ros2_learning tf_demo.launch.py --show-args`.

Exercise: launch the pub/sub pair under a namespace and remap the shared topic. Verify resolved names with ros2 node info. Explain why changing only the publisher's topic name leaves the subscriber silent. Do not enable use_sim_time without a /clock publisher; ROS timers may then wait indefinitely.
