"""
Document Assistant Prompts
Prompts específicos para el caso de uso de asistente de documentos
"""

from typing import Dict, Any, Optional, List
from .base_prompts import BasePrompts


class DocumentAssistantPrompts(BasePrompts):
    """
    Prompts específicos para el asistente de documentos.
    Extiende BasePrompts con funcionalidades específicas de documentos.
    """

    def __init__(
        self,
        personality: str = "warm",
        language: str = "es",
        custom_instructions: str = "",
    ):
        """Inicializa prompts para asistente de documentos."""
        super().__init__(personality, language, custom_instructions)

    def get_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema para asistente de documentos.

        Returns:
            String con el prompt del sistema específico para documentos.
        """
        base_prompt = super().get_system_prompt()

        # Agregar instrucciones específicas de documentos
        document_specific = """

📄 ESPECÍFICO PARA DOCUMENTOS:
• Puedes ayudar a buscar información específica en los documentos
• Puedes resumir secciones de documentos
• Puedes explicar conceptos que aparezcan en los documentos
• Puedes listar los documentos disponibles si el usuario pregunta
• Si el usuario pregunta sobre un documento específico, filtra la búsqueda a ese documento
"""

        return base_prompt + document_specific

    def format_user_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Formatea el prompt del usuario con contexto de documentos.

        Args:
            query: Pregunta del usuario
            context_chunks: Chunks de contexto encontrados en FAISS
            conversation_history: Historial de conversación (opcional)

        Returns:
            String con el prompt formateado.
        """
        # Construir contexto de documentos
        context = "\n\n".join(
            [
                f"[Fuente: {chunk['metadata']['source']}, Chunk {chunk['metadata']['chunk_id']}]\n{chunk['text']}"
                for chunk in context_chunks
            ]
        )

        # Construir historial conversacional si existe
        history_context = ""
        if conversation_history:
            history_context = "Historial de la conversación:\n"
            for msg in conversation_history[-30:]:  # Últimos 30 mensajes
                role = "Usuario" if msg["role"] == "user" else "Asistente"
                history_context += f"{role}: {msg['content']}\n"
            history_context += "\n"

        # Construir el prompt completo
        user_prompt = f"""{history_context}
Contexto de los documentos:
{context}

Pregunta del usuario: {query}

Responde de forma natural y conversacional basándote SOLO en el contexto."""

        return user_prompt

    def get_no_documents_message(self) -> str:
        """
        Obtiene mensaje cuando no hay documentos disponibles.

        Returns:
            String con mensaje apropiado.
        """
        if self.personality == "warm":
            return (
                "No tengo documentos indexados todavía. Sube algunos PDFs para empezar."
            )
        elif self.personality == "professional":
            return "No hay documentos disponibles actualmente. Por favor, cargue documentos para continuar."
        else:
            return (
                "No tengo documentos indexados todavía. Sube algunos PDFs para empezar."
            )

    def get_document_list_message(self, documents: List[str]) -> str:
        """
        Obtiene mensaje con lista de documentos disponibles.

        Args:
            documents: Lista de nombres de documentos

        Returns:
            String con mensaje formateado.
        """
        doc_count = len(documents)
        doc_list = "\n".join([f"• {doc}" for doc in documents])

        if self.personality == "warm":
            return f"Tengo {doc_count} documento{'s' if doc_count > 1 else ''} disponible{'s' if doc_count > 1 else ''}:\n\n{doc_list}\n\n¿Sobre cuál quieres saber más?"
        elif self.personality == "professional":
            return f"Documentos disponibles ({doc_count}):\n\n{doc_list}\n\n¿Sobre cuál documento desea consultar?"
        else:
            return f"Tengo {doc_count} documento{'s' if doc_count > 1 else ''} disponible{'s' if doc_count > 1 else ''}:\n\n{doc_list}\n\n¿Sobre cuál quieres saber más?"

    def get_no_context_found_message(self) -> str:
        """
        Obtiene mensaje cuando no se encuentra contexto relevante.

        Returns:
            String con mensaje apropiado.
        """
        if self.personality == "warm":
            return "No encontré información relevante en los documentos para responder tu pregunta. ¿Podrías reformularla o preguntar sobre otro tema?"
        elif self.personality == "professional":
            return "No se encontró información relevante en los documentos disponibles. Por favor, reformule su pregunta o consulte sobre otro tema."
        else:
            return "No encontré información relevante en los documentos para responder tu pregunta. ¿Podrías reformularla o preguntar sobre otro tema?"
