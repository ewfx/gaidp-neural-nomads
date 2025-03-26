import unittest
from unittest.mock import patch, MagicMock
from Backend_server.services.db_services import (
    initialize_db, get_rules, add_rules, edit_rules, delete_rules, get_transactions
)


class TestDBServices(unittest.TestCase):

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_initialize_db(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        initialize_db()
        mock_cursor.execute.assert_called_once()

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_get_rules(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            ("Rule 1", "Description 1", "Active")]
        result = get_rules()
        self.assertEqual(result, [("Rule 1", "Description 1", "Active")])

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_add_rules(self, mock_connect):
        mock_conn = mock_connect.return_value
        result = add_rules("Rule 1", "Description 1", "Active")
        self.assertIn("New rule added successfully", result)

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_edit_rules(self, mock_connect):
        mock_conn = mock_connect.return_value
        result = edit_rules(1, "name", "Updated Rule")
        self.assertIn("updated successfully", result)

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_delete_rules(self, mock_connect):
        mock_conn = mock_connect.return_value
        result = delete_rules(1)
        self.assertIn("deleted successfully", result)

    @patch("Backend_server.services.db_services.sqlite3.connect")
    def test_get_transactions(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [("Transaction 1", 100)]
        result = get_transactions()
        self.assertEqual(result, [("Transaction 1", 100)])


if __name__ == "__main__":
    unittest.main()
