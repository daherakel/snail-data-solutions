# Variables for IAM module

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

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

variable "raw_documents_bucket_arn" {
  description = "ARN del bucket de documentos raw"
  type        = string
}

variable "processed_documents_bucket_arn" {
  description = "ARN del bucket de documentos procesados"
  type        = string
}

variable "chromadb_backup_bucket_arn" {
  description = "ARN del bucket de backups de ChromaDB"
  type        = string
}

variable "query_cache_table_arn" {
  description = "ARN de la tabla DynamoDB para cache de queries"
  type        = string
}

variable "rate_limit_table_arn" {
  description = "ARN de la tabla DynamoDB para rate limiting"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags adicionales"
  type        = map(string)
  default     = {}
}
