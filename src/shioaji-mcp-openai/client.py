import asyncio
import os
import shutil

from agents import (
    Agent,
    Runner,
    trace,
    gen_trace_id,
    set_default_openai_key,
)
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv


load_dotenv(".env")
set_default_openai_key(os.getenv("OPENAI_API_KEY"))


async def main():
    shioaji_server = MCPServerStdio(
        name="Shioaji",
        cache_tools_list=True,
        params={
            "command": "/Users/abnerteng/.local/bin/uv",
            "args": ["run", "src/shioaji-mcp-openai/server.py"],
        },
    )
    weather_server = MCPServerStdio(
        name="weather",
        cache_tools_list=True,
        params={
            "command": "/Users/abnerteng/.local/bin/uv",
            "args": ["run", "src/weather-server/tool.py"],
        },
    )
    history_conversation = []

    async with shioaji_server as ss, weather_server as ws:
        trace_id = gen_trace_id()
        print(f"View trace: https://platform.openai.com/traces/{trace_id}\n")

        with trace(workflow_name="Multi-MCP Server Workflow", trace_id=trace_id):
            agent = Agent(
                name="MCP Assistant",
                instructions="Use the tools to analyze csv and trade or show weather information",
                model="gpt-4o",
                mcp_servers=[ss, ws],
            )
            while True:
                message = input(
                    "Enter a prompt (MCP servers (ss, ws) are available): ")
                if message.lower() == "exit":
                    print("Exiting conversation")
                    break
                history_conversation.append(f"User: {message}")
                context = "\n".join(history_conversation)
                result = await Runner.run(starting_agent=agent, input=context)
                history_conversation.append(f"Agent: {result}")

                print(f"Result: {result.final_output}")


if __name__ == "__main__":
    if not shutil.which("uv"):
        raise RuntimeError("uv executable not found")

    asyncio.run(main())
