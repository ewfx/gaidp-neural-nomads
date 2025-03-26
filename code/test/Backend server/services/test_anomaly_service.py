import unittest
from unittest.mock import patch, MagicMock
from Backend_server.services.anamoly_service import train_model, detect_anomalies, analyze_anomalies


class TestAnomalyService(unittest.TestCase):

    @patch("Backend_server.services.anamoly_service.pd.read_csv")
    @patch("Backend_server.services.anamoly_service.joblib.dump")
    def test_train_model(self, mock_dump, mock_read_csv):
        mock_read_csv.return_value = MagicMock()
        result = train_model("dummy_path.csv")
        self.assertIn("Model trained and saved", result)

    @patch("Backend_server.services.anamoly_service.joblib.load")
    @patch("Backend_server.services.anamoly_service.pd.read_csv")
    def test_detect_anomalies(self, mock_read_csv, mock_load):
        mock_load.return_value = {
            "model": MagicMock(predict=MagicMock(return_value=[-1, 1])),
            "scaler": MagicMock(transform=MagicMock(return_value=[[0.1], [0.2]])),
            "encoders": {}
        }
        mock_read_csv.return_value = MagicMock()
        result = detect_anomalies("dummy_path.csv")
        self.assertEqual(result, [])

    @patch("Backend_server.services.anamoly_service.joblib.load")
    @patch("Backend_server.services.anamoly_service.pd.read_csv")
    @patch("Backend_server.services.anamoly_service.gemini_model.generate_content")
    def test_analyze_anomalies(self, mock_generate_content, mock_read_csv, mock_load):
        mock_load.return_value = {"df_original": MagicMock()}
        mock_read_csv.return_value = MagicMock()
        mock_generate_content.return_value.text = '{"1": "Reason for anomaly"}'
        result = analyze_anomalies(["1"], "dummy_path.csv")
        self.assertIn("Reason for anomaly", result)


if __name__ == "__main__":
    unittest.main()
