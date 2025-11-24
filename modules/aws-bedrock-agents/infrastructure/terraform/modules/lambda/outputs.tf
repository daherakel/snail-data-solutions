# Outputs for Lambda module

# =====================================================
# Lambda Layer
# =====================================================

output "chromadb_layer_arn" {
  description = "ARN del Lambda layer de ChromaDB"
  value       = var.create_chromadb_layer ? aws_lambda_layer_version.chromadb[0].arn : null
}

output "chromadb_layer_version" {
  description = "Versión del Lambda layer de ChromaDB"
  value       = var.create_chromadb_layer ? aws_lambda_layer_version.chromadb[0].version : null
}

# =====================================================
# PDF Processor Lambda
# =====================================================

output "pdf_processor_function_name" {
  description = "Nombre de la función Lambda PDF processor"
  value       = aws_lambda_function.pdf_processor.function_name
}

output "pdf_processor_function_arn" {
  description = "ARN de la función Lambda PDF processor"
  value       = aws_lambda_function.pdf_processor.arn
}

output "pdf_processor_invoke_arn" {
  description = "ARN para invocar la función Lambda PDF processor"
  value       = aws_lambda_function.pdf_processor.invoke_arn
}

# =====================================================
# Query Handler Lambda
# =====================================================

output "query_handler_function_name" {
  description = "Nombre de la función Lambda query handler"
  value       = aws_lambda_function.query_handler.function_name
}

output "query_handler_function_arn" {
  description = "ARN de la función Lambda query handler"
  value       = aws_lambda_function.query_handler.arn
}

output "query_handler_invoke_arn" {
  description = "ARN para invocar la función Lambda query handler"
  value       = aws_lambda_function.query_handler.invoke_arn
}

output "query_handler_function_url" {
  description = "URL de la función Lambda query handler (si está habilitada)"
  value       = var.create_function_url ? aws_lambda_function_url.query_handler[0].function_url : null
}
