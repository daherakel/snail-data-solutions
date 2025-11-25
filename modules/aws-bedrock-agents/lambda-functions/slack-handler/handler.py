"""
Lambda Function: Slack Handler
Recibe eventos de Slack y procesa consultas usando el query-handler Lambda
"""

import json
import os
import hmac
import hashlib
import time
from typing import Dict, Any

import boto3
import urllib3

# Configuración
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_SIGNING_SECRET = os.environ['SLACK_SIGNING_SECRET']
QUERY_HANDLER_FUNCTION = os.environ.get('QUERY_HANDLER_FUNCTION', 'snail-bedrock-dev-query-handler')
AWS_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

# Clientes
lambda_client = boto3.client('lambda', region_name=AWS_REGION)
http = urllib3.PoolManager()

# No usar cache global - usar el timestamp del mensaje para deduplicar


def verify_slack_signature(event: Dict[str, Any]) -> bool:
    """
    Verifica que el request venga de Slack usando la firma
    """
    # Obtener headers
    headers = event.get('headers', {})
    slack_signature = headers.get('x-slack-signature', headers.get('X-Slack-Signature', ''))
    slack_timestamp = headers.get('x-slack-request-timestamp', headers.get('X-Slack-Request-Timestamp', ''))

    # Verificar timestamp (protección contra replay attacks)
    if abs(time.time() - int(slack_timestamp)) > 60 * 5:
        print("Request timestamp too old")
        return False

    # Construir signature base string
    body = event.get('body', '')
    sig_basestring = f"v0:{slack_timestamp}:{body}"

    # Calcular expected signature
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    # Comparar
    return hmac.compare_digest(my_signature, slack_signature)


def send_slack_message(channel: str, text: str, thread_ts: str = None) -> Dict[str, Any]:
    """
    Envía un mensaje a Slack usando la API
    """
    url = 'https://slack.com/api/chat.postMessage'

    payload = {
        'channel': channel,
        'text': text,
        'unfurl_links': False,
        'unfurl_media': False
    }

    if thread_ts:
        payload['thread_ts'] = thread_ts

    headers = {
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = http.request(
        'POST',
        url,
        body=json.dumps(payload).encode('utf-8'),
        headers=headers
    )

    return json.loads(response.data.decode('utf-8'))


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


def process_query(query: str, conversation_history: list = None) -> Dict[str, Any]:
    """
    Llama al Lambda query-handler para procesar la consulta
    """
    payload = {
        'query': query,
        'conversation_history': conversation_history or []
    }

    response = lambda_client.invoke(
        FunctionName=QUERY_HANDLER_FUNCTION,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    result = json.loads(response['Payload'].read())

    # Parsear el body si es un response de Function URL
    if 'body' in result:
        body = json.loads(result['body']) if isinstance(result['body'], str) else result['body']
        return body

    return result


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal que procesa eventos de Slack
    """
    print(f"Evento recibido: {json.dumps(event)[:500]}")

    # Verificar firma de Slack (comentado para desarrollo, descomentar en producción)
    # if not verify_slack_signature(event):
    #     return {
    #         'statusCode': 403,
    #         'body': json.dumps({'error': 'Invalid signature'})
    #     }

    # Parsear body
    body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})

    # 1. Manejar URL Verification Challenge (cuando configuras el endpoint)
    if body.get('type') == 'url_verification':
        challenge = body.get('challenge')
        print(f"URL Verification - Challenge: {challenge}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/plain'},
            'body': challenge  # Slack espera solo el valor del challenge, no JSON
        }

    # 2. Manejar eventos
    if body.get('type') == 'event_callback':
        event_data = body.get('event', {})
        event_type = event_data.get('type')

        # Ignorar mensajes del bot (para evitar loops)
        if event_data.get('bot_id') or event_data.get('subtype') == 'bot_message':
            return {'statusCode': 200, 'body': json.dumps({'ok': True})}

        # Procesar solo mensajes directos o menciones
        if event_type in ['message', 'app_mention']:
            channel = event_data.get('channel')
            user = event_data.get('user')
            text = event_data.get('text', '')
            ts = event_data.get('ts', '')
            thread_ts = event_data.get('thread_ts') or ts

            # Limpiar el texto (remover menciones del bot)
            text_clean = text.split('>', 1)[-1].strip() if '>' in text else text.strip()

            if not text_clean:
                return {'statusCode': 200, 'body': json.dumps({'ok': True})}

            print(f"Mensaje: '{text_clean}' de {user} en {channel}")

            # Detectar saludos/conversación casual
            text_lower = text_clean.lower().strip()
            casual_greetings = ['hola', 'buenas', 'buenos dias', 'buenas tardes', 'hey', 'hi', 'hello', 'que tal', 'qué tal']

            if any(greeting in text_lower for greeting in casual_greetings) and len(text_clean.split()) <= 4:
                # Es un saludo simple - responder de forma casual
                casual_response = "¡Hola! 👋 ¿En qué puedo ayudarte?"
                send_slack_message(channel, casual_response, thread_ts)
                print("Saludo detectado - respuesta casual enviada")
                return {'statusCode': 200, 'body': json.dumps({'ok': True})}

            try:
                # Procesar query con el agente
                result = process_query(text_clean)

                # Formatear respuesta
                response_text = format_response_for_slack(
                    result.get('answer', 'No encontré esa información en los documentos.'),
                    result.get('sources', [])
                )

                # Enviar UNA sola respuesta
                send_slack_message(channel, response_text, thread_ts)
                print("Respuesta enviada")

            except Exception as e:
                print(f"Error: {e}")
                error_msg = "Ups, algo salió mal. Intenta preguntar de otra forma."
                send_slack_message(channel, error_msg, thread_ts)

    return {
        'statusCode': 200,
        'body': json.dumps({'ok': True})
    }
