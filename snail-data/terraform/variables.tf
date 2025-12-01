variable "aws_region" {
  type        = string
  description = "AWS region for imports"
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  description = "AWS CLI/SDK profile to use"
  default     = "default"
}

variable "environment" {
  type        = string
  description = "Environment label for tagging (dev/stage/prod)"
  default     = "dev"
}

