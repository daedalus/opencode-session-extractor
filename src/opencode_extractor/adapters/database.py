"""Database adapter for opencode_extractor."""

import json
import sqlite3
from typing import Any

DB_PATH = "opencode.db"


def get_sessions(
    db_path: str, limit: int | None = None, search: str | None = None
) -> list[dict[str, Any]]:
    """Fetch sessions from the database.

    Args:
        db_path: Path to SQLite database.
        limit: Maximum number of sessions to return (optional).
        search: Search string to filter by title (optional, case-insensitive).

    Returns:
        List of session dictionaries with keys: id, title, directory, time_created,
        time_updated, project_name.

    Raises:
        sqlite3.Error: If database access fails.

    Example:
        >>> sessions = get_sessions("/path/to/db", limit=5)
        >>> len(sessions) <= 5
        True
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT s.id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
    """
    params: list[str | int] = []
    if search:
        query += " WHERE LOWER(s.title) LIKE ?"
        params.append(f"%{search.lower()}%")

    query += " ORDER BY s.time_updated DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)

    cursor.execute(query, params)
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions


def get_messages(db_path: str, session_id: str) -> list[dict[str, Any]]:
    """Fetch all messages for a session.

    Args:
        db_path: Path to SQLite database.
        session_id: Session ID to fetch messages for.

    Returns:
        List of message dictionaries with parsed data_parsed field.

    Raises:
        sqlite3.Error: If database access fails.
        json.JSONDecodeError: If message data is invalid JSON.

    Example:
        >>> messages = get_messages("/path/to/db", "session123")
        >>> all("data_parsed" in m for m in messages)
        True
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, session_id, time_created, data
        FROM message
        WHERE session_id = ?
        ORDER BY time_created ASC
    """,
        (session_id,),
    )

    messages = []
    for row in cursor.fetchall():
        msg = dict(row)
        msg["data_parsed"] = json.loads(msg["data"])
        messages.append(msg)

    conn.close()
    return messages


def get_parts(db_path: str, message_id: str) -> list[dict[str, Any]]:
    """Fetch all parts for a message.

    Args:
        db_path: Path to SQLite database.
        message_id: Message ID to fetch parts for.

    Returns:
        List of part dictionaries with parsed data_parsed field.

    Raises:
        sqlite3.Error: If database access fails.
        json.JSONDecodeError: If part data is invalid JSON.

    Example:
        >>> parts = get_parts("/path/to/db", "message123")
        >>> isinstance(parts, list)
        True
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, message_id, data
        FROM part
        WHERE message_id = ?
        ORDER BY time_created ASC
    """,
        (message_id,),
    )

    parts = []
    for row in cursor.fetchall():
        part = dict(row)
        part["data_parsed"] = json.loads(part["data"])
        parts.append(part)

    conn.close()
    return parts
