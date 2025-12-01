# Integraciones - Documentación

Documentación de todas las integraciones disponibles para AWS Bedrock Agents.

## Integraciones Disponibles

### ✅ Implementadas

- **[Slack](SLACK.md)** - Integración completa con Slack workspace
  - Mensajes directos
  - Menciones en canales
  - Conversaciones con contexto
  - Verificación de firma

### 🔄 En Desarrollo

- Microsoft Teams
- WhatsApp Business API
- Instagram Direct Messages

## Arquitectura de Integraciones

Todas las integraciones siguen el mismo patrón:

1. **Lambda Handler**: Recibe eventos de la plataforma
2. **Function URL o API Gateway**: Endpoint HTTPS para recibir webhooks
3. **Query Handler**: Procesa consultas usando el agente AI
4. **Conversations**: Almacena historial en DynamoDB

Ver [Base Integration](../../modules/aws-bedrock-agents/shared/integrations/) para más detalles sobre la arquitectura.

## Guía Rápida

### Configurar una Integración

1. Habilitar en configuración del tenant:
   ```yaml
   integrations:
     - "slack"
   ```

2. Desplegar con Terraform:
   ```hcl
   module "slack_integration" {
     source = "../../modules/integrations/slack"
     # ... configuración
   }
   ```

3. Configurar en la plataforma (Slack, Teams, etc.)

Ver documentación específica de cada integración para detalles.

## Seguridad

Todas las integraciones implementan:
- Verificación de autenticación (firmas, tokens)
- IAM roles con permisos mínimos
- Secrets Manager para tokens sensibles
- Logging y monitoreo

---

**Última actualización**: 2025-11-26


