"""
Message Formatter
Utilidades para formatear mensajes para diferentes plataformas
"""

from typing import List, Optional


class MessageFormatter:
    """
    Clase estática con utilidades para formatear mensajes.
    """
    
    @staticmethod
    def format_for_slack(answer: str, sources: Optional[List[str]] = None) -> str:
        """
        Formatea una respuesta para Slack.
        
        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes
        
        Returns:
            Respuesta formateada para Slack
        """
        # Remover "Preguntas relacionadas" si existen
        if "Preguntas relacionadas" in answer:
            answer = answer.split("Preguntas relacionadas")[0].strip()
        if "También podrías preguntar" in answer:
            answer = answer.split("También podrías preguntar")[0].strip()
        
        message = answer.strip()
        
        # Agregar fuentes de forma sutil
        if sources and len(sources) > 1:
            message += f"\n\n_Basado en: {', '.join(sources[:2])}_"
        
        return message
    
    @staticmethod
    def format_for_teams(answer: str, sources: Optional[List[str]] = None) -> str:
        """
        Formatea una respuesta para Microsoft Teams.
        
        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes
        
        Returns:
            Respuesta formateada para Teams
        """
        # Teams usa formato similar a Slack pero con diferentes limitaciones
        message = answer.strip()
        
        if sources and len(sources) > 0:
            message += f"\n\n**Fuentes:** {', '.join(sources[:3])}"
        
        return message
    
    @staticmethod
    def format_for_whatsapp(answer: str, sources: Optional[List[str]] = None) -> str:
        """
        Formatea una respuesta para WhatsApp.
        
        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes
        
        Returns:
            Respuesta formateada para WhatsApp
        """
        # WhatsApp tiene límite de 4096 caracteres y no soporta markdown rico
        message = answer.strip()
        
        # Limitar longitud
        if len(message) > 4000:
            message = message[:4000] + "..."
        
        if sources and len(sources) > 0:
            sources_text = ', '.join(sources[:2])
            message += f"\n\nFuentes: {sources_text}"
        
        return message
    
    @staticmethod
    def format_for_instagram(answer: str, sources: Optional[List[str]] = None) -> str:
        """
        Formatea una respuesta para Instagram Direct Messages.
        
        Args:
            answer: Respuesta del agente
            sources: Lista de fuentes
        
        Returns:
            Respuesta formateada para Instagram
        """
        # Instagram tiene limitaciones similares a WhatsApp
        message = answer.strip()
        
        # Limitar longitud
        if len(message) > 1000:
            message = message[:1000] + "..."
        
        return message

