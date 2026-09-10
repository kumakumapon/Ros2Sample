"""Unit tests for the optional LangChain/RAI tool-wrapping adapter."""

import pytest

from rai_bridge import rai_agent_adapter


def test_is_langchain_available_matches_import():
    """The availability check agrees with actually importing langchain_core.tools."""
    try:
        import langchain_core.tools  # noqa: F401
        available = True
    except ImportError:
        available = False
    assert rai_agent_adapter.is_langchain_available() == available


def test_build_rai_tools_reflects_availability():
    """build_rai_tools either returns five tools or raises a clear fallback error."""
    if rai_agent_adapter.is_langchain_available():
        tools = rai_agent_adapter.build_rai_tools()
        assert len(tools) == 5
    else:
        with pytest.raises(rai_agent_adapter.RaiAgentUnavailableError):
            rai_agent_adapter.build_rai_tools()
