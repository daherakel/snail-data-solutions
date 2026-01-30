# Outputs for EventBridge module

output "event_rule_name" {
  description = "Nombre de la regla de EventBridge"
  value       = aws_cloudwatch_event_rule.s3_object_created.name
}

output "event_rule_arn" {
  description = "ARN de la regla de EventBridge"
  value       = aws_cloudwatch_event_rule.s3_object_created.arn
}
