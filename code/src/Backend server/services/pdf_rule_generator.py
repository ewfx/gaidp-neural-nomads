import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Core imports
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

class DocumentProcessor:

    
    def __init__(self, model_name: str = "gemini-pro"):

        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
            max_output_tokens=4096
        )
        
        # File paths
        self.fields_file = "../Database/rules/temp/extracted_fields.json"
        self.rules_file = "../Database/rules/temp/profiling_rules.json"
        self.checkpoint_file = "../Database/rules/temp/rules_checkpoint.json"
    
    def extract_pdf_text(self, file_path: str) -> str:

        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            return "\n\n".join([doc.page_content for doc in documents])
        except Exception as e:
            print(f" Error extracting PDF text: {str(e)}")
            raise
    
    def split_text(self, text: str, chunk_size: int = 8000) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return text_splitter.split_text(text)
    
    
    def extract_all_fields(self, document_text: str) -> Dict[str, str]:
        print(" Extracting all fields with their numbers from document...")
        
        chunks = self.split_text(document_text, chunk_size=200000)
        
        field_extraction_prompt = PromptTemplate(
            input_variables=["chunk", "chunk_num", "total_chunks"],
            template="""
            Your task is to identify ALL fields with their field numbers in this document.
            
            Document content (section {chunk_num}/{total_chunks}): 
            {chunk}
            
            Instructions:
            1. Examine the text carefully and identify EVERY field number and name mentioned
            2. The document refers to fields as "Field 1", "Field 2", etc., followed by their names
            3. Include ALL field number-name pairs, even if they only appear once
            4. Extract ONLY the field numbers and corresponding names
            5. Do not generate field numbers or names that don't exist in the document
            6. "Do not use" is not a field, it is just a tag to not consider that row of the table
            7. NEVER create a field such as "Field 30" as that is Nonsense. All fields names should be their real names as per the document. No output should be alias of actual field names.
            8. If a field name is not present in the document, do not include it in the output. 

            Return ONLY a dictionary mapping field numbers to field names in JSON format like this:
            {{
                "fields": {{
                    "1": "Field Name 1",
                    "2": "Field Name 2",
                    "3": "Field Name 3",
                    ...
                }}
            }}
            """
        )
        
        field_extraction_chain = LLMChain(llm=self.llm, prompt=field_extraction_prompt)
        
        all_fields = {}  # Dictionary to store field number to field name mapping
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")
            
            max_retries = 3
            retry_delay = 65  # seconds
            
            for retry in range(max_retries):
                try:
                    response = field_extraction_chain.run(
                        chunk=chunk, 
                        chunk_num=i+1, 
                        total_chunks=len(chunks)
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and retry < max_retries - 1:
                        wait_time = retry_delay * (2 ** retry)
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {retry + 1}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"Error in API call: {str(e)}")
                        if retry == max_retries - 1:
                            print("Maximum retries reached, continuing with next chunk")
                            continue
            
            try:
                result = self._extract_and_parse_json(response)
                
                if result and "fields" in result and isinstance(result["fields"], dict):
                    all_fields.update(result["fields"])
                    print(f"Found {len(result['fields'])} field mappings in chunk {i+1}")
                else:
                    print(f"No valid field mappings found in chunk {i+1}")
            except Exception as e:
                print(f"Error parsing JSON from chunk {i+1}: {str(e)}")
                # Fallback: try line-by-line extraction
                all_fields.update(self._extract_fields_fallback(response))
        
        print(f"Total unique field mappings found: {len(all_fields)}")
        return all_fields
    
    def _extract_and_parse_json(self, text: str) -> Optional[Dict]:
        try:
            # Try to extract JSON from response
            start_idx = text.find("{")
            end_idx = text.rfind("}")
            
            if start_idx != -1 and end_idx != -1:
                json_str = text[start_idx:end_idx + 1]
                cleaned_json = self._clean_json_string(json_str)
                return json.loads(cleaned_json)
            return None
        except Exception as e:
            print(json_str)
            print(f"Error extracting JSON: {str(e)}")
            return None
    
    def _extract_fields_fallback(self, text: str) -> Dict[str, str]:
        extracted_fields = {}
        try:
            lines = text.split("\n")
            for line in lines:
                if ":" in line and "Field" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        field_num = parts[0].strip().strip('"').strip("'")
                        field_name = parts[1].strip().strip('"').strip("'").strip(",")
                        
                        # Try to extract just the numeric part if it contains "Field"
                        if "Field" in field_num:
                            field_num = ''.join(filter(str.isdigit, field_num))
                        
                        if field_num and field_name and field_num not in extracted_fields:
                            extracted_fields[field_num] = field_name
        except Exception as e:
            print(f"Fallback extraction failed: {str(e)}")
        
        return extracted_fields
    
    def _clean_json_string(self, json_str: str) -> str:
        # Fix trailing commas
        json_str = json_str.replace(",\n}", "\n}")
        json_str = json_str.replace(",\n]", "\n]")
        json_str = json_str.replace(",}", "}")
        json_str = json_str.replace(",]", "]")
        
        # Fix unquoted property names
        import re
        pattern = r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)'
        json_str = re.sub(pattern, r'\1"\2"\3', json_str)
        
        return json_str
    
    def generate_rules_for_fields(self, document_text: str, fields: Dict[str, str]) -> Dict[str, Any]:
        print(" Generating rules for identified fields...")
        
        field_names = list(fields.values())
        
        name_to_number = {fields[num]: num for num in fields}
        
        fields_per_chunk = 25
        field_chunks = [field_names[i:i+fields_per_chunk] for i in range(0, len(field_names), fields_per_chunk)]
        
        all_rules = {}
        
        if Path(self.checkpoint_file).exists():
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    all_rules = json.load(f)
                print(f" Loaded {len(all_rules)} existing rules from checkpoint")
            except Exception as e:
                print(f" Could not load checkpoint: {str(e)}")
        
        rules_prompt = PromptTemplate(
            input_variables=["document_excerpt", "field_context"],
            template="""
            Generate detailed data profiling rules for the following fields extracted from a document. These rules will be directly converted to SQL queries to identify violating transactions, so ensure all information is complete and explicit.
            
            Document context (excerpt):
            {document_excerpt}
            
            Fields to generate rules for:
            {field_context}
            
            IMPORTANT: When creating rules, use only the actual field name without any field number prefix. For example, if the input contains "Field 28: Cumulative Charge-offs", use only "Cumulative Charge-offs" as the field name in your response.
            
            For each field, determine:
            1. The precise data type (varchar, integer, decimal, date, datetime, boolean, etc.)
            2. Exact format specifications with examples (e.g., "YYYY-MM-DD" for dates, specific regex patterns)
            3. Explicit validation constraints with specific values (min/max values, allowed character sets, exact length requirements)
            4. Nullability status (is NULL allowed or NOT NULL required)
            5. Uniqueness requirements (unique across entire table or within specific contexts)
            6. Business rules with precise thresholds, conditions, and relationships to other fields
            7. Include the field number in your response to maintain traceability
            
            IMPORTANT GUIDELINES:
            - Provide specific values for all thresholds (e.g., "Value must be > 0" not "Value must be positive")
            - Specify exact date formats and ranges (e.g., "Date must be between 2023-01-01 and 2023-12-31")
            - For string patterns, provide explicit regex or exact character requirements
            - Define relationships between fields with precise conditions
            - Avoid vague terms like "reasonable", "appropriate", or "standard"
            - Never use placeholders or references that would need further clarification
            - Each rule must be self-contained with all information needed for SQL implementation
            
            VERY IMPORTANT: Return your answer in valid, correctly formatted JSON. Every property name must be in double quotes. Every string value must be in double quotes. Boolean values (true/false) and numeric values should not be in quotes.
            
            Format for response:
            {{
                "Cumulative Charge-offs": {{
                    "field_number": "28",
                    "data_type": "decimal(18,2)",
                    "format": "Specific format with example: 1234567.89",
                    "required": true,
                    "unique": false,
                    "validation_rules": [
                        "Field length must be exactly 12 characters",
                        "Field must match pattern '^[A-Z]{{3}}-\\d{{3}}-[A-Z0-9]{{4}}$'",
                        "Field must not contain any special characters except hyphens",
                        "Value must be greater than 1000 and less than 9999",
                        "Date must be after 2023-01-01",
                        "Value must be less than or equal to value in OtherField"
                    ]
                }},
                ...
            }}
            
            Analyze the context thoroughly and generate specific, SQL-compatible rules that can be directly translated to database queries without requiring additional information.
            """
        )
        
        rules_chain = LLMChain(llm=self.llm, prompt=rules_prompt)
        
        for i, field_chunk in enumerate(field_chunks):
            if all(field in all_rules for field in field_chunk):
                print(f"Skipping chunk {i+1}/{len(field_chunks)} - rules already generated")
                continue
                
            print(f"Processing rules for fields {i*fields_per_chunk+1}-{i*fields_per_chunk+len(field_chunk)} of {len(field_names)}...")
            
            field_context = []
            for field_name in field_chunk:
                field_num = name_to_number.get(field_name, "")
                field_context.append(f"Field {field_num}: {field_name}")
            
            max_retries = 5
            retry_delay = 65  # seconds
            success = False
            
            for retry in range(max_retries):
                try:
                    response = rules_chain.run(
                        document_excerpt=document_text[:200000],
                        field_context=json.dumps(field_context)
                    )
                    success = True
                    break
                except Exception as e:
                    if "429" in str(e) and retry < max_retries - 1:
                        wait_time = retry_delay * (2 ** retry)
                        print(f"Rate limit hit, waiting {wait_time} seconds before retry {retry + 1}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"Error in API call: {str(e)}")
                        if retry == max_retries - 1:
                            print(f"Maximum retries reached for chunk {i+1}")
                            break
            
            if not success:
                continue
            
            try:
                # Extract and parse JSON
                chunk_rules = self._extract_and_parse_json(response)
                
                if chunk_rules:
                    all_rules.update(chunk_rules)
                    print(f"Successfully generated rules for chunk {i+1}/{len(field_chunks)}")
                    
                    with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                        json.dump(all_rules, f, indent=4)
                    print(f" Saved checkpoint with {len(all_rules)} rules")
                else:
                    print(f"Failed to extract rules for chunk {i+1}")
                    self._process_fields_individually(field_chunk, name_to_number, all_rules)
                    
            except Exception as e:
                print(f"Error processing rules for chunk {i+1}: {str(e)}")
                self._process_fields_individually(field_chunk, name_to_number, all_rules)
        
        return all_rules
    
    def _process_fields_individually(self, field_chunk, name_to_number, all_rules):
        single_field_prompt = PromptTemplate(
            input_variables=["field_num", "field_name"],
            template="""
            Generate a data profiling rule for this field: "Field {field_num}: {field_name}"
            
            Consider:
            1. The likely data type (string, integer, date, etc.)
            2. Format specifications if applicable
            3. Validation rules (min/max values, patterns, etc.)
            4. Whether the field is required
            5. Whether values should be unique
            
            Return ONLY valid JSON with this exact format:
            {{
                "{field_name}": {{
                    "field_number": "{field_num}",
                    "type": "string OR integer OR date OR etc.",
                    "format": "specific format if applicable",
                    "required": true OR false,
                    "unique": true OR false,
                    "validation_rules": [
                        "specific rule 1",
                        "specific rule 2"
                    ]
                }}
            }}
            """
        )
        
        # Create LangChain chain for single field rule generation
        single_field_chain = LLMChain(llm=self.llm, prompt=single_field_prompt)
        
        for field_name in field_chunk:
            if field_name not in all_rules:
                field_num = name_to_number.get(field_name, "")
                print(f"Attempting to generate rule for individual field: Field {field_num}: {field_name}")
                
                try:
                    # Wait between individual field requests
                    time.sleep(2)
                    
                    field_response = single_field_chain.run(
                        field_num=field_num,
                        field_name=field_name
                    )
                    
                    # Extract and parse JSON
                    field_rule = self._extract_and_parse_json(field_response)
                    
                    if field_rule:
                        all_rules.update(field_rule)
                        
                        # Save checkpoint after each field
                        with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                            json.dump(all_rules, f, indent=4)
                        print(f"Added rule for field: {field_name}")
                    else:
                        print(f"Failed to generate rule for field: {field_name}")
                        
                except Exception as field_err:
                    print(f"Failed to generate rule for {field_name}: {str(field_err)}")
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        try:

            print(" Extracting text from PDF...")
            document_text = self.extract_pdf_text(file_path)
            
            fields = self.extract_all_fields(document_text)
            
            with open(self.fields_file, "w", encoding="utf-8") as f:
                json.dump({"fields": fields}, f, indent=4)
            print(f" Saved {len(fields)} fields to {self.fields_file}")
            
            # Check if final rules file already exists
            if Path(self.rules_file).exists():
                print(f" Rules file {self.rules_file} already exists. Regenrating")
            
            if 'document_text' not in locals():
                print(" Extracting text from PDF for rules generation...")
                document_text = self.extract_pdf_text(file_path)
            
            # Generate rules for all fields
            rules = self.generate_rules_for_fields(document_text, fields)
            
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(rules, f, indent=4)
            print(f" Saved rules for {len(rules)} fields to {self.rules_file}")
            
            # Cleanup checkpoint file
            if Path(self.checkpoint_file).exists():
                try:
                    os.remove(self.checkpoint_file)
                    print(" Removed checkpoint file after successful completion")
                except:
                    print(" Could not remove checkpoint file")
            
            return {
                "fields_count": len(fields),
                "rules_count": len(rules),
                "fields_file": self.fields_file,
                "rules_file": self.rules_file
            }
        
        except Exception as e:
            error_message = f"Error processing document: {str(e)}"
            print(f" {error_message}")
            return {"error": error_message}


