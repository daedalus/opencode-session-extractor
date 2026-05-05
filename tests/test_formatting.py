"""Tests for core/formatting.py."""

from opencode_extractor.core.formatting import (
    format_time,
    format_text_part,
    format_tool_part,
    format_file_part,
    format_patch_part,
    format_compaction_part,
    format_part,
)


class TestFormatTime:
    """Tests for format_time function."""

    def test_format_time(self):
        """Test converting millisecond timestamp to readable format (UTC)."""
        result = format_time(1700000000000)
        assert result == "2023-11-14 22:13:20"

    def test_format_time_zero(self):
        """Test formatting timestamp of 0 (UTC)."""
        result = format_time(0)
        assert result == "1970-01-01 00:00:00"


class TestFormatTextPart:
    """Tests for format_text_part function."""

    def test_format_text_part(self):
        """Test extracting text from text part."""
        part_data = {"type": "text", "text": "Hello world"}
        result = format_text_part(part_data)
        assert result == "Hello world"

    def test_format_text_part_empty(self):
        """Test handling empty text."""
        part_data = {"type": "text"}
        result = format_text_part(part_data)
        assert result == ""


class TestFormatToolPart:
    """Tests for format_tool_part function."""

    def test_format_tool_part_with_input_output(self):
        """Test formatting tool part with input and output."""
        part_data = {
            "tool": "bash",
            "state": {"input": {"command": "ls"}, "output": "file1.txt"},
        }
        result = format_tool_part(part_data)
        assert "**Tool: bash**" in result
        assert "Input:" in result
        assert "ls" in result

    def test_format_tool_part_no_input(self):
        """Test formatting tool part without input."""
        part_data = {"tool": "bash", "state": {"output": "result"}}
        result = format_tool_part(part_data)
        assert "**Tool: bash**" in result
        assert "Input:" not in result


class TestFormatFilePart:
    """Tests for format_file_part function."""

    def test_format_file_part(self):
        """Test formatting file part."""
        part_data = {"path": "test.py", "content": "print('hello')"}
        result = format_file_part(part_data)
        assert "**File: test.py**" in result
        assert "print('hello')" in result


class TestFormatPatchPart:
    """Tests for format_patch_part function."""

    def test_format_patch_part(self):
        """Test formatting patch part."""
        part_data = {"diff": "--- a/file\n+++ b/file", "path": "file.txt"}
        result = format_patch_part(part_data)
        assert "**Patch: file.txt**" in result
        assert "diff" in result


class TestFormatCompactionPart:
    """Tests for format_compaction_part function."""

    def test_format_compaction_part(self):
        """Test formatting compaction part."""
        part_data = {"summary": "Previous context compressed"}
        result = format_compaction_part(part_data)
        assert "Context compacted" in result


class TestFormatPart:
    """Tests for format_part function."""

    def test_format_part_text(self):
        """Test formatting text part."""
        part_data = {"type": "text", "text": "Hello"}
        result = format_part(part_data)
        assert result == "Hello"

    def test_format_part_tool(self):
        """Test formatting tool part."""
        part_data = {"type": "tool", "tool": "bash", "state": {}}
        result = format_part(part_data)
        assert "Tool:" in result

    def test_format_part_file(self):
        """Test formatting file part."""
        part_data = {"type": "file", "path": "test.py", "content": "code"}
        result = format_part(part_data)
        assert "File:" in result

    def test_format_part_reasoning(self):
        """Test formatting reasoning part."""
        part_data = {"type": "reasoning", "text": "Thinking..."}
        result = format_part(part_data)
        assert "Reasoning:" in result

    def test_format_part_step_start(self):
        """Test formatting step-start part."""
        part_data = {"type": "step-start"}
        result = format_part(part_data)
        assert result == "---\n"

    def test_format_part_step_finish(self):
        """Test formatting step-finish part."""
        part_data = {"type": "step-finish", "finish": "done"}
        result = format_part(part_data)
        assert "Step finished:" in result

    def test_format_part_patch(self):
        """Test formatting patch part."""
        part_data = {"type": "patch", "diff": "--- a\n+++ b", "path": "f"}
        result = format_part(part_data)
        assert "Patch:" in result

    def test_format_part_compaction(self):
        """Test formatting compaction part."""
        part_data = {"type": "compaction", "summary": "compressed"}
        result = format_part(part_data)
        assert "Context compacted" in result

    def test_format_part_unknown(self):
        """Test formatting unknown part type."""
        part_data = {"type": "unknown_type"}
        result = format_part(part_data)
        assert "**unknown_type**" in result
