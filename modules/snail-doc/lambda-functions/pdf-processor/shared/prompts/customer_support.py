"""
Customer Support Prompts
Prompts específicos para el caso de uso de atención al cliente
(Plantilla para futuro uso)
"""

from typing import Any, Dict, List, Optional

from .base_prompts import BasePrompts


class CustomerSupportPrompts(BasePrompts):
    """
    Prompts específicos para atención al cliente.
    Extiende BasePrompts con funcionalidades específicas de soporte.

    NOTA: Este es un template para futuro uso.
    """

    def __init__(
        self,
        personality: str = "warm",
        language: str = "es",
        custom_instructions: str = "",
    ):
        """Inicializa prompts para atención al cliente."""
        super().__init__(personality, language, custom_instructions)

    def get_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema para atención al cliente.

        Returns:
            String con el prompt del sistema específico para soporte.
        """
        base_prompt = super().get_system_prompt()

        # Agregar instrucciones específicas de atención al cliente
        support_specific = """

🎧 ESPECÍFICO PARA ATENCIÓN AL CLIENTE:
• Debes ser empático y comprensivo con las consultas de los clientes
• Proporciona información clara y precisa sobre productos/servicios
• Si no puedes resolver un problema, orienta sobre cómo obtener ayuda adicional
• Mantén un tono profesional pero cercano
• Prioriza la satisfacción del cliente
"""

        return base_prompt + support_specific

    def get_escalation_message(self) -> str:
        """
        Obtiene mensaje cuando se necesita escalar a un humano.

        Returns:
            String con mensaje de escalación.
        """
        if self.personality == "warm":
            return "Entiendo tu consulta. Para poder ayudarte mejor, voy a conectarte con un agente humano que podrá asistirte de manera más detallada."
        else:
            return "Su consulta requiere atención de un agente humano. Será conectado en breve."

    def format_user_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        Formatea el prompt del usuario con contexto para atención al cliente.

        Args:
            query: Pregunta del usuario/cliente
            context_chunks: Chunks de contexto (puede incluir FAQs, políticas, etc.)
            conversation_history: Historial de conversación

        Returns:
            String con el prompt formateado.
        """
        # Construir contexto
        context = "\n\n".join(
            [
                f"[Fuente: {chunk['metadata']['source']}]\n{chunk['text']}"
                for chunk in context_chunks
            ]
        )

        # Construir historial
        history_context = ""
        if conversation_history:
            history_context = "Historial de la conversación:\n"
            for msg in conversation_history[-20:]:
                role = "Cliente" if msg["role"] == "user" else "Asistente"
                history_context += f"{role}: {msg['content']}\n"
            history_context += "\n"

        # Construir el prompt
        user_prompt = f"""{history_context}
Información disponible:
{context}

Consulta del cliente: {query}

Responde de forma empática y útil basándote en la información disponible."""

        return user_prompt
