"""
Config Loader
Sistema de carga de configuración multi-tenant y multi-ambiente
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """
    Cargador de configuración centralizado para el módulo Bedrock Agents.
    Soporta configuración multi-tenant y multi-ambiente.
    """
    
    def __init__(self, config_base_path: Optional[str] = None):
        """
        Inicializa el cargador de configuración.
        
        Args:
            config_base_path: Ruta base de los archivos de configuración.
                            Si es None, busca en shared/config/ relativo al script.
        """
        if config_base_path is None:
            # Buscar la ruta base del módulo
            current_file = Path(__file__).resolve()
            module_root = current_file.parent.parent.parent
            config_base_path = module_root / "shared" / "config"
        else:
            config_base_path = Path(config_base_path)
        
        self.config_base_path = config_base_path
        self._tenant_config: Optional[Dict[str, Any]] = None
        self._model_config: Optional[Dict[str, Any]] = None
        self._integration_config: Optional[Dict[str, Any]] = None
        
        # Cargar configuración base
        self._load_all_configs()
    
    def _load_all_configs(self) -> None:
        """Carga todos los archivos de configuración."""
        self._tenant_config = self._load_yaml("tenant-config.yaml")
        self._model_config = self._load_yaml("model-config.yaml")
        self._integration_config = self._load_yaml("integration-config.yaml")
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Carga un archivo YAML de configuración."""
        file_path = self.config_base_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo de configuración no encontrado: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def get_tenant_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de un tenant.
        
        Args:
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            Dict con la configuración del tenant.
        """
        if tenant_id is None:
            tenant_id = os.environ.get("TENANT_ID", "default")
        
        tenant_config = self._tenant_config.get(tenant_id)
        
        if tenant_config is None:
            # Fallback a default
            tenant_config = self._tenant_config.get("default", {})
        
        return tenant_config.copy()
    
    def get_environment(self) -> str:
        """Obtiene el ambiente actual desde variables de entorno."""
        return os.environ.get("ENVIRONMENT", "dev")
    
    def get_model_config(self, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de modelos para un ambiente.
        
        Args:
            environment: Ambiente (dev/staging/prod). Si es None, usa ENVIRONMENT de env.
        
        Returns:
            Dict con la configuración de modelos.
        """
        if environment is None:
            environment = self.get_environment()
        
        env_config = self._model_config.get("environments", {}).get(environment, {})
        
        if not env_config:
            # Fallback a dev
            env_config = self._model_config.get("environments", {}).get("dev", {})
        
        return env_config.copy()
    
    def get_integration_config(self, integration_name: str) -> Dict[str, Any]:
        """
        Obtiene la configuración de una integración específica.
        
        Args:
            integration_name: Nombre de la integración (web, slack, teams, etc.)
        
        Returns:
            Dict con la configuración de la integración.
        """
        integrations = self._integration_config.get("integrations", {})
        return integrations.get(integration_name, {}).copy()
    
    def get_integration_env_settings(self, integration_name: str, environment: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de ambiente específica para una integración.
        
        Args:
            integration_name: Nombre de la integración
            environment: Ambiente. Si es None, usa ENVIRONMENT de env.
        
        Returns:
            Dict con la configuración de ambiente de la integración.
        """
        if environment is None:
            environment = self.get_environment()
        
        env_settings = self._integration_config.get("environment_settings", {}).get(environment, {})
        return env_settings.get(integration_name, {}).copy()
    
    def is_integration_enabled(self, integration_name: str, tenant_id: Optional[str] = None) -> bool:
        """
        Verifica si una integración está habilitada para un tenant.
        
        Args:
            integration_name: Nombre de la integración
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            True si la integración está habilitada, False en caso contrario.
        """
        tenant_config = self.get_tenant_config(tenant_id)
        enabled_integrations = tenant_config.get("integrations", [])
        
        return integration_name in enabled_integrations
    
    def is_use_case_enabled(self, use_case: str, tenant_id: Optional[str] = None) -> bool:
        """
        Verifica si un caso de uso está habilitado para un tenant.
        
        Args:
            use_case: Nombre del caso de uso
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            True si el caso de uso está habilitado, False en caso contrario.
        """
        tenant_config = self.get_tenant_config(tenant_id)
        enabled_use_cases = tenant_config.get("use_cases", [])
        
        return use_case in enabled_use_cases
    
    def get_agent_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración del agente para un tenant.
        
        Args:
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            Dict con la configuración del agente.
        """
        tenant_config = self.get_tenant_config(tenant_id)
        return tenant_config.get("agent", {}).copy()
    
    def get_rag_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de RAG para un tenant.
        
        Args:
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            Dict con la configuración de RAG.
        """
        tenant_config = self.get_tenant_config(tenant_id)
        return tenant_config.get("rag", {}).copy()
    
    def get_limits_config(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la configuración de límites para un tenant.
        
        Args:
            tenant_id: ID del tenant. Si es None, usa TENANT_ID de env o 'default'.
        
        Returns:
            Dict con la configuración de límites.
        """
        tenant_config = self.get_tenant_config(tenant_id)
        return tenant_config.get("limits", {}).copy()
    
    def get_recommended_model_for_use_case(self, use_case: str) -> Dict[str, str]:
        """
        Obtiene los modelos recomendados para un caso de uso.
        
        Args:
            use_case: Nombre del caso de uso
        
        Returns:
            Dict con 'llm' y 'embedding' recomendados.
        """
        use_case_models = self._model_config.get("use_case_models", {})
        return use_case_models.get(use_case, {}).copy()


# Instancia global del config loader (singleton pattern)
_config_loader_instance: Optional[ConfigLoader] = None


def get_config_loader(config_base_path: Optional[str] = None) -> ConfigLoader:
    """
    Obtiene la instancia global del config loader (singleton).
    
    Args:
        config_base_path: Ruta base de configuración (solo usado en primera llamada).
    
    Returns:
        Instancia de ConfigLoader.
    """
    global _config_loader_instance
    
    if _config_loader_instance is None:
        _config_loader_instance = ConfigLoader(config_base_path)
    
    return _config_loader_instance


def reload_config(config_base_path: Optional[str] = None) -> ConfigLoader:
    """
    Recarga la configuración (útil para testing o hot-reload).
    
    Args:
        config_base_path: Ruta base de configuración.
    
    Returns:
        Nueva instancia de ConfigLoader.
    """
    global _config_loader_instance
    _config_loader_instance = ConfigLoader(config_base_path)
    return _config_loader_instance

