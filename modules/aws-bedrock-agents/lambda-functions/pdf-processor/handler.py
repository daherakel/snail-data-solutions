"""
Lambda Function: PDF Processor
Procesa PDFs, extrae texto, genera embeddings con Bedrock y guarda en ChromaDB
"""

import json
import os
import tarfile
import tempfile
from typing import Dict, List, Any

import boto3
from PyPDF2 import PdfReader

# Imports de ChromaDB (desde Lambda Layer)
import chromadb
from chromadb.config import Settings

# Configuración desde variables de entorno
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'dev')
RAW_BUCKET = os.environ['RAW_BUCKET']
PROCESSED_BUCKET = os.environ['PROCESSED_BUCKET']
CHROMADB_BACKUP_BUCKET = os.environ['CHROMADB_BACKUP_BUCKET']
CHROMADB_BACKUP_KEY = os.environ.get('CHROMADB_BACKUP_KEY', 'chromadb_data.tar.gz')
BEDROCK_EMBEDDING_MODEL_ID = os.environ.get('BEDROCK_EMBEDDING_MODEL_ID', 'amazon.titan-embed-text-v1')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

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
    Carga ChromaDB desde S3 si existe, sino crea nuevo
    """
    try:
        logger.info(f"Intentando cargar ChromaDB desde s3://{CHROMADB_BACKUP_BUCKET}/{CHROMADB_BACKUP_KEY}")

        # Descargar backup desde S3
        backup_path = '/tmp/chroma_backup.tar.gz'
        s3_client.download_file(CHROMADB_BACKUP_BUCKET, CHROMADB_BACKUP_KEY, backup_path)

        # Extraer
        with tarfile.open(backup_path, 'r:gz') as tar:
            tar.extractall('/tmp/')

        logger.info("ChromaDB cargado exitosamente desde S3")

    except s3_client.exceptions.NoSuchKey:
        logger.info("No existe backup previo de ChromaDB, creando nuevo")
    except Exception as e:
        logger.warning(f"Error cargando ChromaDB desde S3: {e}, creando nuevo")

    # Crear o cargar cliente
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_PERSIST_DIR
    ))

    return client


def persist_chroma_to_s3(client: chromadb.Client):
    """
    Persiste ChromaDB a S3
    """
    try:
        logger.info("Persistiendo ChromaDB a S3...")

        # Comprimir directorio de ChromaDB
        backup_path = '/tmp/chroma_backup.tar.gz'
        with tarfile.open(backup_path, 'w:gz') as tar:
            tar.add(CHROMA_PERSIST_DIR, arcname='chroma')

        # Subir a S3
        s3_client.upload_file(backup_path, CHROMADB_BACKUP_BUCKET, CHROMADB_BACKUP_KEY)

        logger.info(f"ChromaDB persistido exitosamente a s3://{CHROMADB_BACKUP_BUCKET}/{CHROMADB_BACKUP_KEY}")

    except Exception as e:
        logger.error(f"Error persistiendo ChromaDB a S3: {e}")
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


def index_document(
    chroma_client: chromadb.Client,
    doc_id: str,
    chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Indexa documento en ChromaDB
    """
    logger.info(f"Indexando documento {doc_id} con {len(chunks)} chunks")

    # Obtener o crear colección
    collection = chroma_client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

    # Procesar cada chunk
    for chunk in chunks:
        chunk_id = f"{doc_id}_{chunk['id']}"

        # Generar embedding
        embedding = generate_embedding(chunk['text'])

        # Agregar a ChromaDB
        collection.add(
            embeddings=[embedding],
            documents=[chunk['text']],
            metadatas=[{
                "source": doc_id,
                "chunk_id": chunk['id'],
                "start": chunk['start'],
                "end": chunk['end']
            }],
            ids=[chunk_id]
        )

    # Obtener stats de la colección
    stats = {
        'document_id': doc_id,
        'chunks_indexed': len(chunks),
        'total_documents': collection.count()
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

        # 1. Cargar ChromaDB desde S3
        chroma_client = load_chroma_from_s3()

        # 2. Extraer texto del PDF
        text = extract_text_from_pdf(bucket, key)

        # 3. Dividir en chunks
        chunks = chunk_text(text)

        # 4. Indexar en ChromaDB
        doc_id = key.replace('/', '_').replace('.pdf', '')
        stats = index_document(chroma_client, doc_id, chunks)

        # 5. Persistir ChromaDB a S3
        persist_chroma_to_s3(chroma_client)

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
