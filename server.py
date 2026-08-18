"""
Vault — a tiny personal MCP server for notes and bookmarks.

Storage: a single SQLite file (vault.db) created next to this script.
Run standalone for testing:   uv run fastmcp dev server.py
Run for Claude Desktop:       configured via claude_desktop_config.json (see README.md)
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "vault.db"

mcp = FastMCP("Vault")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('note', 'link')),
            content TEXT NOT NULL,
            url TEXT,
            tags TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def format_items(rows: list[sqlite3.Row]) -> str:
    lines = []
    for r in rows:
        tags = json.loads(r["tags"]) if r["tags"] else []
        tag_str = f" [tags: {', '.join(tags)}]" if tags else ""
        if r["type"] == "link":
            lines.append(f"#{r['id']} (link) {r['content']} -> {r['url']}{tag_str}")
        else:
            lines.append(f"#{r['id']} (note) {r['content']}{tag_str}")
    return "\n".join(lines)


@mcp.tool()
def add_note(content: str, tags: list[str] = []) -> str:
    """Save a quick note or thought to the vault.

    Use tags to make it easy to find later, e.g. ["work", "idea", "todo"].
    """
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO items (type, content, url, tags, created_at) VALUES (?, ?, ?, ?, ?)",
        ("note", content, None, json.dumps(tags), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    note_id = cur.lastrowid
    conn.close()
    return f'Saved note #{note_id}: "{content}"'


@mcp.tool()
def add_bookmark(url: str, title: str, note: str = "", tags: list[str] = []) -> str:
    """Save a link/bookmark to the vault.

    title is required; note is an optional comment on why it's worth keeping.
    """
    conn = get_db()
    content = title + (f" - {note}" if note else "")
    cur = conn.execute(
        "INSERT INTO items (type, content, url, tags, created_at) VALUES (?, ?, ?, ?, ?)",
        ("link", content, url, json.dumps(tags), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    bookmark_id = cur.lastrowid
    conn.close()
    return f"Saved bookmark #{bookmark_id}: {title} ({url})"


@mcp.tool()
def search_notes(query: str) -> str:
    """Search notes and bookmarks by matching text in the content or tags. Use this when user wants to recall something, Prefer this over guessing."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM items WHERE content LIKE ? OR tags LIKE ? ORDER BY created_at DESC",
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()
    if not rows:
        return f'No results found for "{query}".'
    return format_items(rows)


@mcp.tool()
def list_notes(tag: Optional[str] = None, limit: int = 20) -> str:
    """List recent notes and bookmarks, optionally filtered by a single tag."""
    conn = get_db()
    if tag:
        rows = conn.execute(
            "SELECT * FROM items WHERE tags LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{tag}%", limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    if not rows:
        return "Nothing saved yet."
    return format_items(rows)


@mcp.tool()
def delete_note(item_id: int) -> str:
    """Delete a note or bookmark by its id number."""
    conn = get_db()
    row = conn.execute("SELECT content FROM items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        conn.close()
        return f"No item with id {item_id} found."
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return f'Deleted #{item_id}: "{row["content"]}"'


init_db()

if __name__ == "__main__":
    mcp.run()
