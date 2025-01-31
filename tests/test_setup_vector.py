import json
import uuid
from unittest.mock import call, patch, MagicMock
from src.setup_vector import DocumentProcessor, EmbeddingIndexer
from langchain.schema import Document

from tests.mocks.mock_data import MOCK_JSON_DATA


@patch("builtins.open", new_callable=MagicMock)
def test_document_processor_load_json_doc(mock_open):
    """
    Test DocumentProcessor.load_json_doc method.
    """
    # Create a file-like object that returns the mock JSON data when read
    mock_file = MagicMock()
    mock_file.read.return_value = json.dumps(MOCK_JSON_DATA)
    mock_open.return_value.__enter__.return_value = mock_file

    processor = DocumentProcessor(file_path="mock_file_path")
    documents = processor.load_json_doc()
    assert documents == MOCK_JSON_DATA


def test_document_processor_process_documents():
    """
    Test DocumentProcessor.process_documents method.
    """
    processor = DocumentProcessor(file_path="mock_file_path")
    documents = MOCK_JSON_DATA
    chunks = processor.process_documents(documents)
    assert len(chunks) == 2
    assert isinstance(chunks, list)
    for idx, chunk in enumerate(chunks):
        doc = MOCK_JSON_DATA[idx]
        assert isinstance(chunk, Document)
        assert chunk.metadata == {
            "tag": "faq",
            "question": doc["question"],
            "answers": ", ".join(doc["answers"]),
            "seq_num": 1,
            "start_index": 0,
            "source": processor.file_path,
        }
        assert chunk.page_content == json.dumps(
            {"question": doc["question"], "answers": doc["answers"]}
        )
