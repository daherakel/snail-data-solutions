# Outputs for S3 module

output "raw_documents_bucket_name" {
  description = "Nombre del bucket de documentos raw"
  value       = aws_s3_bucket.raw_documents.id
}

output "raw_documents_bucket_arn" {
  description = "ARN del bucket de documentos raw"
  value       = aws_s3_bucket.raw_documents.arn
}

output "processed_documents_bucket_name" {
  description = "Nombre del bucket de documentos procesados"
  value       = aws_s3_bucket.processed_documents.id
}

output "processed_documents_bucket_arn" {
  description = "ARN del bucket de documentos procesados"
  value       = aws_s3_bucket.processed_documents.arn
}

output "chromadb_backup_bucket_name" {
  description = "Nombre del bucket de backups de ChromaDB"
  value       = aws_s3_bucket.chromadb_backup.id
}

output "chromadb_backup_bucket_arn" {
  description = "ARN del bucket de backups de ChromaDB"
  value       = aws_s3_bucket.chromadb_backup.arn
}
