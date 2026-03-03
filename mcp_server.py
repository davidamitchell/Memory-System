#!/usr/bin/env python3
"""
mcp_server.py — GitHub Open-Brain MCP Server

Provides three MCP tools to AI agents:
  - search_brain(query)          : Semantic search over memory files via LanceDB.
  - add_memory(title, content, folder) : Create a new timestamped Markdown memory file.
  - refactor_memory(file_path, new_content) : Overwrite an existing memory file.

The server also runs a background file-watcher that re-indexes any .md file
that is created or modified, and auto-commits / pushes changes to GitHub.

Dependencies (install once):
    pip install lancedb sentence-transformers watchdog mcp

Usage:
    python mcp_server.py [--repo-path /path/to/repo] [--db-path /path/to/.lancedb]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from sentence_transformers import SentenceTransformer
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

EMBED_MODEL_NAME = "BAAI/bge-small-en-v1.5"
MEMORY_FOLDERS = ("meetings", "journal", "projects")
TABLE_NAME = "memories"

# LanceDB schema
SCHEMA = pa.schema(
    [
        pa.field("file_path", pa.string()),
        pa.field("title", pa.string()),
        pa.field("content", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)),
    ]
)


# ---------------------------------------------------------------------------
# Embedding helper
# ---------------------------------------------------------------------------


class Embedder:
    """Thin wrapper around SentenceTransformer with lazy loading."""

    _model: SentenceTransformer | None = None

    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            log.info("Loading embedding model %s …", self._model_name)
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed(self, text: str) -> list[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()


# ---------------------------------------------------------------------------
# LanceDB index manager
# ---------------------------------------------------------------------------


class MemoryIndex:
    """Manages the LanceDB table for memory files."""

    def __init__(self, db_path: str, embedder: Embedder) -> None:
        self._db = lancedb.connect(db_path)
        self._embedder = embedder
        self._table = self._open_or_create_table()

    def _open_or_create_table(self) -> Any:
        if TABLE_NAME in self._db.table_names():
            return self._db.open_table(TABLE_NAME)
        return self._db.create_table(TABLE_NAME, schema=SCHEMA)

    def upsert(self, file_path: str, content: str) -> None:
        """Add or replace a memory entry for the given file path."""
        title = Path(file_path).stem
        vector = self._embedder.embed(content)
        # Remove existing entry for this file, then add the new one.
        try:
            self._table.delete(f'file_path = "{file_path}"')
        except Exception:
            pass
        self._table.add(
            [{"file_path": file_path, "title": title, "content": content, "vector": vector}]
        )
        log.info("Indexed %s", file_path)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        vector = self._embedder.embed(query)
        results = (
            self._table.search(vector)
            .select(["file_path", "title", "content"])
            .limit(top_k)
            .to_list()
        )
        return results


# ---------------------------------------------------------------------------
# File watcher
# ---------------------------------------------------------------------------


class MarkdownHandler(FileSystemEventHandler):
    """Re-indexes .md files on creation or modification."""

    def __init__(self, index: MemoryIndex, repo_path: Path) -> None:
        self._index = index
        self._repo_path = repo_path

    def _should_index(self, path: str) -> bool:
        p = Path(path)
        if p.suffix.lower() != ".md":
            return False
        # Only index files inside the memory folders or the root.
        rel = p.relative_to(self._repo_path)
        if rel.parts[0] in MEMORY_FOLDERS or len(rel.parts) == 1:
            return True
        return False

    def _handle(self, path: str) -> None:
        if not self._should_index(path):
            return
        try:
            content = Path(path).read_text(encoding="utf-8")
            rel_path = str(Path(path).relative_to(self._repo_path))
            self._index.upsert(rel_path, content)
        except Exception as exc:
            log.error("Failed to index %s: %s", path, exc)

    def on_created(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory:
            self._handle(event.src_path)


# ---------------------------------------------------------------------------
# Git helper
# ---------------------------------------------------------------------------


def git_commit_and_push(repo_path: Path, message: str) -> None:
    """Stage all changes, commit, and push to origin."""
    try:
        subprocess.run(["git", "-C", str(repo_path), "add", "-A"], check=True, capture_output=True)
        result = subprocess.run(
            ["git", "-C", str(repo_path), "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode == 0:
            return  # Nothing to commit
        subprocess.run(
            ["git", "-C", str(repo_path), "commit", "-m", message],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "-C", str(repo_path), "push"],
            check=True,
            capture_output=True,
        )
        log.info("Committed and pushed: %s", message)
    except subprocess.CalledProcessError as exc:
        log.error("Git error: %s", exc.stderr.decode(errors="replace"))


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------


def build_server(repo_path: Path, index: MemoryIndex) -> Server:
    server = Server("open-brain")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="search_brain",
                description="Semantic search over all memory files. Returns the top matching notes.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Natural language search query"},
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default 5)",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="add_memory",
                description=(
                    "Create a new timestamped Markdown memory file in the specified folder. "
                    "Returns the relative path of the created file."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Short title for the memory"},
                        "content": {"type": "string", "description": "Full Markdown content"},
                        "folder": {
                            "type": "string",
                            "description": "Target folder: meetings | journal | projects",
                            "enum": list(MEMORY_FOLDERS),
                            "default": "journal",
                        },
                    },
                    "required": ["title", "content"],
                },
            ),
            Tool(
                name="refactor_memory",
                description="Overwrite an existing memory file with new content.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative path to the file (e.g. journal/2025-06-15-my-note.md)",
                        },
                        "new_content": {"type": "string", "description": "New Markdown content"},
                    },
                    "required": ["file_path", "new_content"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "search_brain":
            query = arguments["query"]
            top_k = int(arguments.get("top_k", 5))
            results = index.search(query, top_k=top_k)
            if not results:
                return [TextContent(type="text", text="No matching memories found.")]
            lines = []
            for r in results:
                lines.append(f"### {r['title']}\n**File:** `{r['file_path']}`\n\n{r['content']}\n")
            return [TextContent(type="text", text="\n---\n".join(lines))]

        if name == "add_memory":
            title: str = arguments["title"]
            content: str = arguments["content"]
            folder: str = arguments.get("folder", "journal")
            date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
            slug = title.lower().replace(" ", "-").replace("/", "-")
            filename = f"{date_str}-{slug}.md"
            target_dir = repo_path / folder
            target_dir.mkdir(parents=True, exist_ok=True)
            file_path = target_dir / filename
            file_path.write_text(content, encoding="utf-8")
            rel_path = str(file_path.relative_to(repo_path))
            # Index immediately (the watcher will also catch it, but this is faster)
            index.upsert(rel_path, content)
            git_commit_and_push(repo_path, f"memory: add {rel_path}")
            return [TextContent(type="text", text=f"Memory saved to `{rel_path}`.")]

        if name == "refactor_memory":
            rel_file_path: str = arguments["file_path"]
            new_content: str = arguments["new_content"]
            abs_path = repo_path / rel_file_path
            if not abs_path.exists():
                return [TextContent(type="text", text=f"File not found: `{rel_file_path}`.")]
            abs_path.write_text(new_content, encoding="utf-8")
            index.upsert(rel_file_path, new_content)
            git_commit_and_push(repo_path, f"memory: refactor {rel_file_path}")
            return [TextContent(type="text", text=f"Memory `{rel_file_path}` updated.")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    return server


# ---------------------------------------------------------------------------
# Initial bulk-index
# ---------------------------------------------------------------------------


def bulk_index(repo_path: Path, index: MemoryIndex) -> None:
    """Index all existing .md files in memory folders."""
    for folder in MEMORY_FOLDERS:
        folder_path = repo_path / folder
        if not folder_path.exists():
            continue
        for md_file in folder_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                rel_path = str(md_file.relative_to(repo_path))
                index.upsert(rel_path, content)
            except Exception as exc:
                log.error("Could not index %s: %s", md_file, exc)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open-Brain MCP Server")
    parser.add_argument(
        "--repo-path",
        default=os.getcwd(),
        help="Path to the cloned memory repository (default: current directory)",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Path for the LanceDB index (default: <repo-path>/.lancedb)",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    repo_path = Path(args.repo_path).resolve()
    db_path = args.db_path or str(repo_path / ".lancedb")

    log.info("Repo path : %s", repo_path)
    log.info("LanceDB   : %s", db_path)

    embedder = Embedder(EMBED_MODEL_NAME)
    index = MemoryIndex(db_path, embedder)

    # Bulk-index existing files
    log.info("Running initial bulk index …")
    bulk_index(repo_path, index)

    # Start file watcher in a background thread
    handler = MarkdownHandler(index, repo_path)
    observer = Observer()
    observer.schedule(handler, str(repo_path), recursive=True)
    observer.start()
    log.info("File watcher started.")

    # Start MCP server (stdio transport)
    server = build_server(repo_path, index)
    async with stdio_server() as (read_stream, write_stream):
        log.info("MCP server ready.")
        await server.run(read_stream, write_stream, server.create_initialization_options())

    observer.stop()
    observer.join()


if __name__ == "__main__":
    asyncio.run(main())
