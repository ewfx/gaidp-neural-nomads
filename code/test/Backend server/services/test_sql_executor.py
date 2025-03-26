import unittest
from unittest.mock import patch, MagicMock
from Backend_server.services.sql_executor import SQLiteValidator


class TestSQLiteValidator(unittest.TestCase):

    @patch("Backend_server.services.sql_executor.os.path.exists")
    def test_init(self, mock_exists):
        mock_exists.return_value = True
        validator = SQLiteValidator(db_path="dummy.db")
        self.assertEqual(validator.db_path, "dummy.db")

    @patch("Backend_server.services.sql_executor.sqlite3.connect")
    def test_execute_validation_query(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [("txn1",)]
        validator = SQLiteValidator(db_path="dummy.db")
        result = validator.execute_validation_query(
            "SELECT * FROM transactions", "rule1", "Test Rule")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_id"], "txn1")

    @patch("Backend_server.services.sql_executor.json.load")
    @patch("Backend_server.services.sql_executor.open")
    def test_load_validation_rules(self, mock_open, mock_json_load):
        mock_json_load.return_value = {"rule1": {"status": "active"}}
        validator = SQLiteValidator(db_path="dummy.db")
        result = validator.load_validation_rules("dummy_rules.json")
        self.assertIn("rule1", result)

    @patch("Backend_server.services.sql_executor.SQLiteValidator.execute_validation_query")
    @patch("Backend_server.services.sql_executor.sqlite3.connect")
    def test_validate_data(self, mock_connect, mock_execute_query):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = [100]
        mock_execute_query.return_value = [{"transaction_id": "txn1"}]
        validator = SQLiteValidator(db_path="dummy.db")
        result = validator.validate_data("dummy_rules.json")
        self.assertEqual(result["failed_transactions"], 1)


if __name__ == "__main__":
    unittest.main()
