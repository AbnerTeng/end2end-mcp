import json
from path import CUSTOMERS_FILE, FORMS_DIR
from datetime import datetime
from mcp.server.fastmcp import FastMCP
from loguru import logger
from pathlib import Path
import utils

mcp = FastMCP("ibranch")


@mcp.tool()
def new_deposit_form(account_number: str, name: str, amount: int, applicant_id: str, notes: str | None = None) -> dict:
    """將存款內容填入一份全新的表單

    Args:
        account_number: 14碼帳戶號碼
        name: 存入帳戶戶名
        amount: 存款金額
        applicant_id: 申請人身分證字號
        notes: 存款備註
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # verify infos
    assert utils.valid_id(applicant_id)
    assert utils.valid_account(account_number)
    assert amount > 0, "台幣金額需大於0"
    notes = utils.process_notes(notes)

    # form & persist
    form = {"服務名稱": "台幣存款", "帳戶號碼": account_number, "帳戶名稱": name, "金額": amount, "存款備註": notes, "填表時間": timestamp}
    file_name = FORMS_DIR / f"{applicant_id}_{timestamp}.json"
    json.dump(form, open(file_name, "w"))
    return form

@mcp.tool()
def get_filled_formats(applicant_id: str) -> str:
    """以申請人身分證字號取得此人已預填的所有表單

    Args:
        applicant_id: 申請人身分證字號
    """

    form_list = sorted(FORMS_DIR.glob(f'{applicant_id}_*.json'))
    if len(form_list) == 0:
        return f"{FORMS_DIR}中沒有{applicant_id}預填的表單"

    render = ""
    for i, form in enumerate(form_list):
        form = json.load(open(form, "r"))
        render += f"{i}. {form['服務名稱']}: {form['填表時間']}\n"
        for k, v in form.items() :
            if k == "服務名稱":
                continue
            render += f"\t{k}: {v}\n"
    return render

if __name__ == "__main__":
    mcp.run(transport="stdio")
