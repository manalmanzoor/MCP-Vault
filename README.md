# Vault — a tiny personal MCP server

Notes + bookmarks, stored in a single SQLite file, exposed to Claude through 5 tools:
`add_note`, `add_bookmark`, `search_notes`, `list_notes`, `delete_note`.

## 1. Install uv (one-time)

Open PowerShell and run:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal after this so `uv` is on PATH.

## 2. Set up the project

Unzip this folder somewhere permanent, e.g. `C:\Users\<you>\mcp-vault`. Then from inside it:

```powershell
cd C:\Users\<you>\mcp-vault
uv sync
```

This creates a virtual environment and installs `fastmcp`.

## 3. Test it standalone (before touching Claude Desktop)

```powershell
uv run fastmcp dev server.py
```

This opens the MCP Inspector in your browser. Click into the Tools tab, try calling
`add_note` with some text, then `list_notes` — you should see it come back. Ctrl+C to stop
it once you're happy.

## 4. Wire it into Claude Desktop

Open (or create) this file:

```
%APPDATA%\Claude\claude_desktop_config.json
```

Add a `vault` entry under `mcpServers`. If the file already has other servers in it, just
add this key alongside them — don't replace the whole file.

```json
{
  "mcpServers": {
    "vault": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\Users\\<you>\\mcp-vault",
        "fastmcp",
        "run",
        "server.py"
      ]
    }
  }
}
```

Replace `C:\\Users\\<you>\\mcp-vault` with wherever you actually put the folder — use
double backslashes as shown.

## 5. Restart Claude Desktop

Fully quit it (right-click the tray icon → Quit, not just closing the window) and reopen.
Look for the tools icon in the chat box — click it and you should see the 5 vault tools
listed.

## 6. Try it

- "Save a note: renew passport, tag it todo"
- "Save this link: https://example.com, title it Example, tag it reference"
- "What have I saved tagged todo?"
- "Search my notes for passport"
- "Delete note 1"

Your data lives in `vault.db` right next to `server.py` — it's just a SQLite file, so you
can open it with any SQLite browser if you want to poke at it directly.

## Screenshots

<img width="455" height="237" alt="image" src="https://github.com/user-attachments/assets/a2372dc4-3110-426e-b20e-ea9b3b78eff2" />

<img width="456" height="214" alt="image" src="https://github.com/user-attachments/assets/74e7ee94-65fd-4b58-afc6-8dbe9a09d9d2" />



## Notes

- Every tool's docstring is what Claude reads to decide when to call it — if you rename
  or repurpose a tool, keep the docstring accurate, that's the whole interface.
- If Claude Desktop doesn't pick up the server, check `%APPDATA%\Claude\logs\` for errors —
  usually it's a wrong path in the config.
