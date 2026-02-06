# SQLite Invoice MCP Server

## Prerequisites

1. `uv` installed
2. Project dependencies installed

```bash
cd agent-sdk-lab
uv sync
```

## Run MCP Server (HTTP)

Default run (Streamable HTTP on `127.0.0.1:8000/mcp`):

```bash
cd agent-sdk-lab
uv run python mcp_invoice_server.py
```

Custom host/port/path:

```bash
uv run python mcp_invoice_server.py --transport streamable-http --host 0.0.0.0 --port 8001 --path /mcp
```

## Test with MCP Inspector

Start Inspector:

```bash
npx @modelcontextprotocol/inspector@0.19.0
```

In the Inspector UI:

1. Select transport: `Streamable HTTP`
2. Enter URL: `http://127.0.0.1:8000/mcp`
3. List tools and call `get_invoices_by_customer_name`
4. Use sample input:

```json
{"customer_name":"Pioneer Tech"}
```

## Quick Endpoint Check

Use this only to confirm endpoint is up:

```bash
curl -i http://127.0.0.1:8000/mcp
```

Expected result is `406 Not Acceptable` without MCP request headers/body, which confirms the HTTP route is reachable.
