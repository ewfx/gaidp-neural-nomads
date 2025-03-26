import json
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from services.pdf_rule_generator import DocumentProcessor
from services.sql_query_generator import SQLiteQueryGenerator

router = APIRouter()

class PDFRequest(BaseModel):
    file_path: str
    output_file: str

@router.post("/generate/rules")
async def generate_rules(request: PDFRequest):
    try:
        processor = DocumentProcessor(model_name="gemini-2.0-flash")
        results = processor.process_document(request.file_path)
        print(results)

        generator = SQLiteQueryGenerator(model_name="gemini-2.0-flash",output_file=request.output_file)
        results = generator.process_rules()
        
        print("Query generation complete!")
        print(f"Summary: {json.dumps(results, indent=2)}")
        return {"message": "Rules generated successfully", "results": results}
    

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
