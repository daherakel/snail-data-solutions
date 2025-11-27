# Variables for S3 module

variable "project_name" {
  description = "Nombre del proyecto (usado en nombres de recursos)"
  type        = string
  default     = "snail-bedrock"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment debe ser dev, staging o prod"
  }
}

variable "tags" {
  description = "Tags adicionales para todos los recursos"
  type        = map(string)
  default     = {}
}

variable "enable_versioning" {
  description = "Habilitar versionado en bucket de raw documents"
  type        = bool
  default     = true
}

variable "enable_lifecycle_rules" {
  description = "Habilitar reglas de lifecycle (archivado a Glacier)"
  type        = bool
  default     = false
}
