"""LLM-backed RAI agent node for TurtleBot3 natural-language control."""

import collections
from typing import Deque, Optional, Tuple

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rai_bridge import robot_tools
from rai_bridge.nl_command_parser import parse_command
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


# ══════════════════════════════════════════════════════════════════════════════
# LLM CONNECTION  — ここを編集してプロバイダー・モデルを切り替える
#
# 使い方:
#   1. 下記 _build_llm() 内の provider/model を確認する
#   2. config/tb3_rai_agent.yaml で use_llm: true に変更する
#   3. 同 YAML の llm_provider / llm_model を設定する
#   4. API キーを環境変数にセットする（yaml への直書きは非推奨）
#        Anthropic: export ANTHROPIC_API_KEY=sk-ant-...
#        OpenAI:    export OPENAI_API_KEY=sk-...
#   5. 対応する langchain パッケージをインストールする（下記参照）
# ══════════════════════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = (
    'You are a controller for a TurtleBot3 differential-drive robot. '
    'Use the provided tools to fulfill the user command. '
    'Call one or more tools in sequence when needed — do not explain, just call tools.'
)


def _build_llm(provider: str, model: str, api_key: str, base_url: str):
    """
    Instantiate and return a LangChain chat model.

    Edit this function to add or switch LLM providers.

    Supported providers
    -------------------
    ``"anthropic"``
        Install: ``pip install langchain-anthropic``

        API key: ``export ANTHROPIC_API_KEY=sk-ant-...``

        Models: ``"claude-haiku-4-5-20251001"`` (高速・安価),
        ``"claude-sonnet-4-6"``

    ``"openai"``
        Install: ``pip install langchain-openai``

        API key: ``export OPENAI_API_KEY=sk-...``

        Models: ``"gpt-4o-mini"``, ``"gpt-4o"``

    ``"ollama"`` (ローカル LLM)
        Install: ``pip install langchain-ollama``

        Ollama を事前に起動しておく: ``ollama serve``

        base_url デフォルト: ``http://localhost:11434``

        Models: ``"llama3.2"``, ``"qwen2.5"``, ``"mistral"`` など

        注意: ツール呼び出し対応モデルが必要。
        ``ollama pull llama3.2`` で確認してから使用すること。

    ``"openai_compatible"`` (OpenAI 互換ローカルサーバー)
        Install: ``pip install langchain-openai``

        API key: ダミー文字列で可（例: ``"ollama"`` や ``"lm-studio"``）

        base_url にローカルサーバーの URL を指定する:

        - Ollama OpenAI 互換: ``http://localhost:11434/v1``
        - LM Studio:          ``http://localhost:1234/v1``
        - vLLM:               ``http://localhost:8000/v1``

        注意: モデルがツール呼び出し（function calling）に対応していること。
    """
    kw: dict = {'model': model}
    if api_key:
        kw['api_key'] = api_key

    if provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic  # noqa: PLC0415
        return ChatAnthropic(**kw)

    if provider == 'openai':
        from langchain_openai import ChatOpenAI  # noqa: PLC0415
        return ChatOpenAI(**kw)

    if provider == 'ollama':
        from langchain_ollama import ChatOllama  # noqa: PLC0415
        if base_url:
            kw['base_url'] = base_url
        kw.pop('api_key', None)   # Ollama は API キー不要
        return ChatOllama(**kw)

    if provider == 'openai_compatible':
        from langchain_openai import ChatOpenAI  # noqa: PLC0415
        if base_url:
            kw['base_url'] = base_url
        if not api_key:
            kw['api_key'] = 'local'  # OpenAI クライアントはキー必須だがサーバーは検証しない
        return ChatOpenAI(**kw)

    raise ValueError(
        f'Unknown llm_provider "{provider}". '
        'Supported values: "anthropic", "openai", "ollama", "openai_compatible".'
    )


# ══════════════════════════════════════════════════════════════════════════════


# (linear_x, angular_z, remaining_sec)
_Phase = Tuple[float, float, float]


class RaiAgentNode(Node):
    """Subscribe to natural-language goals and drive TurtleBot3 via tool calls."""

    def __init__(self) -> None:
        """Declare parameters, create publishers/subscribers, and initialise LLM."""
        super().__init__('rai_agent_node')

        # ── motion parameters ──────────────────────────────────────────────
        self.declare_parameter('linear_speed', 0.22)    # TB3 Burger max [m/s]
        self.declare_parameter('angular_speed', 2.84)   # TB3 Burger max [rad/s]
        self.declare_parameter('publish_rate', 20.0)    # cmd_vel Hz
        self.declare_parameter('goal_topic', 'rai_goal')
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')

        # ── LLM connection parameters ── edit in config/tb3_rai_agent.yaml ─
        self.declare_parameter('use_llm', False)
        self.declare_parameter('llm_provider', 'anthropic')
        self.declare_parameter('llm_model', 'claude-haiku-4-5-20251001')
        self.declare_parameter('llm_api_key', '')    # prefer env var over this
        self.declare_parameter('llm_base_url', '')   # ローカルLLM用エンドポイント
        # ──────────────────────────────────────────────────────────────────

        lin = float(self.get_parameter('linear_speed').value)
        ang = float(self.get_parameter('angular_speed').value)
        rate = max(1.0, float(self.get_parameter('publish_rate').value))
        self._linear_speed = lin
        self._angular_speed = ang
        self._period_sec = 1.0 / rate

        goal_topic = str(self.get_parameter('goal_topic').value)
        cmd_vel_topic = str(self.get_parameter('cmd_vel_topic').value)
        use_llm = bool(self.get_parameter('use_llm').value)

        self._phase_queue: Deque[_Phase] = collections.deque()
        self._odom_summary = 'unknown'
        self._scan_summary = 'unknown'
        self._llm_with_tools: Optional[object] = None

        self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.status_pub = self.create_publisher(String, 'rai_status', 10)
        self.create_subscription(String, goal_topic, self._on_goal, 10)
        self.create_subscription(Odometry, 'odom', self._on_odom, 10)
        self.create_subscription(LaserScan, 'scan', self._on_scan, 10)
        self.create_timer(self._period_sec, self._on_timer)

        if use_llm:
            self._init_llm()
        else:
            self.get_logger().info(
                f'use_llm=false — rule-based parser active. '
                f'Send goals to /{goal_topic}'
            )

    # ── LLM initialisation ─────────────────────────────────────────────────

    def _init_llm(self) -> None:
        """Build the LLM client and bind tools; fall back to rule-based on error."""
        provider = str(self.get_parameter('llm_provider').value)
        model = str(self.get_parameter('llm_model').value)
        api_key = str(self.get_parameter('llm_api_key').value)
        base_url = str(self.get_parameter('llm_base_url').value)
        try:
            from rai_bridge.rai_agent_adapter import build_rai_tools  # noqa: PLC0415
            llm = _build_llm(provider, model, api_key, base_url)
            tools = build_rai_tools()
            self._llm_with_tools = llm.bind_tools(tools)
            ep = f' ({base_url})' if base_url else ''
            self.get_logger().info(
                f'LLM agent ready: provider={provider} model={model}{ep}'
            )
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(
                f'LLM init failed ({exc}). Falling back to rule-based parser.'
            )

    # ── sensor callbacks ───────────────────────────────────────────────────

    def _on_odom(self, msg: Odometry) -> None:
        """Cache a compact odometry summary for the LLM context."""
        p = msg.pose.pose.position
        self._odom_summary = f'x={p.x:.2f} y={p.y:.2f}'

    def _on_scan(self, msg: LaserScan) -> None:
        """Cache the nearest valid LiDAR reading for the LLM context."""
        valid = [
            r for r in msg.ranges
            if msg.range_min <= r <= msg.range_max
        ]
        self._scan_summary = f'min={min(valid):.2f}m' if valid else 'no valid readings'

    # ── goal callback ──────────────────────────────────────────────────────

    def _on_goal(self, msg: String) -> None:
        """Cancel current motion and process a new natural-language goal."""
        goal = msg.data.strip()
        self.get_logger().info(f'Goal: "{goal}"')
        self._phase_queue.clear()

        if self._llm_with_tools is not None:
            self._run_llm_agent(goal)
        else:
            self._run_rule_based(goal)

    # ── execution paths ────────────────────────────────────────────────────

    def _run_rule_based(self, goal: str) -> None:
        """Parse goal with the rule-based parser and enqueue the resulting phase."""
        command = parse_command(goal)
        self._enqueue_command(command)
        self._publish_status(f'rule-based: {command.action}({command.value:.2f})')

    def _run_llm_agent(self, goal: str) -> None:
        """Call the LLM with current robot state and execute the returned tool calls."""
        from langchain_core.messages import HumanMessage, SystemMessage  # noqa: PLC0415
        context = (
            f'Robot position: {self._odom_summary}. '
            f'Nearest obstacle: {self._scan_summary}.'
        )
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=f'{context}\nCommand: {goal}'),
        ]
        try:
            response = self._llm_with_tools.invoke(messages)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f'LLM call failed: {exc}')
            self._publish_status(f'error: {exc}')
            return

        if not response.tool_calls:
            self.get_logger().warning('LLM returned no tool calls.')
            self._publish_status('no_tool_calls')
            return

        labels = []
        for tc in response.tool_calls:
            command = self._tool_call_to_command(tc['name'], tc['args'])
            if command is not None:
                self._enqueue_command(command)
                labels.append(f'{command.action}({command.value:.2f})')

        self._publish_status('llm: ' + ', '.join(labels))

    # ── tool call → command mapping ────────────────────────────────────────

    @staticmethod
    def _tool_call_to_command(name: str, args: dict):
        """Convert an LLM tool-call name and args to a ParsedCommand, or None."""
        if name == 'move_forward':
            return robot_tools.move_forward(float(args.get('distance_m', 1.0)))
        if name == 'move_backward':
            return robot_tools.move_backward(float(args.get('distance_m', 1.0)))
        if name == 'rotate_left':
            return robot_tools.rotate_left(float(args.get('angle_deg', 90.0)))
        if name == 'rotate_right':
            return robot_tools.rotate_right(float(args.get('angle_deg', 90.0)))
        if name == 'stop':
            return robot_tools.stop()
        return None

    # ── phase queue & cmd_vel timer ────────────────────────────────────────

    def _enqueue_command(self, command) -> None:
        """Convert a ParsedCommand to a Twist phase and append it to the queue."""
        if command.action == 'stop':
            return  # queue already cleared; zero-velocity will be published

        lx, az = robot_tools.twist_values_for_command(
            command, self._linear_speed, self._angular_speed,
        )
        dur = robot_tools.command_duration_sec(
            command, self._linear_speed, self._angular_speed,
        )
        if dur > 0.0:
            self._phase_queue.append((lx, az, dur))

    def _on_timer(self) -> None:
        """Publish the active Twist phase and advance the queue when it expires."""
        twist = Twist()
        if self._phase_queue:
            lx, az, remaining = self._phase_queue[0]
            remaining -= self._period_sec
            if remaining > 0.0:
                twist.linear.x = lx
                twist.angular.z = az
                self._phase_queue[0] = (lx, az, remaining)
            else:
                self._phase_queue.popleft()
        self.cmd_vel_pub.publish(twist)

    def _publish_status(self, text: str) -> None:
        """Publish a human-readable status string to /rai_status."""
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)


def main(args=None) -> None:
    """Run the RAI agent node for TurtleBot3."""
    rclpy.init(args=args)
    node = RaiAgentNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
