import json
from path import CUSTOMERS_FILE

def get_account_by_id(id: str) -> str | None:
    #TODO: id can map to several accounts
    customers = json.load(open(CUSTOMERS_FILE, "r"))
    for k, v in customers.items():
        if v["id"] == id:
            return k
    return None

def get_info_by_account(number: str) -> str | None:
    customers = json.load(open(CUSTOMERS_FILE, "r"))
    try:
        return customers[number]
    except KeyError:
        return None

def valid_account(account_number: str) -> bool:
    if len(account_number) != 14:
        raise Exception("帳號須為14碼")
    if not get_info_by_account(account_number):
        raise Exception("帳號錯誤")
    return True

def valid_id(id: str) -> bool:
    if len(id) != 10:
        raise Exception("身分證字號須為10碼")
    if not get_account_by_id(id):
        raise Exception("查無此人:)")
    return True

def process_notes(notes: str | None) -> str:
    if not notes:
        return ""
    else:
        return strip(notes)
