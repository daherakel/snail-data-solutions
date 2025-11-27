"""
Lambda Function: Query Handler (REFACTORED)
Procesa queries, busca contexto en FAISS y genera respuestas con RAG usando Bedrock.

CAMBIOS PRINCIPALES:
- Sin regex hardcodeado - Usa LLM para detectar intenciones
- Configuración externalizada en YAML
- Sistema de prompts modulares
- Código limpio y mantenible (~400 líneas vs 1650)
"""

import json
import os
import pickle
import hashlib
import time
import uuid
import sys
from typing import Dict, List, Any, Optional

import boto3
import numpy as np
import faiss

# Agregar shared/ al path para imports
# En Lambda, shared está en el mismo directorio que handler.py
sys.path.insert(0, os.path.dirname(__file__))

from shared.prompts.base_prompts import BasePrompts
from shared.nlp.intent_classifier import IntentClassifier
from shared.nlp.response_generator import ResponseGenerator
from shared.nlp.guardrails import Guardrails
from shared.utils.nlp_config_loader import NLPConfigLoader

# =====================================================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# =====================================================

ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
FAISS_BACKUP_BUCKET = os.environ["FAISS_BACKUP_BUCKET"]
FAISS_INDEX_KEY = os.environ.get("FAISS_INDEX_KEY", "faiss_index.bin")
FAISS_METADATA_KEY = os.environ.get("FAISS_METADATA_KEY", "faiss_metadata.pkl")
BEDROCK_EMBEDDING_MODEL_ID = os.environ.get(
    "BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v1"
)
BEDROCK_LLM_MODEL_ID = os.environ.get(
    "BEDROCK_LLM_MODEL_ID", "amazon.titan-text-express-v1"
)
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Cache configuration
CACHE_TABLE_NAME = os.environ.get("CACHE_TABLE_NAME", "")
ENABLE_CACHE = os.environ.get("ENABLE_CACHE", "true").lower() == "true"

# Conversations configuration
CONVERSATIONS_TABLE_NAME = os.environ.get("CONVERSATIONS_TABLE_NAME", "")

# Clientes AWS
s3_client = boto3.client("s3", region_name=AWS_REGION)
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
dynamodb_client = (
    boto3.client("dynamodb", region_name=AWS_REGION)
    if ENABLE_CACHE and CACHE_TABLE_NAME
    else None
)

# Cache de embeddings en memoria
EMBEDDINGS_CACHE = {}


# =====================================================
# SETUP DE LOGGING Y CONFIGURACIÓN
# =====================================================


def setup_logging():
    """Configura logging basado en LOG_LEVEL"""
    import logging

    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(level=level, format="[%(levelname)s] %(asctime)s - %(message)s")
    return logging.getLogger(__name__)


logger = setup_logging()

# Cargar configuración de NLP
nlp_config_loader = NLPConfigLoader()
nlp_config = nlp_config_loader.load()

# Inicializar sistema de prompts
prompts_system = BasePrompts(
    personality=os.environ.get("AGENT_PERSONALITY", "warm"),
    language=os.environ.get("AGENT_LANGUAGE", "es"),
)

# Inicializar clasificador de intenciones
intent_classifier = IntentClassifier(
    bedrock_client=bedrock_client,
    model_id=nlp_config_loader.get_classifier_config().get("model_id"),
)

# Inicializar generador de respuestas
response_generator = ResponseGenerator(prompts_system)

# Inicializar guardrails
guardrails = Guardrails(nlp_config_loader.get_guardrails_config())


# =====================================================
# FUNCIONES DE FAISS
# =====================================================


def load_faiss_from_s3():
    """
    Carga FAISS index y metadata desde S3.
    Returns: (faiss_index, metadata_list)
    """
    try:
        logger.info(
            f"Cargando FAISS index desde s3://{FAISS_BACKUP_BUCKET}/{FAISS_INDEX_KEY}"
        )

        # Descargar index desde S3
        index_path = "/tmp/faiss_index.bin"
        s3_client.download_file(FAISS_BACKUP_BUCKET, FAISS_INDEX_KEY, index_path)
        index = faiss.read_index(index_path)

        # Descargar metadata
        metadata_path = "/tmp/faiss_metadata.pkl"
        s3_client.download_file(FAISS_BACKUP_BUCKET, FAISS_METADATA_KEY, metadata_path)

        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        logger.info(
            f"FAISS cargado: {index.ntotal} vectores, {len(metadata)} metadatas"
        )
        return index, metadata

    except s3_client.exceptions.NoSuchKey:
        logger.warning("No existe FAISS index en S3")
        raise ValueError(
            "No hay documentos indexados aún. Primero sube documentos al bucket raw."
        )
    except Exception as e:
        logger.error(f"Error cargando FAISS desde S3: {e}")
        raise


def generate_embedding(text: str) -> np.ndarray:
    """
    Genera embedding usando Bedrock Titan con cache.
    Returns: numpy array
    """
    try:
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()

        # Verificar cache
        if text_hash in EMBEDDINGS_CACHE:
            logger.debug(f"Cache hit para query hash: {text_hash[:8]}...")
            return EMBEDDINGS_CACHE[text_hash]

        # Generar embedding con Bedrock
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID, body=json.dumps({"inputText": text})
        )

        result = json.loads(response["body"].read())
        embedding = np.array([result["embedding"]], dtype=np.float32)

        # Guardar en cache
        EMBEDDINGS_CACHE[text_hash] = embedding
        logger.debug(f"Embedding generado y cacheado: {text_hash[:8]}...")

        return embedding

    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        raise


def search_similar_chunks(
    faiss_index: faiss.Index,
    metadata_list: List[Dict[str, Any]],
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Busca chunks similares en FAISS.
    """
    logger.info(f"Buscando contexto relevante para: '{query}'")

    if faiss_index.ntotal == 0:
        logger.error("FAISS index está vacío")
        return []

    # Generar embedding de la query
    query_embedding = generate_embedding(query)

    # Buscar en FAISS
    distances, indices = faiss_index.search(
        query_embedding, min(top_k, faiss_index.ntotal)
    )

    # Formatear resultados
    chunks = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata_list):
            chunks.append(
                {
                    "id": idx,
                    "text": metadata_list[idx]["text"],
                    "metadata": {
                        "source": metadata_list[idx]["source"],
                        "chunk_id": metadata_list[idx]["chunk_id"],
                    },
                    "distance": float(distances[0][i]),
                }
            )

    logger.info(f"Encontrados {len(chunks)} chunks relevantes")
    return chunks


def get_available_documents(metadata_list: List[Dict[str, Any]]) -> List[str]:
    """
    Obtiene lista única de documentos disponibles desde metadata.
    """
    documents = set()
    for item in metadata_list:
        if "source" in item:
            documents.add(item["source"])
    return sorted(list(documents))


# =====================================================
# FUNCIONES DE CACHE (DynamoDB)
# =====================================================


def normalize_query(query: str) -> str:
    """Normaliza una query para el cache"""
    normalized = query.lower().strip()
    normalized = " ".join(normalized.split())
    normalized = normalized.rstrip("?!.,;:")
    return normalized


def get_query_hash(query: str) -> str:
    """Genera un hash SHA256 de la query normalizada"""
    normalized = normalize_query(query)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_from_cache(query: str) -> Optional[Dict[str, Any]]:
    """Busca una query en el cache de DynamoDB"""
    if not ENABLE_CACHE or not dynamodb_client or not CACHE_TABLE_NAME:
        return None

    try:
        query_hash = get_query_hash(query)
        logger.info(f"Buscando en cache: {query_hash[:16]}...")

        response = dynamodb_client.get_item(
            TableName=CACHE_TABLE_NAME, Key={"query_hash": {"S": query_hash}}
        )

        if "Item" not in response:
            logger.info("Cache miss - query no encontrada")
            return None

        item = response["Item"]

        # Verificar TTL
        current_time = int(time.time())
        ttl = int(item.get("ttl", {}).get("N", "0"))

        if ttl > 0 and current_time > ttl:
            logger.info("Cache miss - entrada expirada")
            return None

        # Parsear respuesta del cache
        cached_data = {
            "answer": item.get("answer", {}).get("S", ""),
            "sources": [s.get("S", "") for s in item.get("sources", {}).get("L", [])],
            "num_chunks_used": int(item.get("num_chunks_used", {}).get("N", "0")),
            "from_cache": True,
        }

        logger.info("Cache HIT!")
        return cached_data

    except Exception as e:
        logger.error(f"Error al buscar en cache: {e}")
        return None


def save_to_cache(query: str, answer: str, sources: List[str], num_chunks: int) -> None:
    """Guarda una respuesta en el cache de DynamoDB"""
    if not ENABLE_CACHE or not dynamodb_client or not CACHE_TABLE_NAME:
        return

    try:
        query_hash = get_query_hash(query)
        current_time = int(time.time())

        # Obtener TTL desde configuración
        cache_config = nlp_config_loader.get_cache_config()
        ttl = current_time + cache_config.get("default_ttl_seconds", 604800)

        item = {
            "query_hash": {"S": query_hash},
            "query_text": {"S": query[:500]},
            "answer": {"S": answer},
            "sources": {"L": [{"S": s} for s in sources]},
            "num_chunks_used": {"N": str(num_chunks)},
            "created_at": {"N": str(current_time)},
            "ttl": {"N": str(ttl)},
        }

        dynamodb_client.put_item(TableName=CACHE_TABLE_NAME, Item=item)
        logger.info(f"Respuesta guardada en cache (hash: {query_hash[:16]}...)")

    except Exception as e:
        logger.error(f"Error al guardar en cache: {e}")


# =====================================================
# FUNCIONES DE CONVERSACIONES (DynamoDB)
# =====================================================


def load_conversation(conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Carga historial de una conversación"""
    if not CONVERSATIONS_TABLE_NAME:
        return []

    try:
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            KeyConditionExpression="conversation_id = :conv_id",
            ExpressionAttributeValues={":conv_id": {"S": conversation_id}},
            ScanIndexForward=False,
            Limit=limit * 2,
        )

        items = response.get("Items", [])
        messages = []

        for item in reversed(items):
            messages.append(
                {
                    "role": item.get("role", {}).get("S", ""),
                    "content": item.get("content", {}).get("S", ""),
                    "timestamp": int(item.get("timestamp", {}).get("N", "0")),
                }
            )

        logger.info(
            f"Cargados {len(messages)} mensajes de conversación {conversation_id}"
        )
        return messages

    except Exception as e:
        logger.error(f"Error cargando conversación: {e}")
        return []


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    user_id: str = "anonymous",
    title: str = None,
    usage: dict = None,
    sources: list = None,
    num_chunks_used: int = 0,
):
    """Guarda un mensaje en DynamoDB"""
    if not CONVERSATIONS_TABLE_NAME:
        return

    timestamp = int(time.time() * 1000)
    message_id = f"{timestamp}#{uuid.uuid4().hex[:8]}"

    item = {
        "conversation_id": {"S": conversation_id},
        "message_id": {"S": message_id},
        "user_id": {"S": user_id},
        "role": {"S": role},
        "content": {"S": content},
        "timestamp": {"N": str(timestamp)},
        "updated_at": {"N": str(timestamp)},
    }

    if title:
        item["title"] = {"S": title}

    if role == "assistant" and usage:
        item["usage"] = {
            "M": {
                "input_tokens": {"N": str(usage.get("input_tokens", 0))},
                "output_tokens": {"N": str(usage.get("output_tokens", 0))},
                "total_tokens": {"N": str(usage.get("total_tokens", 0))},
            }
        }

    if sources:
        item["sources"] = {"L": [{"S": s} for s in sources]}
        item["num_chunks_used"] = {"N": str(num_chunks_used)}

    try:
        dynamodb_client.put_item(TableName=CONVERSATIONS_TABLE_NAME, Item=item)
        logger.info(f"Mensaje guardado: {conversation_id}/{message_id}")
    except Exception as e:
        logger.error(f"Error guardando mensaje: {e}")


# =====================================================
# GENERACIÓN DE RESPUESTAS CON RAG
# =====================================================


def generate_rag_response(
    query: str,
    context_chunks: List[Dict[str, Any]],
    conversation_history: Optional[List[Dict[str, str]]] = None,
    intent: str = "document_query",
) -> Dict[str, Any]:
    """
    Genera respuesta usando RAG con Bedrock.
    """
    logger.info(f"Generando respuesta con RAG... (Intent: {intent})")

    # Construir prompts usando el generador
    system_prompt, user_prompt = response_generator.build_rag_prompt(
        query=query,
        context_chunks=context_chunks,
        conversation_history=conversation_history,
        intent=intent,
    )

    try:
        # Detectar tipo de modelo
        is_claude = "claude" in BEDROCK_LLM_MODEL_ID.lower()
        is_llama = "llama" in BEDROCK_LLM_MODEL_ID.lower()
        is_titan = "titan" in BEDROCK_LLM_MODEL_ID.lower()

        # Construir request según modelo
        if is_claude:
            messages = []
            if conversation_history:
                for msg in conversation_history[-10:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})

            messages.append({"role": "user", "content": user_prompt})

            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 300,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.5,
            }

        elif is_llama:
            full_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|>"

            if conversation_history:
                for msg in conversation_history[-10:]:
                    role = "user" if msg["role"] == "user" else "assistant"
                    full_prompt += f"<|start_header_id|>{role}<|end_header_id|>\n\n{msg['content']}<|eot_id|>"

            full_prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

            request_body = {
                "prompt": full_prompt,
                "max_gen_len": 300,
                "temperature": 0.5,
                "top_p": 0.9,
            }

        elif is_titan:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"

            request_body = {
                "inputText": full_prompt,
                "textGenerationConfig": {
                    "maxTokenCount": 300,
                    "temperature": 0.5,
                    "topP": 0.8,
                },
            }

        else:
            raise ValueError(f"Modelo no soportado: {BEDROCK_LLM_MODEL_ID}")

        # Invocar modelo
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_LLM_MODEL_ID, body=json.dumps(request_body)
        )

        result = json.loads(response["body"].read())

        # Extraer respuesta según modelo
        if is_claude:
            answer = result["content"][0]["text"]
            input_tokens = result.get("usage", {}).get("input_tokens", 0)
            output_tokens = result.get("usage", {}).get("output_tokens", 0)

        elif is_llama:
            answer = result.get("generation", "").strip()
            input_tokens = result.get("prompt_token_count", 0)
            output_tokens = result.get("generation_token_count", 0)

        elif is_titan:
            answer = result.get("results", [{}])[0].get("outputText", "").strip()
            input_tokens = result.get("inputTextTokenCount", 0)
            output_tokens = result.get("results", [{}])[0].get("tokenCount", 0)

        # Preparar excerpts
        excerpts = []
        for chunk in context_chunks[:3]:
            excerpts.append(
                {
                    "source": chunk["metadata"]["source"],
                    "text": (
                        chunk["text"][:200] + "..."
                        if len(chunk["text"]) > 200
                        else chunk["text"]
                    ),
                    "relevance": round(1 / (1 + chunk["distance"]), 3),
                }
            )

        logger.info(f"Respuesta generada: {len(answer)} caracteres")

        return {
            "answer": answer,
            "sources": list(
                set([chunk["metadata"]["source"] for chunk in context_chunks])
            ),
            "excerpts": excerpts,
            "num_chunks_used": len(context_chunks),
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
            },
        }

    except Exception as e:
        logger.error(f"Error generando respuesta con Bedrock: {e}")
        raise


# =====================================================
# LAMBDA HANDLER PRINCIPAL
# =====================================================


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda.
    Mucho más simple y limpio usando el sistema de NLP.
    """
    try:
        logger.info(
            f"Evento recibido: {json.dumps(event, ensure_ascii=False)[:500]}..."
        )

        # Parsear body desde evento
        if "body" in event:
            body = (
                json.loads(event["body"])
                if isinstance(event["body"], str)
                else event["body"]
            )
        else:
            body = event

        # Obtener query
        query = body.get("query")
        if not query:
            raise ValueError("Evento debe contener 'query'")

        # Obtener o crear conversation_id
        conversation_id = body.get("conversation_id", f"conv_{uuid.uuid4().hex[:12]}")

        # Cargar historial de conversación
        conversation_history = load_conversation(conversation_id)

        # 1. APLICAR GUARDRAILS
        is_valid, rejection_message = guardrails.validate(query)
        if not is_valid:
            return {
                "statusCode": 400,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "query": query,
                        "answer": rejection_message,
                        "sources": [],
                        "guardrail_triggered": True,
                    },
                    ensure_ascii=False,
                ),
            }

        # 2. CLASIFICAR INTENCIÓN CON LLM
        classification = intent_classifier.classify(query, conversation_history)
        intent = classification["intent"]
        requires_docs = classification["requires_documents"]

        logger.info(f"Intención clasificada: {intent} (requiere docs: {requires_docs})")

        # 3. MANEJAR RESPUESTAS SIMPLES (sin documentos)
        if not requires_docs:
            answer = response_generator.generate_simple_response(
                intent=intent, query=query, entities=classification.get("entities", [])
            )

            # Guardar en conversación
            save_message(conversation_id=conversation_id, role="user", content=query)
            save_message(
                conversation_id=conversation_id, role="assistant", content=answer
            )

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "conversation_id": conversation_id,
                        "query": query,
                        "answer": answer,
                        "sources": [],
                        "intent": intent,
                        "usage": {
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "total_tokens": 0,
                        },
                    },
                    ensure_ascii=False,
                ),
            }

        # 4. MANEJAR LISTA DE DOCUMENTOS
        if intent == "document_list":
            faiss_index, metadata_list = load_faiss_from_s3()
            documents = get_available_documents(metadata_list)
            answer = response_generator.generate_document_list_response(documents)

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "conversation_id": conversation_id,
                        "query": query,
                        "answer": answer,
                        "sources": documents,
                        "intent": intent,
                        "is_document_list": True,
                    },
                    ensure_ascii=False,
                ),
            }

        # 5. REVISAR CACHE
        cached_response = get_from_cache(query)
        if cached_response:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "conversation_id": conversation_id,
                        "query": query,
                        "answer": cached_response["answer"],
                        "sources": cached_response["sources"],
                        "num_chunks_used": cached_response["num_chunks_used"],
                        "from_cache": True,
                        "intent": intent,
                    },
                    ensure_ascii=False,
                ),
            }

        # 6. CARGAR FAISS Y BUSCAR CONTEXTO
        faiss_index, metadata_list = load_faiss_from_s3()

        # Obtener top_k desde configuración
        search_config = nlp_config_loader.get_search_config()
        top_k = search_config.get("default_top_k", 5)

        context_chunks = search_similar_chunks(
            faiss_index, metadata_list, query, top_k=top_k
        )

        if not context_chunks:
            return {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "body": json.dumps(
                    {
                        "message": "No se encontraron documentos relevantes para tu pregunta.",
                        "query": query,
                        "answer": "No encontré información relevante en los documentos. ¿Podrías reformular tu pregunta?",
                        "sources": [],
                        "intent": intent,
                    },
                    ensure_ascii=False,
                ),
            }

        # 7. GENERAR RESPUESTA CON RAG
        rag_result = generate_rag_response(
            query, context_chunks, conversation_history, intent
        )

        # 8. GUARDAR EN CONVERSACIÓN
        save_message(conversation_id=conversation_id, role="user", content=query)
        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=rag_result["answer"],
            usage=rag_result["usage"],
            sources=rag_result["sources"],
            num_chunks_used=rag_result["num_chunks_used"],
        )

        # 9. GUARDAR EN CACHE
        save_to_cache(
            query=query,
            answer=rag_result["answer"],
            sources=rag_result["sources"],
            num_chunks=rag_result["num_chunks_used"],
        )

        # 10. RETORNAR RESPUESTA
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "conversation_id": conversation_id,
                    "query": query,
                    "answer": rag_result["answer"],
                    "sources": rag_result["sources"],
                    "excerpts": rag_result["excerpts"],
                    "intent": intent,
                    "num_chunks_used": rag_result["num_chunks_used"],
                    "usage": rag_result["usage"],
                    "from_cache": False,
                },
                ensure_ascii=False,
            ),
        }

    except Exception as e:
        logger.error(f"Error en lambda_handler: {e}", exc_info=True)

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "error": "Ocurrió un error procesando tu solicitud. Por favor intenta de nuevo.",
                    "detail": str(e) if ENVIRONMENT == "dev" else None,
                },
                ensure_ascii=False,
            ),
        }
