# Memory-System — GitHub Open-Brain

A **local-first**, agent-native memory system backed by GitHub Markdown files and [LanceDB](https://lancedb.github.io/lancedb/) semantic search, exposed to AI tools (Claude Desktop, Cursor, GitHub Copilot) via the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

> **Read [`AGENTS.md`](./AGENTS.md) for the constitution that governs how AI agents should interact with this repository.**

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

**GitHub Copilot (VS Code)** — the `.vscode/mcp.json` file in this repository is picked up automatically. Enable MCP in VS Code settings:

```json
{
  "github.copilot.chat.mcp.enabled": true
}
```

---

## GitHub Copilot in Headless Mode (Web / Mobile)

You can interact with this memory system from **github.com or the GitHub mobile app** — no local IDE or terminal required.

### How it works

1. GitHub spins up an ephemeral cloud sandbox for the Copilot coding agent.
2. `.github/copilot-setup-steps.yml` installs dependencies and pre-warms the embedding model.
3. `.vscode/mcp.json` tells Copilot how to launch `mcp_server.py` (stdio transport).
4. The agent can then call all three MCP tools (`search_brain`, `add_memory`, `refactor_memory`).

### Step-by-step

1. Open this repository on **github.com** (or the mobile app).
2. Go to **Issues → New issue** and describe your memory task.
3. In the **Assignees** panel, assign the issue to **Copilot**.
4. Copilot opens a session, runs `copilot-setup-steps.yml`, and works on the task.
5. It opens a **Pull Request** with the resulting `.md` file changes.
6. Review and merge the PR from the browser or phone.

### copilot-setup-steps.yml

The file `.github/copilot-setup-steps.yml` configures the sandbox:

```yaml
steps:
  - name: Set up Python 3.11
    uses: actions/setup-python@v5
    with:
      python-version: "3.11"

  - name: Install Open-Brain dependencies
    run: pip install --upgrade pip && pip install -r requirements.txt

  - name: Pre-warm BAAI/bge-small-en-v1.5 embedding model
    run: |
      python - <<'EOF'
      from sentence_transformers import SentenceTransformer
      SentenceTransformer("BAAI/bge-small-en-v1.5")
      EOF
```

### MCP configuration

`.vscode/mcp.json` — works for both VS Code Copilot and the headless coding agent:

```json
{
  "servers": {
    "open-brain": {
      "type": "stdio",
      "command": "python",
      "args": ["${workspaceFolder}/mcp_server.py"]
    }
  }
}
```

---

## Repository Layout

```
Memory-System/
├── AGENTS.md                  # AI agent constitution (read this first)
├── mcp_server.py              # MCP server + file-watcher + LanceDB indexer
├── requirements.txt           # Python dependencies
├── getting-started-prompt.md  # Original architecture brief & PRD
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
- [`AGENTS.md`](./AGENTS.md) — rules for AI agents working in this repo
