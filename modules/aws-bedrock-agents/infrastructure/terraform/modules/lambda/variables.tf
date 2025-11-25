# Variables for Lambda module

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "snail-bedrock"
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
# Lambda Roles
# =====================================================

variable "lambda_pdf_processor_role_arn" {
  description = "ARN del rol IAM para Lambda PDF processor"
  type        = string
}

variable "lambda_query_handler_role_arn" {
  description = "ARN del rol IAM para Lambda query handler"
  type        = string
}

# =====================================================
# S3 Buckets
# =====================================================

variable "raw_documents_bucket_name" {
  description = "Nombre del bucket de documentos raw"
  type        = string
}

variable "processed_documents_bucket_name" {
  description = "Nombre del bucket de documentos procesados"
  type        = string
}

variable "chromadb_backup_bucket_name" {
  description = "Nombre del bucket de backups de ChromaDB"
  type        = string
}

# =====================================================
# Lambda Layer
# =====================================================

variable "create_chromadb_layer" {
  description = "Crear Lambda layer con ChromaDB"
  type        = bool
  default     = true
}

variable "chromadb_layer_path" {
  description = "Path al archivo ZIP del layer de ChromaDB"
  type        = string
  default     = ""
}

# =====================================================
# Lambda Functions - Source
# =====================================================

variable "pdf_processor_source_dir" {
  description = "Directorio con código de PDF processor"
  type        = string
}

variable "query_handler_source_dir" {
  description = "Directorio con código de query handler"
  type        = string
}

# =====================================================
# Lambda Functions - Configuration
# =====================================================

variable "pdf_processor_timeout" {
  description = "Timeout para PDF processor Lambda (segundos)"
  type        = number
  default     = 300  # 5 minutos
}

variable "pdf_processor_memory" {
  description = "Memoria para PDF processor Lambda (MB)"
  type        = number
  default     = 1024  # 1 GB
}

variable "query_handler_timeout" {
  description = "Timeout para query handler Lambda (segundos)"
  type        = number
  default     = 60
}

variable "query_handler_memory" {
  description = "Memoria para query handler Lambda (MB)"
  type        = number
  default     = 512
}

# =====================================================
# Bedrock Configuration
# =====================================================

variable "bedrock_llm_model_id" {
  description = "Model ID de Bedrock para LLM (Claude)"
  type        = string
  default     = "anthropic.claude-3-haiku-20240307-v1:0"
}

variable "max_context_chunks" {
  description = "Número máximo de chunks a incluir en el contexto"
  type        = number
  default     = 5
}

# =====================================================
# DynamoDB Cache Configuration
# =====================================================

variable "query_cache_table_name" {
  description = "Nombre de la tabla DynamoDB para cache de queries"
  type        = string
}

variable "cache_ttl_seconds" {
  description = "Tiempo de vida del cache en segundos"
  type        = number
}

variable "enable_query_cache" {
  description = "Habilitar caching de queries"
  type        = bool
  default     = true
}

# =====================================================
# Logging
# =====================================================

variable "log_level" {
  description = "Nivel de logging (DEBUG, INFO, WARNING, ERROR)"
  type        = string
  default     = "INFO"
}

variable "log_retention_days" {
  description = "Días de retención de logs en CloudWatch"
  type        = number
  default     = 7
}

# =====================================================
# Function URL
# =====================================================

variable "create_function_url" {
  description = "Crear Function URL para query handler"
  type        = bool
  default     = false
}

# =====================================================
# Tags
# =====================================================

variable "tags" {
  description = "Tags adicionales"
  type        = map(string)
  default     = {}
}
