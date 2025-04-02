# Shioaji-MCP

An MCP (Model Context Protocol) server for Shioaji api.

## Prerequisites

1. Make sure you have `uv` installed.

```bash
uv venv

source .venv/bin/activate

uv sync
```


2. Install Claude Desktop App

## Generate config files for Claude Desktop App

```bash
# MacOS

~/Library/Application Support/Claude/claude_desktop_config.json

# Windows

%APPDATA%\Claude\claude_desktop_config.json
```

Inside the `.json` file, write the execution config for Claude Desktop to recognize

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Desktop",
        "/Users/username/Downloads"
      ]
    }
  }
}
```
```
