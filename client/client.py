import asyncio
import json
import os
from typing import Any, Dict, List
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

from utils import load_config

load_dotenv(".env")


class MCPClient:
    def __init__(self, config_path: str) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self.exit_stack = AsyncExitStack()
        self.config_path = config_path
        self.config = load_config(config_path)
        self.current_conversation: List[Dict[str, Any]] = []

        if os.getenv("LLM_PROVIDER") == "ollama":
            self.llm = OpenAI(
                base_url=os.getenv("OLLAMA_APU_URL"),
                api_key=os.getenv("OLLAMA_API_KEY"),
            )
        elif os.getenv("LLM_PROVIDER") == "openai":
            self.llm = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            )

    def get_response(self, messages: List[Dict[str, str]], tools: List) -> Any:
        model_name = (
            "OLLAMA_MODEL" if os.getenv("LLM_PROVIDER") == "ollama" else "OPENAI_MODEL"
        )
        response = self.llm.chat.completions.create(
            model=os.getenv(model_name),
            max_tokens=4000,
            messages=messages,
            tools=tools,
        )

        return response

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []

        for server_name, session in self.sessions.items():
            response = await session.list_tools()
            available_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": f"{tool.name}",
                        "description": f"[{server_name}] {tool.description}",
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in response.tools
            ]
            all_tools.extend(available_tools)

        return all_tools

    async def connect_to_servers(self) -> None:
        """
        Conncting to MCP servers, usually a json file
        """
        servers_to_connect = list(self.config["mcpServers"].keys())

        for server_name in servers_to_connect:
            await self._connect_to_single_server(server_name)

    async def _connect_to_single_server(self, server_name: str) -> None:
        server_config = self.config["mcpServers"][server_name]
        env = os.environ.copy()

        if server_config.get("env"):
            env.update(server_config["env"])

        server_params = StdioServerParameters(
            command=server_config["command"],
            args=server_config.get("args", []),
            env=env,
        )  # to execute mcp server script

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await session.initialize()
        self.sessions[server_name] = session
        response = await session.list_tools()
        tools = response.tools
        print(
            f"\nConnected to server {server_name} with tools:",
            [tool.name for tool in tools],
        )

    async def call_tool(self, tool_call_name: str, tool_args: Dict) -> Any:
        if ":" in tool_call_name:
            server_name, actual_tool_name = tool_call_name.split(":", 1)
        else:
            server_name = None
            actual_tool_name = tool_call_name

            for name, session in self.sessions.items():
                response = await session.list_tools()
                if any(tool.name == actual_tool_name for tool in response.tools):
                    server_name = name
                    break

            if not server_name:
                raise ValueError(
                    f"Tool '{tool_call_name}' not found in any connected server"
                )

        if server_name not in self.sessions:
            raise ValueError(f"Server '{server_name}' is not connected")

        session = self.sessions[server_name]
        result = await session.call_tool(actual_tool_name, tool_args)
        return result

    async def process_query(self, query: str) -> str:
        messages = self.current_conversation.copy()
        messages.append({"role": "user", "content": query})
        self.current_conversation.append({"role": "user", "content": query})
        available_tools = await self.get_all_tools()

        if not available_tools:
            response = "No tools available"
            self.current_conversation.append({"role": "assistant", "content": response})
            return response

        response = self.get_response(messages, available_tools)
        message = response.choices[0].message

        final_text, tool_results = [], []

        if not message.tool_calls:
            final_text.append(message.content)
            self.current_conversation.append(
                {"role": "assistant", "content": message.content}
            )
        else:
            assistant_response_with_tools = {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [],
            }
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                print(f"Calling tools: {tool_name}")
                print(
                    f"Parameters: {json.dumps(tool_args, ensure_ascii=False, indent=2)}"
                )
                tool_call_info = {
                    "id": tool_call.id,
                    "function": {
                        "name": tool_name,
                        "arguments": tool_call.function.arguments,
                    },
                    "type": "function",
                }
                assistant_response_with_tools["tool_calls"].append(tool_call_info)
                result = await self.call_tool(tool_name, tool_args)
                tool_results.append(
                    {
                        "call": tool_name,
                        "result": result,
                    }
                )
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": [tool_call],
                    }
                )
                tool_result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result.content)
                    if hasattr(result, "content")
                    else str(result),
                }
                messages.append(tool_result_message)
                self.current_conversation.append(assistant_response_with_tools.copy())
                self.current_conversation.append(tool_result_message)

            if tool_results:
                final_response_obj = self.get_response(messages, available_tools)
                final_response = final_response_obj.choices[0].message.content
                final_text.append(final_response)
                self.current_conversation.append(
                    {"role": "assistant", "content": final_response}
                )

        return "\n".join(filter(None, final_text))

    def list_available_servers(self) -> None:
        if not self.config.get("mcpServers"):
            print("No servers configured in config file")
            return

        print("\nConfigured servers:")
        for server_name, config in self.config["mcpServers"].items():
            status = "Connected" if server_name in self.sessions else "Not connected"
            print(
                f"  - {server_name}: {config['command']} {' '.join(config.get('args', []))} [{status}]"
            )

    def _clear_current_conversation(self) -> None:
        self.current_conversation = []
        print("Current session conversation cleared")

    async def chat_loop(self) -> None:
        while True:
            try:
                query = input("\n> ").strip()

                if query.lower() == "exit":
                    break
                elif query.lower() == "clear-current":
                    self._clear_current_conversation()
                else:
                    response = await self.process_query(query)
                    print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def clean_up(self) -> None:
        await self.exit_stack.aclose()


async def main():
    client = MCPClient("/Users/abnerteng/git/end2end-mcp/config.json")

    try:
        await client.connect_to_servers()
        client.list_available_servers()
        await client.chat_loop()
    finally:
        await client.clean_up()


if __name__ == "__main__":
    asyncio.run(main())
