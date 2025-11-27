# Template de Deployment - AWS Bedrock Agents

Template para documentar el deployment de un nuevo tenant/cliente.

## Información del Cliente

- **Tenant ID**: `{TENANT_ID}`
- **Nombre del Cliente**: `{CLIENT_NAME}`
- **Ambiente**: `dev` / `staging` / `prod`
- **Fecha de Deployment**: `{DATE}`
- **Responsable**: `{NAME}`

---

## Configuración del Tenant

### Personalización del Agente

- **Personalidad**: `{warm|professional|technical|friendly}`
- **Tono**: `{conversational|formal|casual}`
- **Idioma**: `{es|en}`

### Casos de Uso Habilitados

- [ ] Document Assistant
- [ ] Customer Support
- [ ] Google Sheets Reader
- [ ] Otro: `{SPECIFY}`

### Integraciones Habilitadas

- [x] Web (Frontend)
- [ ] Slack
- [ ] Microsoft Teams
- [ ] WhatsApp
- [ ] Instagram
- [ ] Otro: `{SPECIFY}`

### Modelos Configurados

- **Embedding Model**: `{MODEL_ID}`
- **LLM Model**: `{MODEL_ID}`

### Configuración de RAG

- **Max Context Chunks**: `{NUMBER}`
- **Chunk Size**: `{NUMBER}`
- **Chunk Overlap**: `{NUMBER}`

---

## Recursos AWS Desplegados

### S3 Buckets

- Raw Documents: `{BUCKET_NAME}`
- Processed Documents: `{BUCKET_NAME}`
- FAISS Backup: `{BUCKET_NAME}`

### Lambda Functions

- Query Handler: `{FUNCTION_NAME}`
- PDF Processor: `{FUNCTION_NAME}`
- Slack Handler: `{FUNCTION_NAME}` (si aplica)

### DynamoDB Tables

- Query Cache: `{TABLE_NAME}`
- Conversations: `{TABLE_NAME}`
- Rate Limiting: `{TABLE_NAME}`

### EventBridge Rules

- PDF Processing Trigger: `{RULE_NAME}`

### Otros Recursos

- API Gateway / Function URLs: `{URLS}`
- Secrets Manager: `{SECRET_NAMES}`
- IAM Roles: `{ROLE_NAMES}`

---

## Configuración de Integraciones

### Slack (si aplica)

- **Slack App ID**: `{APP_ID}`
- **Bot Token**: `{SECRET_NAME}` (en Secrets Manager)
- **Signing Secret**: `{SECRET_NAME}` (en Secrets Manager)
- **Webhook URL**: `{URL}`
- **Workspace**: `{WORKSPACE_NAME}`

### Microsoft Teams (si aplica)

- **App Registration ID**: `{APP_ID}`
- **Tenant ID**: `{TENANT_ID}`
- **Client Secret**: `{SECRET_NAME}` (en Secrets Manager)

### WhatsApp (si aplica)

- **Provider**: `{Twilio|Meta}`
- **Account SID**: `{ACCOUNT_SID}`
- **Phone Number**: `{PHONE_NUMBER}`

---

## Variables de Entorno

```bash
export TENANT_ID="{TENANT_ID}"
export ENVIRONMENT="{ENVIRONMENT}"
export AWS_REGION="us-east-1"
export PROJECT_NAME="{PROJECT_NAME}"
```

---

## Comandos de Deployment

```bash
# 1. Configurar tenant
export TENANT_ID="{TENANT_ID}"
export ENVIRONMENT="{ENVIRONMENT}"

# 2. Deploy infraestructura
cd infrastructure/terraform/environments/{ENVIRONMENT}
terraform init
terraform plan -var="tenant_id=$TENANT_ID" -var-file="{TENANT_ID}.tfvars"
terraform apply -var="tenant_id=$TENANT_ID" -var-file="{TENANT_ID}.tfvars"

# 3. Guardar outputs
terraform output -json > outputs-{TENANT_ID}.json
```

---

## URLs y Endpoints

### Query Handler

- **Function URL**: `{URL}`
- **Test Command**:
  ```bash
  curl -X POST {URL} \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "tenant_id": "{TENANT_ID}"}'
  ```

### Frontend (si aplica)

- **URL**: `{FRONTEND_URL}`
- **API Endpoint**: `{API_URL}`

### Integraciones

- **Slack Webhook**: `{SLACK_URL}`
- **Teams Endpoint**: `{TEAMS_URL}`

---

## Testing y Validación

### Tests Realizados

- [ ] Query handler responde correctamente
- [ ] PDF processing funciona
- [ ] Conversaciones se guardan en DynamoDB
- [ ] Integración Slack funciona (si aplica)
- [ ] Integración Teams funciona (si aplica)
- [ ] Frontend se conecta correctamente
- [ ] Logs en CloudWatch funcionando

### Comandos de Test

```bash
# Test query handler
curl -X POST {QUERY_HANDLER_URL} \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Qué documentos tienes disponibles?",
    "tenant_id": "{TENANT_ID}"
  }'

# Test PDF upload
aws s3 cp test.pdf s3://{RAW_BUCKET}/

# Ver logs
aws logs tail /aws/lambda/{FUNCTION_NAME} --follow
```

---

## Monitoreo y Costos

### CloudWatch Dashboards

- Dashboard: `{DASHBOARD_NAME}`
- URL: `{DASHBOARD_URL}`

### Alertas Configuradas

- Error Rate: `{ALERT_NAME}`
- Cost Alert: `{ALERT_NAME}`
- Lambda Timeout: `{ALERT_NAME}`

### Costo Estimado Mensual

- **Desarrollo**: `{COST}` USD/mes
- **Producción**: `{COST}` USD/mes

Ver: [COST_AND_SCALING.md](../docs/COST_AND_SCALING.md)

---

## Notas y Observaciones

### Configuraciones Especiales

```
{NOTES}
```

### Problemas Encontrados y Soluciones

```
{ISSUES_AND_SOLUTIONS}
```

### Próximos Pasos

- [ ] Personalizar prompts adicionales
- [ ] Configurar más integraciones
- [ ] Optimizar costos
- [ ] Agregar casos de uso adicionales

---

## Contactos y Soporte

- **Cliente Contact**: `{NAME}`, `{EMAIL}`
- **Technical Contact**: `{NAME}`, `{EMAIL}`
- **Support Channel**: `{CHANNEL}`

---

**Última actualización**: `{DATE}`  
**Versión del Deployment**: `{VERSION}`

