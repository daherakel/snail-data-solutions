# EventBridge Module
# Crea reglas de EventBridge para disparar el pipeline de procesamiento

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
# EventBridge Rule: S3 Object Created
# =====================================================

resource "aws_cloudwatch_event_rule" "s3_object_created" {
  name        = "${var.project_name}-${var.environment}-s3-object-created"
  description = "Detecta cuando se sube un nuevo documento a S3"

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [var.raw_documents_bucket_name]
      }
      object = {
        key = [
          {
            suffix = ".pdf"
          }
        ]
      }
    }
  })

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-s3-object-created"
      Environment = var.environment
    }
  )
}

# Target: Step Functions
resource "aws_cloudwatch_event_target" "step_functions" {
  rule      = aws_cloudwatch_event_rule.s3_object_created.name
  target_id = "TriggerStepFunctions"
  arn       = var.step_functions_arn
  role_arn  = var.eventbridge_role_arn

  input_transformer {
    input_paths = {
      bucket = "$.detail.bucket.name"
      key    = "$.detail.object.key"
      time   = "$.time"
    }

    input_template = <<EOF
{
  "bucket": <bucket>,
  "key": <key>,
  "timestamp": <time>,
  "environment": "${var.environment}"
}
EOF
  }
}

# =====================================================
# S3 Bucket Notification (EventBridge)
# =====================================================

resource "aws_s3_bucket_notification" "raw_documents" {
  bucket      = var.raw_documents_bucket_name
  eventbridge = true
}
