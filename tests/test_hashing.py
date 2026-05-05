"""Tests for core/hashing.py."""

import os
import tempfile
from pathlib import Path

from openode_session_extractor.core.hashing import (
    compute_file_hash,
    compute_content_hash,
    write_if_changed,
)


class TestComputeFileHash:
    """Tests for compute_file_hash function."""

    def test_compute_file_hash(self, temp_output_dir):
        """Test computing hash of a file."""
        test_file = Path(temp_output_dir) / "test.txt"
        test_file.write_text("hello world")
        hash_value = compute_file_hash(str(test_file))
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA-256 produces 64 hex chars

    def test_compute_file_hash_empty_file(self, temp_output_dir):
        """Test computing hash of an empty file."""
        test_file = Path(temp_output_dir) / "empty.txt"
        test_file.touch()
        hash_value = compute_file_hash(str(test_file))
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected

    def test_compute_file_hash_missing_file(self):
        """Test that missing file raises FileNotFoundError."""
        try:
            compute_file_hash("/nonexistent/file.txt")
        except FileNotFoundError:
            return
        assert False, "Expected FileNotFoundError"


class TestComputeContentHash:
    """Tests for compute_content_hash function."""

    def test_compute_content_hash(self):
        """Test computing hash of string content."""
        hash_value = compute_content_hash("hello")
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64

    def test_compute_content_hash_empty_string(self):
        """Test computing hash of empty string."""
        hash_value = compute_content_hash("")
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert hash_value == expected

    def test_compute_content_hash_consistency(self):
        """Test that same content produces same hash."""
        content = "test content"
        hash1 = compute_content_hash(content)
        hash2 = compute_content_hash(content)
        assert hash1 == hash2


class TestWriteIfChanged:
    """Tests for write_if_changed function."""

    def test_write_new_file(self, temp_output_dir):
        """Test writing to a new file."""
        output_path = str(Path(temp_output_dir) / "new_file.txt")
        result = write_if_changed(output_path, "content")
        assert result is True
        assert os.path.exists(output_path)
        with open(output_path) as f:
            assert f.read() == "content"

    def test_skip_same_hash(self, temp_output_dir):
        """Test skipping write when content hash matches."""
        output_path = str(Path(temp_output_dir) / "same_hash.txt")
        write_if_changed(output_path, "content")
        result = write_if_changed(output_path, "content")
        assert result is False

    def test_overwrite_larger_content(self, temp_output_dir):
        """Test overwriting when new content is larger."""
        output_path = str(Path(temp_output_dir) / "larger.txt")
        write_if_changed(output_path, "small")
        result = write_if_changed(output_path, "much larger content")
        assert result is True
        with open(output_path) as f:
            assert f.read() == "much larger content"

    def test_skip_smaller_content(self, temp_output_dir):
        """Test skipping when new content is smaller."""
        output_path = str(Path(temp_output_dir) / "smaller.txt")
        write_if_changed(output_path, "large content here")
        result = write_if_changed(output_path, "tiny")
        assert result is False
        with open(output_path) as f:
            assert f.read() == "large content here"
