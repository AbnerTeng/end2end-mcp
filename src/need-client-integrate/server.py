import asyncio
import logging
from typing import Dict, List, Union

import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from prompts import PROMPTS


mcp = Server("Shioaji")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Shioaji MCP")


@mcp.list_prompts()
async def list_prompts() -> List[types.Prompt]:
    return list(PROMPTS.values())


@mcp.get_prompt()
async def get_prompt(
    prompt_name: str, arguments: Dict[str, str]
) -> types.GetPromptResult:
    if prompt_name not in PROMPTS:
        raise ValueError(f"Prompt {prompt_name} not found")

    if prompt_name == "analyze_csv":
        csv_path = arguments.get("csv_path")

        if not csv_path:
            raise ValueError("Missing argument: csv_path")

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Analyze the csv path : {csv_path} into dictionary",
                    ),
                )
            ]
        )

    if prompt_name == "trade":
        stock_id = arguments.get("stock_id")
        price = arguments.get("price")
        quantity = arguments.get("quantity")

        if not all([stock_id, price, quantity]):
            raise ValueError("Missing arguments: stock_id, price, or quantity")

        return types.GetPromptResult(
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Place a long order for stock_id: {stock_id}, price: {price}, quantity: {quantity}",
                    ),
                )
            ]
        )

    raise ValueError("Prompt implemetation not found")


@mcp.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="analyze_csv",
            description="Analyze a CSV file containing stock trading info",
            inputSchema={
                "type": "object",
                "properties": {"csv_path": {"type": "string"}},
                "required": ["csv_path"],
            },
        ),
        types.Tool(
            name="trade",
            description="Place a long order for a stock at a specific price and quantity",
            inputSchema={
                "type": "object",
                "properties": {
                    "stock_id": {"type": "integer"},
                    "price": {"type": "number"},
                    "quantity": {"type": "integer"},
                },
                "required": ["stock_id", "price", "quantity"],
            },
        ),
    ]


@mcp.call_tool()
async def call_tool(
    tool_name: str, arguments: Dict
) -> List[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    if tool_name == "analyze_csv":
        csv_path = arguments.get("csv_path")

        if not csv_path:
            return [
                types.TextContent(type="text", text="Error: Missing csv_path argument")
            ]

        return [
            types.TextContent(type="text", text=f"Attempting to read file: {csv_path}")
        ]

    if tool_name == "trade":
        stock_id = arguments.get("stock_id")
        price = arguments.get("price")
        quantity = arguments.get("quantity")

        if not all([stock_id, price, quantity]):
            return [
                types.TextContent(
                    type="text", text="Error: Missing stock_id, price, or quantity"
                )
            ]

        return [
            types.TextContent(
                type="text",
                text=f"Placing a long order for stock_id: {stock_id}, price: {price}, quantity: {quantity}",
            )
        ]

    raise ValueError("Tool implementation not found")


async def main():
    async with stdio_server() as streams:
        await mcp.run(streams[0], streams[1], mcp.create_initialization_options())


if __name__ == "__main__":
    logger.info("Starting Shioaji MCP server")
    asyncio.run(main())
    logger.info("Shioaji MCP server stopped")
