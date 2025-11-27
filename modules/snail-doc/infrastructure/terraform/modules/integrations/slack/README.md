# Slack Integration Module

Módulo Terraform para desplegar la integración de Slack con el sistema de agentes AWS Bedrock.

## Descripción

Este módulo crea:

- **Lambda Function**: Handler para procesar eventos de Slack
- **Function URL**: Endpoint HTTPS para recibir eventos de Slack
- **CloudWatch Logs**: Logging y monitoreo
- **IAM Policies**: Permisos para leer Secrets Manager (si se usan)
- **CloudWatch Alarms**: Alertas opcionales (configurables)

## Uso

```hcl
module "slack_integration" {
  source = "../../modules/integrations/slack"

  project_name  = "bedrock-agents"
  environment   = "dev"
  aws_region    = "us-east-1"

  # Lambda configuration
  slack_handler_source_dir = "../../../lambda-functions/slack-handler"
  lambda_slack_handler_role_arn = module.iam.slack_handler_role_arn
  
  # Slack configuration (opción 1: variables directas)
  slack_bot_token       = var.slack_bot_token
  slack_signing_secret  = var.slack_signing_secret
  
  # O usar Secrets Manager (opción 2: preferido para producción)
  # slack_bot_token_secret_arn      = "arn:aws:secretsmanager:us-east-1:123456789012:secret:slack/bot-token"
  # slack_signing_secret_secret_arn = "arn:aws:secretsmanager:us-east-1:123456789012:secret:slack/signing-secret"
  
  verify_slack_signature = var.environment != "dev"  # Deshabilitar en dev local

  # Query handler configuration
  query_handler_function_name = module.lambda.query_handler_function_name

  # Function URL configuration
  create_function_url = true
  cors_allowed_origins = ["*"]  # Configurar apropiadamente en producción

  # Logging
  log_level          = "INFO"
  log_retention_days = 7

  tags = {
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}
```

## Variables Principales

### Configuración de Lambda

- `slack_handler_source_dir`: Directorio con código del handler
- `lambda_slack_handler_role_arn`: ARN del rol IAM
- `slack_handler_timeout`: Timeout en segundos (default: 30)
- `slack_handler_memory`: Memoria en MB (default: 256)

### Configuración de Slack

**Opción 1: Variables directas** (desarrollo)
- `slack_bot_token`: Bot Token de Slack
- `slack_signing_secret`: Signing Secret de Slack

**Opción 2: Secrets Manager** (producción - recomendado)
- `slack_bot_token_secret_arn`: ARN del secret para Bot Token
- `slack_signing_secret_secret_arn`: ARN del secret para Signing Secret

- `verify_slack_signature`: Verificar firma de Slack (default: true)

### Configuración de Function URL

- `create_function_url`: Crear Function URL (default: true)
- `cors_allowed_origins`: Orígenes permitidos para CORS

## Outputs

- `slack_handler_function_name`: Nombre de la función Lambda
- `slack_handler_function_arn`: ARN de la función Lambda
- `slack_handler_function_url`: URL de la Function URL (para configurar en Slack)
- `slack_webhook_url`: Alias de function_url (para claridad)

## Configuración en Slack

1. Obtener `slack_handler_function_url` del output de Terraform
2. Configurar en Slack App:
   - Event Subscriptions → Enable Events
   - Request URL: `{slack_handler_function_url}`
   - Subscribe to events:
     - `message.channels`
     - `message.groups`
     - `message.im`
     - `app_mention`

3. Verificar que Slack acepte la URL (URL Verification Challenge)

## Seguridad

- **Verificación de firma**: Habilitada por defecto (verificar `verify_slack_signature`)
- **Secrets Manager**: Recomendado para producción en lugar de variables directas
- **IAM**: El rol debe tener permisos para:
  - Invocar query handler Lambda
  - Leer Secrets Manager (si se usan)
  - Escribir logs en CloudWatch

## Monitoreo

- Logs disponibles en CloudWatch: `/aws/lambda/{function_name}`
- Alarms opcionales configuradas para errores
- Métricas disponibles: Invocations, Errors, Duration, Throttles

## Troubleshooting

### Slack no acepta la URL

- Verificar que Function URL esté creada
- Verificar CORS configuration
- Revisar logs de Lambda para URL verification challenge

### Eventos no llegan

- Verificar que eventos estén suscritos en Slack App
- Verificar permisos del bot en Slack workspace
- Revisar logs de CloudWatch

### Errores de verificación de firma

- En desarrollo: establecer `verify_slack_signature = false`
- En producción: verificar que signing secret sea correcto
- Verificar formato de timestamp en headers

## Referencias

- [Slack Events API](https://api.slack.com/events-api)
- [Slack Signing Secrets](https://api.slack.com/authentication/verifying-requests-from-slack)
- Ver documentación completa: `../../../../docs/integrations/SLACK.md`

