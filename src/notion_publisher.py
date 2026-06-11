from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_VERSION = "2022-06-28"


def _paragraph_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]},
    }


def _heading_block(text: str, level: int) -> dict:
    block_type = {1: "heading_1", 2: "heading_2", 3: "heading_3"}.get(level, "heading_3")
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]},
    }


def _bulleted_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]},
    }


def _code_block(text: str) -> dict:
    return {
        "object": "block",
        "type": "code",
        "code": {
            "language": "markdown",
            "rich_text": [{"type": "text", "text": {"content": text[:1900]}}],
        },
    }


def markdown_to_notion_blocks(markdown: str, limit: int = 95) -> list[dict]:
    blocks: list[dict] = []
    table_buffer: list[str] = []

    def flush_table() -> None:
        nonlocal table_buffer
        if table_buffer:
            blocks.append(_code_block("\n".join(table_buffer)))
            table_buffer = []

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line:
            flush_table()
            continue
        if line.startswith("|"):
            table_buffer.append(line)
            continue

        flush_table()
        if line.startswith("# "):
            blocks.append(_heading_block(line[2:].strip(), 1))
        elif line.startswith("## "):
            blocks.append(_heading_block(line[3:].strip(), 2))
        elif line.startswith("### "):
            blocks.append(_heading_block(line[4:].strip(), 3))
        elif line.startswith("- "):
            blocks.append(_bulleted_block(line[2:].strip()))
        else:
            blocks.append(_paragraph_block(line.strip()))

        if len(blocks) >= limit:
            blocks.append(_paragraph_block("Report truncated for Notion block limit. See the Markdown/HTML files in the repository for the full analysis."))
            return blocks

    flush_table()
    return blocks[:limit]


def publish_report_to_notion(markdown_path: Path, title: str) -> str | None:
    """Publish the Markdown report to Notion when credentials are configured.

    The repository is designed for Notion MCP publication in agent runtimes.
    For environments where the Python process has direct Notion API credentials,
    this function publishes through the official Notion HTTP API as a practical
    fallback while keeping the rest of the recruitment agent decoupled.
    """
    enabled = os.getenv("NOTION_ENABLED", "false").lower() == "true"
    if not enabled:
        return None

    parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not parent_page_id:
        raise RuntimeError("NOTION_ENABLED=true but NOTION_PARENT_PAGE_ID is not configured.")
    if not notion_api_key:
        raise RuntimeError("NOTION_ENABLED=true but NOTION_API_KEY is not configured.")

    markdown = markdown_path.read_text(encoding="utf-8")
    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}],
            }
        },
        "children": markdown_to_notion_blocks(markdown),
    }
    request = Request(
        NOTION_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Notion API returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach Notion API: {exc}") from exc

    return data.get("url")
