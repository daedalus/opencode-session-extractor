"""CLI commands for opencode_extractor."""

import argparse
import os

from opencode_extractor.adapters.database import get_sessions
from opencode_extractor.core.formatting import format_time
from opencode_extractor.services.export import (
    export_session_html,
    export_session_json,
    export_session_markdown,
)

DB_PATH = os.path.expanduser("~/.local/share/opencode/opencode.db")


def list_sessions(db_path: str, limit: int = 20, search: str | None = None) -> None:
    """List available sessions to stdout.

    Args:
        db_path: Path to SQLite database.
        limit: Maximum number of sessions to list (default: 20).
        search: Search string to filter by title (optional).

    Example:
        >>> list_sessions("/path/to/db", limit=5)
        ID                       Title                                        Updated
        ...
    """
    sessions = get_sessions(db_path, limit=limit, search=search)

    print(f"\n{'ID':<25} {'Title':<50} {'Updated'}")
    print("-" * 100)
    for s in sessions:
        title = s["title"][:47] + "..." if len(s["title"]) > 50 else s["title"]
        time_str = format_time(s["time_updated"])
        print(f"{s['id']:<25} {title:<50} {time_str}")
    print()


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for failure).

    Example:
        >>> import sys
        >>> sys.argv = ['opencode_extractor', '--list']
        >>> main()
        0
    """
    parser = argparse.ArgumentParser(description="Extract OpenCode conversations")
    parser.add_argument("--db", default=DB_PATH, help="Path to OpenCode database")
    parser.add_argument("--list", action="store_true", help="List available sessions")
    parser.add_argument("--search", type=str, help="Search sessions by title")
    parser.add_argument(
        "--limit", type=int, default=20, help="Limit number of sessions listed"
    )
    parser.add_argument("--session", type=str, help="Session ID to export")
    parser.add_argument("--all", action="store_true", help="Export all sessions")
    parser.add_argument(
        "--output-dir", type=str, default="./exports", help="Output directory"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "markdown", "html", "all"],
        default="all",
        help="Export format",
    )

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found at {args.db}")
        return 1

    if args.list or (not args.session and not args.all):
        list_sessions(args.db, limit=args.limit, search=args.search)
        return 0

    os.makedirs(args.output_dir, exist_ok=True)

    sessions_to_export = []
    if args.all:
        sessions_to_export = get_sessions(args.db)
    elif args.session:
        sessions_to_export = [{"id": args.session}]

    for session in sessions_to_export:
        session_id = session["id"]
        print(f"Exporting session: {session_id}")

        if args.format in ["json", "all"]:
            output_path = os.path.join(args.output_dir, f"{session_id}.json")
            export_session_json(args.db, session_id, output_path)
            print(f"  JSON: {output_path}")

        if args.format in ["markdown", "all"]:
            output_path = os.path.join(args.output_dir, f"{session_id}.md")
            written = export_session_markdown(args.db, session_id, output_path)
            status = "written" if written else "skipped (hash match)"
            print(f"  Markdown: {output_path} [{status}]")

        if args.format in ["html", "all"]:
            output_path = os.path.join(args.output_dir, f"{session_id}.html")
            written = export_session_html(args.db, session_id, output_path)
            status = "written" if written else "skipped (hash match)"
            print(f"  HTML: {output_path} [{status}]")

    return 0
