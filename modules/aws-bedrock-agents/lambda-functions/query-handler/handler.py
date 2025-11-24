"""
Lambda Function: Query Handler
Procesa queries, busca contexto en FAISS y genera respuestas con RAG usando Bedrock
"""

import json
import os
import pickle
from typing import Dict, List, Any

import boto3
import numpy as np

# FAISS for vector search (desde Lambda Layer)
import faiss

# Configuración desde variables de entorno
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
FAISS_BACKUP_BUCKET = os.environ['FAISS_BACKUP_BUCKET']
FAISS_INDEX_KEY = os.environ.get('FAISS_INDEX_KEY', 'faiss_index.bin')
FAISS_METADATA_KEY = os.environ.get('FAISS_METADATA_KEY', 'faiss_metadata.pkl')
BEDROCK_EMBEDDING_MODEL_ID = os.environ.get('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1')
BEDROCK_LLM_MODEL_ID = os.environ.get('BEDROCK_LLM_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
MAX_CONTEXT_CHUNKS = int(os.environ.get('MAX_CONTEXT_CHUNKS', '5'))

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)


def setup_logging():
    """Configura logging basado en LOG_LEVEL"""
    import logging
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(asctime)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()


def load_faiss_from_s3():
    """
    Carga FAISS index y metadata desde S3
    Returns: (faiss_index, metadata_list)
    """
    try:
        logger.info(f"Cargando FAISS index desde s3://{FAISS_BACKUP_BUCKET}/{FAISS_INDEX_KEY}")

        # Descargar index desde S3
        index_path = '/tmp/faiss_index.bin'
        s3_client.download_file(FAISS_BACKUP_BUCKET, FAISS_INDEX_KEY, index_path)

        # Cargar index
        index = faiss.read_index(index_path)

        # Descargar metadata
        metadata_path = '/tmp/faiss_metadata.pkl'
        s3_client.download_file(FAISS_BACKUP_BUCKET, FAISS_METADATA_KEY, metadata_path)

        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)

        logger.info(f"FAISS cargado: {index.ntotal} vectores, {len(metadata)} metadatas")

        return index, metadata

    except s3_client.exceptions.NoSuchKey:
        logger.warning("No existe FAISS index en S3")
        raise ValueError("No hay documentos indexados aún. Primero sube documentos al bucket raw.")

    except Exception as e:
        logger.error(f"Error cargando FAISS desde S3: {e}")
        raise


def generate_embedding(text: str) -> np.ndarray:
    """
    Genera embedding usando Bedrock Titan
    Returns: numpy array
    """
    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": text})
        )

        result = json.loads(response['body'].read())
        embedding = np.array([result['embedding']], dtype=np.float32)

        return embedding

    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        raise


def search_similar_chunks(
    faiss_index: faiss.Index,
    metadata_list: List[Dict[str, Any]],
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca chunks similares en FAISS
    """
    logger.info(f"Buscando contexto relevante para: '{query}'")

    if faiss_index.ntotal == 0:
        logger.error("FAISS index está vacío")
        return []

    # Generar embedding de la query
    query_embedding = generate_embedding(query)

    # Buscar en FAISS (retorna distances y indices)
    distances, indices = faiss_index.search(query_embedding, min(top_k, faiss_index.ntotal))

    # Formatear resultados
    chunks = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata_list):  # Validar índice
            chunks.append({
                'id': idx,
                'text': metadata_list[idx]['text'],
                'metadata': {
                    'source': metadata_list[idx]['source'],
                    'chunk_id': metadata_list[idx]['chunk_id']
                },
                'distance': float(distances[0][i])  # L2 distance
            })

    logger.info(f"Encontrados {len(chunks)} chunks relevantes")

    return chunks


def generate_rag_response(query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Genera respuesta usando RAG con Bedrock Claude
    """
    logger.info("Generando respuesta con RAG...")

    # Construir contexto
    context = "\n\n".join([
        f"[Fuente: {chunk['metadata']['source']}, Chunk {chunk['metadata']['chunk_id']}]\n{chunk['text']}"
        for chunk in context_chunks
    ])

    # Prompt para Claude
    prompt = f"""Eres un asistente útil que responde preguntas basándote en documentos.

Contexto de los documentos:
{context}

Pregunta del usuario: {query}

Instrucciones:
- Responde la pregunta basándote SOLO en el contexto proporcionado
- Si la información no está en el contexto, di "No encontré información sobre eso en los documentos"
- Cita las fuentes mencionando el documento y chunk
- Sé conciso y preciso

Respuesta:"""

    # Llamar a Bedrock Claude
    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3
        }

        response = bedrock_client.invoke_model(
            modelId=BEDROCK_LLM_MODEL_ID,
            body=json.dumps(request_body)
        )

        result = json.loads(response['body'].read())
        answer = result['content'][0]['text']

        logger.info(f"Respuesta generada: {len(answer)} caracteres")

        return {
            'answer': answer,
            'sources': list(set([chunk['metadata']['source'] for chunk in context_chunks])),
            'num_chunks_used': len(context_chunks)
        }

    except Exception as e:
        logger.error(f"Error generando respuesta con Bedrock: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda

    Evento esperado:
    {
        "query": "¿Qué dice el documento sobre...?"
    }

    O desde Function URL (HTTP):
    {
        "body": "{\"query\": \"...\"}"
    }
    """
    try:
        logger.info(f"Evento recibido: {json.dumps(event)}")

        # Parsear query desde evento
        if 'body' in event:
            # Request desde Function URL (HTTP)
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            query = body.get('query')
        else:
            # Invocación directa
            query = event.get('query')

        if not query:
            raise ValueError("Evento debe contener 'query'")

        # 1. Cargar FAISS index desde S3
        faiss_index, metadata_list = load_faiss_from_s3()

        # 2. Buscar chunks relevantes
        context_chunks = search_similar_chunks(
            faiss_index,
            metadata_list,
            query,
            top_k=MAX_CONTEXT_CHUNKS
        )

        if not context_chunks:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'message': 'No se encontraron documentos relevantes',
                    'query': query
                })
            }

        # 3. Generar respuesta con RAG
        rag_result = generate_rag_response(query, context_chunks)

        # Resultado exitoso
        result = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'query': query,
                'answer': rag_result['answer'],
                'sources': rag_result['sources'],
                'num_chunks_used': rag_result['num_chunks_used']
            }, ensure_ascii=False)
        }

        logger.info("Query procesada exitosamente")

        return result

    except Exception as e:
        logger.error(f"Error en lambda_handler: {e}", exc_info=True)

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }
