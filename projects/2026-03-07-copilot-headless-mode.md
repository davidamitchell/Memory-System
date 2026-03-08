---
title: "Copilot Headless Mode Setup"
date: 2026-03-07
tags: [copilot, headless, mcp, setup, github-actions]
superseded_by: ""
---

# Copilot Headless Mode Setup

## Context

This note documents the files added to enable GitHub Copilot's coding agent to
operate on this memory system from the **GitHub web UI or mobile app**, with no
local IDE or terminal required.

## Files Added

### `.github/copilot-setup-steps.yml`

Prepares the ephemeral Copilot sandbox before the agent starts working.

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

Why pre-warm the model? `sentence-transformers` downloads ~130 MB from HuggingFace
on first use. Doing it in the setup step means the first `search_brain` call
returns in milliseconds rather than blocking on a download.

### `.vscode/mcp.json`

Tells Copilot (and VS Code) how to start the MCP server via stdio transport.

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

This file is picked up automatically by:
- VS Code + GitHub Copilot extension (with `github.copilot.chat.mcp.enabled: true`)
- GitHub Copilot coding agent running in the cloud sandbox

## Headless Workflow

1. Open **github.com** or the **GitHub mobile app**.
2. Navigate to this repository → **Issues → New issue**.
3. Describe the memory task (e.g. "Add a note about today's architecture decision").
4. Assign the issue to **@copilot** (Assignees panel).
5. Copilot sets up the sandbox, starts the MCP server, and completes the task.
6. Review and merge the resulting Pull Request.

## Key Constraints

- The `.lancedb/` index is **not persisted** between sessions (excluded from git).
  Each session rebuilds from `.md` files. For typical repo sizes this takes < 30 s.
- The background file-watcher runs only for the lifetime of the agent session.
- Copilot needs **write permission** to open PRs. Grant it under
  **Settings → Copilot → Coding agent → Repository access**.

## Related

- [`.github/copilot-instructions.md`](../.github/copilot-instructions.md) — AI agent constitution and headless-mode section 15
- [README.md](../README.md) — Quick-start and MCP configuration reference
- [getting-started-prompt.md](../getting-started-prompt.md) — Original architecture PRD
