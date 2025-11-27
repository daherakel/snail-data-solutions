# Variables for DEV environment

# =====================================================
# Project Configuration
# =====================================================

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "snail-bedrock"
}

variable "environment" {
  description = "Ambiente"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner del proyecto"
  type        = string
  default     = "Snail Data Solutions"
}

variable "cost_center" {
  description = "Centro de costos"
  type        = string
  default     = "AI-Agents"
}

# =====================================================
# S3 Configuration
# =====================================================

variable "enable_s3_versioning" {
  description = "Habilitar versionado en buckets"
  type        = bool
  default     = true
}

variable "enable_s3_lifecycle" {
  description = "Habilitar lifecycle rules (archivado a Glacier)"
  type        = bool
  default     = false  # Deshabilitado en dev
}

# =====================================================
# DynamoDB Configuration
# =====================================================

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PAY_PER_REQUEST or PROVISIONED)"
  type        = string
  default     = "PAY_PER_REQUEST"  # On-demand for variable workloads
}

variable "enable_rate_limiting" {
  description = "Habilitar tabla de rate limiting"
  type        = bool
  default     = true
}

variable "enable_dynamodb_pitr" {
  description = "Habilitar Point-in-Time Recovery para DynamoDB"
  type        = bool
  default     = true
}

variable "cache_ttl_days" {
  description = "Días para mantener cache de queries"
  type        = number
  default     = 7
}

variable "enable_query_cache" {
  description = "Habilitar caching de queries en query-handler"
  type        = bool
  default     = true
}

# =====================================================
# Lambda Configuration
# =====================================================

variable "pdf_processor_source_dir" {
  description = "Path al código de PDF processor"
  type        = string
  default     = "../../../../lambda-functions/pdf-processor"
}

variable "query_handler_source_dir" {
  description = "Path al código de query handler"
  type        = string
  default     = "../../../../lambda-functions/query-handler"
}

variable "pdf_processor_timeout" {
  description = "Timeout para PDF processor (segundos)"
  type        = number
  default     = 300  # 5 minutos
}

variable "pdf_processor_memory" {
  description = "Memoria para PDF processor (MB)"
  type        = number
  default     = 1024  # 1 GB
}

variable "query_handler_timeout" {
  description = "Timeout para query handler (segundos)"
  type        = number
  default     = 60
}

variable "query_handler_memory" {
  description = "Memoria para query handler (MB)"
  type        = number
  default     = 512
}

variable "create_chromadb_layer" {
  description = "Crear Lambda layer con ChromaDB"
  type        = bool
  default     = false  # Se crea manualmente primero
}

variable "chromadb_layer_path" {
  description = "Path al ZIP del layer de ChromaDB"
  type        = string
  default     = ""
}

# =====================================================
# Bedrock Configuration
# =====================================================

variable "bedrock_llm_model_id" {
  description = "Model ID de Bedrock para LLM"
  type        = string
  default     = "anthropic.claude-3-haiku-20240307-v1:0"  # Haiku para dev (más barato)
}

variable "max_context_chunks" {
  description = "Número máximo de chunks en el contexto"
  type        = number
  default     = 5
}

variable "max_history_messages" {
  description = "Número máximo de mensajes de historial conversacional a enviar"
  type        = number
  default     = 10
}

# =====================================================
# Logging Configuration
# =====================================================

variable "lambda_log_level" {
  description = "Nivel de logging para Lambda (DEBUG, INFO, WARNING, ERROR)"
  type        = string
  default     = "DEBUG"  # DEBUG en dev
}

variable "step_functions_log_level" {
  description = "Nivel de logging para Step Functions (ALL, ERROR, FATAL, OFF)"
  type        = string
  default     = "ALL"  # ALL en dev
}

variable "log_retention_days" {
  description = "Días de retención de logs"
  type        = number
  default     = 7
}

# =====================================================
# Monitoring Configuration
# =====================================================

variable "enable_xray" {
  description = "Habilitar AWS X-Ray"
  type        = bool
  default     = false  # Deshabilitado en dev para reducir costos
}

variable "create_cloudwatch_alarms" {
  description = "Crear alarmas de CloudWatch"
  type        = bool
  default     = false  # Deshabilitado en dev
}

# =====================================================
# Function URL Configuration
# =====================================================

variable "create_function_url" {
  description = "Crear Function URL para query handler"
  type        = bool
  default     = true  # Habilitado en dev para testing fácil
}
