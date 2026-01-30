variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "us-east-1"
}

variable "bucket_name" {
  type        = string
  description = "Nombre unico global del bucket S3"
  default     = "bucket-poc-1-snail-data"
}

variable "tags" {
  type        = map(string)
  description = "Tags opcionales"
  default     = {}
}
