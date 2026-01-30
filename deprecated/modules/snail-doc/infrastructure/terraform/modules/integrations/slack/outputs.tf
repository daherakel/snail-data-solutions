# Outputs for Slack Integration module

output "slack_handler_function_name" {
  description = "Nombre de la función Lambda Slack handler"
  value       = aws_lambda_function.slack_handler.function_name
}

output "slack_handler_function_arn" {
  description = "ARN de la función Lambda Slack handler"
  value       = aws_lambda_function.slack_handler.arn
}

output "slack_handler_function_url" {
  description = "URL de la función Lambda para recibir eventos de Slack"
  value       = var.create_function_url ? aws_lambda_function_url.slack_handler[0].function_url : null
}

output "slack_handler_invoke_arn" {
  description = "ARN para invocar la función Lambda"
  value       = aws_lambda_function.slack_handler.invoke_arn
}

output "cloudwatch_log_group_name" {
  description = "Nombre del log group de CloudWatch"
  value       = aws_cloudwatch_log_group.slack_handler.name
}

output "slack_webhook_url" {
  description = "URL del webhook para configurar en Slack (Function URL)"
  value       = var.create_function_url ? aws_lambda_function_url.slack_handler[0].function_url : null
}

