from typing import Any, Dict

import shioaji as sj


class Parser:
    def __init__(self, trade_info: sj.order.Trade) -> None:
        self.trade_info = trade_info
        self.contract_keys = ["exchange", "code", "name", "unit", "reference"]
        self.status_keys = ["status", "msg"]

    def parse_contract(self):
        return {
            k: v
            for k, v in self.trade_info["contract"].items()
            if k in self.contract_keys
        }

    def parse_order(self):
        pass

    def parse_status(self) -> Dict[str, Any]:
        return {
            k: v for k, v in self.trade_info["status"].items() if k in self.status_keys
        }
