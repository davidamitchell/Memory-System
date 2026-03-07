# Memory-System — GitHub Open-Brain

A **local-first**, agent-native memory system backed by GitHub Markdown files and [LanceDB](https://lancedb.github.io/lancedb/) semantic search, exposed to AI tools (Claude Desktop, Cursor, GitHub Copilot) via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

> **AI agents: read [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) for the rules and conventions that govern this repository.**

---

## How It Works

```
┌─────────────────────────────────────┐
│  AI Agent (Claude / Copilot / Cursor)│
└────────────────┬────────────────────┘
                 │ MCP tools
                 ▼
        ┌────────────────┐
        │  mcp_server.py │  ← runs locally on your machine
        └───┬────────┬───┘
            │        │
     search │        │ write
            ▼        ▼
      ┌──────────┐  ┌──────────────┐
      │  LanceDB │  │  .md files   │
      │  index   │  │  (this repo) │
      └──────────┘  └──────┬───────┘
                           │ git push
                           ▼
                    GitHub (cloud backup)
```

1. **Storage** — Your memories live as `.md` files in `/meetings`, `/journal`, and `/projects`.
2. **Vector Layer** — `mcp_server.py` embeds every file using [`BAAI/bge-small-en-v1.5`](https://huggingface.co/BAAI/bge-small-en-v1.5) and stores the index in a local `.lancedb` folder (excluded from git).
3. **MCP Bridge** — The server exposes three tools to any MCP-compatible AI client:
   - `search_brain(query)` — semantic search over all memories.
   - `add_memory(title, content, folder)` — create a new timestamped memory file.
   - `refactor_memory(file_path, new_content)` — overwrite an existing memory file.
4. **Auto-sync** — Every write is automatically committed and pushed to GitHub.

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/<you>/Memory-System.git
cd Memory-System
pip install -r requirements.txt
```

### 2. Run the MCP server

```bash
python mcp_server.py
# or point it at a different repo:
python mcp_server.py --repo-path /path/to/repo --db-path /path/to/.lancedb
```

### 3. Connect your AI client

**Claude Desktop** — add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "open-brain": {
      "command": "python",
      "args": ["/path/to/Memory-System/mcp_server.py"]
    }
  }
}
```

**Cursor** — add the same block under `mcp` in your Cursor settings.

---

## Repository Layout

```
Memory-System/
├── .github/
│   ├── copilot-instructions.md  # AI agent instructions (read this first)
│   ├── skills/                  # Agent skills submodule (davidamitchell/Skills)
│   └── workflows/
│       └── sync-skills.yml      # Weekly skills submodule update
├── docs/
│   └── adr/                     # Architecture Decision Records (MADR format)
├── mcp_server.py              # MCP server + file-watcher + LanceDB indexer
├── requirements.txt           # Python dependencies
├── getting-started-prompt.md  # Original architecture brief & PRD
├── BACKLOG.md                 # Work backlog (backlog-manager skill format)
├── PROGRESS.md                # Append-only session history
├── CHANGELOG.md               # User-facing change log (Keep a Changelog)
├── meetings/                  # Meeting notes
├── journal/                   # Daily thoughts & reflections
└── projects/                  # Project context & decisions
```

---

## Cost

| Component | Cost |
|---|---|
| GitHub storage | Free |
| LanceDB (embedded) | Free |
| Embeddings (`bge-small-en-v1.5`, local) | Free |
| **Total** | **$0.00 / month** |

---

## Further Reading

- [`getting-started-prompt.md`](./getting-started-prompt.md) — full PRD and architectural blueprint
- [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — rules for AI agents working in this repo
