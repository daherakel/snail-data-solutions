# DynamoDB Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
}

variable "billing_mode" {
  description = "DynamoDB billing mode: PAY_PER_REQUEST or PROVISIONED"
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.billing_mode)
    error_message = "Billing mode must be either PAY_PER_REQUEST or PROVISIONED"
  }
}

variable "read_capacity" {
  description = "Read capacity units (only used if billing_mode is PROVISIONED)"
  type        = number
  default     = 5
}

variable "write_capacity" {
  description = "Write capacity units (only used if billing_mode is PROVISIONED)"
  type        = number
  default     = 5
}

variable "enable_point_in_time_recovery" {
  description = "Enable point-in-time recovery for data protection"
  type        = bool
  default     = true
}

variable "kms_key_arn" {
  description = "ARN of KMS key for server-side encryption. If null, uses AWS managed key."
  type        = string
  default     = null
}

variable "enable_rate_limiting" {
  description = "Whether to create the rate limiting table"
  type        = bool
  default     = true
}

variable "create_alarms" {
  description = "Whether to create CloudWatch alarms for the tables"
  type        = bool
  default     = true
}

variable "cache_ttl_days" {
  description = "Number of days to keep cache entries before expiration"
  type        = number
  default     = 7

  validation {
    condition     = var.cache_ttl_days > 0 && var.cache_ttl_days <= 30
    error_message = "Cache TTL must be between 1 and 30 days"
  }
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
