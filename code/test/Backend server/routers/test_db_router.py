import pytest
from fastapi.testclient import TestClient
from Backend_server.routers.db_router import router
from unittest.mock import patch

client = TestClient(router)


def test_get_all_rules():
    with patch("services.db_services.get_rules") as mock_get_rules:
        mock_get_rules.return_value = [
            (1, "Rule 1", "Description 1", "active")]
        response = client.get("/dbget")
        assert response.status_code == 200
        assert response.json() == {
            "rules": [{"id": 1, "name": "Rule 1", "description": "Description 1", "status": "active"}]
        }


def test_add_new_rule():
    with patch("services.db_services.add_rules") as mock_add_rules:
        mock_add_rules.return_value = "Rule added successfully"
        response = client.post(
            "/dbadd",
            json={"name": "Rule 1",
                  "description": "Description 1", "status": "active"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Rule added successfully"}


def test_delete_rule():
    with patch("services.db_services.delete_rules") as mock_delete_rules:
        mock_delete_rules.return_value = "Rule deleted successfully"
        response = client.delete("/dbdelete/1")
        assert response.status_code == 200
        assert response.json() == {"message": "Rule deleted successfully"}


def test_update_rule():
    with patch("services.db_services.edit_rules") as mock_edit_rules:
        mock_edit_rules.return_value = "Rule updated successfully"
        response = client.put(
            "/dbupdate/1",
            json={"field_name": "status", "value": "inactive"}
        )
        assert response.status_code == 200
        assert response.json() == {"message": "Rule updated successfully"}


def test_get_all_transactions():
    with patch("services.db_services.get_transactions") as mock_get_transactions:
        mock_get_transactions.return_value = [{"id": 1, "amount": 100}]
        response = client.get("/dbgetTransaction")
        assert response.status_code == 200
        assert response.json() == {"transactions": [{"id": 1, "amount": 100}]}


def test_upload_transaction_csv():
    with patch("services.db_services.update_transactions_from_csv") as mock_update_csv:
        mock_update_csv.return_value = "Transactions updated successfully"
        response = client.post("/uploadTransactionCSV/1")
        assert response.status_code == 200
        assert response.json() == {
            "message": "Transactions updated successfully"}
