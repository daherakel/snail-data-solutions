# Integración Slack - Guía Completa

Guía completa para configurar e implementar la integración de Slack con AWS Bedrock Agents.

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Prerrequisitos](#prerrequisitos)
3. [Configuración en Slack](#configuración-en-slack)
4. [Configuración en AWS](#configuración-en-aws)
5. [Deployment con Terraform](#deployment-con-terraform)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)
8. [Seguridad](#seguridad)

---

## Introducción

La integración de Slack permite que los usuarios interactúen con el agente AI directamente desde Slack. El bot puede:

- Responder a mensajes directos
- Responder a menciones en canales
- Mantener conversaciones con contexto
- Integrar con el sistema de documentos

## Prerrequisitos

1. **Slack Workspace** con permisos de administrador
2. **AWS Account** con permisos para crear recursos
3. **Terraform** >= 1.0 instalado
4. **AWS CLI** configurado

---

## Configuración en Slack

### Paso 1: Crear Slack App

1. Ir a https://api.slack.com/apps
2. Click en **"Create New App"**
3. Seleccionar **"From scratch"**
4. Nombrar la app (ej: "Bedrock AI Assistant")
5. Seleccionar el workspace

### Paso 2: Configurar Bot Token Scopes

1. Ir a **OAuth & Permissions** en el menú lateral
2. Scopes necesarios:
   - `chat:write` - Enviar mensajes
   - `channels:read` - Leer información de canales
   - `im:read` - Leer mensajes directos
   - `im:write` - Escribir mensajes directos
   - `app_mentions:read` - Leer menciones

3. Click en **"Install to Workspace"**
4. Copiar el **Bot User OAuth Token** (comienza con `xoxb-`)

### Paso 3: Configurar Signing Secret

1. Ir a **Basic Information** en el menú lateral
2. En la sección **App Credentials**, copiar el **Signing Secret**

### Paso 4: Configurar Event Subscriptions

1. Ir a **Event Subscriptions** en el menú lateral
2. Activar **"Enable Events"**
3. **Request URL**: Se configurará después del deployment (Function URL)
4. Subscribe to bot events:
   - `message.channels` - Mensajes en canales públicos
   - `message.groups` - Mensajes en canales privados
   - `message.im` - Mensajes directos
   - `app_mention` - Menciones del bot

### Paso 5: Guardar Tokens

Guardar los siguientes valores (se usarán después):
- **Bot Token**: `xoxb-...`
- **Signing Secret**: `...`

---

## Configuración en AWS

### Opción 1: Usar AWS Secrets Manager (Recomendado para Producción)

```bash
# Crear secret para Bot Token
aws secretsmanager create-secret \
  --name "bedrock-agents-dev/slack/bot-token" \
  --secret-string '{"bot_token":"xoxb-YOUR-TOKEN-HERE"}'

# Crear secret para Signing Secret
aws secretsmanager create-secret \
  --name "bedrock-agents-dev/slack/signing-secret" \
  --secret-string '{"signing_secret":"YOUR-SIGNING-SECRET-HERE"}'
```

### Opción 2: Variables de Entorno (Desarrollo)

Los tokens se pueden pasar como variables de entorno directamente (no recomendado para producción).

---

## Deployment con Terraform

### Paso 1: Configurar Variables

Editar `infrastructure/terraform/environments/dev/main.tf` o crear un archivo de variables:

```hcl
# Variables para Slack
variable "slack_bot_token" {
  description = "Bot Token de Slack"
  type        = string
  sensitive   = true
  default     = ""
}

variable "slack_signing_secret" {
  description = "Signing Secret de Slack"
  type        = string
  sensitive   = true
  default     = ""
}

# O usar Secrets Manager ARNs
variable "slack_bot_token_secret_arn" {
  description = "ARN del secret en Secrets Manager para Bot Token"
  type        = string
  default     = ""
}

variable "slack_signing_secret_secret_arn" {
  description = "ARN del secret en Secrets Manager para Signing Secret"
  type        = string
  default     = ""
}
```

### Paso 2: Agregar Módulo Slack

En `infrastructure/terraform/environments/dev/main.tf`:

```hcl
module "slack_integration" {
  source = "../../modules/integrations/slack"

  project_name  = var.project_name
  environment   = var.environment
  aws_region    = var.aws_region

  # Lambda configuration
  slack_handler_source_dir = "../../../lambda-functions/slack-handler"
  lambda_slack_handler_role_arn = module.iam.slack_handler_role_arn

  # Slack configuration - Opción 1: Secrets Manager (recomendado)
  slack_bot_token_secret_arn      = var.slack_bot_token_secret_arn
  slack_signing_secret_secret_arn = var.slack_signing_secret_secret_arn

  # Slack configuration - Opción 2: Variables directas (desarrollo)
  # slack_bot_token       = var.slack_bot_token
  # slack_signing_secret  = var.slack_signing_secret

  # Verificación de firma
  verify_slack_signature = var.environment != "dev"  # Habilitar en staging/prod

  # Query handler configuration
  query_handler_function_name = module.lambda.query_handler_function_name

  # Function URL
  create_function_url = true
  cors_allowed_origins = ["*"]  # Configurar apropiadamente en producción

  # Logging
  log_level          = "INFO"
  log_retention_days = 7

  tags = var.tags
}
```

### Paso 3: Crear Rol IAM para Slack Handler

En el módulo IAM, agregar rol para Slack handler:

```hcl
resource "aws_iam_role" "slack_handler" {
  name = "${var.project_name}-${var.environment}-slack-handler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "slack_handler" {
  name = "${var.project_name}-${var.environment}-slack-handler-policy"
  role = aws_iam_role.slack_handler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = module.lambda.query_handler_function_arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          var.slack_bot_token_secret_arn,
          var.slack_signing_secret_secret_arn
        ]
      }
    ]
  })
}
```

### Paso 4: Deploy

```bash
cd infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply
```

### Paso 5: Obtener Function URL

```bash
terraform output slack_handler_function_url
```

Copiar la URL (ej: `https://abc123.lambda-url.us-east-1.on.aws/`)

### Paso 6: Configurar URL en Slack

1. Ir a **Event Subscriptions** en Slack App
2. Pegar la Function URL en **Request URL**
3. Slack intentará verificar la URL (URL Verification Challenge)
4. Si es exitoso, verás un check verde

---

## Testing

### Test 1: URL Verification

Al configurar la URL en Slack, deberías ver en los logs:

```
[INFO] URL Verification - Challenge: 3eZbrwq...
```

### Test 2: Enviar Mensaje Directo

1. Abrir DM con el bot en Slack
2. Enviar: "Hola"
3. El bot debería responder con saludo

### Test 3: Probar Query

1. Enviar: "¿Qué documentos tienes disponibles?"
2. El bot debería responder con lista de documentos

### Test 4: Conversación con Contexto

1. Enviar: "¿De qué trata el documento X?"
2. Seguir con: "Y qué más dice sobre Y?"
3. El bot debería mantener contexto

### Ver Logs

```bash
# Ver logs del Slack handler
aws logs tail /aws/lambda/{project-name}-{env}-slack-handler --follow

# Ver logs del Query handler
aws logs tail /aws/lambda/{project-name}-{env}-query-handler --follow
```

---

## Troubleshooting

### Problema: Slack no acepta la URL

**Síntomas**: Error "URL verification failed" en Slack

**Soluciones**:
1. Verificar que Function URL esté creada:
   ```bash
   terraform output slack_handler_function_url
   ```
2. Verificar CORS configuration en Terraform
3. Revisar logs de Lambda para ver el challenge
4. Verificar que el handler maneje URL verification correctamente

### Problema: Eventos no llegan

**Síntomas**: No se reciben mensajes en Lambda

**Soluciones**:
1. Verificar que eventos estén suscritos en Slack App
2. Verificar permisos del bot en workspace
3. Verificar que el bot esté en el canal (para canales públicos)
4. Revisar logs de CloudWatch

### Problema: Error de verificación de firma

**Síntomas**: Lambda retorna 403 "Invalid signature"

**Soluciones**:
1. Verificar que `SLACK_SIGNING_SECRET` sea correcto
2. Verificar formato del body (debe ser string, no objeto)
3. En desarrollo: deshabilitar verificación temporalmente:
   ```hcl
   verify_slack_signature = false
   ```

### Problema: El bot no responde

**Síntomas**: Mensajes no reciben respuesta

**Soluciones**:
1. Verificar que el bot tenga permisos en el canal
2. Revisar logs de Lambda para errores
3. Verificar que query handler esté funcionando
4. Verificar que DynamoDB conversations table exista

### Problema: Respuestas duplicadas

**Síntomas**: El bot envía múltiples respuestas

**Soluciones**:
1. Verificar que no haya múltiples subscriptions en Slack
2. Verificar que el bot ignore sus propios mensajes
3. Revisar lógica de deduplicación

---

## Seguridad

### Mejores Prácticas

1. **Usar Secrets Manager** en producción (no variables de entorno)
2. **Habilitar verificación de firma** en producción
3. **Limitar CORS origins** a dominios conocidos
4. **Monitorear logs** para actividad sospechosa
5. **Rotar tokens** periódicamente
6. **Usar IAM roles** con permisos mínimos

### Verificación de Firma

La verificación de firma protege contra:
- Replay attacks (usando timestamp)
- Requests falsos (usando HMAC signature)

Siempre habilitar en producción.

---

## Configuración Avanzada

### Conversaciones por Thread

El bot mantiene contexto por thread. Cada thread en Slack tiene su propio `conversation_id`.

### Personalización de Respuestas

Las respuestas se formatean automáticamente para Slack:
- Se remueven "Preguntas relacionadas"
- Se agregan fuentes de forma sutil
- Se mantiene formato conversacional

### Rate Limiting

Configurar rate limiting en DynamoDB si es necesario (ver módulo DynamoDB).

---

## Referencias

- [Slack Events API](https://api.slack.com/events-api)
- [Slack Signing Secrets](https://api.slack.com/authentication/verifying-requests-from-slack)
- [Módulo Terraform](infrastructure/terraform/modules/integrations/slack/)
- [Handler Lambda](lambda-functions/slack-handler/)

---

**Última actualización**: 2025-11-26  
**Versión**: 1.0.0


