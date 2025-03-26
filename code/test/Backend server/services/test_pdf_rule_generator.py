import unittest
from unittest.mock import patch, MagicMock
from Backend_server.services.pdf_rule_generator import DocumentProcessor


class TestDocumentProcessor(unittest.TestCase):

    @patch("Backend_server.services.pdf_rule_generator.PyPDFLoader")
    def test_extract_pdf_text(self, mock_loader):
        mock_loader.return_value.load.return_value = [
            MagicMock(page_content="Page 1 content"),
            MagicMock(page_content="Page 2 content")
        ]
        processor = DocumentProcessor()
        result = processor.extract_pdf_text("dummy_path.pdf")
        self.assertEqual(result, "Page 1 content\n\nPage 2 content")

    def test_split_text(self):
        processor = DocumentProcessor()
        text = "This is a test document. " * 100
        chunks = processor.split_text(text, chunk_size=50)
        self.assertTrue(all(len(chunk) <= 50 for chunk in chunks))

    @patch("Backend_server.services.pdf_rule_generator.LLMChain.run")
    def test_extract_all_fields(self, mock_run):
        mock_run.return_value = '{"fields": {"1": "Field Name 1", "2": "Field Name 2"}}'
        processor = DocumentProcessor()
        result = processor.extract_all_fields("Sample document text")
        self.assertEqual(result, {"1": "Field Name 1", "2": "Field Name 2"})

    @patch("Backend_server.services.pdf_rule_generator.LLMChain.run")
    def test_generate_rules_for_fields(self, mock_run):
        mock_run.return_value = '{"Field Name 1": {"field_number": "1", "data_type": "string"}}'
        processor = DocumentProcessor()
        fields = {"1": "Field Name 1"}
        result = processor.generate_rules_for_fields(
            "Sample document text", fields)
        self.assertIn("Field Name 1", result)


if __name__ == "__main__":
    unittest.main()
