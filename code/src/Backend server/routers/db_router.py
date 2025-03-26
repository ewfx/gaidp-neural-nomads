from http.client import HTTPException
import os
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel
from services.db_services import get_rules, edit_rules, delete_rules, add_rules, get_transactions, edit_transactions, get_transactions_by_id, update_transactions_from_csv, delete_transactions, downloadTransactionCsv, get_analysed_transactions
from fastapi.responses import FileResponse



router = APIRouter()

class Rule(BaseModel):
    name: str
    description: str
    status: str

class UpdateRuleRequest(BaseModel):
    field_name: str
    value: str

class UpdateTransactionRequest(BaseModel):
    field_name: str
    value: str

@router.get("/dbget")
def get_all_rules():
    rules = get_rules()
    return {"rules": [{"id": rule[0], "name": rule[1], "description": rule[2], "status": rule[3]} for rule in rules]}

@router.post("/dbadd")
def add_new_rule(rule: Rule):
    return {"message": add_rules(rule.name, rule.description, rule.status)}

@router.delete("/dbdelete/{rule_id}")
def delete_rule(rule_id: int):
    return {"message": delete_rules(rule_id)}

@router.put("/dbupdate/{rule_id}")
def update_rule(rule_id: int, update_request: UpdateRuleRequest):
    return {"message": edit_rules(rule_id, update_request.field_name, update_request.value)}

@router.get("/dbgetTransaction")
def get_all_transactions():
    return {"transactions": get_transactions()}

@router.get("/dbgetTransactionById/{transaction_id}")
def get_transaction_by_id(transaction_id: str):
    return {"transactions": get_transactions_by_id(transaction_id)}

@router.post("/uploadTransactionCSV/{analysed}")
async def upload_transaction_csv(analysed: int):
    return {"message": update_transactions_from_csv(analysed=analysed)}

@router.put("/dbupdateTransaction/{transaction_id}")
def update_transaction(transaction_id: str, update_request: UpdateTransactionRequest):
    return {"message": edit_transactions(transaction_id, update_request.field_name, update_request.value)}

@router.delete("/dbdelete")
def delete_transaction():
    return {"message": delete_transactions()}

@router.get("/dbanalysedTransaction")
def get_all_analysed_transactions():
    return {"transactions": get_analysed_transactions()}

@router.get("/downloadTransactionCSV")
def download_transaction_csv():
    return {"message": downloadTransactionCsv()}


@router.get("/download/anamoly_result")
async def download_validation_results():
    file_path = f'../Temp_files/analysed_transaction.xlsx'
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=f'anamoly_results.xlsx')
    raise HTTPException(status_code=404, detail="File not found")
