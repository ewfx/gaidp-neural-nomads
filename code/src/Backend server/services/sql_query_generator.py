import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

class SQLiteQueryGenerator:

    
    def __init__(self, output_file: str,model_name: str = "gemini-pro"):
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,
            max_output_tokens=4096
        )
        
        # File paths
        self.rules_file = "../Database/rules/temp/profiling_rules.json"
        self.sql_queries_file = output_file
        self.checkpoint_file = "../Database/rules/temp/sql_queries_checkpoint.json"
    
    def load_profiling_rules(self) -> Dict[str, Any]:
        try:
            if not Path(self.rules_file).exists():
                raise FileNotFoundError(f"Rules file {self.rules_file} not found")
                
            with open(self.rules_file, "r", encoding="utf-8") as f:
                rules = json.load(f)
            
            print(f" Loaded {len(rules)} field rules from {self.rules_file}")
            return rules
        except Exception as e:
            print(f" Error loading profiling rules: {str(e)}")
            raise
    
    def generate_sql_queries(self, field_rules: Dict[str, Any]) -> Dict[str, Any]:
        print(" Generating SQLite validation queries...")
        
        all_sql_queries = {}
        rule_id_counter = 1000  # Starting rule ID
        
        # Load existing queries from checkpoint if it exists
        if Path(self.checkpoint_file).exists():
            try:
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoint_data = json.load(f)
                    all_sql_queries = checkpoint_data.get("queries", {})
                    rule_id_counter = checkpoint_data.get("next_rule_id", rule_id_counter)
                print(f" Loaded {len(all_sql_queries)} existing SQL queries from checkpoint")
            except Exception as e:
                print(f" Could not load checkpoint: {str(e)}")
        
        # Create prompt template for SQL query generation specifically for SQLite
        sql_query_prompt = PromptTemplate(
            input_variables=["field_name", "field_number", "field_rules", "rule_id_start"],
            template="""
            Generate SQLite-compatible SQL validation queries for a data profiling rule. The queries should identify transactions that violate the validation rules.
            
            Field Information:
            - Field Name: {field_name}
            - Field Number: {field_number}
            - Field Rules: {field_rules}
            - Starting Rule ID: {rule_id_start}
            
            Task:
            1. For each validation rule, create a separate SQL query
            2. Each SQL query should:
            - Return the actual Transaction ID, not a string literal
            - Be optimized for performance
            - Use SQLite-compatible syntax
            3. The table name should be "transactions"
            4. Assume the column names in the database match the field names from the rules
            
            Important Requirements:
            - Ensure the query returns the real Transaction ID column
            - Use proper column references
            - Check for column existence using PRAGMA table_info
            - Handle potential NULL values
            - Validate only non-null/non-empty fields
            
            Format your response as valid JSON following this structure:
            {{
                "rule_id_1": {{
                    "rule_id": "rule_id_1",
                    "rule_name": "Short, descriptive name for the rule",
                    "rule_description": "Detailed description of what the rule validates",
                    "sql_query": "Complete SQL query that checks for violations and returns actual Transaction ID",
                    "status": "active"
                }},
                "rule_id_2": {{
                    ...
                }}
            }}
            
            Example output for a "Customer ID" field with a length validation rule:
            {{
                "1001": {{
                    "rule_id": "1001",
                    "rule_name": "Customer ID Length Validation",
                    "rule_description": "Validates that Customer ID field is not longer than 255 characters",
                    "sql_query": "SELECT \"Transaction ID\" FROM transactions WHERE LENGTH(\"Customer ID\") > 255 AND \"Customer ID\" IS NOT NULL",
                    "status": "active"
                }}
            }}
            
            Specific Guidelines:
            - Use actual column names without string literals
            - Return the Transaction ID column directly
            - Add appropriate NULL checks and validation conditions
            - Ensure the query will return meaningful results
            
            Return ONLY the JSON with no additional text or explanation.
            """
        )
        
        # Create LangChain chain for SQL query generation
        sql_query_chain = LLMChain(llm=self.llm, prompt=sql_query_prompt)
        
        # Process each field and its rules
        for idx, (field_name, field_data) in enumerate(field_rules.items()):
            print(f"Processing field {idx+1}/{len(field_rules)}: {field_name}")
            
            # Skip fields that already have SQL queries generated
            field_rule_ids = self._find_existing_rule_ids(all_sql_queries, field_name)
            if field_rule_ids:
                print(f"  ↳ Skipping - SQL queries already generated ({len(field_rule_ids)} rules)")
                continue
            
            field_number = field_data.get("field_number", "")
            
            max_retries = 3
            retry_delay = 10  # seconds
            
            for retry in range(max_retries):
                try:
                    # Run the SQL query generation chain
                    response = sql_query_chain.run(
                        field_name=field_name,
                        field_number=field_number,
                        field_rules=json.dumps(field_data),
                        rule_id_start=rule_id_counter
                    )
                    break
                except Exception as e:
                    if "429" in str(e) and retry < max_retries - 1:
                        wait_time = retry_delay * (2 ** retry)
                        print(f"  ↳ Rate limit hit, waiting {wait_time} seconds before retry {retry + 1}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ↳ Error in API call: {str(e)}")
                        if retry == max_retries - 1:
                            print("  ↳ Maximum retries reached, skipping field")
                            continue
            
            try:
                # Extract and parse JSON
                field_sql_queries = self._extract_and_parse_json(response)
                
                if field_sql_queries and isinstance(field_sql_queries, dict):
                    # Update the maximum rule ID for future fields
                    rule_ids = [int(rule_id) for rule_id in field_sql_queries.keys() if rule_id.isdigit()]
                    if rule_ids:
                        rule_id_counter = max(rule_ids) + 1
                    
                    # Add the new SQL queries to the collection
                    all_sql_queries.update(field_sql_queries)
                    print(f"  ↳ Generated {len(field_sql_queries)} SQL queries for field: {field_name}")
                    
                    # Save checkpoint
                    checkpoint_data = {
                        "queries": all_sql_queries,
                        "next_rule_id": rule_id_counter
                    }
                    with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                        json.dump(checkpoint_data, f, indent=4)
                    print(f"  ↳ Saved checkpoint with {len(all_sql_queries)} total SQL queries")
                else:
                    print(f"  ↳ Failed to generate SQL queries for field: {field_name}")
            except Exception as e:
                print(f"  ↳ Error processing SQL queries for field: {str(e)}")
        
        return all_sql_queries
    
    def _find_existing_rule_ids(self, all_sql_queries: Dict[str, Any], field_name: str) -> List[str]:
        rule_ids = []
        field_name_pattern = re.compile(re.escape(field_name), re.IGNORECASE)
        
        for rule_id, rule_data in all_sql_queries.items():
            # Check if this rule is for the current field
            rule_name = rule_data.get("rule_name", "")
            rule_description = rule_data.get("rule_description", "")
            sql_query = rule_data.get("sql_query", "")
            
            if (field_name_pattern.search(rule_name) or 
                field_name_pattern.search(rule_description) or 
                field_name_pattern.search(sql_query)):
                rule_ids.append(rule_id)
        
        return rule_ids
    
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
            print(f"Error extracting JSON: {str(e)}")
            return None
    
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
    
    def process_rules(self) -> Dict[str, Any]:
        try:
            # Check if final SQL queries file already exists
            if Path(self.sql_queries_file).exists():
                print(f" SQL queries file {self.sql_queries_file} already exists. Regenerating")
                            
            # Load the profiling rules
            field_rules = self.load_profiling_rules()
            
            # Generate SQL queries for all field rules
            sql_queries = self.generate_sql_queries(field_rules)
            
            # Save SQL queries to final JSON file
            with open(self.sql_queries_file, "w", encoding="utf-8") as f:
                json.dump(sql_queries, f, indent=4)
            print(f" Saved {len(sql_queries)} SQL queries to {self.sql_queries_file}")
            
            # Cleanup checkpoint file
            if Path(self.checkpoint_file).exists():
                try:
                    os.remove(self.checkpoint_file)
                    print(" Removed checkpoint file after successful completion")
                except:
                    print(" Could not remove checkpoint file")
            
            return {
                "sql_queries_count": len(sql_queries),
                "sql_queries_file": self.sql_queries_file
            }
        
        except Exception as e:
            error_message = f"Error processing rules: {str(e)}"
            print(f" {error_message}")
            return {"error": error_message}


# Main execution
if __name__ == "__main__":
    print(" Generating SQLite-compatible validation queries from profiling rules")
    
    # Create SQL query generator and process the rules
    generator = SQLiteQueryGenerator(model_name="gemini-2.0-flash")
    results = generator.process_rules()
    
    print(" Query generation complete!")
    print(f"Summary: {json.dumps(results, indent=2)}")