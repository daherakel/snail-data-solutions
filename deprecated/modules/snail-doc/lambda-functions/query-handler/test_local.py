"""
Script de testing local para query-handler
Permite testear el handler sin necesidad de deployar a AWS
"""

import json
import os
import sys

# Agregar el directorio actual al path para imports
sys.path.insert(0, os.path.dirname(__file__))

# Agregar shared/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

# Configurar variables de entorno antes de importar el handler
os.environ["ENVIRONMENT"] = "dev"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["FAISS_BACKUP_BUCKET"] = "snail-bedrock-dev-chromadb-backup"
os.environ["FAISS_INDEX_KEY"] = "faiss_index.bin"
os.environ["FAISS_METADATA_KEY"] = "faiss_metadata.pkl"
os.environ["BEDROCK_EMBEDDING_MODEL_ID"] = "amazon.titan-embed-text-v1"
os.environ["BEDROCK_LLM_MODEL_ID"] = "amazon.titan-text-express-v1"
os.environ["CACHE_TABLE_NAME"] = "snail-bedrock-dev-query-cache"
os.environ["ENABLE_CACHE"] = "true"
os.environ["CONVERSATIONS_TABLE_NAME"] = "snail-bedrock-dev-conversations"
os.environ["LOG_LEVEL"] = "INFO"
os.environ["AGENT_PERSONALITY"] = "warm"
os.environ["AGENT_LANGUAGE"] = "es"

# Ahora importar el handler
from handler import lambda_handler


def test_query(query: str, conversation_id: str = None):
    """
    Testea una query contra el handler local.

    Args:
        query: Query del usuario
        conversation_id: ID de conversación (opcional)
    """
    print(f"\n{'='*80}")
    print(f"TESTING QUERY: {query}")
    print(f"{'='*80}\n")

    # Construir evento
    event = {
        "body": json.dumps(
            {"query": query, "conversation_id": conversation_id, "action": "query"}
        )
    }

    # Ejecutar handler
    try:
        response = lambda_handler(event, None)

        # Parsear respuesta
        status_code = response.get("statusCode", 500)
        body = json.loads(response.get("body", "{}"))

        print(f"Status Code: {status_code}")
        print(f"\nResponse:")
        print(json.dumps(body, indent=2, ensure_ascii=False))

        # Extraer información relevante
        if status_code == 200:
            print(f"\n{'='*80}")
            print(f"ANSWER: {body.get('answer', 'N/A')}")
            print(f"INTENT: {body.get('intent', 'N/A')}")
            print(f"SOURCES: {', '.join(body.get('sources', []))}")
            print(f"FROM CACHE: {body.get('from_cache', False)}")
            print(f"{'='*80}\n")

        return body

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return None


def run_test_suite():
    """
    Ejecuta una suite de tests para verificar el nuevo sistema.
    """
    print("\n" + "=" * 80)
    print("QUERY HANDLER LOCAL TEST SUITE")
    print("=" * 80)

    tests = [
        # Test 1: Saludo
        {"name": "Saludo simple", "query": "hola", "expected_intent": "greeting"},
        # Test 2: Saludo con typo
        {
            "name": "Saludo con typo",
            "query": "holaa como estas",
            "expected_intent": "greeting",
        },
        # Test 3: Agradecimiento
        {"name": "Agradecimiento", "query": "gracias", "expected_intent": "thanks"},
        # Test 4: Agradecimiento con typo
        {
            "name": "Agradecimiento con typo",
            "query": "garcias perfecto",
            "expected_intent": "thanks",
        },
        # Test 5: Lista de documentos
        {
            "name": "Lista de documentos",
            "query": "que documentos tenes",
            "expected_intent": "document_list",
        },
        # Test 6: Query sobre documentos
        {
            "name": "Query sobre documentos",
            "query": "¿Qué dice el documento sobre AWS Bedrock?",
            "expected_intent": "document_query",
        },
        # Test 7: Multi-idioma (inglés)
        {
            "name": "Multi-idioma (inglés)",
            "query": "thank you",
            "expected_intent": "thanks",
        },
    ]

    passed = 0
    failed = 0

    for i, test in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(tests)}: {test['name']}")
        print(f"{'='*80}")

        result = test_query(test["query"])

        if result:
            actual_intent = result.get("intent", "unknown")
            expected_intent = test["expected_intent"]

            if actual_intent == expected_intent:
                print(f"✅ PASSED - Intent detectado correctamente: {actual_intent}")
                passed += 1
            else:
                print(f"❌ FAILED - Expected: {expected_intent}, Got: {actual_intent}")
                failed += 1
        else:
            print(f"❌ FAILED - Error ejecutando test")
            failed += 1

    # Resumen
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {(passed/len(tests)*100):.1f}%")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test query handler locally")
    parser.add_argument("--query", type=str, help="Single query to test")
    parser.add_argument("--conversation-id", type=str, help="Conversation ID")
    parser.add_argument("--suite", action="store_true", help="Run full test suite")

    args = parser.parse_args()

    if args.suite:
        run_test_suite()
    elif args.query:
        test_query(args.query, args.conversation_id)
    else:
        print("Usage:")
        print("  python test_local.py --query 'hola'")
        print("  python test_local.py --suite")
        print(
            "  python test_local.py --query '¿qué documentos hay?' --conversation-id conv_123"
        )
