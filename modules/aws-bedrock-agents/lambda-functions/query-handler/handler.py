"""
Lambda Function: Query Handler
Procesa queries, busca contexto en ChromaDB y genera respuestas con RAG usando Bedrock
"""

import json
import os
import tarfile
from typing import Dict, List, Any

import boto3

# Imports de ChromaDB (desde Lambda Layer)
import chromadb
from chromadb.config import Settings

# Configuración desde variables de entorno
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
CHROMADB_BACKUP_BUCKET = os.environ['CHROMADB_BACKUP_BUCKET']
CHROMADB_BACKUP_KEY = os.environ.get('CHROMADB_BACKUP_KEY', 'chromadb_data.tar.gz')
BEDROCK_EMBEDDING_MODEL_ID = os.environ.get('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1')
BEDROCK_LLM_MODEL_ID = os.environ.get('BEDROCK_LLM_MODEL_ID', 'anthropic.claude-3-haiku-20240307-v1:0')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
MAX_CONTEXT_CHUNKS = int(os.environ.get('MAX_CONTEXT_CHUNKS', '5'))

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# ChromaDB temp directory
CHROMA_PERSIST_DIR = '/tmp/chroma'


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


def load_chroma_from_s3() -> chromadb.Client:
    """
    Carga ChromaDB desde S3
    """
    try:
        logger.info(f"Cargando ChromaDB desde s3://{CHROMADB_BACKUP_BUCKET}/{CHROMADB_BACKUP_KEY}")

        # Descargar backup desde S3
        backup_path = '/tmp/chroma_backup.tar.gz'
        s3_client.download_file(CHROMADB_BACKUP_BUCKET, CHROMADB_BACKUP_KEY, backup_path)

        # Extraer
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall('/tmp/')

        logger.info("ChromaDB cargado exitosamente")

    except s3_client.exceptions.NoSuchKey:
        logger.warning("No existe backup de ChromaDB, la base está vacía")
        raise ValueError("No hay documentos indexados aún. Primero sube documentos al bucket raw.")

    except Exception as e:
        logger.error(f"Error cargando ChromaDB desde S3: {e}")
        raise

    # Crear cliente
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_PERSIST_DIR
    ))

    return client


def generate_embedding(text: str) -> List[float]:
    """
    Genera embedding usando Bedrock Titan
    """
    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": text})
        )

        result = json.loads(response['body'].read())
        embedding = result['embedding']

        return embedding

    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        raise


def search_similar_chunks(
    chroma_client: chromadb.Client,
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Busca chunks similares en ChromaDB
    """
    logger.info(f"Buscando contexto relevante para: '{query}'")

    # Obtener colección
    try:
        collection = chroma_client.get_collection(name="documents")
    except Exception:
        logger.error("Colección 'documents' no existe")
        return []

    # Generar embedding de la query
    query_embedding = generate_embedding(query)

    # Buscar en ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances']
    )

    # Formatear resultados
    chunks = []
    if results['ids'] and results['ids'][0]:
        for i in range(len(results['ids'][0])):
            chunks.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
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
            'sources': [chunk['metadata']['source'] for chunk in context_chunks],
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

        # 1. Cargar ChromaDB desde S3
        chroma_client = load_chroma_from_s3()

        # 2. Buscar chunks relevantes
        context_chunks = search_similar_chunks(
            chroma_client,
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
