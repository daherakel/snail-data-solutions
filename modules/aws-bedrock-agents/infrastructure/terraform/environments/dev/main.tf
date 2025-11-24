# Main Terraform configuration for DEV environment
# Conecta todos los módulos para crear la infraestructura completa

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# =====================================================
# Data Sources
# =====================================================

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# =====================================================
# Local Variables
# =====================================================

locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  aws_region     = data.aws_region.current.name

  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
}

# =====================================================
# S3 Buckets Module
# =====================================================

module "s3" {
  source = "../../modules/s3"

  project_name            = var.project_name
  environment             = var.environment
  enable_versioning       = var.enable_s3_versioning
  enable_lifecycle_rules  = var.enable_s3_lifecycle
  tags                    = local.common_tags
}

# =====================================================
# IAM Roles Module
# =====================================================

module "iam" {
  source = "../../modules/iam"

  project_name                    = var.project_name
  environment                     = var.environment
  aws_region                      = local.aws_region
  aws_account_id                  = local.aws_account_id
  raw_documents_bucket_arn        = module.s3.raw_documents_bucket_arn
  processed_documents_bucket_arn  = module.s3.processed_documents_bucket_arn
  chromadb_backup_bucket_arn      = module.s3.chromadb_backup_bucket_arn
  tags                            = local.common_tags
}

# =====================================================
# Lambda Functions Module
# =====================================================

module "lambda" {
  source = "../../modules/lambda"

  project_name                    = var.project_name
  environment                     = var.environment
  aws_region                      = local.aws_region

  # IAM Roles
  lambda_pdf_processor_role_arn   = module.iam.lambda_pdf_processor_role_arn
  lambda_query_handler_role_arn   = module.iam.lambda_query_handler_role_arn

  # S3 Buckets
  raw_documents_bucket_name       = module.s3.raw_documents_bucket_name
  processed_documents_bucket_name = module.s3.processed_documents_bucket_name
  chromadb_backup_bucket_name     = module.s3.chromadb_backup_bucket_name

  # Lambda Source Directories
  pdf_processor_source_dir        = var.pdf_processor_source_dir
  query_handler_source_dir        = var.query_handler_source_dir

  # Lambda Configuration
  pdf_processor_timeout           = var.pdf_processor_timeout
  pdf_processor_memory            = var.pdf_processor_memory
  query_handler_timeout           = var.query_handler_timeout
  query_handler_memory            = var.query_handler_memory

  # Bedrock Configuration
  bedrock_llm_model_id            = var.bedrock_llm_model_id
  max_context_chunks              = var.max_context_chunks

  # Layer
  create_chromadb_layer           = var.create_chromadb_layer
  chromadb_layer_path             = var.chromadb_layer_path

  # Logging
  log_level                       = var.lambda_log_level
  log_retention_days              = var.log_retention_days

  # Function URL
  create_function_url             = var.create_function_url

  tags = local.common_tags
}

# =====================================================
# Step Functions Module
# =====================================================

module "step_functions" {
  source = "../../modules/step-functions"

  project_name               = var.project_name
  environment                = var.environment
  step_functions_role_arn    = module.iam.step_functions_role_arn
  pdf_processor_lambda_arn   = module.lambda.pdf_processor_invoke_arn
  log_level                  = var.step_functions_log_level
  log_retention_days         = var.log_retention_days
  enable_xray                = var.enable_xray
  create_alarms              = var.create_cloudwatch_alarms
  tags                       = local.common_tags
}

# =====================================================
# EventBridge Module
# =====================================================

module "eventbridge" {
  source = "../../modules/eventbridge"

  project_name                = var.project_name
  environment                 = var.environment
  raw_documents_bucket_name   = module.s3.raw_documents_bucket_name
  step_functions_arn          = module.step_functions.state_machine_arn
  eventbridge_role_arn        = module.iam.eventbridge_role_arn
  tags                        = local.common_tags
}
