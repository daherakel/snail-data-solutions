"""
Guardrails
Sistema de validación y guardrails para queries
"""

import re
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


class Guardrails:
    """
    Sistema de guardrails para validar queries y proteger contra uso indebido.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa guardrails.

        Args:
            config: Configuración de guardrails desde nlp-config.yaml
        """
        self.enabled = config.get("enabled", True)
        self.max_query_length = config.get("max_query_length", 500)
        self.blocked_patterns = config.get("blocked_patterns", [])
        self.rejection_message = config.get(
            "rejection_message", "Lo siento, no puedo procesar ese tipo de solicitud."
        )

    def validate(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Valida una query contra los guardrails.

        Args:
            query: Query del usuario

        Returns:
            Tupla (is_valid, rejection_message)
            - is_valid: True si pasa validación, False si se rechaza
            - rejection_message: Mensaje de rechazo si is_valid=False, None si is_valid=True
        """
        if not self.enabled:
            return True, None

        # 1. Verificar que no esté vacía
        if not query or not query.strip():
            return False, "Por favor, escribe una pregunta válida."

        # 2. Verificar longitud
        if len(query) > self.max_query_length:
            return (
                False,
                f"Tu pregunta es demasiado larga. Por favor, límitala a {self.max_query_length} caracteres.",
            )

        # 3. Verificar patrones bloqueados
        query_lower = query.lower()
        for pattern in self.blocked_patterns:
            if isinstance(pattern, str):
                # Búsqueda simple de substring
                if pattern.lower() in query_lower:
                    logger.warning(
                        f"Guardrail triggered: blocked pattern detected: {pattern}"
                    )
                    return False, self.rejection_message
            else:
                # Si es regex
                if re.search(pattern, query_lower):
                    logger.warning(
                        f"Guardrail triggered: blocked regex pattern detected"
                    )
                    return False, self.rejection_message

        # 4. Detectar repetición excesiva (spam)
        if self._is_spam(query):
            logger.warning("Guardrail triggered: spam detected")
            return False, "Por favor, haz una pregunta válida sin caracteres repetidos."

        # Todo OK
        return True, None

    def _is_spam(self, text: str) -> bool:
        """
        Detecta si el texto es spam (repetición excesiva de caracteres).

        Args:
            text: Texto a verificar

        Returns:
            True si es spam, False si es válido
        """
        # Detectar más de 20 caracteres idénticos consecutivos
        if re.search(r"(.)\1{20,}", text):
            return True

        # Detectar más de 10 palabras idénticas consecutivas
        words = text.lower().split()
        if len(words) >= 10:
            for i in range(len(words) - 9):
                if len(set(words[i : i + 10])) == 1:
                    return True

        return False

    def sanitize_query(self, query: str) -> str:
        """
        Sanitiza una query limpiando espacios y caracteres innecesarios.

        Args:
            query: Query original

        Returns:
            Query sanitizada
        """
        # Remover espacios múltiples
        sanitized = " ".join(query.split())

        # Remover espacios antes de puntuación
        sanitized = re.sub(r"\s+([?.!,])", r"\1", sanitized)

        return sanitized.strip()
