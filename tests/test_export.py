"""Tests for services/export.py."""

import json
from pathlib import Path

from openode_session_extractor.services.export import (
    export_session_json,
    export_session_markdown,
    export_session_html,
)


class TestExportSessionJson:
    """Tests for export_session_json function."""

    def test_export_session_json(self, temp_db, temp_output_dir):
        """Test exporting session to JSON."""
        output_path = str(Path(temp_output_dir) / "output.json")
        result = export_session_json(temp_db, "sess1", output_path)
        assert result is True
        assert Path(output_path).exists()

        with open(output_path) as f:
            data = json.load(f)
        assert "session_id" in data
        assert "messages" in data

    def test_export_session_json_skip_same_content(self, temp_db, temp_output_dir):
        """Test that identical content is not rewritten."""
        output_path = str(Path(temp_output_dir) / "output.json")
        export_session_json(temp_db, "sess1", output_path)
        result = export_session_json(temp_db, "sess1", output_path)
        assert result is False


class TestExportSessionMarkdown:
    """Tests for export_session_markdown function."""

    def test_export_session_markdown(self, temp_db, temp_output_dir):
        """Test exporting session to Markdown."""
        output_path = str(Path(temp_output_dir) / "output.md")
        result = export_session_markdown(temp_db, "sess1", output_path)
        assert result is True
        assert Path(output_path).exists()

        with open(output_path) as f:
            content = f.read()
        assert "#" in content  # Header

    def test_export_session_markdown_skip_same_content(self, temp_db, temp_output_dir):
        """Test that identical content is not rewritten."""
        output_path = str(Path(temp_output_dir) / "output.md")
        export_session_markdown(temp_db, "sess1", output_path)
        result = export_session_markdown(temp_db, "sess1", output_path)
        assert result is False


class TestExportSessionHtml:
    """Tests for export_session_html function."""

    def test_export_session_html(self, temp_db, temp_output_dir):
        """Test exporting session to HTML."""
        output_path = str(Path(temp_output_dir) / "output.html")
        result = export_session_html(temp_db, "sess1", output_path)
        assert result is True
        assert Path(output_path).exists()

        with open(output_path) as f:
            content = f.read()
        assert "<html>" in content
        assert "</html>" in content

    def test_export_session_html_skip_same_content(self, temp_db, temp_output_dir):
        """Test that identical content is not rewritten."""
        output_path = str(Path(temp_output_dir) / "output.html")
        export_session_html(temp_db, "sess1", output_path)
        result = export_session_html(temp_db, "sess1", output_path)
        assert result is False
