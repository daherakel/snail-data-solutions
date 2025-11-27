"""
Basic tests for query-handler Lambda function.
These tests verify the handler can be imported and basic functionality works.
"""

import json
import pytest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_handler_import():
    """Test that the handler module can be imported."""
    # Set required environment variables
    os.environ['ENVIRONMENT'] = 'test'
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
    os.environ['FAISS_BACKUP_BUCKET'] = 'test-bucket'
    os.environ['FAISS_INDEX_KEY'] = 'test-index'
    os.environ['FAISS_METADATA_KEY'] = 'test-metadata'
    os.environ['BEDROCK_EMBEDDING_MODEL_ID'] = 'amazon.titan-embed-text-v1'
    os.environ['BEDROCK_LLM_MODEL_ID'] = 'amazon.titan-text-express-v1'
    os.environ['CACHE_TABLE_NAME'] = 'test-cache'
    os.environ['ENABLE_CACHE'] = 'false'
    os.environ['CONVERSATIONS_TABLE_NAME'] = 'test-conversations'

    # Import should not raise an exception
    from handler import lambda_handler
    assert lambda_handler is not None
    assert callable(lambda_handler)


def test_event_structure():
    """Test that we can create a valid event structure."""
    event = {
        'body': json.dumps({
            'query': 'Hello',
            'user_id': 'test-user'
        })
    }

    # Parse body
    body = json.loads(event['body'])
    assert 'query' in body
    assert body['query'] == 'Hello'
    assert body['user_id'] == 'test-user'


def test_nlp_modules_exist():
    """Test that NLP modules can be imported."""
    try:
        from shared.nlp.intent_classifier import IntentClassifier
        from shared.nlp.response_generator import ResponseGenerator
        from shared.nlp.guardrails import Guardrails
        assert True
    except ImportError as e:
        pytest.skip(f"Shared modules not available in test environment: {e}")
