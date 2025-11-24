# Lambda Module
# Crea Lambda functions y layers para el procesamiento de documentos

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }
}

# =====================================================
# Lambda Layer: ChromaDB + dependencies
# =====================================================

resource "aws_lambda_layer_version" "chromadb" {
  count               = var.create_chromadb_layer ? 1 : 0
  filename            = var.chromadb_layer_path
  layer_name          = "${var.project_name}-${var.environment}-chromadb-layer"
  compatible_runtimes = ["python3.11", "python3.12"]

  description = "ChromaDB vector database + PyPDF2 + boto3"

  # Solo crear si el archivo existe
  lifecycle {
    create_before_destroy = true
  }
}

# =====================================================
# Lambda: PDF Processor
# =====================================================

# Empaquetar código de PDF processor
data "archive_file" "pdf_processor" {
  type        = "zip"
  source_dir  = var.pdf_processor_source_dir
  output_path = "${path.module}/.terraform/pdf-processor.zip"
}

resource "aws_lambda_function" "pdf_processor" {
  filename         = data.archive_file.pdf_processor.output_path
  function_name    = "${var.project_name}-${var.environment}-pdf-processor"
  role            = var.lambda_pdf_processor_role_arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.pdf_processor.output_base64sha256
  runtime         = "python3.11"

  timeout     = var.pdf_processor_timeout
  memory_size = var.pdf_processor_memory

  layers = var.create_chromadb_layer ? [aws_lambda_layer_version.chromadb[0].arn] : []

  environment {
    variables = {
      ENVIRONMENT                = var.environment
      RAW_BUCKET                 = var.raw_documents_bucket_name
      PROCESSED_BUCKET           = var.processed_documents_bucket_name
      CHROMADB_BACKUP_BUCKET     = var.chromadb_backup_bucket_name
      CHROMADB_BACKUP_KEY        = "chromadb_data.tar.gz"
      BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
      AWS_REGION                 = var.aws_region
      LOG_LEVEL                  = var.log_level
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-pdf-processor"
      Environment = var.environment
      Function    = "PDF document processing and embedding"
    }
  )
}

# CloudWatch Log Group para PDF Processor
resource "aws_cloudwatch_log_group" "pdf_processor" {
  name              = "/aws/lambda/${aws_lambda_function.pdf_processor.function_name}"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-pdf-processor-logs"
      Environment = var.environment
    }
  )
}

# =====================================================
# Lambda: Query Handler
# =====================================================

# Empaquetar código de Query handler
data "archive_file" "query_handler" {
  type        = "zip"
  source_dir  = var.query_handler_source_dir
  output_path = "${path.module}/.terraform/query-handler.zip"
}

resource "aws_lambda_function" "query_handler" {
  filename         = data.archive_file.query_handler.output_path
  function_name    = "${var.project_name}-${var.environment}-query-handler"
  role            = var.lambda_query_handler_role_arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.query_handler.output_base64sha256
  runtime         = "python3.11"

  timeout     = var.query_handler_timeout
  memory_size = var.query_handler_memory

  layers = var.create_chromadb_layer ? [aws_lambda_layer_version.chromadb[0].arn] : []

  environment {
    variables = {
      ENVIRONMENT                = var.environment
      CHROMADB_BACKUP_BUCKET     = var.chromadb_backup_bucket_name
      CHROMADB_BACKUP_KEY        = "chromadb_data.tar.gz"
      BEDROCK_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v1"
      BEDROCK_LLM_MODEL_ID       = var.bedrock_llm_model_id
      AWS_REGION                 = var.aws_region
      LOG_LEVEL                  = var.log_level
      MAX_CONTEXT_CHUNKS         = var.max_context_chunks
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-query-handler"
      Environment = var.environment
      Function    = "Query processing and RAG response generation"
    }
  )
}

# CloudWatch Log Group para Query Handler
resource "aws_cloudwatch_log_group" "query_handler" {
  name              = "/aws/lambda/${aws_lambda_function.query_handler.function_name}"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-query-handler-logs"
      Environment = var.environment
    }
  )
}

# =====================================================
# Lambda Function URL para Query Handler (opcional)
# =====================================================

resource "aws_lambda_function_url" "query_handler" {
  count              = var.create_function_url ? 1 : 0
  function_name      = aws_lambda_function.query_handler.function_name
  authorization_type = "NONE"  # Cambiar a "AWS_IAM" para requerir autenticación

  cors {
    allow_credentials = true
    allow_origins     = ["*"]
    allow_methods     = ["POST"]
    allow_headers     = ["*"]
    max_age          = 86400
  }
}
