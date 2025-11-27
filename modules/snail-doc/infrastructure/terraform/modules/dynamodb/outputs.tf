# DynamoDB Module Outputs

output "query_cache_table_name" {
  description = "Name of the query cache DynamoDB table"
  value       = aws_dynamodb_table.query_cache.name
}

output "query_cache_table_arn" {
  description = "ARN of the query cache DynamoDB table"
  value       = aws_dynamodb_table.query_cache.arn
}

output "query_cache_table_id" {
  description = "ID of the query cache DynamoDB table"
  value       = aws_dynamodb_table.query_cache.id
}

output "rate_limit_table_name" {
  description = "Name of the rate limit DynamoDB table"
  value       = var.enable_rate_limiting ? aws_dynamodb_table.rate_limit[0].name : null
}

output "rate_limit_table_arn" {
  description = "ARN of the rate limit DynamoDB table"
  value       = var.enable_rate_limiting ? aws_dynamodb_table.rate_limit[0].arn : null
}

output "rate_limit_table_id" {
  description = "ID of the rate limit DynamoDB table"
  value       = var.enable_rate_limiting ? aws_dynamodb_table.rate_limit[0].id : null
}

output "cache_ttl_seconds" {
  description = "Cache TTL in seconds"
  value       = var.cache_ttl_days * 24 * 60 * 60
}
