# rai_bridge

[日本語](README.md) | [English](README.en.md)

A minimal sample that turns free-form natural-language text commands into
`cmd_vel` `Twist` commands. It demonstrates the core pattern behind
[RobotecAI's RAI](https://github.com/RobotecAI/rai) -- an LLM agent calling
ROS 2 capabilities as "tools" -- using a rule-based implementation that needs
no network access or LLM API key.

## Build

Run from the workspace root after installing ROS 2 and resolving dependencies.
`--packages-up-to` also builds workspace dependencies such as ground_robot_sim.
Source the overlay in every terminal.

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install --packages-up-to rai_bridge
source install/setup.bash
ros2 launch rai_bridge nl_teleop_demo.launch.py
```

This starts `ground_robot_node`, `nl_command_node`, and `nl_demo_publisher`
together; the demo publisher replays a scripted sequence of forward, turn,
and stop commands from `config/nl_command_demo.yaml`. Watch it move with
`ros2 topic echo /odom`.

You can also drive it interactively:

```bash
ros2 run ground_robot_sim ground_robot_node &
ros2 run rai_bridge nl_command_node &
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: 'move forward 2 m'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: 'rotate left 90 degrees'"
ros2 topic pub -1 /nl_command std_msgs/msg/String "data: 'stop'"
ros2 topic echo /nl_command_status
```

## Executables

| Executable | Purpose |
| --- | --- |
| `nl_command_node` | Subscribe to `nl_command` (`std_msgs/String`) and publish `cmd_vel` and `nl_command_status`. |
| `nl_demo_publisher` | Replay the scripted commands from `config/nl_command_demo.yaml` onto `nl_command`. |

Individual nodes use `ros2 run rai_bridge <executable>`.

## Interfaces and parameters

`nl_command_node`: `input_topic` defaults to `nl_command`; `linear_speed=0.3` m/s,
`angular_speed=0.6` rad/s, `publish_rate=20.0` Hz, `default_distance_m=1.0`,
`default_angle_deg=90.0` are used when the text does not specify a number.

`nl_demo_publisher`: `output_topic=nl_command`, `commands` (a scripted list of
forward/turn/stop phrases), `interval_sec=4.0`, `loop=true`.

Use `ros2 param list /<node>` and `ros2 param describe /<node> <parameter>` to
inspect the active configuration.

## Recognized commands

| Example text | Recognized action |
| --- | --- |
| `前進して` / `forward` | `move_forward` (default 1.0 m) |
| `3メートル進んで` / `move forward 3 m` | `move_forward` (3.0 m) |
| `後退して` / `move backward 2.5 m` | `move_backward` |
| `右に曲がって` / `turn right` | `rotate_right` (default 90 deg) |
| `左に45度回転して` / `rotate left 45 degrees` | `rotate_left` (45 deg) |
| `止まって` / `stop` | `stop` |
| Anything else | `unknown` (the raw text is reported on `nl_command_status`) |

## Extending toward LangChain / RAI

The functions in `rai_bridge.robot_tools` (`move_forward`, `move_backward`,
`rotate_left`, `rotate_right`, `stop`) already have the exact shape a RAI or
LangChain agent expects a "tool" to have: typed arguments, a docstring, and
a side-effect-free return value. With the optional `langchain-core` package
installed, `rai_agent_adapter.build_rai_tools()` wraps the same functions as
LangChain `Tool` objects:

```bash
pip install langchain-core
python3 -c "
from rai_bridge.rai_agent_adapter import build_rai_tools
for t in build_rai_tools():
    print(t.name, '-', t.description)
"
```

`langchain-core` is intentionally not part of the regular `rosdep` set (a
heavy optional dependency, treated the same way `openusd_bridge` treats
`pxr`). The build, unit tests, and `nl_teleop_demo.launch.py` all work with
the rule-based parser alone when it is absent. A real LLM agent loop (prompt
design, conversation history, wiring into the real `rai_core` / ROS 2 tool
set from [RobotecAI's RAI](https://github.com/RobotecAI/rai)) is out of
scope for this sample.

## Verify

```bash
ros2 node list
ros2 topic list -t
colcon test --packages-select rai_bridge
colcon test-result --verbose
```

See the [English learning path](../../docs/tutorials/en/00_learning_path.md)
and the [Japanese package reference](README.md) for extended examples.
