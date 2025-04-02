from typing import Any, Dict

import shioaji as sj


class Parser:
    def __init__(self, trade_info: sj.order.Trade) -> None:
        self.trade_info = trade_info
        self.order_keys = ["action", "price", "quantity"]
        self.status_keys = ["status", "msg"]

    def parse_order(self):
        return {
            k: v
            for k, v in self.trade_info["order"].items()
            if k in self.order_keys
        }

    def parse_status(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.trade_info["status"].items() if k in self.status_keys
        }
