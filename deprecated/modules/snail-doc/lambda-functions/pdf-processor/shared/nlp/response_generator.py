"""
Response Generator
Genera respuestas usando prompts configurables y el sistema modular de prompts
"""

import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Genera respuestas según la intención del usuario.
    Usa el sistema de prompts modulares en lugar de hardcodear respuestas.
    """

    def __init__(self, prompts_system):
        """
        Inicializa el generador.

        Args:
            prompts_system: Instancia de BasePrompts (shared/prompts/base_prompts.py)
        """
        self.prompts = prompts_system

    def generate_simple_response(
        self, intent: str, query: str, entities: Optional[List[str]] = None
    ) -> str:
        """
        Genera respuesta simple para intenciones que no requieren documentos.

        Args:
            intent: Tipo de intención (greeting, thanks, off_topic)
            query: Query del usuario
            entities: Entidades extraídas (opcional)

        Returns:
            Respuesta como string
        """
        if intent == "greeting":
            # Usar sistema de prompts para respuestas de saludo
            responses = self.prompts.get_greeting_responses()
            return random.choice(responses)

        elif intent == "thanks":
            # Usar sistema de prompts para respuestas de agradecimiento
            responses = self.prompts.get_thanks_responses()
            return random.choice(responses)

        elif intent == "off_topic":
            return "Lo siento 🙏, solo puedo ayudarte con información de los documentos cargados."

        elif intent == "clarification":
            return "¿Podrías reformular tu pregunta? Quiero asegurarme de entenderte bien para darte la mejor respuesta."

        else:
            # Default
            return "¿En qué puedo ayudarte con los documentos?"

    def generate_document_list_response(self, available_documents: List[str]) -> str:
        """
        Genera respuesta listando documentos disponibles.

        Args:
            available_documents: Lista de nombres de documentos

        Returns:
            Respuesta formateada con la lista
        """
        if not available_documents:
            return (
                "No tengo documentos indexados todavía. Sube algunos PDFs para empezar."
            )

        count = len(available_documents)
        doc_list = "\n".join([f"• {doc}" for doc in available_documents])

        plural_docs = "documento" if count == 1 else "documentos"
        plural_verb = "disponible" if count == 1 else "disponibles"

        return f"Tengo {count} {plural_docs} {plural_verb}:\n\n{doc_list}\n\n¿Sobre cuál quieres saber más?"

    def build_rag_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        intent: str = "document_query",
    ) -> tuple[str, str]:
        """
        Construye prompts para RAG usando el sistema de prompts modulares.

        Args:
            query: Query del usuario
            context_chunks: Chunks de contexto de FAISS
            conversation_history: Historial de conversación (opcional)
            intent: Tipo de intención

        Returns:
            Tupla (system_prompt, user_prompt)
        """
        # Obtener system prompt del sistema modular
        system_prompt = self.prompts.get_system_prompt()

        # Agregar instrucciones específicas de intención
        intent_instructions = self.prompts.format_intent_instructions(intent)
        system_prompt += f"\n\n📌 Intención detectada: {intent}\n{intent_instructions}"

        # Construir contexto de documentos
        context = "\n\n".join(
            [
                f"[Fuente: {chunk['metadata']['source']}, Chunk {chunk['metadata']['chunk_id']}]\n{chunk['text']}"
                for chunk in context_chunks
            ]
        )

        # Construir historial conversacional si existe
        history_context = ""
        if conversation_history and len(conversation_history) > 0:
            history_context = "Historial de la conversación:\n"
            for msg in conversation_history[-10:]:  # Últimos 10 mensajes
                role = "Usuario" if msg["role"] == "user" else "Asistente"
                history_context += f"{role}: {msg['content']}\n"
            history_context += "\n"

        # Construir prompt del usuario
        user_prompt = f"""{history_context}Contexto de los documentos:
{context}

Pregunta del usuario: {query}

Responde de forma natural y conversacional basándote SOLO en el contexto."""

        return system_prompt, user_prompt

    def format_response_with_sources(
        self,
        answer: str,
        sources: List[str],
        excerpts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Formatea respuesta con fuentes y excerpts.

        Args:
            answer: Respuesta generada
            sources: Lista de fuentes
            excerpts: Excerpts relevantes (opcional)

        Returns:
            Dict con respuesta formateada
        """
        result = {"answer": answer, "sources": sources}

        if excerpts:
            result["excerpts"] = excerpts

        return result
