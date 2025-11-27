# S3 Buckets Module
# Crea buckets para documentos raw, processed y ChromaDB backups

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Bucket para documentos raw (subidos por el usuario)
resource "aws_s3_bucket" "raw_documents" {
  bucket = "${var.project_name}-${var.environment}-raw-documents"

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-raw-documents"
      Environment = var.environment
      Purpose     = "Raw document storage"
    }
  )
}

# Bucket para documentos procesados (embeddings listos)
resource "aws_s3_bucket" "processed_documents" {
  bucket = "${var.project_name}-${var.environment}-processed-documents"

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-processed-documents"
      Environment = var.environment
      Purpose     = "Processed document storage"
    }
  )
}

# Bucket para backups de ChromaDB
resource "aws_s3_bucket" "chromadb_backup" {
  bucket = "${var.project_name}-${var.environment}-chromadb-backup"

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-chromadb-backup"
      Environment = var.environment
      Purpose     = "ChromaDB vector store backups"
    }
  )
}

# Versionado para ChromaDB backups (importante para rollback)
resource "aws_s3_bucket_versioning" "chromadb_backup" {
  bucket = aws_s3_bucket.chromadb_backup.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Versionado para raw documents (opcional pero recomendado)
resource "aws_s3_bucket_versioning" "raw_documents" {
  bucket = aws_s3_bucket.raw_documents.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

# Encriptación server-side para todos los buckets
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_documents" {
  bucket = aws_s3_bucket.raw_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_documents" {
  bucket = aws_s3_bucket.processed_documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "chromadb_backup" {
  bucket = aws_s3_bucket.chromadb_backup.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bloquear acceso público (seguridad)
resource "aws_s3_bucket_public_access_block" "raw_documents" {
  bucket = aws_s3_bucket.raw_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_documents" {
  bucket = aws_s3_bucket.processed_documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "chromadb_backup" {
  bucket = aws_s3_bucket.chromadb_backup.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy para ChromaDB backups (retener solo últimas 10 versiones)
resource "aws_s3_bucket_lifecycle_configuration" "chromadb_backup" {
  bucket = aws_s3_bucket.chromadb_backup.id

  rule {
    id     = "cleanup-old-versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
      newer_noncurrent_versions = 10
    }
  }

  rule {
    id     = "delete-incomplete-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Lifecycle policy para raw documents (opcional - mover a Glacier después de 90 días)
resource "aws_s3_bucket_lifecycle_configuration" "raw_documents" {
  count  = var.enable_lifecycle_rules ? 1 : 0
  bucket = aws_s3_bucket.raw_documents.id

  rule {
    id     = "archive-old-documents"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "delete-incomplete-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
