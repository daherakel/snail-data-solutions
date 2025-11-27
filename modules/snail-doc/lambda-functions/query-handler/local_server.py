"""
Local HTTP Server para emular Lambda Function URL
Permite testear el frontend conectado al handler local
"""

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Agregar paths para imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))

# Configurar variables de entorno
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

# Importar handler
from handler import lambda_handler


class LambdaLocalHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP que emula Lambda Function URL.
    """

    def do_OPTIONS(self):
        """Maneja preflight CORS"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def do_POST(self):
        """Maneja requests POST"""
        try:
            # Leer body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")

            print(f"\n{'='*80}")
            print(f"INCOMING REQUEST")
            print(f"{'='*80}")
            print(f"Body: {body}")
            print(f"{'='*80}\n")

            # Construir evento Lambda
            event = {
                "body": body,
                "headers": dict(self.headers),
                "requestContext": {"http": {"method": "POST", "path": self.path}},
            }

            # Ejecutar handler
            response = lambda_handler(event, None)

            # Extraer status y body
            status_code = response.get("statusCode", 200)
            response_body = response.get("body", "{}")
            response_headers = response.get("headers", {})

            # Enviar respuesta
            self.send_response(status_code)
            self.send_cors_headers()

            # Headers adicionales del handler
            for key, value in response_headers.items():
                if key.lower() != "access-control-allow-origin":  # Ya lo mandamos
                    self.send_header(key, value)

            self.end_headers()
            self.wfile.write(response_body.encode("utf-8"))

            print(f"\n{'='*80}")
            print(f"RESPONSE SENT")
            print(f"{'='*80}")
            print(f"Status: {status_code}")
            print(f"Body: {response_body[:200]}...")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback

            traceback.print_exc()

            # Enviar error
            self.send_response(500)
            self.send_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            error_response = json.dumps(
                {"error": "Internal server error", "detail": str(e)}
            )
            self.wfile.write(error_response.encode("utf-8"))

    def send_cors_headers(self):
        """Envía headers CORS para permitir requests desde el frontend"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Type", "application/json")

    def log_message(self, format, *args):
        """Override para logging más limpio"""
        pass  # Silenciar logs automáticos


def run_server(port=8000):
    """
    Ejecuta el servidor local.

    Args:
        port: Puerto donde escuchar (default: 8000)
    """
    server_address = ("", port)
    httpd = HTTPServer(server_address, LambdaLocalHandler)

    print(f"\n{'='*80}")
    print(f"🚀 LOCAL LAMBDA SERVER RUNNING")
    print(f"{'='*80}")
    print(f"Listening on: http://localhost:{port}")
    print(f"\nPara conectar el frontend, actualiza .env.local:")
    print(f"  LAMBDA_QUERY_URL=http://localhost:{port}")
    print(f"\nPresiona Ctrl+C para detener")
    print(f"{'='*80}\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n\n{'='*80}")
        print(f"🛑 SERVER STOPPED")
        print(f"{'='*80}\n")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Local Lambda server")
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )

    args = parser.parse_args()

    run_server(args.port)
