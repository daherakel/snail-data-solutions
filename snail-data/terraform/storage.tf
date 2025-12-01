# Storage (S3)

resource "aws_s3_bucket" "s3_snail_bedrock_dev_raw_documents" {
  bucket = "snail-bedrock-dev-raw-documents"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_bedrock_dev_processed_documents" {
  bucket = "snail-bedrock-dev-processed-documents"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_bedrock_dev_chromadb_backup" {
  bucket = "snail-bedrock-dev-chromadb-backup"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_athena_output" {
  bucket = "snail-athena-output"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_landing" {
  bucket = "s3-snail-landing"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_lambda_layers" {
  bucket = "snail-lambda-layers-1763961583"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_snail_rds_snapshots" {
  bucket = "snail-rds-snapshots"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_glue_snail_bucket" {
  bucket = "glue-snail-bucket"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_knowledge_base_snail" {
  bucket = "knowledge-base-snail"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_ahh_audio_bucket" {
  bucket = "ahh-audio-bucket"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_ahh_healthscribe_output" {
  bucket = "ahh-healthscribe-output"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_ahh_transcribe_demo" {
  bucket = "ahh-transcribe-demo"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_amazon_sagemaker_assets" {
  bucket = "amazon-sagemaker-471112687668-us-east-1-49dadeb59b4a"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_aws_glue_assets" {
  bucket = "aws-glue-assets-471112687668-us-east-1"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_dycom_poc" {
  bucket = "dycom-poc"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket" "s3_amplify_backend_dev" {
  provider = aws.use2
  bucket   = "amplify-backend-dev-98473-deployment"

  lifecycle {
    prevent_destroy = true
  }
}
