"""
NLP Config Loader
Carga y parsea configuración de NLP desde archivos YAML
"""

import logging
import os
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class NLPConfigLoader:
    """
    Carga configuración de NLP desde YAML.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa el loader.

        Args:
            config_path: Ruta al archivo de configuración (opcional)
        """
        if config_path is None:
            # Default: shared/config/nlp-config.yaml
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, "..", "config", "nlp-config.yaml")

        self.config_path = config_path
        self._config = None

    def load(self) -> Dict[str, Any]:
        """
        Carga la configuración desde el archivo YAML.

        Returns:
            Dict con la configuración completa
        """
        if self._config is not None:
            return self._config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)

            logger.info(f"NLP config loaded from: {self.config_path}")
            return self._config

        except FileNotFoundError:
            logger.error(f"NLP config file not found: {self.config_path}")
            return self._get_default_config()

        except Exception as e:
            logger.error(f"Error loading NLP config: {e}")
            return self._get_default_config()

    def get_intent_config(self, intent: str) -> Dict[str, Any]:
        """
        Obtiene configuración para una intención específica.

        Args:
            intent: Tipo de intención

        Returns:
            Dict con configuración de la intención
        """
        config = self.load()
        intents = config.get("intents", {})

        if intent not in intents:
            logger.warning(f"Intent '{intent}' not found in config, using defaults")
            return {
                "requires_documents": True,
                "use_llm_response": True,
                "max_chunks": 5,
                "max_response_length": 300,
                "cache_enabled": True,
                "cache_ttl_seconds": 604800,
            }

        return intents[intent]

    def get_classifier_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración del clasificador de intenciones.

        Returns:
            Dict con configuración del clasificador
        """
        config = self.load()
        return config.get(
            "intent_classifier",
            {
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "temperature": 0.3,
                "max_tokens": 200,
            },
        )

    def get_search_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de búsqueda semántica.

        Returns:
            Dict con configuración de búsqueda
        """
        config = self.load()
        return config.get(
            "search",
            {"default_top_k": 5, "max_top_k": 20, "min_similarity_threshold": 0.0},
        )

    def get_cache_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de cache.

        Returns:
            Dict con configuración de cache
        """
        config = self.load()
        return config.get(
            "cache",
            {"enabled": True, "default_ttl_seconds": 604800, "normalize_queries": True},
        )

    def get_guardrails_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de guardrails.

        Returns:
            Dict con configuración de guardrails
        """
        config = self.load()
        return config.get(
            "guardrails",
            {
                "enabled": True,
                "max_query_length": 500,
                "blocked_patterns": [],
                "rejection_message": "Lo siento, no puedo procesar ese tipo de solicitud.",
            },
        )

    def get_response_config(self) -> Dict[str, Any]:
        """
        Obtiene configuración de respuestas.

        Returns:
            Dict con configuración de respuestas
        """
        config = self.load()
        return config.get(
            "responses", {"max_length": 300, "temperature": 0.5, "limits": {}}
        )

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Retorna configuración por defecto en caso de error.

        Returns:
            Dict con configuración mínima por defecto
        """
        return {
            "intent_classifier": {
                "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
                "temperature": 0.3,
                "max_tokens": 200,
            },
            "intents": {
                "greeting": {
                    "requires_documents": False,
                    "use_llm_response": False,
                    "cache_enabled": False,
                },
                "thanks": {
                    "requires_documents": False,
                    "use_llm_response": False,
                    "cache_enabled": False,
                },
                "document_query": {
                    "requires_documents": True,
                    "use_llm_response": True,
                    "max_chunks": 5,
                    "cache_enabled": True,
                },
            },
            "search": {"default_top_k": 5, "max_top_k": 20},
            "cache": {"enabled": True, "default_ttl_seconds": 604800},
            "guardrails": {
                "enabled": True,
                "max_query_length": 500,
                "blocked_patterns": [],
                "rejection_message": "Lo siento, no puedo procesar ese tipo de solicitud.",
            },
            "responses": {"max_length": 300, "temperature": 0.5},
        }
