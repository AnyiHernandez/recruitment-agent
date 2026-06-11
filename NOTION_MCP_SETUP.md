# Notion MCP Setup Instructions

These are the steps Pablo can follow to configure Notion MCP and run this recruitment agent with new vacancies.

## 1. Create a Notion Integration

1. Go to Notion's integration page.
2. Create a new internal integration.
3. Copy the integration secret.
4. Open the Notion page or workspace where reports should be published.
5. Share that page with the integration.
6. Copy the target parent page ID.

## 2. Configure Environment Variables

Create a `.env` file from the example:

```bash
copy .env.example .env
```

Set:

```env
RECRUITMENT_DATA_DIR=sample-pack/sample-pack
REPORTS_DIR=reports
NOTION_ENABLED=true
NOTION_PARENT_PAGE_ID=<notion-parent-page-id>
NOTION_API_KEY=<notion-integration-secret>
```

`NOTION_API_KEY` is used by the Python fallback publisher. The MCP server can use the same integration secret.

If the MCP server expects a differently named token, also map the same secret to the variable it requires:

```env
NOTION_TOKEN=<notion-integration-secret>
```

## 3. Configure Notion MCP In Cowork / Codex / OpenCode

Add a Notion MCP server using the environment's MCP configuration UI or JSON config.

Use the official Notion MCP server if available in the tool catalog. If a manual config is required, use the Notion MCP package supported by the environment and pass the Notion integration secret as an environment variable.

Conceptual MCP config:

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "NOTION_API_KEY": "<notion-integration-secret>"
      }
    }
  }
}
```

If the environment uses a different Notion MCP package name, keep the same intent:

- Start a Notion MCP server.
- Authenticate it with the Notion integration secret.
- Ensure it exposes page creation/update tools.
- Share the destination Notion page with the integration.

## 4. Run The Agent

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python src/main.py
```

The agent will:

1. Read vacancies from `sample-pack/sample-pack/jobs`.
2. Read candidates from `sample-pack/sample-pack/candidates`.
3. Generate Markdown and HTML reports in `reports/`.
4. Attempt Notion publication when a Notion MCP transport is available.

## 5. Running With New Vacancies

Replace the input files:

```text
sample-pack/sample-pack/jobs
sample-pack/sample-pack/candidates
```

Or point to another folder:

```env
RECRUITMENT_DATA_DIR=path/to/new-pack
```

Expected structure:

```text
new-pack/
├── jobs/
└── candidates/
```

Then run:

```bash
python src/main.py
```

## 6. Publishing Behavior

The analysis pipeline and report generation are fully implemented locally.

The `src/notion_publisher.py` module is intentionally isolated so the Notion publishing transport can be swapped depending on the MCP runtime provided by Cowork, Codex, or OpenCode.

When `NOTION_ENABLED=true`, `NOTION_PARENT_PAGE_ID`, and `NOTION_API_KEY` are set, the current implementation publishes through the official Notion HTTP API. This gives Pablo a working publication path even if the Python process cannot directly call the active MCP tool transport.

In an environment with a dedicated Notion MCP tool, replace `publish_report_to_notion` with the MCP page creation call while keeping the same interface:

```python
publish_report_to_notion(markdown_path, title) -> notion_url
```
