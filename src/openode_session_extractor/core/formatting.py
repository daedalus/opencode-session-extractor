"""Formatting utilities for openode_session_extractor."""

import json
from datetime import UTC, datetime
from typing import Any


def format_time(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to readable date string (UTC).

    Args:
        timestamp_ms: Timestamp in milliseconds.

    Returns:
        Formatted string in "YYYY-MM-DD HH:MM:SS" format (UTC).

    Example:
        >>> format_time(1700000000000)
        '2023-11-14 19:13:20'
    """
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def format_text_part(part_data: dict[str, Any]) -> str:
    """Extract text from a text part.

    Args:
        part_data: Dictionary containing part type and data.

    Returns:
        The text content of the part.

    Example:
        >>> format_text_part({"type": "text", "text": "Hello world"})
        'Hello world'
    """
    return str(part_data.get("text", ""))


def format_tool_part(part_data: dict[str, Any]) -> str:
    """Format tool call part for Markdown output.

    Args:
        part_data: Dictionary containing tool call data.

    Returns:
        Formatted string with tool name, input, and output.

    Example:
        >>> data = {"tool": "bash", "state": {"input": {"command": "ls"}, "output": "file1.txt"}}
        >>> format_tool_part(data)
        '**Tool: bash**\\n\\nInput:\\n```json\\n{\\n  "command": "ls"\\n}\\n```\\n\\nOutput:\\n```\\nfile1.txt\\n```\\n'
    """
    tool_name = part_data.get("tool", part_data.get("name", "unknown"))
    state = part_data.get("state", {})
    input_data = state.get("input", {})
    output_data = state.get("output", "")

    result = f"**Tool: {tool_name}**\n\n"
    if input_data and input_data != {}:
        result += f"Input:\n```json\n{json.dumps(input_data, indent=2)}\n```\n\n"
    if output_data:
        if isinstance(output_data, str):
            try:
                output_json = json.loads(output_data)
                result += (
                    f"Output:\n```json\n{json.dumps(output_json, indent=2)}\n```\n"
                )
            except (json.JSONDecodeError, ValueError):
                result += f"Output:\n```\n{output_data}\n```\n"
        else:
            result += f"Output:\n```json\n{json.dumps(output_data, indent=2)}\n```\n"
    return result


def format_file_part(part_data: dict[str, Any]) -> str:
    """Format file part for Markdown output.

    Args:
        part_data: Dictionary containing file part data.

    Returns:
        Formatted string with file path and content.

    Example:
        >>> format_file_part({"path": "test.py", "content": "print('hello')"})
        '**File: test.py**\\n```\\nprint(\\'hello\\')\\n```\\n'
    """
    path = part_data.get("path", "unknown")
    content = part_data.get("content", "")
    return f"**File: {path}**\n```\n{content}\n```\n"


def format_patch_part(part_data: dict[str, Any]) -> str:
    """Format patch/diff part for Markdown output.

    Args:
        part_data: Dictionary containing patch data.

    Returns:
        Formatted string with patch diff.

    Example:
        >>> format_patch_part({"diff": "--- a/file\\n+++ b/file", "path": "file.txt"})
        '**Patch: file.txt**\\n```diff\\n--- a/file\\n+++ b/file\\n```\\n'
    """
    diff = part_data.get("diff", "")
    file_path = part_data.get("path", "unknown")
    return f"**Patch: {file_path}**\n```diff\n{diff}\n```\n"


def format_compaction_part(part_data: dict[str, Any]) -> str:
    """Format compaction part for Markdown output.

    Args:
        part_data: Dictionary containing compaction data.

    Returns:
        Formatted string indicating context compaction.

    Example:
        >>> format_compaction_part({"summary": "Previous context compressed"})
        '*[Context compacted: Previous context compressed]*\\n\\n'
    """
    return f"*[Context compacted: {part_data.get('summary', '...')}]*\n\n"


def format_part(part_data: dict[str, Any]) -> str:
    """Format a message part based on its type for Markdown output.

    Args:
        part_data: Dictionary containing part type and data.

    Returns:
        Formatted string based on part type.

    Raises:
        ValueError: If part type is unknown (returns fallback format).

    Example:
        >>> format_part({"type": "text", "text": "Hello"})
        'Hello'
    """
    part_type = part_data.get("type", "")

    if part_type == "text":
        return format_text_part(part_data)
    if part_type == "tool":
        return format_tool_part(part_data)
    if part_type == "file":
        return format_file_part(part_data)
    if part_type == "reasoning":
        return f"**Reasoning:**\n{part_data.get('text', '')}\n"
    if part_type == "step-start":
        return "---\n"
    if part_type == "step-finish":
        return f"**Step finished:** {part_data.get('finish', '')}\n"
    if part_type == "patch":
        return format_patch_part(part_data)
    if part_type == "compaction":
        return format_compaction_part(part_data)
    return f"**{part_type}**\n"
