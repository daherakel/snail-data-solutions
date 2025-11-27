# Guía de Setup para Nuevo Tenant

Esta guía te ayudará a configurar un nuevo tenant/cliente en el sistema AWS Bedrock Agents.

## Paso 1: Crear Configuración del Tenant

1. Abrir `shared/config/tenant-config.yaml`
2. Agregar nueva sección con el ID del tenant:

```yaml
{tenant_id}:
  tenant_id: "{tenant_id}"
  tenant_name: "Nombre del Cliente"
  
  agent:
    personality: "warm"  # Elegir: warm, professional, technical, friendly
    tone: "conversational"  # Elegir: conversational, formal, casual
    language: "es"  # Elegir: es, en
  
  use_cases:
    - "document_assistant"
    # Agregar más casos de uso si aplica
  
  integrations:
    - "web"
    # Agregar más integraciones si aplica
    # - "slack"
    # - "teams"
  
  models:
    embedding: "amazon.titan-embed-text-v1"
    llm: "anthropic.claude-3-haiku-20240307-v1:0"
  
  rag:
    max_context_chunks: 5
    chunk_size: 1000
    chunk_overlap: 200
  
  limits:
    max_query_length: 500
    max_conversation_history: 30
    rate_limit_per_minute: 60
```

## Paso 2: Configurar Variables de Entorno

Crear archivo `.env.tenant` o agregar a variables de entorno:

```bash
export TENANT_ID="{tenant_id}"
export ENVIRONMENT="dev"
export AWS_REGION="us-east-1"
```

## Paso 3: Configurar Terraform Variables

Copiar template:

```bash
cp infrastructure/terraform/environments/dev/terraform.tfvars.example \
   infrastructure/terraform/environments/dev/{tenant_id}.tfvars
```

Editar `{tenant_id}.tfvars`:

```hcl
project_name = "{tenant_id}"
environment  = "dev"
tenant_id    = "{tenant_id}"

# Configuración de modelos
bedrock_llm_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

# Configuración de RAG
max_context_chunks = 5

# Otros ajustes según necesidades
```

## Paso 4: Deployment

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform plan -var-file="{tenant_id}.tfvars"
terraform apply -var-file="{tenant_id}.tfvars"
```

## Paso 5: Validar Deployment

1. Verificar que los recursos se crearon:
   ```bash
   terraform output
   ```

2. Probar query handler:
   ```bash
   export QUERY_URL=$(terraform output -raw query_handler_url)
   curl -X POST $QUERY_URL \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "tenant_id": "{tenant_id}"}'
   ```

## Paso 6: Configurar Integraciones (si aplica)

### Slack

1. Crear Slack App en https://api.slack.com/apps
2. Configurar OAuth y permisos necesarios
3. Guardar tokens en Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name "{tenant_id}/slack/tokens" \
     --secret-string '{"bot_token":"xoxb-...","signing_secret":"..."}'
   ```
4. Habilitar en configuración del tenant (agregar "slack" a integrations)

### Otras Integraciones

Ver documentación específica en `docs/integrations/`

## Personalización Adicional

### Personalizar Prompts

Si necesitas prompts completamente personalizados:

1. Crear directorio:
   ```bash
   mkdir -p config/tenants/{tenant_id}/prompts
   ```

2. Crear archivo de prompts personalizados

3. Actualizar configuración del tenant:
   ```yaml
   prompts:
     system_prompt_template: "custom"
     custom_instructions: "Instrucciones específicas..."
   ```

### Personalizar Personalidad

Editar `agent.personality` en configuración del tenant:

- `warm`: Cálido y amigable
- `professional`: Formal y preciso
- `technical`: Directo y técnico
- `friendly`: Casual y relajado

## Checklist

- [ ] Configuración del tenant creada
- [ ] Variables de entorno configuradas
- [ ] Terraform variables file creado
- [ ] Deployment realizado
- [ ] Query handler funcionando
- [ ] Integraciones configuradas (si aplica)
- [ ] Documentos se pueden subir y procesar
- [ ] Logs verificados

## Próximos Pasos

1. Subir documentos de prueba
2. Configurar integraciones adicionales
3. Personalizar prompts según necesidades
4. Monitorear costos y uso
5. Iterar basándose en feedback

## Recursos

- [Guía de Replicabilidad Completa](REPLICABILITY.md)
- [Template de Deployment](DEPLOYMENT_TEMPLATE.md)
- [README Principal](README.md)

