#!/usr/bin/env python3
"""
OpenCode Conversation Extractor
Extracts agent conversations from OpenCode SQLite database and exports to JSON, Markdown, and HTML formats.
"""

import sqlite3
import json
import html
import os
import hashlib
import difflib
from datetime import datetime
from typing import Optional


def compute_file_hash(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def write_if_changed(output_path: str, content: str) -> bool:
    """
    Session collision handling:
    - If hash(file_on_disk) == hash(content): data = [] (no write, return False)
    - If len(content_in_RAM) > len(content_on_disk): write file
    Returns True if written, False if skipped (hash match, data = []).
    """
    if os.path.exists(output_path):
        existing_hash = compute_file_hash(output_path)
        new_hash = compute_content_hash(content)

        if existing_hash == new_hash:
            return False  # hashes equal, data = []

        # Hashes differ - check if RAM content is larger
        disk_content_len = os.path.getsize(output_path)
        if len(content) > disk_content_len:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False

    # New file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


DB_PATH = os.path.expanduser("~/.local/share/opencode/opencode.db")


def format_time(timestamp_ms: int) -> str:
    """Convert millisecond timestamp to readable date string."""
    return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")


def get_sessions(
    db_path: str, limit: Optional[int] = None, search: Optional[str] = None
):
    """Fetch sessions from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT s.id, s.title, s.directory, s.time_created, s.time_updated,
               p.name as project_name
        FROM session s
        LEFT JOIN project p ON s.project_id = p.id
    """
    params = []
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


def get_messages(db_path: str, session_id: str):
    """Fetch all messages for a session."""
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


def get_parts(db_path: str, message_id: str):
    """Fetch all parts for a message."""
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


def format_text_part(part_data: dict) -> str:
    """Extract text from a text part."""
    return part_data.get("text", "")


def format_tool_part(part_data: dict) -> str:
    """Format tool call part."""
    tool_name = part_data.get("tool", part_data.get("name", "unknown"))
    state = part_data.get("state", {})
    input_data = state.get("input", {})
    output_data = state.get("output", "")

    result = f"**Tool: {tool_name}**\n\n"
    if input_data and input_data != {}:
        result += f"Input:\n```json\n{json.dumps(input_data, indent=2)}\n```\n\n"
    if output_data:
        # Output might be a string (JSON) or dict
        if isinstance(output_data, str):
            try:
                output_json = json.loads(output_data)
                result += (
                    f"Output:\n```json\n{json.dumps(output_json, indent=2)}\n```\n"
                )
            except:
                result += f"Output:\n```\n{output_data}\n```\n"
        else:
            result += f"Output:\n```json\n{json.dumps(output_data, indent=2)}\n```\n"
    return result


def format_file_part(part_data: dict) -> str:
    """Format file part."""
    path = part_data.get("path", "unknown")
    content = part_data.get("content", "")
    return f"**File: {path}**\n```\n{content}\n```\n"


def format_patch_part(part_data: dict) -> str:
    """Format patch/diff part."""
    diff = part_data.get("diff", "")
    file_path = part_data.get("path", "unknown")
    return f"**Patch: {file_path}**\n```diff\n{diff}\n```\n"


def format_compaction_part(part_data: dict) -> str:
    """Format compaction part."""
    return f"*[Context compacted: {part_data.get('summary', '...')}]*\n\n"


def format_part(part_data: dict) -> str:
    """Format a message part based on its type."""
    part_type = part_data.get("type", "")

    if part_type == "text":
        return format_text_part(part_data)
    elif part_type == "tool":
        return format_tool_part(part_data)
    elif part_type == "file":
        return format_file_part(part_data)
    elif part_type == "reasoning":
        return f"**Reasoning:**\n{part_data.get('text', '')}\n"
    elif part_type == "step-start":
        return "---\n"
    elif part_type == "step-finish":
        return f"**Step finished:** {part_data.get('finish', '')}\n"
    elif part_type == "patch":
        return format_patch_part(part_data)
    elif part_type == "compaction":
        return format_compaction_part(part_data)
    else:
        return f"**{part_type}**\n"


def export_session_json(db_path: str, session_id: str, output_path: str):
    """Export a session to JSON format. Returns True if file was written, False if skipped."""
    messages = get_messages(db_path, session_id)

    export_data = {"session_id": session_id, "messages": []}

    for msg in messages:
        msg_data = msg["data_parsed"]
        msg_entry = {
            "id": msg["id"],
            "role": msg_data.get("role"),
            "time": format_time(
                msg_data.get("time", {}).get("created", msg["time_created"])
            ),
            "model": msg_data.get("model", {}),
            "parts": [],
        }

        parts = get_parts(db_path, msg["id"])
        for part in parts:
            msg_entry["parts"].append(part["data_parsed"])

        export_data["messages"].append(msg_entry)

    content = json.dumps(export_data, indent=2, ensure_ascii=False)
    return write_if_changed(output_path, content)


def export_session_markdown(db_path: str, session_id: str, output_path: str):
    """Export a session to Markdown format. Returns True if file was written, False if skipped."""
    messages = get_messages(db_path, session_id)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, directory FROM session WHERE id = ?", (session_id,))
    session_info = cursor.fetchone()
    conn.close()

    md_lines = []
    md_lines.append(f"# {session_info[0] if session_info else session_id}")
    md_lines.append(
        f"\n**Directory:** `{session_info[1] if session_info else 'N/A'}`\n"
    )
    md_lines.append("---\n")

    for msg in messages:
        msg_data = msg["data_parsed"]
        role = msg_data.get("role", "unknown")
        time_str = format_time(
            msg_data.get("time", {}).get("created", msg["time_created"])
        )

        md_lines.append(f"\n## {role.upper()} ({time_str})\n")

        if role == "assistant":
            model = msg_data.get("model", {})
            if model:
                md_lines.append(
                    f"*Model: {model.get('providerID', '')}/{model.get('modelID', '')}*\n"
                )

        parts = get_parts(db_path, msg["id"])
        for part in parts:
            part_data = part["data_parsed"]
            md_lines.append(format_part(part_data))

        md_lines.append("\n")

    content = "\n".join(md_lines)
    return write_if_changed(output_path, content)


def export_session_html(db_path: str, session_id: str, output_path: str):
    """Export a session to HTML format. Returns True if file was written, False if skipped."""
    messages = get_messages(db_path, session_id)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT title, directory FROM session WHERE id = ?", (session_id,))
    session_info = cursor.fetchone()
    conn.close()

    title = session_info[0] if session_info else session_id
    directory = session_info[1] if session_info else "N/A"

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{html.escape(title)}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }}
        .session-header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .message {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .message.user {{ border-left: 4px solid #007bff; }}
        .message.assistant {{ border-left: 4px solid #28a745; }}
        .message-header {{ font-weight: bold; margin-bottom: 10px; color: #333; }}
        .message-time {{ color: #666; font-size: 0.9em; }}
        .message-content {{ white-space: pre-wrap; line-height: 1.6; }}
        .model-info {{ color: #666; font-size: 0.9em; font-style: italic; }}
        .part {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }}
        .part-text {{ }}
        .part-tool {{ border-left: 3px solid #ffc107; }}
        .part-file {{ border-left: 3px solid #17a2b8; }}
        .part-reasoning {{ border-left: 3px solid #6c757d; color: #6c757d; }}
        code {{ background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
        pre {{ background: #e9ecef; padding: 15px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <div class="session-header">
        <h1>{html.escape(title)}</h1>
        <p><strong>Directory:</strong> <code>{html.escape(directory)}</code></p>
        <p><strong>Session ID:</strong> <code>{html.escape(session_id)}</code></p>
    </div>
""")

    for msg in messages:
        msg_data = msg["data_parsed"]
        role = msg_data.get("role", "unknown")
        time_str = format_time(
            msg_data.get("time", {}).get("created", msg["time_created"])
        )

        html_parts.append(f'<div class="message {role}">')
        html_parts.append(
            f'<div class="message-header">{role.upper()} <span class="message-time">({time_str})</span></div>'
        )

        if role == "assistant":
            model = msg_data.get("model", {})
            if model:
                html_parts.append(
                    f'<div class="model-info">Model: {html.escape(model.get("providerID", ""))}/{html.escape(model.get("modelID", ""))}</div>'
                )

        parts = get_parts(db_path, msg["id"])
        for part in parts:
            part_data = part["data_parsed"]
            part_type = part_data.get("type", "")

            if part_type == "text":
                content = html.escape(part_data.get("text", ""))
                html_parts.append(
                    f'<div class="part part-text"><div class="message-content">{content}</div></div>'
                )
            elif part_type == "tool":
                tool_name = html.escape(part_data.get("name", "unknown"))
                input_json = html.escape(
                    json.dumps(part_data.get("input", {}), indent=2)
                )
                output_json = html.escape(
                    json.dumps(part_data.get("output", {}), indent=2)
                )
                html_parts.append(
                    f'<div class="part part-tool"><strong>Tool: {tool_name}</strong>'
                )
                if part_data.get("input"):
                    html_parts.append(f"<pre>Input: {input_json}</pre>")
                if part_data.get("output"):
                    html_parts.append(f"<pre>Output: {output_json}</pre>")
                html_parts.append("</div>")
            elif part_type == "reasoning":
                content = html.escape(part_data.get("text", ""))
                html_parts.append(
                    f'<div class="part part-reasoning"><em>Reasoning: {content}</em></div>'
                )
            elif part_type == "step-start":
                html_parts.append("<hr>")
            elif part_type == "step-finish":
                html_parts.append(
                    f'<div class="part"><em>Step finished: {html.escape(part_data.get("finish", ""))}</em></div>'
                )

        html_parts.append("</div>")

    html_parts.append("</body></html>")

    content = "\n".join(html_parts)
    return write_if_changed(output_path, content)


def list_sessions(db_path: str, limit: int = 20, search: Optional[str] = None):
    """List available sessions."""
    sessions = get_sessions(db_path, limit=limit, search=search)

    print(f"\n{'ID':<25} {'Title':<50} {'Updated'}")
    print("-" * 100)
    for s in sessions:
        title = s["title"][:47] + "..." if len(s["title"]) > 50 else s["title"]
        time_str = format_time(s["time_updated"])
        print(f"{s['id']:<25} {title:<50} {time_str}")
    print()


def main():
    import argparse

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
        return

    if args.list or (not args.session and not args.all):
        list_sessions(args.db, limit=args.limit, search=args.search)
        return

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


if __name__ == "__main__":
    main()
