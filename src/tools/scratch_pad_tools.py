"""Scratch pad tools for tracking file diffs and changes.

This module provides tools for reading and writing to a scratch pad that maintains
a record of file diffs and modifications made during the agent's execution.
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.state import DeepAgentState


@tool(parse_docstring=True)
def write_scratch_pad(
    diffs: dict[str, str],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create or update the scratch pad with file diffs.

    Use this tool to record changes and diffs made to files. Each key should be
    a file path and the value should be the diff or change description.

    Args:
        diffs: Dictionary mapping file paths to their diff content or change descriptions
        tool_call_id: Tool call identifier for message response

    Returns:
        Command to update agent state with new diffs
    """
    return Command(
        update={
            "diffs": diffs,
            "messages": [
                ToolMessage(f"Updated scratch pad with {len(diffs)} file(s)", tool_call_id=tool_call_id)
            ],
        }
    )


@tool(parse_docstring=True)
def read_scratch_pad(
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> str:
    """Read the current scratch pad containing file diffs.

    This tool allows you to retrieve and review all recorded diffs and changes
    to track what modifications have been made to files.

    Args:
        state: Injected agent state containing the current diffs
        tool_call_id: Injected tool call identifier for message tracking

    Returns:
        Formatted string representation of the current scratch pad
    """
    diffs = state.get("diffs", {})
    if not diffs:
        return "Scratch pad is empty. No diffs recorded yet."

    result = "Current Scratch Pad:\n" + "=" * 50 + "\n"
    for i, (filename, diff_content) in enumerate(diffs.items(), 1):
        result += f"\n{i}. {filename}\n"
        result += "-" * 50 + "\n"
        result += diff_content + "\n"

    return result.strip()
