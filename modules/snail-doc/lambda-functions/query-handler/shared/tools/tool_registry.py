"""
Tool Registry
Registro de herramientas disponibles para el agente
"""

from typing import Any, Dict, List, Optional, Type
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Clase abstracta base para todas las herramientas.

    Las herramientas permiten al agente realizar acciones específicas,
    como buscar en documentos, leer Google Sheets, etc.
    """

    def __init__(self, name: str, description: str):
        """
        Inicializa la herramienta.

        Args:
            name: Nombre de la herramienta
            description: Descripción de qué hace la herramienta
        """
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta la herramienta.

        Args:
            **kwargs: Parámetros específicos de la herramienta

        Returns:
            Resultado de la ejecución
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Obtiene el schema de la herramienta (parámetros esperados).

        Returns:
            Schema en formato JSON Schema
        """
        pass


class ToolRegistry:
    """
    Registro centralizado de herramientas disponibles.
    """

    def __init__(self):
        """Inicializa el registro de herramientas."""
        self._tools: Dict[str, BaseTool] = {}
        logger.info("Tool Registry inicializado")

    def register(self, tool: BaseTool) -> None:
        """
        Registra una herramienta.

        Args:
            tool: Instancia de la herramienta a registrar
        """
        if tool.name in self._tools:
            logger.warning(
                f"Herramienta '{tool.name}' ya está registrada. Sobrescribiendo..."
            )

        self._tools[tool.name] = tool
        logger.info(f"Herramienta registrada: {tool.name}")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """
        Obtiene una herramienta por nombre.

        Args:
            name: Nombre de la herramienta

        Returns:
            Instancia de la herramienta o None si no existe
        """
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """
        Lista todos los nombres de herramientas registradas.

        Returns:
            Lista de nombres de herramientas
        """
        return list(self._tools.keys())

    def get_available_tools_schema(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene el schema de todas las herramientas disponibles.

        Returns:
            Diccionario con schemas de todas las herramientas
        """
        return {name: tool.get_schema() for name, tool in self._tools.items()}

    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta una herramienta por nombre.

        Args:
            name: Nombre de la herramienta
            **kwargs: Parámetros para la herramienta

        Returns:
            Resultado de la ejecución

        Raises:
            ValueError: Si la herramienta no existe
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Herramienta '{name}' no encontrada")

        logger.info(f"Ejecutando herramienta: {name}")
        return tool.execute(**kwargs)


# Instancia global del registro
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """
    Obtiene la instancia global del registro de herramientas (singleton).

    Returns:
        Instancia de ToolRegistry
    """
    global _tool_registry

    if _tool_registry is None:
        _tool_registry = ToolRegistry()

    return _tool_registry
