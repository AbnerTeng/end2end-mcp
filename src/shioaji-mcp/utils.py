import shioaji as sj
from shioaji.constant import (
    OrderType,
    Action,
    StockPriceType,
)


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
