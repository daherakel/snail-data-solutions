# Variables for Step Functions module

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "snail-bedrock"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
}

variable "step_functions_role_arn" {
  description = "ARN del rol IAM para Step Functions"
  type        = string
}

variable "pdf_processor_lambda_arn" {
  description = "ARN de la Lambda para procesar PDFs"
  type        = string
}

variable "log_level" {
  description = "Nivel de logging para Step Functions (ALL, ERROR, FATAL, OFF)"
  type        = string
  default     = "ERROR"
}

variable "log_retention_days" {
  description = "Días de retención de logs en CloudWatch"
  type        = number
  default     = 7
}

variable "enable_xray" {
  description = "Habilitar AWS X-Ray tracing"
  type        = bool
  default     = false
}

variable "create_alarms" {
  description = "Crear alarmas de CloudWatch"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Tags adicionales"
  type        = map(string)
  default     = {}
}
