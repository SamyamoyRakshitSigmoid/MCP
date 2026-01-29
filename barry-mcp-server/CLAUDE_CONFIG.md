# Claude Desktop Configuration for Barry Server

## Simple Configuration (Recommended)

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "barry-server": {
      "command": "/Users/username/Documents/MCP Servers/barry-mcp-server/.venv/bin/python",
      "args": [
        "-m",
        "barry_server.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/username/Documents/MCP Servers/barry-mcp-server/src"
      }
    }
  }
}
```

## What This Does

- Uses the virtual environment's Python (which has pandas and mcp installed)
- Runs the server module directly with `-m barry_server.server`
- Sets PYTHONPATH so Python can find the barry_server package
- No complicated `uv run` or script entry points needed!

## Testing

Test it works:
```bash
cd "/Users/username/Documents/MCP Servers/barry-mcp-server"
PYTHONPATH=src .venv/bin/python -m barry_server.server
```

You should see:
```
🚀 Starting Barry MCP Server...
✓ Loaded dataset from: ...
✓ Dataset: 81,716 rows and 288 columns
✓ Server ready!
```
