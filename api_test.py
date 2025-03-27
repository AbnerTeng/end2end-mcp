import shioaji as sj
from shioaji.constant import (
    OrderType,
    Action,
    StockPriceType,
)

from config import (
    API_KEY,
    SECRET_KEY,
    CA_CERT_PATH,
    CA_PASSWORD
)
from parser import Parser
from utils import place_long_order


api = sj.Shioaji(simulation=True)
account = api.login(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
)
api.activate_ca(
    ca_path=CA_CERT_PATH,
    ca_passwd=CA_PASSWORD
)
trade = place_long_order(api, "2609", 80, 1)
parser = Parser(trade)
print("===")
print(f"Status: {parser.parse_contract()}")
print(f"Message: {parser.parse_status()}")
