# 01. Publisher and subscriber

[日本語](../01_publisher_subscriber.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

Topics carry asynchronous streams. A publisher and subscriber must agree on the topic name, message type and compatible QoS; their node names can differ. The sample uses std_msgs/msg/String on chatter.

```bash
ros2 launch ros2_learning pubsub_demo.launch.py
```

In a second sourced terminal:

```bash
ros2 node list
ros2 topic list -t
ros2 topic info /chatter -v
ros2 topic echo /chatter
# Stop echo with Ctrl+C, then measure the stream
ros2 topic hz /chatter
```

You should see numbered messages and subscriber log output. Inspect minimal_publisher.py: the constructor creates a publisher and a timer, the timer callback builds a String, and spin processes callbacks. minimal_subscriber.py registers a subscription callback instead.

Stop the launch and run each executable separately. To change the publisher rate, pass a parameter at startup:

```bash
ros2 run ros2_learning minimal_publisher --ros-args -p publish_rate_hz:=5.0
# Another terminal
ros2 run ros2_learning minimal_subscriber
```

The measured rate should be near 5 Hz; scheduling introduces variation. Remap chatter on BOTH nodes with `--ros-args -r chatter:=lesson_chatter`, then verify the new topic. Changing only one endpoint breaks communication.

Exercise: add a second subscriber and confirm that both receive the same stream. Explain why topics suit telemetry but do not directly represent a request with a single reply. If no messages arrive, check both terminals source the same overlay and use the same ROS_DOMAIN_ID, then inspect topic type and QoS.
