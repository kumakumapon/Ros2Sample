"""
Optional adapter wrapping robot_tools as LangChain tools for a real agent.

``rai_bridge`` works fully offline with ``nl_command_parser``'s rule-based
parser -- that is what CI exercises, since it needs no network access or LLM
API key. RobotecAI's RAI framework (https://github.com/RobotecAI/rai) and
plain LangChain agents both build on the same primitive demonstrated here:
wrapping a ROS 2 capability as a small, typed, documented Python function
("tool") that an LLM can choose to call. Install the optional
``langchain-core`` package (and, for a full RAI agent, the ``rai`` ROS 2
packages plus an LLM API key) to move beyond the rule-based parser.
"""

from rai_bridge import robot_tools


class RaiAgentUnavailableError(RuntimeError):
    """Raised when a LangChain/RAI-backed agent is requested but unavailable."""


def is_langchain_available() -> bool:
    """Return whether langchain_core is importable in the current environment."""
    try:
        import langchain_core.tools  # noqa: F401
    except ImportError:
        return False
    return True


def build_rai_tools():
    """
    Wrap robot_tools functions as LangChain Tool objects.

    Raises RaiAgentUnavailableError when langchain_core is not installed, so
    callers can fall back to nl_command_parser.parse_command instead.
    """
    try:
        from langchain_core.tools import tool
    except ImportError as exc:
        raise RaiAgentUnavailableError(
            'langchain_core is not installed; install the optional langchain-core '
            'package (and, for a full RAI agent, the rai ROS 2 packages) to use an '
            'LLM-backed agent instead of the built-in rule-based parser.'
        ) from exc

    @tool
    def move_forward(distance_m: float) -> str:
        """Drive the robot forward by distance_m meters."""
        command = robot_tools.move_forward(distance_m)
        return f'{command.action}({command.value})'

    @tool
    def move_backward(distance_m: float) -> str:
        """Drive the robot backward by distance_m meters."""
        command = robot_tools.move_backward(distance_m)
        return f'{command.action}({command.value})'

    @tool
    def rotate_left(angle_deg: float) -> str:
        """Rotate the robot left (counter-clockwise) by angle_deg degrees."""
        command = robot_tools.rotate_left(angle_deg)
        return f'{command.action}({command.value})'

    @tool
    def rotate_right(angle_deg: float) -> str:
        """Rotate the robot right (clockwise) by angle_deg degrees."""
        command = robot_tools.rotate_right(angle_deg)
        return f'{command.action}({command.value})'

    @tool
    def stop() -> str:
        """Stop the robot immediately."""
        command = robot_tools.stop()
        return f'{command.action}({command.value})'

    return [move_forward, move_backward, rotate_left, rotate_right, stop]
