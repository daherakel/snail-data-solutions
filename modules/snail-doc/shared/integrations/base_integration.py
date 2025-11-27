"""
Base Integration
Clase abstracta base para todas las integraciones
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseIntegration(ABC):
    """
    Clase abstracta base para todas las integraciones.

    Todas las integraciones (Slack, Teams, WhatsApp, etc.) deben extender esta clase.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la integración con configuración.

        Args:
            config: Diccionario con configuración de la integración
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.enabled = config.get("enabled", True)

        logger.info(f"Inicializando integración: {self.name}")

    @abstractmethod
    def verify_request(self, event: Dict[str, Any]) -> bool:
        """
        Verifica que el request venga de la plataforma (autenticación/autorización).

        Args:
            event: Evento recibido de la plataforma

        Returns:
            True si el request es válido, False en caso contrario
        """
        pass

    @abstractmethod
    def parse_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parsea el evento de la plataforma a formato estándar.

        Args:
            event: Evento crudo de la plataforma

        Returns:
            Evento parseado con formato estándar, o None si no es procesable
        """
        pass

    @abstractmethod
    def send_message(
        self, recipient: str, text: str, thread_id: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Envía un mensaje a través de la plataforma.

        Args:
            recipient: ID del destinatario (canal, chat, etc.)
            text: Texto del mensaje
            thread_id: ID del thread (opcional)
            **kwargs: Argumentos adicionales específicos de la plataforma

        Returns:
            Respuesta de la API de la plataforma
        """
        pass

    @abstractmethod
    def format_response(self, answer: str, sources: Optional[List[str]] = None) -> str:
        """
        Formatea la respuesta del agente para la plataforma específica.

        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes (opcional)

        Returns:
            Respuesta formateada para la plataforma
        """
        pass

    def handle_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja un evento de la plataforma (método principal).

        Args:
            event: Evento crudo de la plataforma

        Returns:
            Respuesta HTTP apropiada
        """
        # Verificar request
        if not self.verify_request(event):
            logger.warning(f"Request inválido rechazado para {self.name}")
            return {
                "statusCode": 403,
                "headers": {"Content-Type": "application/json"},
                "body": '{"error": "Invalid request"}',
            }

        # Parsear evento
        parsed_event = self.parse_event(event)
        if not parsed_event:
            logger.debug(f"Evento no procesable ignorado para {self.name}")
            return {"statusCode": 200, "body": '{"ok": true}'}

        # Procesar evento
        try:
            result = self.process_message(parsed_event)
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": result if isinstance(result, str) else json.dumps(result),
            }
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}", exc_info=True)
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": '{"error": "Internal server error"}',
            }

    def process_message(self, parsed_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa un mensaje parseado (llama al query handler).

        Args:
            parsed_event: Evento parseado con formato estándar

        Returns:
            Resultado del procesamiento
        """
        # Esta implementación debe ser extendida por cada integración
        # para llamar al query handler apropiadamente
        raise NotImplementedError("Subclass must implement process_message")

    def get_conversation_id(self, channel: str, user: str) -> str:
        """
        Genera un ID de conversación único para la plataforma.

        Args:
            channel: ID del canal/chat
            user: ID del usuario

        Returns:
            ID de conversación único
        """
        return f"{self.name}_{channel}"
