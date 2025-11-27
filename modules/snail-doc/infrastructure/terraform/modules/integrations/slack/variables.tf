# Variables for Slack Integration module

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "bedrock-agents"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# =====================================================
# Lambda Configuration
# =====================================================

variable "slack_handler_source_dir" {
  description = "Directorio con código del Slack handler"
  type        = string
}

variable "lambda_slack_handler_role_arn" {
  description = "ARN del rol IAM para Lambda Slack handler"
  type        = string
}

variable "slack_handler_timeout" {
  description = "Timeout para Slack handler Lambda (segundos)"
  type        = number
  default     = 30
}

variable "slack_handler_memory" {
  description = "Memoria para Slack handler Lambda (MB)"
  type        = number
  default     = 256
}

# =====================================================
# Slack Configuration
# =====================================================

variable "slack_bot_token" {
  description = "Bot Token de Slack (alternativa a secret_arn)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "slack_signing_secret" {
  description = "Signing Secret de Slack (alternativa a secret_arn)"
  type        = string
  default     = ""
  sensitive   = true
}

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

variable "verify_slack_signature" {
  description = "Verificar firma de Slack (deshabilitar en dev local)"
  type        = bool
  default     = true
}

# =====================================================
# Query Handler Configuration
# =====================================================

variable "query_handler_function_name" {
  description = "Nombre de la función Lambda query handler a invocar"
  type        = string
}

# =====================================================
# Function URL Configuration
# =====================================================

variable "create_function_url" {
  description = "Crear Function URL para recibir eventos de Slack"
  type        = bool
  default     = true
}

variable "cors_allowed_origins" {
  description = "Orígenes permitidos para CORS"
  type        = list(string)
  default     = ["*"]
}

# =====================================================
# VPC Configuration (opcional)
# =====================================================

variable "vpc_config" {
  description = "Configuración de VPC para Lambda (opcional)"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

# =====================================================
# Logging and Monitoring
# =====================================================

variable "log_level" {
  description = "Nivel de logging"
  type        = string
  default     = "INFO"
}

variable "log_retention_days" {
  description = "Días de retención de logs en CloudWatch"
  type        = number
  default     = 7
}

variable "enable_alarms" {
  description = "Habilitar CloudWatch alarms"
  type        = bool
  default     = false
}

variable "alarm_sns_topic_arn" {
  description = "ARN del SNS topic para alarmas"
  type        = string
  default     = ""
}

# =====================================================
# Tags
# =====================================================

variable "tags" {
  description = "Tags para recursos"
  type        = map(string)
  default     = {}
}

