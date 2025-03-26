import pytest
from fastapi.testclient import TestClient
from Backend_server.routers.rule_router import router
from unittest.mock import patch

client = TestClient(router)


def test_get_rules_by_identifier():
    with patch("services.rule_services.get_rules") as mock_get_rules:
        mock_get_rules.return_value = {
            "1": {"rule_id": "1", "rule_name": "Rule 1", "rule_description": "Description 1", "status": "active"}
        }
        response = client.get("/rules/test_identifier")
        assert response.status_code == 200
        assert response.json() == {
            "rules": [{"id": "1", "name": "Rule 1", "description": "Description 1", "status": "active"}]
        }


def test_update_rule():
    with patch("services.rule_services.edit_rule") as mock_edit_rule:
        mock_edit_rule.return_value = "Rule updated successfully"
        response = client.put(
            "/rules/test_identifier/1",
            json={"field_name": "status", "value": "inactive"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Rule updated successfully"}


def test_delete_rule_by_identifier():
    with patch("services.rule_services.delete_rule") as mock_delete_rule:
        mock_delete_rule.return_value = "Rule deleted successfully"
        response = client.delete("/rules/test_identifier/1")
        assert response.status_code == 200
        assert response.json() == {"message": "Rule deleted successfully"}


def test_validate_rules_by_identifier():
    with patch("services.sql_executor.SQLiteValidator.validate_data") as mock_validate_data:
        mock_validate_data.return_value = {"valid": True}
        response = client.get("/rules/validate/test_identifier")
        assert response.status_code == 200
        assert response.json() == {"valid": True}


def test_download_validation_results():
    with patch("os.path.exists") as mock_exists, patch("fastapi.responses.FileResponse") as mock_file_response:
        mock_exists.return_value = True
        response = client.get("/download/test_identifier")
        assert response.status_code == 200
        mock_file_response.assert_called_once()
