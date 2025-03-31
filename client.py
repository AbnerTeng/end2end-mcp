import asyncio
import json
import os
from typing import Any, Dict, List
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv(".env")


def serialize_text_content(text_content):
    return {
        "type": text_content.type,
        "text": text_content.text,
        "annotations": (
            text_content.annotations if text_content.annotations is not None else ""
        ),
    }


class MCPClient:
    def __init__(self) -> None:
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.client = OpenAI(
            # base_url="https://ycden-ollama.ngrok.app/v1",
            # api_key="ollama",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
        )
        # self.model = "llama3.2:1b"
        self.model = "gpt-4o"
        self.tools = []

    def get_response(self, messages: List, tools: List) -> Any:
        print(messages)
        response = self.client.chat.completions.create(
            model=self.model, max_tokens=1000, messages=messages, tools=tools
        )

        return response

    async def get_tools(self) -> List[Dict[str, Any]]:
        response = await self.session.list_tools()
        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]

        return available_tools

    async def connect_to_server(self, server_script_path: str) -> None:
        """
        Connect to an MCP server

        Args:
            server_script_path (str): Path to the server script (.py or .js)
        """
        server_params = StdioServerParameters(
            command="python", args=[server_script_path], env=None
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # list all tools available on the server
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        available_tools = await self.get_tools()
        response = self.get_response(messages, available_tools)

        final_text = []
        tool_results = []

        message = response.choices[0].message
        is_tool_call = message.tool_calls

        if not is_tool_call:
            final_text.append(message.content)

        else:
            tool_name = message.tool_calls[0].function.name
            tool_args = json.loads(message.tool_calls[0].function.arguments)
            result = await self.session.call_tool(tool_name, tool_args)
            tool_results.append({"call": tool_name, "result": result})
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

            if message.content and hasattr(message.content, "text"):
                messages.append({"role": "assistant", "content": message.content})

            messages.append(
                {
                    "role": "user",
                    "content": result.content,
                }
            )
            response = self.get_response(messages, available_tools)
            final_text.append(response.choices[0].message.content)

        return "\\n".join(final_text)

    async def chat_loop(self) -> None:
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError!!!: {str(e)}")

    async def cleanup(self) -> None:
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
