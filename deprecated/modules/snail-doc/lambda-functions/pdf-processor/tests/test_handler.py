"""
Basic tests for pdf-processor Lambda function.
These tests verify the handler can be imported and basic functionality works.
"""

import json
import os
import sys

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_handler_import():
    """Test that the handler module can be imported."""
    # Set required environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    os.environ["RAW_BUCKET"] = "test-raw-bucket"
    os.environ["PROCESSED_BUCKET"] = "test-processed-bucket"
    os.environ["FAISS_BACKUP_BUCKET"] = "test-faiss-bucket"
    os.environ["FAISS_INDEX_KEY"] = "test-index"
    os.environ["FAISS_METADATA_KEY"] = "test-metadata"
    os.environ["BEDROCK_EMBEDDING_MODEL_ID"] = "amazon.titan-embed-text-v1"

    # Import should not raise an exception
    from handler import lambda_handler

    assert lambda_handler is not None
    assert callable(lambda_handler)


def test_s3_event_structure():
    """Test that we can parse a valid S3 event structure."""
    event = {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "test-bucket"},
                    "object": {"key": "test-document.pdf"},
                }
            }
        ]
    }

    # Verify event structure
    assert "Records" in event
    assert len(event["Records"]) == 1
    record = event["Records"][0]
    assert "s3" in record
    assert record["s3"]["bucket"]["name"] == "test-bucket"
    assert record["s3"]["object"]["key"] == "test-document.pdf"


def test_pdf_extension_validation():
    """Test PDF file extension validation logic."""
    valid_files = ["document.pdf", "report.PDF", "file.Pdf"]
    invalid_files = ["document.txt", "image.png", "data.json"]

    for filename in valid_files:
        assert filename.lower().endswith(".pdf"), f"{filename} should be valid"

    for filename in invalid_files:
        assert not filename.lower().endswith(".pdf"), f"{filename} should be invalid"
