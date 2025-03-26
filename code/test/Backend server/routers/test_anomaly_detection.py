from fastapi.testclient import TestClient
from unittest.mock import patch
from Backend_server.routers.anamoly_detection import router


client = TestClient(router)


@patch("services.anamoly_service.train_model")
def test_initiate(mock_train_model):
    mock_train_model.return_value = {
        "status": "success", "message": "Model trained successfully"}

    response = client.get("/initiate")

    mock_train_model.assert_called_once_with("../Temp_files/transaction.csv")
    assert response.status_code == 200
    assert response.json() == {"status": "success",
                               "message": "Model trained successfully"}


@patch("services.anamoly_service.detect_anomalies")
@patch("services.anamoly_service.analyze_anomalies")
def test_anamoly_detection_and_analysis(mock_analyze_anomalies, mock_detect_anomalies):
    mock_detect_anomalies.return_value = [{"id": 1, "value": "anomaly"}]
    mock_analyze_anomalies.return_value = {"analysis": "detailed analysis"}

    response = client.get("/anamoly_detection_and_analysis")

    mock_detect_anomalies.assert_called_once_with("../Temp_files/new_tran.csv")
    mock_analyze_anomalies.assert_called_once_with(
        [{"id": 1, "value": "anomaly"}], "../Temp_files/new_tran.csv")
    assert response.status_code == 200
    assert response.json() == {"analysis": "detailed analysis"}


@patch("services.anamoly_service.train_model")
@patch("services.anamoly_service.detect_anomalies")
@patch("services.anamoly_service.analyze_anomalies")
def test_anamoly_detection_pipeline(mock_analyze_anomalies, mock_detect_anomalies, mock_train_model):
    mock_train_model.return_value = {
        "status": "success", "message": "Model trained successfully"}
    mock_detect_anomalies.return_value = [{"id": 1, "value": "anomaly"}]
    mock_analyze_anomalies.return_value = {"analysis": "detailed analysis"}

    response = client.get("/anamoly_detection_pipeline")

    mock_train_model.assert_called_once_with("../Temp_files/new_tran.csv")
    mock_detect_anomalies.assert_called_once_with("../Temp_files/new_tran.csv")
    mock_analyze_anomalies.assert_called_once_with(
        [{"id": 1, "value": "anomaly"}], "../Temp_files/new_tran.csv")
    assert response.status_code == 200
    assert response.json() == {"analysis": "detailed analysis"}
