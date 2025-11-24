"""
Lambda Function: PDF Processor
Procesa PDFs, extrae texto, genera embeddings con Bedrock y guarda en FAISS index
"""

import json
import os
import pickle
from typing import Dict, List, Any

import boto3
from PyPDF2 import PdfReader
import numpy as np

# FAISS for vector search (desde Lambda Layer)
import faiss

# Configuración desde variables de entorno
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
RAW_BUCKET = os.environ['RAW_BUCKET']
PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']
FAISS_BACKUP_BUCKET = os.environ['FAISS_BACKUP_BUCKET']
FAISS_INDEX_KEY = os.environ.get('FAISS_INDEX_KEY', 'faiss_index.bin')
FAISS_METADATA_KEY = os.environ.get('FAISS_METADATA_KEY', 'faiss_metadata.pkl')
BEDROCK_EMBEDDING_MODEL_ID = os.environ.get('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

# Dimensión de embeddings de Titan
EMBEDDING_DIMENSION = 1536


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
    Carga FAISS index y metadata desde S3 si existe, sino crea nuevo
    Returns: (faiss_index, metadata_list)
    """
    try:
        logger.info(f"Intentando cargar FAISS index desde s3://{FAISS_BACKUP_BUCKET}/{FAISS_INDEX_KEY}")

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

        logger.info(f"FAISS index cargado: {index.ntotal} vectores")

        return index, metadata

    except s3_client.exceptions.NoSuchKey:
        logger.info("No existe backup previo de FAISS, creando nuevo index")
    except Exception as e:
        logger.warning(f"Error cargando FAISS desde S3: {e}, creando nuevo index")

    # Crear nuevo index (IndexFlatL2 para búsqueda exacta con L2 distance)
    index = faiss.IndexFlatL2(EMBEDDING_DIMENSION)
    metadata = []

    return index, metadata


def persist_faiss_to_s3(index: faiss.Index, metadata: List[Dict[str, Any]]):
    """
    Persiste FAISS index y metadata a S3
    """
    try:
        logger.info("Persistiendo FAISS index a S3...")

        # Guardar index
        index_path = '/tmp/faiss_index.bin'
        faiss.write_index(index, index_path)
        s3_client.upload_file(index_path, FAISS_BACKUP_BUCKET, FAISS_INDEX_KEY)

        # Guardar metadata
        metadata_path = '/tmp/faiss_metadata.pkl'
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        s3_client.upload_file(metadata_path, FAISS_BACKUP_BUCKET, FAISS_METADATA_KEY)

        logger.info(f"FAISS persistido: s3://{FAISS_BACKUP_BUCKET}/ ({index.ntotal} vectores)")

    except Exception as e:
        logger.error(f"Error persistiendo FAISS a S3: {e}")
        raise


def extract_text_from_pdf(bucket: str, key: str) -> str:
    """
    Extrae texto de un PDF en S3
    """
    logger.info(f"Extrayendo texto de s3://{bucket}/{key}")

    # Descargar PDF
    pdf_path = '/tmp/document.pdf'
    s3_client.download_file(bucket, key, pdf_path)

    # Extraer texto
    reader = PdfReader(pdf_path)
    text = ""

    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += f"\n--- Página {page_num + 1} ---\n{page_text}"

    logger.info(f"Texto extraído: {len(text)} caracteres, {len(reader.pages)} páginas")

    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Divide texto en chunks con overlap
    """
    chunks = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append({
            'id': chunk_id,
            'text': chunk,
            'start': start,
            'end': end
        })

        start += (chunk_size - overlap)
        chunk_id += 1

    logger.info(f"Texto dividido en {len(chunks)} chunks")

    return chunks


def generate_embedding(text: str) -> np.ndarray:
    """
    Genera embedding usando Bedrock Titan
    Returns: numpy array de dimensión EMBEDDING_DIMENSION
    """
    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": text})
        )

        result = json.loads(response['body'].read())
        embedding = np.array(result['embedding'], dtype=np.float32)

        return embedding

    except Exception as e:
        logger.error(f"Error generando embedding: {e}")
        raise


def index_document(
    faiss_index: faiss.Index,
    metadata_list: List[Dict[str, Any]],
    doc_id: str,
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Indexa documento en FAISS
    """
    logger.info(f"Indexando documento {doc_id} con {len(chunks)} chunks")

    # Procesar cada chunk
    embeddings = []
    for chunk in chunks:
        # Generar embedding
        embedding = generate_embedding(chunk['text'])
        embeddings.append(embedding)

        # Agregar metadata
        metadata_list.append({
            "source": doc_id,
            "chunk_id": chunk['id'],
            "text": chunk['text'],
            "start": chunk['start'],
            "end": chunk['end']
        })

    # Convertir a numpy array y agregar a FAISS
    embeddings_array = np.array(embeddings, dtype=np.float32)
    faiss_index.add(embeddings_array)

    # Stats
    stats = {
        'document_id': doc_id,
        'chunks_indexed': len(chunks),
        'total_vectors': faiss_index.ntotal
    }

    logger.info(f"Documento indexado: {stats}")

    return stats


def save_processed_metadata(bucket: str, key: str, metadata: Dict[str, Any]):
    """
    Guarda metadata del documento procesado en S3
    """
    processed_key = key.replace('.pdf', '_metadata.json')

    s3_client.put_object(
        Bucket=bucket,
        Key=processed_key,
        Body=json.dumps(metadata, indent=2),
        ContentType='application/json'
    )

    logger.info(f"Metadata guardada en s3://{bucket}/{processed_key}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda

    Evento esperado:
    {
        "bucket": "bucket-name",
        "key": "path/to/document.pdf"
    }
    """
    try:
        logger.info(f"Evento recibido: {json.dumps(event)}")

        # Extraer parámetros del evento
        bucket = event.get('bucket') or event.get('Bucket')
        key = event.get('key') or event.get('Key')

        if not bucket or not key:
            raise ValueError("Evento debe contener 'bucket' y 'key'")

        # 1. Cargar FAISS index desde S3
        faiss_index, metadata_list = load_faiss_from_s3()

        # 2. Extraer texto del PDF
        text = extract_text_from_pdf(bucket, key)

        # 3. Dividir en chunks
        chunks = chunk_text(text)

        # 4. Indexar en FAISS
        doc_id = key.replace('/', '_').replace('.pdf', '')
        stats = index_document(faiss_index, metadata_list, doc_id, chunks)

        # 5. Persistir FAISS a S3
        persist_faiss_to_s3(faiss_index, metadata_list)

        # 6. Guardar metadata
        metadata = {
            'source_bucket': bucket,
            'source_key': key,
            'document_id': doc_id,
            'processed_at': context.aws_request_id,
            'stats': stats
        }
        save_processed_metadata(PROCESSED_BUCKET, key, metadata)

        # Resultado exitoso
        result = {
            'statusCode': 200,
            'body': {
                'message': 'Documento procesado exitosamente',
                'document_id': doc_id,
                'stats': stats
            }
        }

        logger.info(f"Procesamiento completado: {result}")

        return result

    except Exception as e:
        logger.error(f"Error en lambda_handler: {e}", exc_info=True)

        return {
            'statusCode': 500,
            'body': {
                'error': str(e)
            }
        }
