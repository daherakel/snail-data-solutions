"""
Lambda Function: Query Handler
Procesa queries, busca contexto en FAISS y genera respuestas con RAG usando Bedrock
Incluye soporte para conversaciones con historial, guardrails y límites de uso
"""

import json
import os
import pickle
import hashlib
import re
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple

import boto3
import numpy as np

# FAISS for vector search (desde Lambda Layer)
import faiss

# Cache de embeddings en memoria (para queries)
EMBEDDINGS_CACHE = {}

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

# Cache configuration
CACHE_TABLE_NAME = os.environ.get('CACHE_TABLE_NAME', '')
CACHE_TTL_SECONDS = int(os.environ.get('CACHE_TTL_SECONDS', '604800'))  # 7 days default
ENABLE_CACHE = os.environ.get('ENABLE_CACHE', 'true').lower() == 'true'

# Límites conversacionales
MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', '10'))  # Últimos 10 mensajes
MAX_TOKENS_PER_RESPONSE = int(os.environ.get('MAX_TOKENS_PER_RESPONSE', '800'))  # Limitar respuesta
MAX_QUERY_LENGTH = int(os.environ.get('MAX_QUERY_LENGTH', '500'))  # Caracteres máximos por query

# Conversations configuration
CONVERSATIONS_TABLE_NAME = os.environ.get('CONVERSATIONS_TABLE_NAME', '')
MAX_HISTORY_MESSAGES = int(os.environ.get('MAX_HISTORY_MESSAGES', '10'))

# Clientes AWS
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION) if ENABLE_CACHE and CACHE_TABLE_NAME else None


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


def detect_user_intent(text: str) -> str:
    """
    Detecta la intención del usuario para adaptar la respuesta
    Returns: intent type (search, summarize, explain, list, compare, question, thanks, greeting)
    """
    text_lower = text.lower().strip()

    # Agradecimientos y cortesías (más prioritario)
    if is_thanks_or_courtesy(text_lower):
        return 'thanks'

    # Saludos (permiten texto adicional después)
    if re.search(r'^(hola|hi|hey|buenas|buenos días|buenas tardes|buenas noches|saludos|qué tal|que tal|cómo estás|como estas|qué onda|que onda)', text_lower):
        return 'greeting'

    # Intent patterns
    if re.search(r'(resume|resumen|resumir|sintetiza|sintetizar|overview)', text_lower):
        return 'summarize'

    if re.search(r'(explica|explicar|qué significa|qué es|define|definir|cómo funciona)', text_lower):
        return 'explain'

    if re.search(r'(lista|listar|cuáles son|enumera|muestra|menciona)', text_lower):
        return 'list'

    if re.search(r'(compara|comparar|diferencia|diferencias|vs|versus)', text_lower):
        return 'compare'

    if re.search(r'(encuentra|busca|buscar|dónde|donde dice)', text_lower):
        return 'search'

    # Default: question
    return 'question'


def is_thanks_or_courtesy(text: str) -> bool:
    """
    Detecta agradecimientos y expresiones de cortesía
    """
    text_lower = text.lower().strip()

    # Patrones de agradecimiento
    thanks_patterns = [
        r'^(muchas\s+)?gracias(\s+(lindo|genial|perfecto|excelente))?[\s\!¡\.]*$',
        r'^(perfecto|genial|excelente|buenísimo|ok|okay|bien|de\s+lujo)[\s\!¡\.]*$',
        r'^(perfecto|genial|excelente)\s+(muchas\s+)?gracias[\s\!¡\.]*$',
        r'^gracias(\s+(por|x))?\s+(todo|la\s+ayuda|tu\s+ayuda|la\s+info)[\s\!¡\.]*$',
        r'^muy\s+(bien|bueno|útil|claro)[\s\!¡\.]*$',
        r'^(te|le)\s+agradezco[\s\!¡\.]*$',
        r'^eso\s+es\s+todo[\s\!¡\.]*$',
        r'^nada\s+más[\s\!¡\.]*$',
    ]

    for pattern in thanks_patterns:
        if re.search(pattern, text_lower):
            return True

    return False


def get_available_documents(metadata_list: List[Dict[str, Any]]) -> List[str]:
    """
    Obtiene lista única de documentos disponibles desde metadata
    """
    documents = set()
    for item in metadata_list:
        if 'source' in item:
            documents.add(item['source'])
    return sorted(list(documents))


def is_document_list_request(text: str) -> bool:
    """
    Detecta si el usuario está pidiendo ver la lista de documentos
    """
    text_lower = text.lower().strip()

    patterns = [
        # Preguntas directas sobre documentos
        r'(qué|que|cuáles|cuales)\s+(documentos|archivos|pdfs?)\s+(tienes|tenes|hay|están|estan|disponibles)',
        r'(documentos|archivos|pdfs?)\s+(tienes|tenes|hay|disponibles)',

        # Solicitudes de listar
        r'(lista|listar|mostrar|enumerar)\s+.*?(documentos|archivos|pdfs?)',
        r'(quiero|queres|podes|puedes)\s+que\s+.*?(liste|listes|muestre|muestres)\s+.*?(documentos|archivos|titulos?)',

        # Mencionar o dar títulos
        r'(podes|puedes|podés)\s+.*?(mencionarme|decirme|darme|mostrarme)\s+.*?(titulos?|documentos|archivos)',
        r'(mencionar|decir|dar|mostrar)\s+.*?(titulos?|documentos)',

        # Preguntas sobre disponibilidad
        r'(documentos|archivos|pdfs?)\s+disponibles',
        r'^(lista|muestra|dame)\s+(documentos|archivos)',
        r'(cuántos|cuantos)\s+(documentos|archivos)',

        # Títulos de documentos
        r'títulos?\s+de\s+(documentos|archivos)',
        r'títulos?\s+(de\s+los\s+)?(documentos|archivos)',
    ]

    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def clean_formal_phrases(text: str) -> str:
    """
    Elimina frases formales/académicas de las respuestas
    """
    # Lista de frases a eliminar (con variaciones)
    formal_phrases = [
        # Frases con palabras de relleno + según/de acuerdo
        r'^(Veamos|Bueno|Bien|Ok|Okay)[,\s]+según (los documentos|la información|el contexto)[,\s]+',
        r'^(Veamos|Bueno|Bien|Ok|Okay)[,\s]+de acuerdo con (los documentos|la información)[,\s]+',

        # Frases al inicio de párrafos
        r'^Según la información (que tengo|proporcionada|disponible|del contexto|de los documentos)[,\s]+',
        r'^Según los (documentos|datos|archivos)[,\s]+',
        r'^De acuerdo con (la información|los documentos|el contexto|los datos)[,\s]+',
        r'^En los documentos se menciona (que)?[,\s]+',
        r'^La información proporcionada indica (que)?[,\s]+',
        r'^Basándome en (la información|los documentos|el contexto)[,\s]+',
        r'^Con base en (la información|los documentos)[,\s]+',

        # Frases en medio de texto
        r',?\s*según (la información proporcionada|los documentos|el contexto),?\s*',
        r',?\s*de acuerdo con (los documentos|la información),?\s*',
        r',?\s*como se menciona en los documentos,?\s*',

        # Palabras formales innecesarias
        r'^Lamentablemente,?\s+',
        r'^Desafortunadamente,?\s+',
        r'^Desgraciadamente,?\s+',
    ]

    cleaned_text = text
    for pattern in formal_phrases:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)

    # Limpiar espacios múltiples y saltos de línea al inicio
    cleaned_text = re.sub(r'^\s+', '', cleaned_text)
    cleaned_text = re.sub(r'\s{2,}', ' ', cleaned_text)

    # Capitalizar la primera letra
    cleaned_text = cleaned_text.strip()
    if cleaned_text:
        cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]

    return cleaned_text


def is_casual_conversation(text: str) -> tuple[bool, Optional[str]]:
    """
    Detecta si es conversación casual (saludo, despedida, etc.)
    Returns: (is_casual, suggested_response)
    """
    text_lower = text.lower().strip()

    # Patrones de saludos
    greetings = [
        r'^(hola|hello|hi|hey|buenas|buenos días|buenas tardes|buenas noches|qué tal|cómo estás)[\s!?]*$',
        r'^(saludos|holi|ola)[\s!?]*$',
    ]

    for pattern in greetings:
        if re.search(pattern, text_lower):
            response = """¡Hola! 👋

Soy tu asistente de documentos. Puedo ayudarte a:
• Buscar información en los documentos
• Responder preguntas sobre el contenido
• Listar los documentos disponibles
• Y mucho más

¿Qué necesitas?"""
            return True, response

    # Patrones de despedida
    farewells = [
        r'^(adiós|adios|chau|bye|hasta luego|nos vemos|gracias|thank you|thanks)[\s!?]*$',
    ]

    for pattern in farewells:
        if re.search(pattern, text_lower):
            response = "¡Hasta luego! 👋 Si necesitas consultar algo más sobre los documentos, aquí estaré. ¡Que tengas un excelente día!"
            return True, response

    # Agradecimientos
    thanks = [
        r'^(gracias|muchas gracias|graciass|thank you|thanks)[\s!?]*$',
    ]

    for pattern in thanks:
        if re.search(pattern, text_lower):
            response = "¡De nada! 😊 Estoy aquí para ayudarte. Si tienes más preguntas sobre los documentos, no dudes en consultarme."
            return True, response

    return False, None


def normalize_query(query: str) -> str:
    """
    Normaliza una query para el cache (lowercase, trim, remove extra spaces)
    """
    # Convertir a minúsculas
    normalized = query.lower().strip()
    # Remover espacios múltiples
    normalized = ' '.join(normalized.split())
    # Remover signos de puntuación al final (pero no en medio)
    normalized = normalized.rstrip('?!.,;:')
    return normalized


def get_query_hash(query: str) -> str:
    """
    Genera un hash SHA256 de la query normalizada para usar como key en DynamoDB
    """
    normalized = normalize_query(query)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def get_from_cache(query: str) -> Optional[Dict[str, Any]]:
    """
    Busca una query en el cache de DynamoDB
    Returns: cached response dict or None if not found/expired
    """
    if not ENABLE_CACHE or not dynamodb_client or not CACHE_TABLE_NAME:
        return None

    try:
        query_hash = get_query_hash(query)
        logger.info(f"Buscando en cache: {query_hash[:16]}...")

        response = dynamodb_client.get_item(
            TableName=CACHE_TABLE_NAME,
            Key={'query_hash': {'S': query_hash}}
        )

        if 'Item' not in response:
            logger.info("Cache miss - query no encontrada")
            return None

        item = response['Item']

        # Verificar TTL manualmente (DynamoDB TTL puede tardar en limpiar)
        import time
        current_time = int(time.time())
        ttl = int(item.get('ttl', {}).get('N', '0'))

        if ttl > 0 and current_time > ttl:
            logger.info("Cache miss - entrada expirada")
            return None

        # Incrementar hit_count
        try:
            dynamodb_client.update_item(
                TableName=CACHE_TABLE_NAME,
                Key={'query_hash': {'S': query_hash}},
                UpdateExpression='SET hit_count = hit_count + :inc, last_accessed = :time',
                ExpressionAttributeValues={
                    ':inc': {'N': '1'},
                    ':time': {'N': str(current_time)}
                }
            )
        except Exception as e:
            logger.warning(f"Error actualizando hit_count: {e}")

        # Parsear respuesta del cache
        cached_data = {
            'answer': item.get('answer', {}).get('S', ''),
            'sources': [s.get('S', '') for s in item.get('sources', {}).get('L', [])],
            'num_chunks_used': int(item.get('num_chunks_used', {}).get('N', '0')),
            'user_intent': item.get('user_intent', {}).get('S', 'question'),
            'from_cache': True,
            'cache_hit_count': int(item.get('hit_count', {}).get('N', '0')) + 1
        }

        logger.info(f"Cache HIT! Query encontrada (hits: {cached_data['cache_hit_count']})")
        return cached_data

    except Exception as e:
        logger.error(f"Error al buscar en cache: {e}")
        return None


def save_to_cache(query: str, answer: str, sources: List[str], num_chunks: int, user_intent: str) -> None:
    """
    Guarda una respuesta en el cache de DynamoDB
    """
    if not ENABLE_CACHE or not dynamodb_client or not CACHE_TABLE_NAME:
        return

    try:
        import time
        query_hash = get_query_hash(query)
        current_time = int(time.time())
        ttl = current_time + CACHE_TTL_SECONDS

        # Preparar item para DynamoDB
        item = {
            'query_hash': {'S': query_hash},
            'query_text': {'S': query[:500]},  # Guardar primeros 500 chars para debugging
            'answer': {'S': answer},
            'sources': {'L': [{'S': s} for s in sources]},
            'num_chunks_used': {'N': str(num_chunks)},
            'user_intent': {'S': user_intent},
            'created_at': {'N': str(current_time)},
            'last_accessed': {'N': str(current_time)},
            'hit_count': {'N': '0'},
            'ttl': {'N': str(ttl)}
        }

        dynamodb_client.put_item(
            TableName=CACHE_TABLE_NAME,
            Item=item
        )

        logger.info(f"Respuesta guardada en cache (hash: {query_hash[:16]}..., TTL: {CACHE_TTL_SECONDS}s)")

    except Exception as e:
        logger.error(f"Error al guardar en cache: {e}")


def apply_guardrails(text: str) -> tuple[bool, Optional[str]]:
    """
    Aplica guardrails al contenido del usuario
    Returns: (is_safe, rejection_message)
    """
    # Convertir a minúsculas para búsqueda
    text_lower = text.lower()

    # Lista de palabras/patrones prohibidos (guardrails básicos)
    blocked_patterns = [
        # Intentos de jailbreak
        r'ignore\s+previous\s+instructions',
        r'ignore\s+all\s+previous',
        r'disregard\s+all\s+previous',
        r'forget\s+everything',
        r'new\s+instructions',
        r'system\s+prompt',

        # Solicitudes inapropiadas
        r'how\s+to\s+(hack|exploit|crack)',
        r'(illegal|unlawful)\s+activities',
        r'how\s+to\s+make\s+(bomb|weapon|drug)',

        # Spam/abuso
        r'(.)\1{20,}',  # Repetición excesiva de caracteres
    ]

    for pattern in blocked_patterns:
        if re.search(pattern, text_lower):
            logger.warning(f"Guardrail activado: patrón prohibido detectado")
            return False, "Lo siento, no puedo procesar ese tipo de solicitud. Por favor, haz una pregunta relacionada con los documentos."

    # Verificar longitud
    if len(text) > MAX_QUERY_LENGTH:
        return False, f"Tu pregunta es demasiado larga. Por favor, límitala a {MAX_QUERY_LENGTH} caracteres."

    # Verificar que no esté vacía
    if not text.strip():
        return False, "Por favor, escribe una pregunta válida."

    return True, None


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
    Genera embedding usando Bedrock Titan con cache
    Returns: numpy array
    """
    try:
        # Generar hash del texto para cache
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()

        # Verificar cache
        if text_hash in EMBEDDINGS_CACHE:
            logger.debug(f"Cache hit para query hash: {text_hash[:8]}...")
            return EMBEDDINGS_CACHE[text_hash]

        # Generar embedding con Bedrock
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            body=json.dumps({"inputText": text})
        )

        result = json.loads(response['body'].read())
        embedding = np.array([result['embedding']], dtype=np.float32)

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


def format_conversation_history(history: List[Dict[str, str]]) -> str:
    """
    Formatea el historial de conversación para el prompt
    Limita a los últimos MAX_CONVERSATION_HISTORY mensajes
    """
    if not history:
        return ""

    # Tomar solo los últimos mensajes
    recent_history = history[-MAX_CONVERSATION_HISTORY:]

    formatted = "Historial de la conversación:\n"
    for msg in recent_history:
        role = "Usuario" if msg['role'] == 'user' else "Asistente"
        formatted += f"{role}: {msg['content']}\n"

    return formatted + "\n"


def generate_rag_response(
    query: str,
    context_chunks: List[Dict[str, Any]],
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_intent: str = 'question'
) -> Dict[str, Any]:
    """
    Genera respuesta usando RAG con Bedrock Claude
    Incluye soporte para historial conversacional, detección de intent y follow-up questions
    """
    logger.info(f"Generando respuesta con RAG... (Intent: {user_intent})")

    # Construir contexto de documentos con extractos
    context_with_metadata = []
    for chunk in context_chunks:
        context_with_metadata.append({
            'source': chunk['metadata']['source'],
            'chunk_id': chunk['metadata']['chunk_id'],
            'text': chunk['text'],
            'distance': chunk['distance']
        })

    context = "\n\n".join([
        f"[Fuente: {chunk['metadata']['source']}, Chunk {chunk['metadata']['chunk_id']}]\n{chunk['text']}"
        for chunk in context_chunks
    ])

    # Construir historial conversacional si existe
    history_context = format_conversation_history(conversation_history) if conversation_history else ""

    # Intent-specific instructions
    intent_instructions = {
        'summarize': "El usuario quiere un RESUMEN. Sé conciso, organizado y destaca los puntos principales. Usa bullets si es apropiado.",
        'explain': "El usuario quiere una EXPLICACIÓN detallada. Sé claro, didáctico y profundiza en el tema.",
        'list': "El usuario quiere una LISTA. Enumera los items claramente, preferiblemente con bullets o números.",
        'compare': "El usuario quiere COMPARAR. Destaca similitudes y diferencias de forma clara y estructurada.",
        'search': "El usuario está BUSCANDO información específica. Sé directo y cita exactamente dónde está la información.",
        'question': "El usuario tiene una pregunta general. Responde de forma natural y completa."
    }

    # System prompt con instrucciones específicas del usuario
    system_prompt = """Sos un asistente cálido, profesional y moderno. Tu tarea es leer los documentos disponibles y responder únicamente en base a su contenido. No inventes información ni respondas sobre temas que no aparezcan en los documentos. Tu objetivo es ayudar al usuario de manera natural, útil y breve.

Identificá la intención del usuario y actuá así:

1. greeting - Saludá de forma cercana y positiva.
   Ejemplo: "¡Hola! 👋 ¿En qué puedo ayudarte hoy?"

2. document_query - Cuando el usuario pregunte por información contenida en los documentos (conceptos, datos, procesos, definiciones, pasos), respondé de forma clara y directa, siempre basándote únicamente en lo leído.
   Ejemplo: "Según el documento, el proceso comienza con una validación inicial de datos…"

3. analysis_request - Si el usuario pide un análisis, resumen o explicación, ofrecé una respuesta sencilla y bien organizada, sin agregar contenido que no exista en los documentos.
   Ejemplo: "Te resumo lo que indica el archivo: …"

4. action_intent - Si el usuario quiere aplicar la información, tomar una decisión o avanzar con un paso mencionado en los documentos, orientalo y guiá la acción según lo que el material permita.
   Ejemplo: "El documento indica que el siguiente paso sería completar el formulario…"

5. limitations - Si el usuario pregunta por algo que no está en los documentos, o que excede su alcance, respondé con claridad y amabilidad.
   Ejemplo: "Perdón 🙏, esa información no aparece en los documentos disponibles."

6. complaint - Si el usuario expresa confusión o problema con la información, respondé con empatía y ofrecé aclararla.
   Ejemplo: "Lamento la confusión 😔. Si querés, reviso el documento y te explico nuevamente."

7. other - Si el usuario pide temas totalmente ajenos (política, chistes, consejos personales, opiniones, etc.), mantené el límite de forma amable.
   Ejemplo: "Lo siento 🙏, solo puedo ayudarte con lo que está en los documentos."

⚠️ REGLAS IMPORTANTES:
• Nunca digas que sos un asistente virtual ni un modelo de lenguaje
• No inventes información. Si un dato no está en los documentos, decí que no aparece
• Mantené siempre un tono cálido, amable, profesional y conversacional
• Respuestas de máximo 3 frases
• Respondé siempre en español
• Tu conocimiento se limita exclusivamente a los documentos cargados"""

    # Construir el prompt completo
    user_prompt = f"""{history_context}
Contexto de los documentos:
{context}

Pregunta del usuario: {query}

Responde de forma natural y conversacional basándote SOLO en el contexto."""

    # Llamar a Bedrock Claude con messages API
    try:
        messages = []

        # Agregar historial si existe (excluyendo el mensaje actual)
        if conversation_history:
            # Convertir historial al formato de Claude
            for msg in conversation_history[-MAX_CONVERSATION_HISTORY:]:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })

        # Agregar el mensaje actual con el contexto
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS_PER_RESPONSE,
            "system": system_prompt,
            "messages": messages,
            "temperature": 0.3
        }

        response = bedrock_client.invoke_model(
            modelId=BEDROCK_LLM_MODEL_ID,
            body=json.dumps(request_body)
        )

        result = json.loads(response['body'].read())
        answer = result['content'][0]['text']

        # Limpiar frases formales
        answer = clean_formal_phrases(answer)

        # Calcular uso de tokens
        input_tokens = result.get('usage', {}).get('input_tokens', 0)
        output_tokens = result.get('usage', {}).get('output_tokens', 0)

        # Extraer follow-up questions de la respuesta
        follow_up_questions = []
        follow_up_pattern = r'Preguntas relacionadas.*?:\s*\n\s*(?:1\.?\s*(.+?)\n\s*2\.?\s*(.+?)\n\s*3\.?\s*(.+?)(?:\n|$))'
        match = re.search(follow_up_pattern, answer, re.DOTALL | re.IGNORECASE)
        if match:
            follow_up_questions = [q.strip() for q in match.groups() if q]

        # Preparar extractos relevantes
        excerpts = []
        for chunk in context_chunks[:3]:  # Top 3 chunks más relevantes
            excerpts.append({
                'source': chunk['metadata']['source'],
                'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                'relevance': round(1 / (1 + chunk['distance']), 3)  # Convert distance to relevance score
            })

        logger.info(f"Respuesta generada: {len(answer)} caracteres, {input_tokens} tokens input, {output_tokens} tokens output")
        logger.info(f"Follow-up questions extraídas: {len(follow_up_questions)}")

        return {
            'answer': answer,
            'sources': list(set([chunk['metadata']['source'] for chunk in context_chunks])),
            'excerpts': excerpts,
            'follow_up_questions': follow_up_questions,
            'user_intent': user_intent,
            'num_chunks_used': len(context_chunks),
            'usage': {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens
            }
        }

    except Exception as e:
        logger.error(f"Error generando respuesta con Bedrock: {e}")
        raise


# =====================================================
# Conversational Sessions Functions
# =====================================================

def create_conversation(user_id: str = 'anonymous') -> str:
    """
    Crea una nueva conversación
    Returns: conversation_id
    """
    conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
    logger.info(f"Nueva conversación creada: {conversation_id}")
    return conversation_id


def generate_conversation_title(first_user_message: str) -> str:
    """
    Genera título de conversación basado en el primer mensaje
    """
    # Tomar primeras 50 caracteres o hasta primer signo de puntuación
    title = first_user_message[:50]

    # Buscar primer punto, pregunta o salto de línea
    for char in ['.', '?', '!', '\n']:
        if char in title:
            title = title[:title.index(char)]
            break

    return title.strip() or "Nueva conversación"


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    user_id: str = 'anonymous',
    title: str = None,
    usage: dict = None,
    sources: list = None,
    num_chunks_used: int = 0
):
    """
    Guarda un mensaje en DynamoDB
    """
    if not CONVERSATIONS_TABLE_NAME:
        logger.warning("CONVERSATIONS_TABLE_NAME no configurado - skip save")
        return

    timestamp = int(time.time() * 1000)
    message_id = f"{timestamp}#{uuid.uuid4().hex[:8]}"

    item = {
        'conversation_id': {'S': conversation_id},
        'message_id': {'S': message_id},
        'user_id': {'S': user_id},
        'role': {'S': role},
        'content': {'S': content},
        'timestamp': {'N': str(timestamp)},
        'updated_at': {'N': str(timestamp)}
    }

    # Título de la conversación
    if title:
        item['title'] = {'S': title}

    # Metadata solo para mensajes assistant
    if role == 'assistant':
        if usage:
            item['usage'] = {
                'M': {
                    'input_tokens': {'N': str(usage.get('input_tokens', 0))},
                    'output_tokens': {'N': str(usage.get('output_tokens', 0))},
                    'total_tokens': {'N': str(usage.get('total_tokens', 0))}
                }
            }
        if sources:
            item['sources'] = {'L': [{'S': s} for s in sources]}
        item['num_chunks_used'] = {'N': str(num_chunks_used)}

    try:
        dynamodb_client.put_item(
            TableName=CONVERSATIONS_TABLE_NAME,
            Item=item
        )
        logger.info(f"Mensaje guardado: {conversation_id}/{message_id}")
    except Exception as e:
        logger.error(f"Error guardando mensaje: {e}")
        # No raise - queremos que continúe aunque falle el guardado


def load_conversation(conversation_id: str, limit: int = None) -> List[Dict[str, Any]]:
    """
    Carga historial de una conversación
    Returns: Lista de mensajes [{role, content, timestamp}, ...]
    """
    if not CONVERSATIONS_TABLE_NAME:
        logger.warning("CONVERSATIONS_TABLE_NAME no configurado - no history")
        return []

    if limit is None:
        limit = MAX_HISTORY_MESSAGES

    try:
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            KeyConditionExpression='conversation_id = :conv_id',
            ExpressionAttributeValues={
                ':conv_id': {'S': conversation_id}
            },
            ScanIndexForward=False,  # Orden descendente (más recientes primero)
            Limit=limit * 2  # *2 porque cada intercambio son 2 mensajes
        )

        items = response.get('Items', [])

        # Parsear mensajes
        messages = []
        for item in reversed(items):  # Revertir para orden cronológico
            messages.append({
                'role': item.get('role', {}).get('S', ''),
                'content': item.get('content', {}).get('S', ''),
                'timestamp': int(item.get('timestamp', {}).get('N', '0'))
            })

        logger.info(f"Cargados {len(messages)} mensajes de conversación {conversation_id}")
        return messages

    except Exception as e:
        logger.error(f"Error cargando conversación: {e}")
        return []


def list_conversations(user_id: str = 'anonymous', limit: int = 50) -> List[Dict[str, Any]]:
    """
    Lista conversaciones del usuario
    Returns: Lista de conversaciones con título y última actualización
    """
    if not CONVERSATIONS_TABLE_NAME:
        logger.warning("CONVERSATIONS_TABLE_NAME no configurado")
        return []

    try:
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            IndexName='UserConversationsIndex',
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={
                ':uid': {'S': user_id}
            },
            ScanIndexForward=False,  # Más recientes primero
            Limit=limit
        )

        # Agrupar por conversation_id y tomar el mensaje más reciente de cada una
        conversations = {}
        for item in response.get('Items', []):
            conv_id = item.get('conversation_id', {}).get('S', '')
            if conv_id not in conversations:
                conversations[conv_id] = {
                    'conversation_id': conv_id,
                    'title': item.get('title', {}).get('S', 'Sin título'),
                    'updated_at': int(item.get('updated_at', {}).get('N', '0')),
                    'preview': item.get('content', {}).get('S', '')[:100]
                }

        # Convertir a lista y ordenar por updated_at
        conv_list = list(conversations.values())
        conv_list.sort(key=lambda x: x['updated_at'], reverse=True)

        logger.info(f"Listadas {len(conv_list)} conversaciones para usuario {user_id}")
        return conv_list

    except Exception as e:
        logger.error(f"Error listando conversaciones: {e}")
        return []


def delete_conversation(conversation_id: str, user_id: str = 'anonymous') -> bool:
    """
    Borra una conversación completa (todos sus mensajes)
    Returns: True si fue exitoso, False si falló
    """
    if not CONVERSATIONS_TABLE_NAME:
        logger.warning("CONVERSATIONS_TABLE_NAME no configurado")
        return False

    try:
        # Primero obtener todos los mensajes de la conversación
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            KeyConditionExpression='conversation_id = :conv_id',
            ExpressionAttributeValues={
                ':conv_id': {'S': conversation_id}
            }
        )

        # Borrar cada mensaje
        items = response.get('Items', [])
        for item in items:
            message_id = item.get('message_id', {}).get('S', '')
            if message_id:
                dynamodb_client.delete_item(
                    TableName=CONVERSATIONS_TABLE_NAME,
                    Key={
                        'conversation_id': {'S': conversation_id},
                        'message_id': {'S': message_id}
                    }
                )

        logger.info(f"Conversación {conversation_id} borrada ({len(items)} mensajes)")
        return True

    except Exception as e:
        logger.error(f"Error borrando conversación {conversation_id}: {e}")
        return False


def update_conversation_title(conversation_id: str, new_title: str, user_id: str = 'anonymous') -> bool:
    """
    Actualiza el título de una conversación
    Returns: True si fue exitoso, False si falló
    """
    if not CONVERSATIONS_TABLE_NAME:
        logger.warning("CONVERSATIONS_TABLE_NAME no configurado")
        return False

    try:
        # Obtener el primer mensaje (que tiene el título)
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            KeyConditionExpression='conversation_id = :conv_id',
            ExpressionAttributeValues={
                ':conv_id': {'S': conversation_id}
            },
            Limit=1,
            ScanIndexForward=True  # Orden ascendente para obtener el primero
        )

        items = response.get('Items', [])
        if not items:
            logger.warning(f"No se encontró conversación {conversation_id}")
            return False

        # Actualizar el título del primer mensaje
        message_id = items[0].get('message_id', {}).get('S', '')
        if message_id:
            dynamodb_client.update_item(
                TableName=CONVERSATIONS_TABLE_NAME,
                Key={
                    'conversation_id': {'S': conversation_id},
                    'message_id': {'S': message_id}
                },
                UpdateExpression='SET title = :title, updated_at = :updated',
                ExpressionAttributeValues={
                    ':title': {'S': new_title},
                    ':updated': {'N': str(int(time.time() * 1000))}
                }
            )

            logger.info(f"Título actualizado para conversación {conversation_id}: '{new_title}'")
            return True

        return False

    except Exception as e:
        logger.error(f"Error actualizando título de conversación {conversation_id}: {e}")
        return False


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de Lambda con soporte conversacional

    Evento esperado:
    {
        "query": "¿Qué dice el documento sobre...?",
        "conversation_history": [
            {"role": "user", "content": "pregunta anterior"},
            {"role": "assistant", "content": "respuesta anterior"}
        ]
    }
    """
    try:
        logger.info(f"Evento recibido: {json.dumps(event, ensure_ascii=False)[:500]}...")

        # Parsear body desde evento
        if 'body' in event:
            # Request desde Function URL (HTTP)
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Invocación directa
            body = event

        # Detectar acción (para gestión de sesiones)
        action = body.get('action', 'query')

        # ===== ACTIONS DE GESTIÓN DE SESIONES =====
        if action == 'list_conversations':
            user_id = body.get('user_id', 'anonymous')
            conversations = list_conversations(user_id)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'conversations': conversations
                }, ensure_ascii=False)
            }

        if action == 'create_conversation':
            user_id = body.get('user_id', 'anonymous')
            new_conv_id = create_conversation(user_id)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'conversation_id': new_conv_id
                }, ensure_ascii=False)
            }

        if action == 'load_conversation':
            conversation_id = body.get('conversation_id')
            if not conversation_id:
                raise ValueError("conversation_id es requerido para load_conversation")

            messages = load_conversation(conversation_id)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'messages': messages
                }, ensure_ascii=False)
            }

        if action == 'delete_conversation':
            conversation_id = body.get('conversation_id')
            user_id = body.get('user_id', 'anonymous')

            if not conversation_id:
                raise ValueError("conversation_id es requerido para delete_conversation")

            success = delete_conversation(conversation_id, user_id)
            return {
                'statusCode': 200 if success else 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': success,
                    'message': 'Conversación eliminada' if success else 'Error al eliminar conversación'
                }, ensure_ascii=False)
            }

        if action == 'update_title':
            conversation_id = body.get('conversation_id')
            new_title = body.get('new_title')
            user_id = body.get('user_id', 'anonymous')

            if not conversation_id or not new_title:
                raise ValueError("conversation_id y new_title son requeridos para update_title")

            success = update_conversation_title(conversation_id, new_title, user_id)
            return {
                'statusCode': 200 if success else 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': success,
                    'message': 'Título actualizado' if success else 'Error al actualizar título'
                }, ensure_ascii=False)
            }

        # ===== QUERY NORMAL CON SESIONES =====
        query = body.get('query')
        if not query:
            raise ValueError("Evento debe contener 'query'")

        # Obtener o crear conversation_id
        conversation_id = body.get('conversation_id')
        is_new_conversation = False
        if not conversation_id:
            conversation_id = create_conversation()
            is_new_conversation = True
            logger.info(f"Nueva conversación creada: {conversation_id}")

        # Cargar historial de la conversación desde DynamoDB
        conversation_history = load_conversation(conversation_id)
        logger.info(f"Historial cargado: {len(conversation_history)} mensajes")

        # Generar título si es nueva conversación
        conversation_title = None
        if is_new_conversation:
            conversation_title = generate_conversation_title(query)

        # Guardar mensaje del usuario
        save_message(
            conversation_id=conversation_id,
            role='user',
            content=query,
            title=conversation_title
        )

        # Aplicar guardrails
        is_safe, rejection_message = apply_guardrails(query)
        if not is_safe:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'query': query,
                    'answer': rejection_message,
                    'sources': [],
                    'guardrail_triggered': True
                }, ensure_ascii=False)
            }

        # Detectar conversación casual (saludos, despedidas, etc.)
        is_casual, casual_response = is_casual_conversation(query)
        if is_casual:
            logger.info("Conversación casual detectada - respondiendo sin buscar en documentos")
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'query': query,
                    'answer': casual_response,
                    'sources': [],
                    'num_chunks_used': 0,
                    'usage': {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0
                    },
                    'conversation_history_count': len(conversation_history),
                    'is_casual_response': True
                }, ensure_ascii=False)
            }

        # 1. Detectar si piden listar documentos
        if is_document_list_request(query):
            logger.info("Detectada solicitud de listar documentos")
            # Cargar FAISS solo para obtener metadata
            faiss_index, metadata_list = load_faiss_from_s3()
            documents = get_available_documents(metadata_list)

            if documents:
                doc_list = "\n".join([f"• {doc}" for doc in documents])
                response_text = f"Tengo {len(documents)} documento{'s' if len(documents) > 1 else ''} disponible{'s' if len(documents) > 1 else ''}:\n\n{doc_list}\n\n¿Sobre cuál quieres saber más?"
            else:
                response_text = "No tengo documentos indexados todavía. Sube algunos PDFs para empezar."

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'query': query,
                    'answer': response_text,
                    'sources': documents,
                    'num_chunks_used': 0,
                    'usage': {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0
                    },
                    'is_document_list': True
                }, ensure_ascii=False)
            }

        # 2. Detectar intención del usuario
        user_intent = detect_user_intent(query)
        logger.info(f"Intent detectado: {user_intent}")

        # 2.1. Manejar agradecimientos y saludos (sin RAG)
        if user_intent == 'thanks':
            thanks_responses = [
                "¡De nada! Si necesitas algo más, pregunta nomás.",
                "¡Un placer! Aquí estoy si necesitas más info.",
                "¡Para eso estoy! Cualquier otra duda, avisame.",
                "¡Con gusto! ¿Necesitas saber algo más?",
            ]
            import random
            answer = random.choice(thanks_responses)

            save_message(
                conversation_id=conversation_id,
                role='assistant',
                content=answer,
                title=conversation_title
            )

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'conversation_id': conversation_id,
                    'query': query,
                    'answer': answer,
                    'sources': [],
                    'user_intent': 'thanks',
                    'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
                    'cached': False
                }, ensure_ascii=False)
            }

        if user_intent == 'greeting':
            greeting_responses = [
                "¡Hola! 👋 ¿En qué puedo ayudarte hoy?",
                "¡Buenas! 😊 ¿Qué necesitás saber?",
                "¡Hola! ¿Te ayudo con algo de los documentos?",
                "¡Hey! 👋 Contame, ¿qué estás buscando?",
            ]
            import random
            answer = random.choice(greeting_responses)

            save_message(
                conversation_id=conversation_id,
                role='assistant',
                content=answer,
                title=conversation_title
            )

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'conversation_id': conversation_id,
                    'query': query,
                    'answer': answer,
                    'sources': [],
                    'user_intent': 'greeting',
                    'usage': {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0},
                    'cached': False
                }, ensure_ascii=False)
            }

        # 3. Revisar cache de DynamoDB
        cached_response = get_from_cache(query)
        if cached_response:
            # Cache HIT - retornar respuesta inmediatamente
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'query': query,
                    'answer': cached_response['answer'],
                    'sources': cached_response['sources'],
                    'num_chunks_used': cached_response['num_chunks_used'],
                    'user_intent': cached_response['user_intent'],
                    'from_cache': True,
                    'cache_hit_count': cached_response.get('cache_hit_count', 1),
                    'usage': {
                        'input_tokens': 0,
                        'output_tokens': 0,
                        'total_tokens': 0
                    },
                    'conversation_history_count': len(conversation_history)
                }, ensure_ascii=False)
            }

        # 4. Cargar FAISS index desde S3
        faiss_index, metadata_list = load_faiss_from_s3()

        # 5. Buscar chunks relevantes
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
                    'message': 'No se encontraron documentos relevantes para tu pregunta.',
                    'query': query,
                    'answer': 'No encontré información relevante en los documentos para responder tu pregunta. ¿Podrías reformularla o preguntar sobre otro tema?',
                    'sources': [],
                    'user_intent': user_intent
                }, ensure_ascii=False)
            }

        # 4. Generar respuesta con RAG, conversación e intent
        rag_result = generate_rag_response(query, context_chunks, conversation_history, user_intent)

        # Guardar respuesta del asistente en DynamoDB
        save_message(
            conversation_id=conversation_id,
            role='assistant',
            content=rag_result['answer'],
            title=conversation_title,
            usage=rag_result['usage'],
            sources=rag_result['sources'],
            num_chunks_used=rag_result['num_chunks_used']
        )

        # Resultado exitoso con mejoras
        result = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'conversation_id': conversation_id,
                'query': query,
                'answer': rag_result['answer'],
                'sources': rag_result['sources'],
                'excerpts': rag_result['excerpts'],
                'follow_up_questions': rag_result['follow_up_questions'],
                'user_intent': rag_result['user_intent'],
                'num_chunks_used': rag_result['num_chunks_used'],
                'usage': rag_result['usage'],
                'conversation_history_count': len(conversation_history),
                'from_cache': False
            }, ensure_ascii=False)
        }

        # Guardar respuesta en cache para futuras consultas
        save_to_cache(
            query=query,
            answer=rag_result['answer'],
            sources=rag_result['sources'],
            num_chunks=rag_result['num_chunks_used'],
            user_intent=rag_result['user_intent']
        )

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
                'error': 'Ocurrió un error procesando tu solicitud. Por favor intenta de nuevo.',
                'detail': str(e) if ENVIRONMENT == 'dev' else None
            }, ensure_ascii=False)
        }
