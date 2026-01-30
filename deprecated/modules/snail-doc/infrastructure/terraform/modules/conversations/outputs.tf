output "table_name" {
  description = "Name of the DynamoDB conversations table"
  value       = aws_dynamodb_table.conversations.name
}

output "table_arn" {
  description = "ARN of the DynamoDB conversations table"
  value       = aws_dynamodb_table.conversations.arn
}

output "gsi_name" {
  description = "Name of the UserConversations GSI"
  value       = "UserConversationsIndex"
}
