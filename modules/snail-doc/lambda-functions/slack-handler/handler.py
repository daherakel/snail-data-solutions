"""
Lambda Function: Slack Handler
Recibe eventos de Slack y procesa consultas usando el query-handler Lambda
Incluye soporte para conversaciones con DynamoDB y verificación de firma configurable
"""

import hashlib
import hmac
import json
import logging
import os
import time
from typing import Any, Dict, Optional

import boto3
import urllib3

# Configuración
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
PROJECT_NAME = os.environ.get("PROJECT_NAME", "bedrock-agents")
QUERY_HANDLER_FUNCTION = os.environ.get(
    "QUERY_HANDLER_FUNCTION", f"{PROJECT_NAME}-{ENVIRONMENT}-query-handler"
)
VERIFY_SLACK_SIGNATURE = (
    os.environ.get("VERIFY_SLACK_SIGNATURE", "true").lower() == "true"
)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Configuración de Slack (puede venir de variables de entorno o Secrets Manager)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")

# Configuración de conversaciones
CONVERSATIONS_TABLE_NAME = os.environ.get(
    "CONVERSATIONS_TABLE_NAME", f"{PROJECT_NAME}-{ENVIRONMENT}-conversations"
)

# Clientes AWS
lambda_client = boto3.client("lambda", region_name=AWS_REGION)
dynamodb_client = (
    boto3.client("dynamodb", region_name=AWS_REGION)
    if CONVERSATIONS_TABLE_NAME
    else None
)
secrets_client = boto3.client("secretsmanager", region_name=AWS_REGION)
http = urllib3.PoolManager()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="[%(levelname)s] %(asctime)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_slack_secrets() -> tuple[str, str]:
    """
    Obtiene los secrets de Slack desde variables de entorno o Secrets Manager.

    Returns:
        Tuple (bot_token, signing_secret)
    """
    # Si ya están en variables de entorno, usarlas
    if SLACK_BOT_TOKEN and SLACK_SIGNING_SECRET:
        return SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET

    # Intentar obtener desde Secrets Manager
    try:
        # Buscar secrets por nombre común
        bot_token_secret_arn = os.environ.get("SLACK_BOT_TOKEN_SECRET_ARN", "")
        signing_secret_arn = os.environ.get("SLACK_SIGNING_SECRET_SECRET_ARN", "")

        bot_token = SLACK_BOT_TOKEN
        signing_secret = SLACK_SIGNING_SECRET

        if bot_token_secret_arn:
            response = secrets_client.get_secret_value(SecretId=bot_token_secret_arn)
            secret_data = json.loads(response["SecretString"])
            bot_token = (
                secret_data.get("bot_token")
                or secret_data.get("SLACK_BOT_TOKEN")
                or secret_data.get("token")
            )

        if signing_secret_arn:
            response = secrets_client.get_secret_value(SecretId=signing_secret_arn)
            secret_data = json.loads(response["SecretString"])
            signing_secret = (
                secret_data.get("signing_secret")
                or secret_data.get("SLACK_SIGNING_SECRET")
                or secret_data.get("secret")
            )

        if bot_token and signing_secret:
            return bot_token, signing_secret
    except Exception as e:
        logger.warning(f"Error obteniendo secrets de Secrets Manager: {e}")

    # Fallback: intentar desde variables de entorno
    if not SLACK_BOT_TOKEN or not SLACK_SIGNING_SECRET:
        raise ValueError(
            "SLACK_BOT_TOKEN y SLACK_SIGNING_SECRET deben estar configurados"
        )

    return SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET


# Obtener secrets al inicio (cachear)
_slack_bot_token, _slack_signing_secret = None, None


def get_cached_slack_secrets() -> tuple[str, str]:
    """Obtiene secrets de Slack con cache."""
    global _slack_bot_token, _slack_signing_secret

    if not _slack_bot_token or not _slack_signing_secret:
        _slack_bot_token, _slack_signing_secret = get_slack_secrets()

    return _slack_bot_token, _slack_signing_secret


def verify_slack_signature(event: Dict[str, Any]) -> bool:
    """
    Verifica que el request venga de Slack usando la firma.

    Args:
        event: Evento de Lambda con headers y body

    Returns:
        True si la firma es válida, False en caso contrario
    """
    if not VERIFY_SLACK_SIGNATURE:
        logger.debug("Verificación de firma deshabilitada")
        return True

    try:
        _, signing_secret = get_cached_slack_secrets()

        # Obtener headers
        headers = event.get("headers", {})
        slack_signature = headers.get(
            "x-slack-signature", headers.get("X-Slack-Signature", "")
        )
        slack_timestamp = headers.get(
            "x-slack-request-timestamp", headers.get("X-Slack-Request-Timestamp", "")
        )

        if not slack_signature or not slack_timestamp:
            logger.warning("Headers de Slack faltantes")
            return False

        # Verificar timestamp (protección contra replay attacks - 5 minutos)
        try:
            timestamp_int = int(slack_timestamp)
            if abs(time.time() - timestamp_int) > 60 * 5:
                logger.warning("Request timestamp too old")
                return False
        except ValueError:
            logger.warning("Invalid timestamp format")
            return False

        # Construir signature base string
        body = event.get("body", "")
        if isinstance(body, dict):
            body = json.dumps(body)
        sig_basestring = f"v0:{slack_timestamp}:{body}"

        # Calcular expected signature
        my_signature = (
            "v0="
            + hmac.new(
                signing_secret.encode(), sig_basestring.encode(), hashlib.sha256
            ).hexdigest()
        )

        # Comparar usando timing-safe comparison
        is_valid = hmac.compare_digest(my_signature, slack_signature)

        if not is_valid:
            logger.warning("Invalid Slack signature")

        return is_valid

    except Exception as e:
        logger.error(f"Error verificando firma de Slack: {e}")
        return False


def send_slack_message(
    channel: str, text: str, thread_ts: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envía un mensaje a Slack usando la API.

    Args:
        channel: ID del canal de Slack
        text: Texto del mensaje
        thread_ts: Timestamp del thread (opcional, para responder en thread)

    Returns:
        Respuesta de la API de Slack
    """
    try:
        bot_token, _ = get_cached_slack_secrets()
        url = "https://slack.com/api/chat.postMessage"

        payload = {
            "channel": channel,
            "text": text,
            "unfurl_links": False,
            "unfurl_media": False,
        }

        if thread_ts:
            payload["thread_ts"] = thread_ts

        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json",
        }

        response = http.request(
            "POST", url, body=json.dumps(payload).encode("utf-8"), headers=headers
        )

        result = json.loads(response.data.decode("utf-8"))

        if not result.get("ok"):
            logger.error(f"Error enviando mensaje a Slack: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"Error enviando mensaje a Slack: {e}")
        raise


def format_response_for_slack(answer: str, sources: list = None) -> str:
    """
    Formatea la respuesta para Slack - conversacional y fácil de leer
    """
    # Remover las "Preguntas relacionadas" del answer si existen
    if "Preguntas relacionadas" in answer or "También podrías preguntar" in answer:
        # Cortar todo después de ese texto
        answer = answer.split("Preguntas relacionadas")[0]
        answer = answer.split("También podrías preguntar")[0]
        answer = answer.strip()

    # Limpiar formato excesivo
    message = answer.strip()

    # Agregar fuentes de forma sutil
    if sources and len(sources) > 0:
        # Solo mostrar si hay más de una fuente
        if len(sources) > 1:
            message += f"\n\n_Basado en: {', '.join(sources[:2])}_"

    return message


def get_conversation_id(channel: str, user: str) -> str:
    """
    Genera un ID de conversación único para un canal/usuario en Slack.

    Args:
        channel: ID del canal de Slack
        user: ID del usuario de Slack

    Returns:
        ID de conversación único
    """
    # Usar canal como base del conversation_id (permite threads por canal)
    return f"slack_{channel}"


def load_conversation_history(
    conversation_id: str, limit: int = 10
) -> list[Dict[str, str]]:
    """
    Carga el historial de conversación desde DynamoDB.

    Args:
        conversation_id: ID de la conversación
        limit: Número máximo de mensajes a cargar

    Returns:
        Lista de mensajes [{role, content}, ...]
    """
    if not dynamodb_client or not CONVERSATIONS_TABLE_NAME:
        logger.debug("DynamoDB no configurado - sin historial")
        return []

    try:
        response = dynamodb_client.query(
            TableName=CONVERSATIONS_TABLE_NAME,
            KeyConditionExpression="conversation_id = :conv_id",
            ExpressionAttributeValues={":conv_id": {"S": conversation_id}},
            ScanIndexForward=False,  # Más recientes primero
            Limit=limit * 2,  # *2 porque cada intercambio son 2 mensajes
        )

        items = response.get("Items", [])

        # Parsear mensajes y revertir para orden cronológico
        messages = []
        for item in reversed(items):
            messages.append(
                {
                    "role": item.get("role", {}).get("S", ""),
                    "content": item.get("content", {}).get("S", ""),
                }
            )

        logger.debug(f"Historial cargado: {len(messages)} mensajes")
        return messages

    except Exception as e:
        logger.warning(f"Error cargando historial de conversación: {e}")
        return []


def process_query(
    query: str,
    conversation_id: Optional[str] = None,
    conversation_history: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Llama al Lambda query-handler para procesar la consulta.

    Args:
        query: Pregunta del usuario
        conversation_id: ID de la conversación (opcional)
        conversation_history: Historial de conversación (opcional)

    Returns:
        Resultado del query handler
    """
    payload = {
        "query": query,
        "conversation_history": conversation_history or [],
        "action": "query",
    }

    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        response = lambda_client.invoke(
            FunctionName=QUERY_HANDLER_FUNCTION,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload),
        )

        result = json.loads(response["Payload"].read())

        # Parsear el body si es un response de Function URL
        if "body" in result:
            body = (
                json.loads(result["body"])
                if isinstance(result["body"], str)
                else result["body"]
            )
            return body

        return result

    except Exception as e:
        logger.error(f"Error invocando query handler: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal que procesa eventos de Slack.

    Maneja:
    - URL Verification Challenge
    - Event Callbacks (mensajes, menciones)
    - Verificación de firma de Slack
    - Integración con conversaciones DynamoDB
    """
    logger.info(f"Evento recibido: {json.dumps(event, default=str)[:500]}")

    # Verificar firma de Slack si está habilitado
    if VERIFY_SLACK_SIGNATURE:
        if not verify_slack_signature(event):
            logger.warning("Invalid Slack signature - rechazando request")
            return {
                "statusCode": 403,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid signature"}),
            }
    else:
        logger.debug("Verificación de firma deshabilitada")

    # Parsear body
    body = (
        json.loads(event.get("body", "{}"))
        if isinstance(event.get("body"), str)
        else event.get("body", {})
    )

    # 1. Manejar URL Verification Challenge (cuando configuras el endpoint)
    if body.get("type") == "url_verification":
        challenge = body.get("challenge")
        print(f"URL Verification - Challenge: {challenge}")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": challenge,  # Slack espera solo el valor del challenge, no JSON
        }

    # 2. Manejar eventos
    if body.get("type") == "event_callback":
        event_data = body.get("event", {})
        event_type = event_data.get("type")

        # Ignorar mensajes del bot (para evitar loops)
        if event_data.get("bot_id") or event_data.get("subtype") == "bot_message":
            return {"statusCode": 200, "body": json.dumps({"ok": True})}

        # Procesar solo mensajes directos o menciones
        if event_type in ["message", "app_mention"]:
            channel = event_data.get("channel")
            user = event_data.get("user")
            text = event_data.get("text", "")
            ts = event_data.get("ts", "")
            thread_ts = event_data.get("thread_ts") or ts

            if not channel or not user:
                logger.warning(f"Evento sin channel o user: {event_data}")
                return {"statusCode": 200, "body": json.dumps({"ok": True})}

            # Limpiar el texto (remover menciones del bot)
            text_clean = text.split(">", 1)[-1].strip() if ">" in text else text.strip()

            if not text_clean:
                logger.debug("Mensaje vacío - ignorando")
                return {"statusCode": 200, "body": json.dumps({"ok": True})}

            logger.info(f"Mensaje de {user} en {channel}: '{text_clean[:100]}'")

            # Obtener o crear conversation_id
            conversation_id = get_conversation_id(channel, user)

            # Cargar historial de conversación
            conversation_history = load_conversation_history(conversation_id)

            # Detectar saludos/conversación casual
            text_lower = text_clean.lower().strip()
            casual_greetings = [
                "hola",
                "buenas",
                "buenos dias",
                "buenas tardes",
                "hey",
                "hi",
                "hello",
                "que tal",
                "qué tal",
            ]

            if (
                any(greeting in text_lower for greeting in casual_greetings)
                and len(text_clean.split()) <= 4
            ):
                # Es un saludo simple - responder de forma casual
                casual_response = "¡Hola! 👋 ¿En qué puedo ayudarte?"
                send_slack_message(channel, casual_response, thread_ts)
                logger.info("Saludo detectado - respuesta casual enviada")
                return {"statusCode": 200, "body": json.dumps({"ok": True})}

            try:
                # Procesar query con el agente (con historial de conversación)
                result = process_query(
                    query=text_clean,
                    conversation_id=conversation_id,
                    conversation_history=conversation_history,
                )

                # Formatear respuesta
                response_text = format_response_for_slack(
                    result.get(
                        "answer", "No encontré esa información en los documentos."
                    ),
                    result.get("sources", []),
                )

                # Enviar respuesta
                send_slack_message(channel, response_text, thread_ts)
                logger.info("Respuesta enviada exitosamente")

            except Exception as e:
                logger.error(f"Error procesando query: {e}", exc_info=True)
                error_msg = "Ups, algo salió mal. Intenta preguntar de otra forma."
                try:
                    send_slack_message(channel, error_msg, thread_ts)
                except Exception as send_error:
                    logger.error(f"Error enviando mensaje de error: {send_error}")

    return {"statusCode": 200, "body": json.dumps({"ok": True})}
