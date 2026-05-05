"""OpenCode Extractor - Extract agent conversations from OpenCode SQLite database."""

__version__ = "0.1.0"
__all__ = ["__version__", "main"]

from .cli.commands import main
