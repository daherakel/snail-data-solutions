# Outputs for Step Functions module

output "state_machine_name" {
  description = "Nombre de la Step Functions state machine"
  value       = aws_sfn_state_machine.document_processing.name
}

output "state_machine_arn" {
  description = "ARN de la Step Functions state machine"
  value       = aws_sfn_state_machine.document_processing.arn
}

output "state_machine_id" {
  description = "ID de la Step Functions state machine"
  value       = aws_sfn_state_machine.document_processing.id
}

output "log_group_name" {
  description = "Nombre del CloudWatch log group"
  value       = aws_cloudwatch_log_group.step_functions.name
}
