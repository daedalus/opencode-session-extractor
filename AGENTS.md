# AGENTS.md — openode_session_extractor

## Overview

OpenCode Extractor is a CLI tool that extracts agent conversations from the OpenCode SQLite database and exports them to JSON, Markdown, and HTML formats. It includes hash-based collision detection to avoid overwriting files with identical or smaller content.

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `prospector --with-tool ruff --with-tool mypy src/` | Lint + type check (with blending) |
| `semgrep --config=auto src/` | Security and pattern scanning |

## Development

```bash
# Setup
pip install -e ".[test]"

# Test
pytest

# Format
ruff format src/ tests/

# Lint + type check (prospector runs ruff check + mypy together)
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/
```

## Testing

Tests are written using pytest with coverage requirements >= 80%. Test files are located in the `tests/` directory.

Run tests with:
```bash
pytest -v
```

## Code Style

- Format: ruff format
- Lint + Type check: prospector (runs ruff check + mypy with blending)
- Docstrings: Google style

## Release

```bash
# Bump version
bumpversion patch  # or minor/major
git tag v<version>
git push && git push --tags
```
