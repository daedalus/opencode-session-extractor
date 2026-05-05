"""Pytest configuration for opencode_extractor tests."""

import tempfile
import json
import sqlite3
import os
from pathlib import Path

import pytest


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database with test data."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE project (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE session (
            id TEXT PRIMARY KEY,
            title TEXT,
            directory TEXT,
            time_created INTEGER,
            time_updated INTEGER,
            project_id TEXT,
            FOREIGN KEY (project_id) REFERENCES project(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE message (
            id TEXT PRIMARY KEY,
            session_id TEXT,
            time_created INTEGER,
            data TEXT,
            FOREIGN KEY (session_id) REFERENCES session(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE part (
            id TEXT PRIMARY KEY,
            message_id TEXT,
            time_created INTEGER,
            data TEXT,
            FOREIGN KEY (message_id) REFERENCES message(id)
        )
    """)

    # Insert test data
    cursor.execute(
        "INSERT INTO project (id, name) VALUES (?, ?)", ("proj1", "Test Project")
    )

    cursor.execute(
        "INSERT INTO session (id, title, directory, time_created, time_updated, project_id) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "sess1",
            "Test Session",
            "/home/user/project",
            1700000000000,
            1700001000000,
            "proj1",
        ),
    )

    cursor.execute(
        "INSERT INTO message (id, session_id, time_created, data) VALUES (?, ?, ?, ?)",
        (
            "msg1",
            "sess1",
            1700000000000,
            json.dumps(
                {
                    "role": "user",
                    "time": {"created": 1700000000000},
                    "model": {},
                    "parts": [],
                }
            ),
        ),
    )

    cursor.execute(
        "INSERT INTO part (id, message_id, time_created, data) VALUES (?, ?, ?, ?)",
        (
            "part1",
            "msg1",
            1700000000000,
            json.dumps({"type": "text", "text": "Hello world"}),
        ),
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    os.unlink(db_path)


@pytest.fixture
def temp_output_dir():
    """Create a temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir
