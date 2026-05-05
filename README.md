**openode_session_extractor** — Extract agent conversations from OpenCode SQLite database.

[![PyPI](https://img.shields.io/pypi/v/openode_session_extractor.svg)](https://pypi.org/project/openode_session_extractor/)
[![Python](https://img.shields.io/pypi/pyversions/openode_session_extractor.svg)](https://pypi.org/project/openode_session_extractor/)
[![Coverage](https://codecov.io/gh/daedalus/openode_session_extractor/branch/master/graph/badge.svg)](https://codecov.io/gh/daedalus/openode_session_extractor)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/daedalus/openode_session_extractor)

## Install

```bash
pip install openode_session_extractor
```

## Usage

```python
from openode_session_extractor import export_session_json, export_session_markdown, export_session_html

# Export a session to JSON
export_session_json("/path/to/opencode.db", "session_id", "output.json")

# Export to Markdown
export_session_markdown("/path/to/opencode.db", "session_id", "output.md")

# Export to HTML
export_session_html("/path/to/opencode.db", "session_id", "output.html")
```

## CLI

```bash
# List available sessions
openode_session_extractor --list

# Search sessions
openode_session_extractor --list --search "my project"

# Export a specific session to all formats
openode_session_extractor --session SESSION_ID --output-dir ./exports

# Export all sessions to Markdown only
openode_session_extractor --all --format markdown --output-dir ./exports

# Use custom database path
openode_session_extractor --db /path/to/custom.db --list
```

## API

### Core Functions

- `compute_file_hash(filepath: str) -> str` - Compute SHA-256 hash of a file
- `compute_content_hash(content: str) -> str` - Compute SHA-256 hash of string content
- `write_if_changed(output_path: str, content: str) -> bool` - Write file only if content changed (hash-based collision detection)

### Database Functions

- `get_sessions(db_path: str, limit: Optional[int], search: Optional[str]) -> List[dict]` - Fetch sessions from database
- `get_messages(db_path: str, session_id: str) -> List[dict]` - Fetch messages for a session
- `get_parts(db_path: str, message_id: str) -> List[dict]` - Fetch parts for a message

### Export Functions

- `export_session_json(db_path: str, session_id: str, output_path: str) -> bool` - Export to JSON
- `export_session_markdown(db_path: str, session_id: str, output_path: str) -> bool` - Export to Markdown
- `export_session_html(db_path: str, session_id: str, output_path: str) -> bool` - Export to HTML

### Formatting Functions

- `format_time(timestamp_ms: int) -> str` - Convert millisecond timestamp to readable date
- `format_part(part_data: dict) -> str` - Format a message part based on its type

## Development

```bash
git clone https://github.com/daedalus/openode_session_extractor.git
cd openode_session_extractor
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint + type check (prospector runs ruff check + mypy together)
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/
```
