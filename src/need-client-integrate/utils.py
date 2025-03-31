import logging
from typing import Any, Dict, Tuple

import pandas as pd
import shioaji as sj
from shioaji.constant import (
    OrderType,
    Action,
    StockPriceType,
)

from config import API_KEY, SECRET_KEY, CA_CERT_PATH, CA_PASSWORD
from parser import Parser


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("Shioaji MCP")


def place_long_order(api: sj.Shioaji, stock_id: str, price: float, quantity: int):
    contract = api.Contracts.Stocks.TSE[stock_id]

    order = api.Order(
        price=price,
        quantity=quantity,
        action=Action.Buy,
        price_type=StockPriceType.LMT,
        order_type=OrderType.ROD,
        account=api.stock_account,
    )
    trade = api.place_order(contract, order)
    api.update_status()

    return trade


def analyze_csv(csv_path: str) -> Dict[str, Tuple[float, int]]:
    """
    Analyze a CSV file containing stock trading info

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

    data_dict = {col: (data[col].iloc[0], data[col].iloc[1]) for col in data.columns}

    return data_dict


def trade(stock_id: int, price: float, quantity: int) -> Tuple[Dict[str, Any], ...]:
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
    api.activate_ca(ca_path=CA_CERT_PATH, ca_passwd=CA_PASSWORD)
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
