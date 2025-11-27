"""
Base Use Case
Clase abstracta base para todos los casos de uso
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseUseCase(ABC):
    """
    Clase abstracta base para todos los casos de uso.

    Ejemplos de casos de uso:
    - Document Assistant: Asistente para consultar documentos
    - Customer Support: Atención al cliente
    - Google Sheets Reader: Leer y consultar Google Sheets
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa el caso de uso con configuración.

        Args:
            config: Diccionario con configuración del caso de uso
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.enabled = config.get("enabled", True)

        logger.info(f"Inicializando caso de uso: {self.name}")

    @abstractmethod
    def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Procesa una consulta del usuario.

        Args:
            query: Pregunta del usuario
            conversation_history: Historial de conversación (opcional)
            **kwargs: Argumentos adicionales específicos del caso de uso

        Returns:
            Resultado del procesamiento con answer, sources, etc.
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Obtiene el prompt del sistema para este caso de uso.

        Returns:
            String con el prompt del sistema
        """
        pass

    @abstractmethod
    def get_context(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Obtiene el contexto relevante para la consulta.

        Args:
            query: Pregunta del usuario
            **kwargs: Argumentos adicionales

        Returns:
            Lista de chunks de contexto con metadata
        """
        pass

    def is_query_relevant(self, query: str) -> bool:
        """
        Determina si una consulta es relevante para este caso de uso.

        Args:
            query: Pregunta del usuario

        Returns:
            True si la consulta es relevante, False en caso contrario
        """
        # Implementación por defecto: todas las consultas son relevantes
        # Las subclases pueden sobrescribir esto
        return True

    def format_response(
        self, answer: str, sources: Optional[List[str]] = None, **kwargs
    ) -> str:
        """
        Formatea la respuesta para el caso de uso específico.

        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes
            **kwargs: Argumentos adicionales

        Returns:
            Respuesta formateada
        """
        # Implementación por defecto: devolver respuesta tal cual
        return answer
