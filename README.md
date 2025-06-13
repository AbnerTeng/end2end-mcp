# end2end-mcp

An end-to-end example of building Model Context Protocol (MCP) clients and communicates between several MCP servers with OpenAI compatible APIs.

![image](asset/screen_record.gif)

## TL;DR

You can run your MCP servers with a similar method as you run them with Claude Desktop App for just a simple command:

```bash
uv run python client/client.py
```

## Prerequisites

1. Make sure you have `uv` installed.

```bash
uv venv

source .venv/bin/activate

uv sync
```

## Brief Introduction

### Example MCP servers

1. Shioaji: An example MCP server that provides basic stock trading functionalities using [Shioaji API](https://sinotrade.github.io/), you'll need further configuration to properly use it.
2. Weather: Just a simple example from [MCP official doc](https://modelcontextprotocol.io/quickstart/server)

### MCP host

Instead of following the Claude API, I replace it with OpenAI compatible APIs, supporting two main LLM providers:

1. OpenAI
2. Ollama

Where you can change between them by modifying the `LLM_PROVIDER` environment variable.

### Connect with MCP host

After choosing your LLM provider, you can connect servers with the MCP host by modifying the `config.json` file, just like the example below:

```json
{
  "mcpServers": {
    "weather": {
      "args": [
        "--directory",
        "root_path",
        "run",
        "server_file.py"
      ],
      "command": "uv_exec_command"
    }
  }
}
```

### Run MCP host

You can run the MCP host with the following command:

```bash
uv run python client/client.py
```

After finishing playing with the MCP host, you can just type `exit` to leave

> The **shioaji-server** in `server/` is certified by MCP Review. The [mcp review link](https://mcpreview.com/mcp-servers/AbnerTeng/shioaji-mcp)
