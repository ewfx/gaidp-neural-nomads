import json
import pytest
from fastapi.testclient import TestClient
from Backend_server.routers.create_rules import router

client = TestClient(router)


@pytest.fixture
def mock_pdf_request():
    return {
        "file_path": "test_files/sample.pdf",
        "output_file": "test_files/output.json"
    }


def test_generate_rules_success(mock_pdf_request, monkeypatch):
    class MockDocumentProcessor:
        def __init__(self, model_name):
            pass

        def process_document(self, file_path):
            return {"mock_key": "mock_value"}

    class MockSQLiteQueryGenerator:
        def __init__(self, model_name, output_file):
            pass

        def process_rules(self):
            return {"rules": ["rule1", "rule2"]}

    monkeypatch.setattr(
        "Backend_server.routers.create_rules.DocumentProcessor",
        MockDocumentProcessor
    )
    monkeypatch.setattr(
        "Backend_server.routers.create_rules.SQLiteQueryGenerator",
        MockSQLiteQueryGenerator
    )

    response = client.post("/generate/rules", json=mock_pdf_request)
    assert response.status_code == 200
    assert response.json()["message"] == "Rules generated successfully"
    assert "results" in response.json()


def test_generate_rules_failure(mock_pdf_request, monkeypatch):
    class MockDocumentProcessor:
        def __init__(self, model_name):
            pass

        def process_document(self, file_path):
            raise Exception("Mock processing error")

    monkeypatch.setattr(
        "Backend_server.routers.create_rules.DocumentProcessor",
        MockDocumentProcessor
    )

    response = client.post("/generate/rules", json=mock_pdf_request)
    assert response.status_code == 500
    assert "detail" in response.json()
    assert response.json()["detail"] == "Mock processing error"
