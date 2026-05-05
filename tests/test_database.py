"""Tests for adapters/database.py."""

import json
import sqlite3
from pathlib import Path

from openode_session_extractor.adapters.database import get_sessions, get_messages, get_parts


class TestGetSessions:
    """Tests for get_sessions function."""

    def test_get_sessions(self, temp_db):
        """Test fetching sessions from database."""
        sessions = get_sessions(temp_db)
        assert isinstance(sessions, list)
        assert len(sessions) >= 1
        assert "id" in sessions[0]
        assert "title" in sessions[0]

    def test_get_sessions_with_limit(self, temp_db):
        """Test fetching sessions with limit."""
        sessions = get_sessions(temp_db, limit=1)
        assert len(sessions) <= 1

    def test_get_sessions_with_search(self, temp_db):
        """Test searching sessions by title."""
        sessions = get_sessions(temp_db, search="Test")
        assert all("Test" in s["title"] for s in sessions)

    def test_get_sessions_with_search_no_results(self, temp_db):
        """Test searching with no matching results."""
        sessions = get_sessions(temp_db, search="nonexistent123")
        assert len(sessions) == 0


class TestGetMessages:
    """Tests for get_messages function."""

    def test_get_messages(self, temp_db):
        """Test fetching messages for a session."""
        messages = get_messages(temp_db, "sess1")
        assert isinstance(messages, list)
        assert len(messages) >= 1
        assert "data_parsed" in messages[0]

    def test_get_messages_nonexistent_session(self, temp_db):
        """Test fetching messages for nonexistent session."""
        messages = get_messages(temp_db, "nonexistent")
        assert messages == []


class TestGetParts:
    """Tests for get_parts function."""

    def test_get_parts(self, temp_db):
        """Test fetching parts for a message."""
        parts = get_parts(temp_db, "msg1")
        assert isinstance(parts, list)
        assert len(parts) >= 1
        assert "data_parsed" in parts[0]

    def test_get_parts_nonexistent_message(self, temp_db):
        """Test fetching parts for nonexistent message."""
        parts = get_parts(temp_db, "nonexistent")
        assert parts == []
