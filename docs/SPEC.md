# SPEC.md — openode_session_extractor

## Purpose

OpenCode Extractor is a CLI tool that extracts agent conversations from the OpenCode SQLite database (`~/.local/share/opencode/opencode.db`) and exports them to JSON, Markdown, and HTML formats. It supports listing sessions, exporting individual or all sessions, and uses hash-based collision detection to avoid overwriting files with identical or smaller content.

## Scope

- **In scope:**
  - Connect to OpenCode SQLite database
  - List available sessions with optional search and limit
  - Export sessions to JSON format (preserving message structure and parts)
  - Export sessions to Markdown format (human-readable)
  - Export sessions to HTML format (styled web view)
  - Hash-based file collision detection (SHA-256)
  - CLI interface via argparse

- **Not in scope:**
  - Modifying the OpenCode database
  - Real-time monitoring of sessions
  - Exporting to formats other than JSON, Markdown, HTML
  - MCP server functionality
  - Python library API (CLI-only tool)

## Public API / Interface

### `compute_file_hash(filepath: str) -> str`
Compute SHA-256 hash of a file.

- **Signature:** `compute_file_hash(filepath: str) -> str`
- **Args:** `filepath` - Path to the file to hash
- **Returns:** Hex string of SHA-256 hash
- **Invariants:** File must exist and be readable
- **Error behavior:** Raises `FileNotFoundError` or `IOError` on failure

### `compute_content_hash(content: str) -> str`
Compute SHA-256 hash of string content.

- **Signature:** `compute_content_hash(content: str) -> str`
- **Args:** `content` - String content to hash
- **Returns:** Hex string of SHA-256 hash

### `write_if_changed(output_path: str, content: str) -> bool`
Session collision handling based on hash comparison.

- **Signature:** `write_if_changed(output_path: str, content: str) -> bool`
- **Args:**
  - `output_path` - Path to output file
  - `content` - Content to write
- **Returns:** `True` if file was written, `False` if skipped
- **Behavior:**
  - If file exists and `hash(existing) == hash(content)`: skip, return `False`
  - If file exists and `len(content) > len(existing)`: write, return `True`
  - If file doesn't exist: write, return `True`
  - Otherwise: skip, return `False`

### `format_time(timestamp_ms: int) -> str`
Convert millisecond timestamp to readable date string.

- **Signature:** `format_time(timestamp_ms: int) -> str`
- **Args:** `timestamp_ms` - Timestamp in milliseconds
- **Returns:** Formatted string "YYYY-MM-DD HH:MM:SS"

### `get_sessions(db_path: str, limit: Optional[int] = None, search: Optional[str] = None) -> List[dict]`
Fetch sessions from the database.

- **Signature:** `get_sessions(db_path: str, limit: Optional[int] = None, search: Optional[str] = None) -> List[dict]`
- **Args:**
  - `db_path` - Path to SQLite database
  - `limit` - Maximum number of sessions to return (optional)
  - `search` - Search string to filter by title (optional, case-insensitive)
- **Returns:** List of session dictionaries with keys: id, title, directory, time_created, time_updated, project_name
- **Error behavior:** Raises `sqlite3.Error` on database errors

### `get_messages(db_path: str, session_id: str) -> List[dict]`
Fetch all messages for a session.

- **Signature:** `get_messages(db_path: str, session_id: str) -> List[dict]`
- **Args:**
  - `db_path` - Path to SQLite database
  - `session_id` - Session ID to fetch messages for
- **Returns:** List of message dictionaries with parsed `data_parsed` field
- **Error behavior:** Raises `sqlite3.Error` on database errors, `json.JSONDecodeError` on invalid data

### `get_parts(db_path: str, message_id: str) -> List[dict]`
Fetch all parts for a message.

- **Signature:** `get_parts(db_path: str, message_id: str) -> List[dict]`
- **Args:**
  - `db_path` - Path to SQLite database
  - `message_id` - Message ID to fetch parts for
- **Returns:** List of part dictionaries with parsed `data_parsed` field

### `format_part(part_data: dict) -> str`
Format a message part based on its type (Markdown output).

- **Signature:** `format_part(part_data: dict) -> str`
- **Args:** `part_data` - Dictionary containing part type and data
- **Returns:** Formatted string based on part type
- **Supported types:** text, tool, file, reasoning, step-start, step-finish, patch, compaction

### `export_session_json(db_path: str, session_id: str, output_path: str) -> bool`
Export a session to JSON format.

- **Signature:** `export_session_json(db_path: str, session_id: str, output_path: str) -> bool`
- **Args:**
  - `db_path` - Path to SQLite database
  - `session_id` - Session ID to export
  - `output_path` - Path to output JSON file
- **Returns:** `True` if file was written, `False` if skipped

### `export_session_markdown(db_path: str, session_id: str, output_path: str) -> bool`
Export a session to Markdown format.

- **Signature:** `export_session_markdown(db_path: str, session_id: str, output_path: str) -> bool`
- **Args:**
  - `db_path` - Path to SQLite database
  - `session_id` - Session ID to export
  - `output_path` - Path to output Markdown file
- **Returns:** `True` if file was written, `False` if skipped

### `export_session_html(db_path: str, session_id: str, output_path: str) -> bool`
Export a session to HTML format.

- **Signature:** `export_session_html(db_path: str, session_id: str, output_path: str) -> bool`
- **Args:**
  - `db_path` - Path to SQLite database
  - `session_id` - Session ID to export
  - `output_path` - Path to output HTML file
- **Returns:** `True` if file was written, `False` if skipped

### `list_sessions(db_path: str, limit: int = 20, search: Optional[str] = None) -> None`
List available sessions to stdout.

- **Signature:** `list_sessions(db_path: str, limit: int = 20, search: Optional[str] = None) -> None`
- **Args:**
  - `db_path` - Path to SQLite database
  - `limit` - Maximum number of sessions to list (default: 20)
  - `search` - Search string to filter by title (optional)

### CLI Interface (`__main__.py`)

```
openode_session_extractor [OPTIONS]

Options:
  --db PATH              Path to OpenCode database (default: ~/.local/share/opencode/opencode.db)
  --list                 List available sessions
  --search TEXT          Search sessions by title
  --limit INTEGER        Limit number of sessions listed (default: 20)
  --session TEXT         Session ID to export
  --all                  Export all sessions
  --output-dir PATH      Output directory (default: ./exports)
  --format [json|markdown|html|all]  Export format (default: all)
```

## Data Formats

### Input
- **SQLite database** at `~/.local/share/opencode/opencode.db`
- **Tables used:**
  - `session`: id, title, directory, time_created, time_updated, project_id
  - `project`: id, name
  - `message`: id, session_id, time_created, data (JSON)
  - `part`: id, message_id, time_created, data (JSON)

### Output - JSON
```json
{
  "session_id": "string",
  "messages": [
    {
      "id": "string",
      "role": "user|assistant",
      "time": "YYYY-MM-DD HH:MM:SS",
      "model": {"providerID": "string", "modelID": "string"},
      "parts": [...]
    }
  ]
}
```

### Output - Markdown
Human-readable format with headers, code blocks, and formatting for different part types.

### Output - HTML
Styled HTML page with CSS, displaying messages in a chat-like interface with color-coded roles.

## Edge Cases

1. **Database not found**: Print error message and exit gracefully
2. **Empty session (no messages)**: Export empty messages array (JSON) or just headers (Markdown/HTML)
3. **Invalid session ID**: Should handle gracefully (empty export or error)
4. **File collision (same hash)**: Skip writing, return False
5. **File collision (larger content)**: Overwrite with larger content
6. **File collision (smaller content)**: Skip writing, return False
7. **Invalid JSON in database**: Should raise `json.JSONDecodeError`
8. **Output directory doesn't exist**: Create it automatically
9. **Very long session titles**: Truncate to 50 chars in list display with "..." suffix
10. **Missing project name**: Display "N/A" for directory in exports

## Performance & Constraints

- **Target Python version:** 3.11+
- **Dependencies:** sqlite3 (stdlib), json (stdlib), html (stdlib), os (stdlib), hashlib (stdlib), datetime (stdlib)
- **No external dependencies** required
- **O(n)** where n = number of messages/parts in session
- **Memory:** Loads one session at a time (not all sessions at once for export)
- **Database:** Read-only operations, no modifications to OpenCode database
