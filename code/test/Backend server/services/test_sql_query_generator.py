import unittest
from unittest.mock import patch, MagicMock
from Backend_server.services.sql_query_generator import SQLiteQueryGenerator


class TestSQLiteQueryGenerator(unittest.TestCase):

    @patch("Backend_server.services.sql_query_generator.Path.exists")
    @patch("Backend_server.services.sql_query_generator.json.load")
    def test_load_profiling_rules(self, mock_json_load, mock_path_exists):
        mock_path_exists.return_value = True
        mock_json_load.return_value = {"field1": {"rule": "rule1"}}
        generator = SQLiteQueryGenerator(output_file="dummy_output.json")
        result = generator.load_profiling_rules()
        self.assertEqual(result, {"field1": {"rule": "rule1"}})

    @patch("Backend_server.services.sql_query_generator.LLMChain.run")
    @patch("Backend_server.services.sql_query_generator.Path.exists")
    def test_generate_sql_queries(self, mock_path_exists, mock_run):
        mock_path_exists.return_value = False
        mock_run.return_value = '{"1001": {"rule_id": "1001", "rule_name": "Test Rule", "sql_query": "SELECT * FROM transactions"}}'
        generator = SQLiteQueryGenerator(output_file="dummy_output.json")
        field_rules = {"field1": {"field_number": "1", "rule": "rule1"}}
        result = generator.generate_sql_queries(field_rules)
        self.assertIn("1001", result)

    @patch("Backend_server.services.sql_query_generator.Path.exists")
    @patch("Backend_server.services.sql_query_generator.json.dump")
    @patch("Backend_server.services.sql_query_generator.SQLiteQueryGenerator.generate_sql_queries")
    def test_process_rules(self, mock_generate_sql_queries, mock_json_dump, mock_path_exists):
        mock_path_exists.return_value = False
        mock_generate_sql_queries.return_value = {"1001": {"rule_id": "1001"}}
        generator = SQLiteQueryGenerator(output_file="dummy_output.json")
        result = generator.process_rules()
        self.assertEqual(result["sql_queries_count"], 1)


if __name__ == "__main__":
    unittest.main()
