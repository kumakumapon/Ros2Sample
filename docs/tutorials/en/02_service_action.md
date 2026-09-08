# 02. Services and actions

[日本語](../02_service_action.md) | [English learning path](00_learning_path.md)

Prerequisite: build the workspace and source `install/setup.bash` in each terminal.

A service pairs a request with a response. An action adds feedback and a goal lifecycle for longer operations. This repository uses SetBool and NavigateWaypoints, not AddTwoInts or Fibonacci.

Start the service pair:

```bash
ros2 launch ros2_learning service_demo.launch.py
# Another terminal
ros2 service list -t
ros2 interface show std_srvs/srv/SetBool
ros2 service call /set_flag std_srvs/srv/SetBool '{data: true}'
```

Expect success=true. The supplied client toggles the flag every two seconds with call_async; its response callback reads the Future. Avoid blocking an executor callback while waiting for a response that requires the same executor.

Stop this demo. For a controlled action experiment start ONLY the server, so the supplied client does not send competing goals:

```bash
ros2 run ros2_learning minimal_action_server
# Another terminal
ros2 interface show sample_interfaces/action/NavigateWaypoints
ros2 action info /navigate_waypoints
ros2 action send_goal /navigate_waypoints sample_interfaces/action/NavigateWaypoints \
  '{waypoints: [{pose: {position: {x: 0.3, y: 0.0}, orientation: {w: 1.0}}}], loop: false, tolerance_m: 0.05}' --feedback
```

Expect feedback with distance_to_current, followed by success=true and waypoints_completed=1. Empty waypoint lists are rejected. For the automatic paired example, stop the standalone server and run `ros2 launch ros2_learning action_demo.launch.py`.

Read minimal_action_client.py to follow wait_for_server, send_goal_async and get_result_async. The server separates acceptance, execution and cancellation callbacks. The bundled integration test exercises rejection, feedback and completion; it does not assert cancellation behavior.

Exercise: send two reachable waypoints and verify a completion count of two. Explain why a continuously published position stream belongs on a topic, a flag toggle on a service, and a multi-step mission on an action.
