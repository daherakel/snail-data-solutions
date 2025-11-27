# Outputs for DEV environment

# =====================================================
# S3 Buckets
# =====================================================

output "raw_documents_bucket" {
  description = "Nombre del bucket de documentos raw"
  value       = module.s3.raw_documents_bucket_name
}

output "processed_documents_bucket" {
  description = "Nombre del bucket de documentos procesados"
  value       = module.s3.processed_documents_bucket_name
}

output "chromadb_backup_bucket" {
  description = "Nombre del bucket de backups de ChromaDB"
  value       = module.s3.chromadb_backup_bucket_name
}

# =====================================================
# Lambda Functions
# =====================================================

output "pdf_processor_function_name" {
  description = "Nombre de la Lambda PDF processor"
  value       = module.lambda.pdf_processor_function_name
}

output "query_handler_function_name" {
  description = "Nombre de la Lambda query handler"
  value       = module.lambda.query_handler_function_name
}

output "query_handler_url" {
  description = "URL de la Lambda query handler (para testing)"
  value       = module.lambda.query_handler_function_url
}

# =====================================================
# Step Functions
# =====================================================

output "step_functions_name" {
  description = "Nombre de la Step Functions state machine"
  value       = module.step_functions.state_machine_name
}

output "step_functions_arn" {
  description = "ARN de la Step Functions state machine"
  value       = module.step_functions.state_machine_arn
}

# =====================================================
# EventBridge
# =====================================================

output "eventbridge_rule_name" {
  description = "Nombre de la regla de EventBridge"
  value       = module.eventbridge.event_rule_name
}

# =====================================================
# Quick Start Instructions
# =====================================================

output "quick_start" {
  description = "Instrucciones para empezar a usar el sistema"
  value       = <<-EOT

    ========================================
    AWS Bedrock Agents - DEV Environment
    ========================================

    📦 Upload de documentos:
       aws s3 cp tu-documento.pdf s3://${module.s3.raw_documents_bucket_name}/

    🔍 Query handler URL:
       ${module.lambda.query_handler_function_url != null ? module.lambda.query_handler_function_url : "No habilitada"}

    📊 Monitorear ejecuciones:
       aws stepfunctions list-executions --state-machine-arn ${module.step_functions.state_machine_arn}

    📝 Ver logs:
       Lambda PDF Processor: /aws/lambda/${module.lambda.pdf_processor_function_name}
       Lambda Query Handler: /aws/lambda/${module.lambda.query_handler_function_name}
       Step Functions: ${module.step_functions.log_group_name}

    ========================================
  EOT
}
