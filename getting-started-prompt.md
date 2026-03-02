# Getting Started Prompt: GitHub Open-Brain Memory System

> **Note:** This document captures the original architectural brief and PRD for the GitHub Open-Brain project.

---

## Part 1: Initial Architecture Brief

Yes, you can absolutely build a GitHub-based memory system using the Model Context Protocol (MCP) and LanceDB. While the video you referenced focuses on a "Postgres + Supabase" stack, your proposed stack of GitHub + LanceDB + Markdown is a highly efficient, "local-first" alternative that is popular in the developer community.

Here is how you can architect this system to integrate with your AI agents and chat bots.

### System Architecture

Instead of a live cloud database, you will use a **Local-to-GitHub sync pattern**.

- **Storage:** Your memory lives in a GitHub repository as `.md` files. This gives you version control, easy manual editing, and a free cloud backup.
- **Vector Database:** LanceDB is perfect for this because it is serverless and stores data in files (OSS format). You can store the LanceDB index directly in your GitHub repo or a local folder synced to it.
- **The Bridge (MCP):** You use an MCP Server (running locally on your machine) that "watches" your Markdown files, embeds them into LanceDB, and provides a search tool to your AI clients (Claude Desktop, Cursor, etc.).

### How to Build It

#### 1. The GitHub Setup

- Create a private repository (e.g., `my-ai-memory`).
- Organize it with simple folders like `/meetings`, `/journal`, and `/projects`.
- The AI will read these `.md` files to understand your context.

#### 2. The LanceDB Integration

Since LanceDB is an embedded database, you don't need to host it. You can write a simple Python or Node.js script that:

- Scans your GitHub repo folder.
- Uses an embedding model (like OpenAI's `text-embedding-3-small` or a local one via Ollama) to turn your notes into vectors.
- Saves that index into a `.lancedb` folder in your repo.

#### 3. The MCP Server

You need an MCP server that exposes two main tools to your AI agents:

- `search_memory(query)`: Performs a semantic search using LanceDB to find relevant notes.
- `add_memory(content)`: Appends a new Markdown file to your GitHub repo (which then gets auto-indexed).

### Why This Fits Your Request

- **No SaaS Middlemen:** Unlike the Supabase approach in the video, you aren't relying on a third-party database provider. If GitHub disappeared, you still have the files locally.
- **Agent Readable:** By using MCP, your memory becomes "agent-native." When you chat with Claude or Cursor, the agent can autonomously call your `search_memory` tool to see what you decided "last Tuesday" without you having to copy-paste.
- **Low Cost:** GitHub and LanceDB are free. Your only cost would be the tiny fraction of a cent for embeddings, often totaling less than $0.10 a month.

### Implementation Tip

If you want to skip building the MCP server from scratch, you can look for existing "Filesystem" or "Markdown" MCP servers on GitHub and modify them to include a LanceDB search step. This allows you to "Chat with your GitHub Repo" across any AI tool that supports the MCP standard.

---

## Part 2: Full PRD — GitHub Open-Brain

This is the complete, consolidated PRD and architectural blueprint for **GitHub Open-Brain**. It defines a system that is private, free to operate, and specifically designed to let AI agents manage and improve their own memory.

### 1. Product Concept: The "Agent-First" Open-Brain

Most AI memory is a "Silo." Claude knows what you said in Claude; ChatGPT knows what you said in ChatGPT. Open-Brain moves that memory into a **private GitHub repository you own**.

By using the Model Context Protocol (MCP) and LanceDB, any AI agent (Cursor, Claude Desktop, Copilot) can read from and write to this repository. It treats your notes not just as text, but as a **Vectorized Knowledge Graph**.

#### Core Goals

- **Interoperability:** One "Brain" for every AI tool.
- **Agent Autonomy:** Agents are "hired" to maintain the repo, prune old data, and cross-link ideas.
- **Zero-Cost Privacy:** Uses local Open-Source embeddings (No OpenAI/Anthropic API fees for memory) and GitHub's free storage.

### 2. Technical Architecture

The system functions as a **Local-Cloud Hybrid**.

- **Storage (Source of Truth):** A private GitHub Repo containing `.md` files.
- **Vector Layer (Performance):** LanceDB (serverless/embedded) stored in a local `.lancedb` folder.
- **The Bridge (Protocol):** An MCP Server running locally that "watches" your Markdown files and provides tools to the AI.

### 3. The "Standard Agent-First" Definition

To be Agent-First, a system must move beyond "Search" and into "Agency."

- **Bi-Directional Access:** The agent doesn't just read your notes; it has the authority to write new ones and refactor old ones.
- **Versioning as Context:** The agent uses Git history to understand how your thinking has evolved over time.
- **Self-Correction:** The agent is explicitly tasked with finding "Bugs" in its own memory structure and fixing them.

### 4. Implementation Guide

#### Step 1: Initialize the Repo

- Create a private GitHub repo: `my-open-brain`.
- Clone it to your local machine.
- Install dependencies: `pip install lancedb sentence-transformers watchdog`.

#### Step 2: Define the AGENTS.md Constitution

Create `AGENTS.md` in the root. This is the most important file. It tells the agent how to behave. You must include this directive:

> **Mandatory System Self-Improvement**
>
> - **Architectural Awareness:** You are not just a user of this memory; you are its architect. Always look for ways to improve the tagging, folder structure, or AGENTS.md logic.
> - **Proactive Maintenance:** If you find a note that is outdated or contradicts a newer decision, do not delete it—create a `superseded_by` link to the new note.
> - **Optimization:** Periodically suggest new local embedding models or LanceDB indexing strategies if you detect retrieval latency or poor semantic matches.
> - **Knowledge Graphing:** Every time you write a memory, search for 3 related existing memories and add a `## Related` section with links.

#### Step 3: The Background Sync Service

You will run a local Python script (The MCP Server) that performs three automated tasks:

- **File Watcher:** Whenever you (or an agent) saves a `.md` file, it immediately updates the local LanceDB index using a local model (e.g., `BAAI/bge-small-en-v1.5`).
- **Git Manager:** It automatically commits and pushes changes to GitHub so your "Brain" is backed up in real-time.
- **MCP Tool Provider:** It exposes these tools to your AI Chat:
  - `search_brain(query)`: High-speed semantic search.
  - `add_memory(title, content)`: Creates a new timestamped Markdown file.
  - `refactor_memory(file_path, new_content)`: Allows the agent to clean up existing notes.

### 5. Why This Works with GitHub Copilot & Claude

When you open GitHub Copilot in VS Code, it sees the repo structure. It reads `AGENTS.md` and realizes it has "permission" to improve the code.

When you use Claude Desktop, you connect it to the same local MCP server. Because both tools are looking at the same LanceDB index and the same GitHub files, the context is identical.

#### Example Workflow

- **Morning (Mobile):** You're on the train and type a thought into a GitHub Issue on your phone.
- **Mid-day (Claude):** You ask Claude to "Summarize my morning thoughts." Claude uses MCP to pull the new file from the repo and index it via LanceDB.
- **Evening (Copilot):** You start coding. Copilot says, "I see you were thinking about LanceDB indexing this morning; should I implement that schema now?"

### 6. Success Metrics

- **Cost:** $0.00 (using local embeddings and GitHub Free).
- **Latency:** Retrieval in <100ms (local LanceDB is faster than cloud APIs).
- **Resilience:** If GitHub goes down, your memory is still local. If your laptop dies, your memory is on GitHub.
