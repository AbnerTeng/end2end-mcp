import asyncio
import os
import shutil

from agents import (
    Agent,
    Runner,
    trace,
    set_default_openai_key,
)
from agents.mcp import MCPServer, MCPServerStdio
from dotenv import load_dotenv


load_dotenv('.env')
set_default_openai_key(os.getenv("OPENAI_API_KEY"))


async def run(
    mcp_server: MCPServer,
    dir_path: str
) -> None:
    agent = Agent(
        name="Trade Assistant",
        instructions=f"Please analyze the CSV file in {dir_path} and place trade positions. You must trade with the price and quantity that you've analyzed",
        model="gpt-4o",
        mcp_servers=[mcp_server],
    )
    message = "Please analyze the csv file and place trade positions"
    result = await Runner.run(starting_agent=agent, input=message)

    print(f"Result: {result.final_output}")


async def main():
    dir_path = input("Please enter the directory path: ")

    async with MCPServerStdio(
        cache_tools_list=True,
        params={
            "command": "/Users/abnerteng/.local/bin/uv",
            "args": [
                "run",
                "src/shioaji-mcp-openai/server.py"
            ]
        }
    ) as server:
        with trace(workflow_name="MCP Shioaji Workflow"):
            await run(server, dir_path)


if __name__ == "__main__":
    if not shutil.which("uv"):
        raise RuntimeError("uv executable not found")

    asyncio.run(main())
