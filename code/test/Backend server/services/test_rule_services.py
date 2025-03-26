import unittest
from unittest.mock import patch, mock_open
from Backend_server.services.rule_services import get_rules, edit_rule, delete_rule


class TestRuleServices(unittest.TestCase):

    @patch("Backend_server.services.rule_services.open", new_callable=mock_open, read_data='{"rule1": {"rule_id": "1"}}')
    def test_get_rules(self, mock_file):
        result = get_rules("dummy_rules.json")
        self.assertIn("rule1", result)

    @patch("Backend_server.services.rule_services.open", new_callable=mock_open, read_data='{"rule1": {"rule_id": "1"}}')
    @patch("Backend_server.services.rule_services.json.dump")
    def test_edit_rule(self, mock_json_dump, mock_file):
        result = edit_rule("dummy_rules.json", "1", "field_name", "new_value")
        self.assertIn("updated successfully", result)

    @patch("Backend_server.services.rule_services.open", new_callable=mock_open, read_data='{"rule1": {"rule_id": "1"}}')
    @patch("Backend_server.services.rule_services.json.dump")
    def test_delete_rule(self, mock_json_dump, mock_file):
        result = delete_rule("dummy_rules.json", "rule1")
        self.assertIn("deleted successfully", result)


if __name__ == "__main__":
    unittest.main()
