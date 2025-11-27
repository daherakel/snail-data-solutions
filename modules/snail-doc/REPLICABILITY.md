# Guía de Replicabilidad - AWS Bedrock Agents

Esta guía explica cómo replicar el módulo AWS Bedrock Agents para un nuevo cliente o tenant.

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerrequisitos](#prerrequisitos)
3. [Proceso de Replicación](#proceso-de-replicación)
4. [Configuración de Tenant](#configuración-de-tenant)
5. [Personalización del Agente](#personalización-del-agente)
6. [Habilitación de Integraciones](#habilitación-de-integraciones)
7. [Deployment](#deployment)
8. [Validación y Testing](#validación-y-testing)
9. [Checklist de Replicación](#checklist-de-replicación)

---

## Introducción

El módulo AWS Bedrock Agents está diseñado para ser completamente replicable. Cada cliente puede tener su propia configuración (tenant) con:

- Personalización del agente (personalidad, tono, idioma)
- Casos de uso específicos habilitados
- Integraciones configuradas (Slack, Teams, WhatsApp, etc.)
- Configuración de modelos independiente
- Prompts personalizados

---

## Prerrequisitos

Antes de replicar el módulo, asegúrate de tener:

1. **AWS Account** con permisos para crear recursos
2. **Terraform** >= 1.0 instalado
3. **AWS CLI** configurado
4. **Acceso a Bedrock** habilitado en tu cuenta AWS
5. **Conocimiento básico** de la arquitectura del módulo

---

## Proceso de Replicación

### Paso 1: Crear Configuración de Tenant

1. Copiar template de configuración:
   ```bash
   cp shared/config/tenant-config.yaml shared/config/tenants/{TENANT_ID}-config.yaml
   ```

2. Editar la configuración para el nuevo tenant:
   ```yaml
   {TENANT_ID}:
     tenant_id: "{TENANT_ID}"
     tenant_name: "Nombre del Cliente"
     
     agent:
       personality: "warm"  # warm, professional, technical, friendly
       tone: "conversational"
       language: "es"
     
     use_cases:
       - "document_assistant"
       # - "customer_support"  # Habilitar si aplica
     
     integrations:
       - "web"
       - "slack"  # Habilitar integraciones necesarias
     
     models:
       embedding: "amazon.titan-embed-text-v1"
       llm: "anthropic.claude-3-haiku-20240307-v1:0"
   ```

3. Agregar el tenant al archivo principal:
   ```yaml
   # En tenant-config.yaml, agregar:
   {TENANT_ID}:
     # ... configuración del tenant
   ```

### Paso 2: Configurar Variables de Entorno

Crear archivo `.env.tenant` o agregar a variables de entorno:

```bash
export TENANT_ID="{TENANT_ID}"
export ENVIRONMENT="dev"  # o staging/prod
export AWS_REGION="us-east-1"
```

### Paso 3: Personalizar Prompts (Opcional)

Si necesitas prompts completamente personalizados:

1. Crear archivo de prompts personalizados:
   ```bash
   cp templates/prompts/document-assistant-template.md config/tenants/{TENANT_ID}/prompts/
   ```

2. Modificar según necesidades del cliente

3. Actualizar configuración del tenant:
   ```yaml
   prompts:
     system_prompt_template: "custom"
     custom_instructions: "Instrucciones específicas del cliente..."
   ```

### Paso 4: Configurar Integraciones

Para habilitar integraciones específicas:

#### Slack

1. Crear Slack App en https://api.slack.com/apps
2. Obtener tokens (Bot Token, Signing Secret)
3. Configurar eventos y permisos
4. Guardar tokens en AWS Secrets Manager:
   ```bash
   aws secretsmanager create-secret \
     --name "{TENANT_ID}/slack/tokens" \
     --secret-string '{"bot_token":"xoxb-...","signing_secret":"..."}'
   ```

5. Habilitar en configuración del tenant:
   ```yaml
   integrations:
     - "slack"
   ```

#### Otras Integraciones

Ver documentación específica en `docs/integrations/` para:
- Microsoft Teams
- WhatsApp
- Instagram

### Paso 5: Deployment con Terraform

1. Copiar template de Terraform:
   ```bash
   cp infrastructure/terraform/environments/dev/terraform.tfvars.example \
      infrastructure/terraform/environments/dev/{TENANT_ID}.tfvars
   ```

2. Configurar variables:
   ```hcl
   project_name = "{TENANT_ID}"
   environment  = "dev"
   tenant_id    = "{TENANT_ID}"
   
   # Configuración específica del cliente
   bedrock_llm_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
   ```

3. Deploy:
   ```bash
   cd infrastructure/terraform/environments/dev
   terraform init
   terraform plan -var-file="{TENANT_ID}.tfvars"
   terraform apply -var-file="{TENANT_ID}.tfvars"
   ```

---

## Configuración de Tenant

### Parámetros Principales

| Parámetro | Descripción | Valores Posibles |
|-----------|-------------|------------------|
| `tenant_id` | ID único del tenant | String alfanumérico |
| `tenant_name` | Nombre descriptivo | String |
| `agent.personality` | Personalidad del agente | warm, professional, technical, friendly |
| `agent.tone` | Tono de conversación | conversational, formal, casual |
| `agent.language` | Idioma del agente | es, en |
| `use_cases` | Casos de uso habilitados | Lista de nombres de casos de uso |
| `integrations` | Integraciones habilitadas | Lista de nombres de integraciones |

### Ejemplo Completo

```yaml
client_acme:
  tenant_id: "client_acme"
  tenant_name: "ACME Corporation"
  
  agent:
    personality: "professional"
    tone: "formal"
    language: "es"
    max_response_length: 2048
    temperature: 0.3
  
  use_cases:
    - "document_assistant"
    - "customer_support"
  
  integrations:
    - "web"
    - "slack"
  
  models:
    embedding: "amazon.titan-embed-text-v1"
    llm: "anthropic.claude-3-5-sonnet-20241022-v2:0"
  
  rag:
    max_context_chunks: 5
    chunk_size: 1000
  
  limits:
    max_query_length: 500
    max_conversation_history: 30
    rate_limit_per_minute: 60
  
  prompts:
    system_prompt_template: "base"
    custom_instructions: |
      - Priorizar información de productos ACME
      - Referenciar siempre la documentación oficial
```

---

## Personalización del Agente

### Personalidades Disponibles

1. **warm** (Cálido): Tono amigable y cercano, usa emojis moderadamente
2. **professional** (Profesional): Tono formal y preciso
3. **technical** (Técnico): Tono directo, usa terminología específica
4. **friendly** (Amigable): Tono casual y relajado

### Personalización de Prompts

Los prompts pueden personalizarse de dos formas:

1. **Usando template base con custom_instructions**:
   ```yaml
   prompts:
     system_prompt_template: "base"
     custom_instructions: "Instrucciones adicionales..."
   ```

2. **Creando prompt completamente personalizado**:
   - Crear archivo en `config/tenants/{TENANT_ID}/prompts/`
   - Referenciar en configuración

---

## Habilitación de Integraciones

### Web (Frontend)

Siempre habilitada. No requiere configuración adicional.

### Slack

1. Crear Slack App
2. Configurar OAuth y permisos
3. Guardar tokens en Secrets Manager
4. Habilitar en configuración del tenant

Ver guía completa: `docs/integrations/SLACK.md`

### Otras Integraciones

- **Microsoft Teams**: Requiere Azure AD App Registration
- **WhatsApp**: Requiere cuenta Business API (Twilio o Meta)
- **Instagram**: Requiere Facebook App y Page

---

## Deployment

### Deployment Manual

```bash
# 1. Configurar tenant
export TENANT_ID="client_example"

# 2. Deploy infraestructura
cd infrastructure/terraform/environments/dev
terraform init
terraform apply -var="tenant_id=$TENANT_ID"

# 3. Configurar integraciones (si aplica)
# Ver docs/integrations/ para cada integración
```

### Deployment con Script

```bash
# Usar script de deployment
./scripts/deploy-tenant.sh client_example dev
```

---

## Validación y Testing

### Validar Configuración

```bash
# Validar configuración del tenant
python scripts/validate-config.py --tenant client_example
```

### Testear Integración

```bash
# Testear integración específica
./scripts/test-integration.sh slack client_example
```

### Verificar Deployment

1. Verificar recursos en AWS Console
2. Probar query handler con curl:
   ```bash
   curl -X POST $QUERY_HANDLER_URL \
     -H "Content-Type: application/json" \
     -d '{"query": "test", "tenant_id": "client_example"}'
   ```
3. Verificar logs en CloudWatch

---

## Checklist de Replicación

### Pre-Deployment

- [ ] Configuración de tenant creada en `shared/config/tenant-config.yaml`
- [ ] Variables de entorno configuradas
- [ ] Prompts personalizados (si aplica)
- [ ] Integraciones configuradas y tokens guardados en Secrets Manager
- [ ] Terraform variables file creado

### Deployment

- [ ] Infraestructura desplegada con Terraform
- [ ] Lambda functions funcionando
- [ ] S3 buckets creados
- [ ] DynamoDB tables creadas
- [ ] Secrets configurados

### Post-Deployment

- [ ] Query handler respondiendo correctamente
- [ ] Integraciones funcionando (Slack, Teams, etc.)
- [ ] Documentos se pueden subir y procesar
- [ ] Conversaciones funcionando
- [ ] Logs verificados en CloudWatch
- [ ] Costos monitoreados

### Documentación

- [ ] README del tenant creado (si aplica)
- [ ] Configuración documentada
- [ ] Proceso de replicación documentado

---

## Troubleshooting

### Problema: Configuración no se carga

**Solución**: Verificar que `TENANT_ID` esté en variables de entorno y que el tenant exista en `tenant-config.yaml`.

### Problema: Integración no funciona

**Solución**: 
1. Verificar que esté habilitada en configuración del tenant
2. Verificar tokens en Secrets Manager
3. Revisar logs de Lambda específica de la integración

### Problema: Prompts no se personalizan

**Solución**: Verificar que `system_prompt_template` y `custom_instructions` estén correctamente configurados.

---

## Próximos Pasos

Después de replicar el módulo:

1. Personalizar prompts según necesidades del cliente
2. Configurar casos de uso adicionales (si aplica)
3. Habilitar integraciones requeridas
4. Monitorear costos y uso
5. Iterar basándose en feedback del cliente

---

## Recursos Adicionales

- [README Principal](README.md) - Visión general del módulo
- [Deployment Guide](../docs/DEPLOYMENT.md) - Guía de deployment detallada
- [Cost Analysis](../docs/COST_AND_SCALING.md) - Análisis de costos
- [Integration Docs](docs/integrations/) - Documentación por integración

---

**Última actualización**: 2025-11-26  
**Versión**: 1.0.0

