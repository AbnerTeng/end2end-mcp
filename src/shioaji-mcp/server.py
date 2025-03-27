import logging
from typing import Any, Dict, Tuple

import shioaji as sj
import pandas as pd
from mcp.server.fastmcp import FastMCP

from config import (
    API_KEY,
    SECRET_KEY,
    CA_CERT_PATH,
    CA_PASSWORD
)
from parser import Parser
from utils import place_long_order


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Shioaji MCP")

mcp = FastMCP("Shioaji", dependencies=["shioaji"])


@mcp.prompt()
def trader(trade_info: str) -> str:
    return f"Please trade with the following info: {trade_info}"


@mcp.tool()
async def analyze_csv(csv_path: str) -> Dict[str, Tuple[float, int]]:
    """
    Analyze a CSB file containing stock trading info

    Inputs:
        - csv_path: str

    Returns:
        - Stock: Dict[str, Tuple[float, int]]
    """
    print(f"Attempting to reading file: {csv_path}")

    try:
        data = pd.read_csv(csv_path)

    except Exception as e:
        return f"Error reading file: {e}"

    data_dict = {
        col: (data[col].iloc[0], data[col].iloc[1]) for col in data.columns
    }

    return data_dict


@mcp.tool()
async def trade(
    stock_id: int,
    price: float,
    quantity: int
) -> Tuple[Dict[str, Any], ...]:
    """
    Place a long order for a stock_id at a specific price and quantity

    Inputs:
        - stock_id: int
        - price: float
        - quantity: int

    Returns:
        - Message: str
    """
    api = sj.Shioaji(simulation=True)
    account = api.login(
        api_key=API_KEY,
        secret_key=SECRET_KEY,
    )
    print(f"Available account: {account}")
    api.activate_ca(
        ca_path=CA_CERT_PATH,
        ca_passwd=CA_PASSWORD
    )
    if isinstance(stock_id, int):
        stock_id_str = str(stock_id)

    trade = place_long_order(api, stock_id_str, price, quantity)
    api.update_status()

    parser = Parser(trade)

    contract = parser.parse_contract()
    status = parser.parse_status()

    logger.info(f"Contract: {contract}")
    logger.info(f"Status: {status}")

    return contract, status


if __name__ == "__main__":
    logger.info("Starting Shioaji MCP server")
    mcp.run(transport="stdio")
    logger.info("Shioaji MCP server stopped")
