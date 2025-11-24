# Outputs for IAM module

output "lambda_pdf_processor_role_arn" {
  description = "ARN del rol IAM para Lambda PDF processor"
  value       = aws_iam_role.lambda_pdf_processor.arn
}

output "lambda_pdf_processor_role_name" {
  description = "Nombre del rol IAM para Lambda PDF processor"
  value       = aws_iam_role.lambda_pdf_processor.name
}

output "lambda_query_handler_role_arn" {
  description = "ARN del rol IAM para Lambda query handler"
  value       = aws_iam_role.lambda_query_handler.arn
}

output "lambda_query_handler_role_name" {
  description = "Nombre del rol IAM para Lambda query handler"
  value       = aws_iam_role.lambda_query_handler.name
}

output "step_functions_role_arn" {
  description = "ARN del rol IAM para Step Functions"
  value       = aws_iam_role.step_functions.arn
}

output "step_functions_role_name" {
  description = "Nombre del rol IAM para Step Functions"
  value       = aws_iam_role.step_functions.name
}

output "eventbridge_role_arn" {
  description = "ARN del rol IAM para EventBridge"
  value       = aws_iam_role.eventbridge.arn
}

output "eventbridge_role_name" {
  description = "Nombre del rol IAM para EventBridge"
  value       = aws_iam_role.eventbridge.name
}
