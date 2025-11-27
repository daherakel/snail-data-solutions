"""
Intent Classifier
Usa LLM para detectar intenciones del usuario de forma robusta (sin regex hardcodeado)
"""

import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Clasificador de intenciones usando LLM.
    Mucho más robusto y escalable que regex patterns hardcodeados.
    """

    def __init__(
        self, bedrock_client, model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"
    ):
        """
        Inicializa el clasificador.

        Args:
            bedrock_client: Cliente de Bedrock
            model_id: Modelo a usar (Haiku por defecto - barato y rápido)
        """
        self.bedrock_client = bedrock_client
        self.model_id = model_id

    def classify(
        self, query: str, conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Clasifica la intención del usuario usando el LLM.

        Args:
            query: Query del usuario
            conversation_history: Historial de conversación (opcional)

        Returns:
            Dict con:
            {
                "intent": str,  # greeting, thanks, document_query, analysis_request, etc.
                "confidence": float,  # 0.0 - 1.0
                "requires_documents": bool,
                "entities": List[str],  # Entidades mencionadas (documentos, conceptos)
                "language": str  # es, en
            }
        """
        try:
            # System prompt para clasificación de intenciones
            system_prompt = """Sos un clasificador de intenciones para un asistente de documentos.

Tu tarea es analizar el mensaje del usuario y clasificarlo en UNA de estas categorías:

1. **greeting** - Saludos iniciales (hola, buenos días, qué tal, etc.)
2. **thanks** - Agradecimientos o despedidas (gracias, perfecto, ok, chau, etc.)
3. **document_list** - Pide ver lista de documentos disponibles
4. **document_query** - Pregunta específica sobre contenido de documentos
5. **analysis_request** - Pide análisis, resumen, explicación o comparación
6. **action_intent** - Quiere hacer algo con la información (aplicar, decidir, etc.)
7. **clarification** - No entiende o pide aclaración
8. **off_topic** - Temas no relacionados con documentos

Responde SOLO con un JSON válido (sin markdown, sin explicaciones):
{
    "intent": "categoria",
    "confidence": 0.95,
    "requires_documents": true/false,
    "entities": ["documento X", "concepto Y"],
    "language": "es"
}

REGLAS:
- greeting y thanks NO requieren documentos
- document_query, analysis_request, action_intent SÍ requieren documentos
- Extrae nombres de documentos o conceptos mencionados en "entities"
- Detecta el idioma (es/en)
- Sé preciso en la confianza (0.0 - 1.0)"""

            # Construir contexto si hay historial
            context = ""
            if conversation_history and len(conversation_history) > 0:
                recent = conversation_history[-3:]  # Últimos 3 mensajes
                context = "Contexto de conversación reciente:\n"
                for msg in recent:
                    role = "Usuario" if msg["role"] == "user" else "Asistente"
                    context += f"{role}: {msg['content']}\n"
                context += "\n"

            # Prompt del usuario
            user_prompt = f"""{context}Mensaje actual del usuario:
"{query}"

Clasifica este mensaje:"""

            # Llamar al LLM (Haiku - rápido y barato)
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 200,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_prompt}],
                "temperature": 0.3,  # Baja temperatura para clasificación consistente
            }

            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            result = json.loads(response["body"].read())
            answer = result["content"][0]["text"].strip()

            # Parsear JSON de respuesta
            # Limpiar markdown si viene con ```json
            if answer.startswith("```"):
                answer = answer.split("```")[1]
                if answer.startswith("json"):
                    answer = answer[4:]
                answer = answer.strip()

            classification = json.loads(answer)

            # Validar estructura
            required_fields = ["intent", "confidence", "requires_documents"]
            for field in required_fields:
                if field not in classification:
                    raise ValueError(f"Missing field: {field}")

            # Defaults para campos opcionales
            classification.setdefault("entities", [])
            classification.setdefault("language", "es")

            logger.info(
                f"Intent classified: {classification['intent']} (confidence: {classification['confidence']:.2f})"
            )

            return classification

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LLM response as JSON: {e}, response: {answer}")
            # Fallback a intent genérico
            return self._fallback_classification(query)

        except Exception as e:
            logger.error(f"Error classifying intent: {e}")
            return self._fallback_classification(query)

    def _fallback_classification(self, query: str) -> Dict[str, Any]:
        """
        Clasificación fallback simple si el LLM falla.
        Usa heurísticas muy básicas solo como último recurso.
        """
        query_lower = query.lower().strip()

        # Heurísticas mínimas solo para casos extremos
        if len(query_lower) < 15 and any(
            word in query_lower for word in ["hola", "hi", "hey", "buenas"]
        ):
            return {
                "intent": "greeting",
                "confidence": 0.7,
                "requires_documents": False,
                "entities": [],
                "language": "es",
            }

        if len(query_lower) < 20 and any(
            word in query_lower for word in ["gracias", "thanks", "perfecto", "ok"]
        ):
            return {
                "intent": "thanks",
                "confidence": 0.7,
                "requires_documents": False,
                "entities": [],
                "language": "es",
            }

        # Default: asumir que es una consulta de documento
        return {
            "intent": "document_query",
            "confidence": 0.5,
            "requires_documents": True,
            "entities": [],
            "language": "es",
        }

    def is_simple_response(self, intent: str) -> bool:
        """
        Verifica si la intención requiere solo una respuesta simple (sin RAG).

        Args:
            intent: Tipo de intención

        Returns:
            True si es respuesta simple, False si requiere búsqueda en documentos
        """
        simple_intents = ["greeting", "thanks", "off_topic"]
        return intent in simple_intents
