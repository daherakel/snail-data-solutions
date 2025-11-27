# Configuration Files

Este directorio contiene archivos de configuración YAML para el sistema de AI Document Assistant.

## Archivos Principales

### `tenant-config.yaml`
Configuración por tenant (cliente). Define personalidad del agente, casos de uso, integraciones y modelos.

**Ejemplo:**
```yaml
tenant_default:
  tenant_id: "default"
  tenant_name: "Default Tenant"

  agent:
    personality: "warm"  # warm, professional, technical, friendly
    tone: "conversational"
    language: "es"

  use_cases:
    - "document_assistant"

  integrations:
    - "web"

  models:
    embedding: "amazon.titan-embed-text-v1"
    llm: "anthropic.claude-3-haiku-20240307-v1:0"
```

### `model-config.yaml`
Configuración de modelos de Bedrock disponibles y sus parámetros.

### `integration-config.yaml`
Configuración de integraciones (Slack, Teams, WhatsApp, etc.).

### `nlp-config.yaml`
**NUEVO**: Configuración de NLP (Natural Language Processing).

Define:
- Clasificador de intenciones
- Comportamiento por intención
- Configuración de búsqueda semántica
- Cache
- Guardrails
- Límites de respuestas

**Intenciones soportadas:**
- `greeting` - Saludos
- `thanks` - Agradecimientos
- `document_list` - Lista de documentos
- `document_query` - Consultas sobre documentos
- `analysis_request` - Análisis y resúmenes
- `action_intent` - Acciones con la información
- `clarification` - Aclaraciones
- `off_topic` - Fuera de tema

## Uso

### En Lambda Functions

```python
from shared.utils.nlp_config_loader import NLPConfigLoader

# Cargar configuración
config_loader = NLPConfigLoader()
nlp_config = config_loader.load()

# Obtener config específica
intent_config = config_loader.get_intent_config('document_query')
classifier_config = config_loader.get_classifier_config()
search_config = config_loader.get_search_config()
```

### Variables de Entorno

Puedes sobrescribir configuración usando variables de entorno:

- `AGENT_PERSONALITY` - Personalidad del agente (warm, professional, technical, friendly)
- `AGENT_LANGUAGE` - Idioma (es, en)
- `NLP_CONFIG_PATH` - Ruta custom al archivo nlp-config.yaml

## Personalización

Para personalizar el comportamiento del agente:

1. Edita `nlp-config.yaml` para cambiar límites, cache, guardrails
2. Edita `tenant-config.yaml` para cambiar personalidad y casos de uso
3. Los prompts se personalizan en `shared/prompts/base_prompts.py`

## Beneficios

✅ Configuración centralizada
✅ Fácil de modificar sin tocar código
✅ Replicable por tenant
✅ Versionable en Git
✅ Multi-ambiente (dev/staging/prod)
