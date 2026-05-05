"""Export services for openode_session_extractor."""

import html
import json
import sqlite3
from typing import Any

from openode_session_extractor.adapters.database import get_messages, get_parts
from openode_session_extractor.core.formatting import format_part, format_time
from openode_session_extractor.core.hashing import write_if_changed


def export_session_json(db_path: str, session_id: str, output_path: str) -> bool:
    """Export a session to JSON format.

    Args:
        db_path: Path to SQLite database.
        session_id: Session ID to export.
        output_path: Path to output JSON file.

    Returns:
        True if file was written, False if skipped.

    Raises:
        sqlite3.Error: If database access fails.
        json.JSONDecodeError: If message data is invalid JSON.

    Example:
        >>> export_session_json("/path/to/db", "session123", "/tmp/out.json")
        True
    """
    messages = get_messages(db_path, session_id)

    export_messages: list[dict[str, Any]] = []

    for msg in messages:
        msg_data = msg["data_parsed"]
        msg_entry: dict[str, Any] = {
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

        export_messages.append(msg_entry)

    export_data: dict[str, Any] = {
        "session_id": session_id,
        "messages": export_messages,
    }
    content = json.dumps(export_data, indent=2, ensure_ascii=False)
    return write_if_changed(output_path, content)


def export_session_markdown(db_path: str, session_id: str, output_path: str) -> bool:  # pylint: disable=too-many-locals
    """Export a session to Markdown format.

    Args:
        db_path: Path to SQLite database.
        session_id: Session ID to export.
        output_path: Path to output Markdown file.

    Returns:
        True if file was written, False if skipped.

    Raises:
        sqlite3.Error: If database access fails.

    Example:
        >>> export_session_markdown("/path/to/db", "session123", "/tmp/out.md")
        True
    """
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


def export_session_html(db_path: str, session_id: str, output_path: str) -> bool:  # pylint: disable=too-many-locals
    """Export a session to HTML format.

    Args:
        db_path: Path to SQLite database.
        session_id: Session ID to export.
        output_path: Path to output HTML file.

    Returns:
        True if file was written, False if skipped.

    Raises:
        sqlite3.Error: If database access fails.

    Example:
        >>> export_session_html("/path/to/db", "session123", "/tmp/out.html")
        True
    """
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
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                        Roboto, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .session-header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .message {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .message.user {{ border-left: 4px solid #007bff; }}
        .message.assistant {{ border-left: 4px solid #28a745; }}
        .message-header {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .message-time {{ color: #666; font-size: 0.9em; }}
        .message-content {{
            white-space: pre-wrap;
            line-height: 1.6;
        }}
        .model-info {{
            color: #666;
            font-size: 0.9em;
            font-style: italic;
        }}
        .part {{
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .part-text {{ }}
        .part-tool {{ border-left: 3px solid #ffc107; }}
        .part-file {{ border-left: 3px solid #17a2b8; }}
        .part-reasoning {{
            border-left: 3px solid #6c757d;
            color: #6c757d;
        }}
        code {{
            background: #e9ecef;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            background: #e9ecef;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }}
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
