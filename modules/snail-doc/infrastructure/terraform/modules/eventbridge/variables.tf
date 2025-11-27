# Variables for EventBridge module

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "snail-bedrock"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "raw_documents_bucket_name" {
  description = "Nombre del bucket de documentos raw"
  type        = string
}

variable "step_functions_arn" {
  description = "ARN de la Step Function a ejecutar"
  type        = string
}

variable "eventbridge_role_arn" {
  description = "ARN del rol IAM para EventBridge"
  type        = string
}

variable "tags" {
  description = "Tags adicionales"
  type        = map(string)
  default     = {}
}
