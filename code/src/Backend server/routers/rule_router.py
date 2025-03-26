from http.client import HTTPException
import json
from fastapi import APIRouter
from fastapi.responses import FileResponse
import os
from services.rule_services import get_rules, edit_rule, delete_rule
from services.sql_executor import SQLiteValidator
from pydantic import BaseModel

class UpdateRuleRequest(BaseModel):
    field_name: str
    value: str

router = APIRouter()

@router.get("/rules/{identifier}")
def get_rules_by_identifier(identifier: str):
    file_path = f'../Database/rules/{identifier}.json'
    rules = get_rules(file_path)
    # Filter rules based on identifier
    filtered_rules = [rule for rule in rules.values()]
    # Return rules in the required format
    return {"rules": [{"id": rule["rule_id"], "name": rule["rule_name"], "description": rule["rule_description"], "status": rule["status"]} for rule in filtered_rules]}

@router.put("/rules/{identifier}/{rule_id}")
def update_rule(identifier: str, rule_id: str, update_request: UpdateRuleRequest):
    file_path = f'../Database/rules/{identifier}.json'
    return {"message": edit_rule(file_path, rule_id, update_request.field_name, update_request.value)}

@router.delete("/rules/{identifier}/{rule_id}")
def delete_rule_by_identifier(identifier: str, rule_id: str):
    file_path = f'../Database/rules/{identifier}.json'
    return {"message": delete_rule(file_path, rule_id)}


@router.get("/rules/validate/{identifier}")
def validate_rules_by_identifier(identifier: str):
    try:
        file_path = f'../Database/rules/{identifier}.json'
        validator = SQLiteValidator("../Database/transaction.db")
        results = validator.validate_data(file_path, identifier=identifier,output_file= f'../Database/{identifier}.csv',excel_output_file= f'../Database/{identifier}.xlsx')
        print(json.dumps(results, indent=2))
        return results
    except Exception as e:
        print(f"Validation failed: {e}")


@router.get("/download/{identifier}")
async def download_validation_results(identifier: str):
    file_path = f'../Database/{identifier}.xlsx'
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=f'{identifier}_validation_results.xlsx')
    raise HTTPException(status_code=404, detail="File not found")
