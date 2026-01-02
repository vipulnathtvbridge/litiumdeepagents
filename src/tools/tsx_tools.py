"""TSX file management tools for agent state management.

This module provides tools for reading and writing TSX/TypeScript React files
stored in the agent state virtual filesystem.
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.prompts.tsx import READ_TSX_DESCRIPTION, WRITE_TSX_DESCRIPTION
from src.state import DeepAgentState


@tool(description=READ_TSX_DESCRIPTION, parse_docstring=True)
def read_tsx(
    file_path: str,
    state: Annotated[DeepAgentState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read TSX file content from virtual filesystem with optional offset and limit.

    Args:
        file_path: Path to the TSX file to read
        state: Agent state containing virtual filesystem (injected in tool node)
        offset: Line number to start reading from (default: 0)
        limit: Maximum number of lines to read (default: 2000)

    Returns:
        Formatted file content with line numbers, or error message if file not found
    """
    files = state.get("files", {})
    if file_path not in files:
        return f"Error: TSX file '{file_path}' not found"

    content = files[file_path]
    if not content:
        return "System reminder: TSX file exists but has empty contents"

    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"

    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i][:2000]  # Truncate long lines
        result_lines.append(f"{i + 1:6d}\t{line_content}")

    return "\n".join(result_lines)


@tool(description=WRITE_TSX_DESCRIPTION, parse_docstring=True)
def write_tsx(
    file_path: str,
    content: str,
    state: Annotated[DeepAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a TSX file in the virtual filesystem.

    Args:
        file_path: Path where the TSX file should be created/updated
        content: TSX/TypeScript code to write to the file
        state: Agent state containing virtual filesystem (injected in tool node)
        tool_call_id: Tool call identifier for message response (injected in tool node)

    Returns:
        Command to update agent state with new TSX file content
    """
    files = state.get("files", {})
    files[file_path] = content
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(f"Updated TSX file {file_path}", tool_call_id=tool_call_id)
            ],
        }
    )
