output "bucket_name" {
  description = "Nombre del bucket"
  value       = aws_s3_bucket.poc.bucket
}

output "bucket_arn" {
  description = "ARN del bucket"
  value       = aws_s3_bucket.poc.arn
}
