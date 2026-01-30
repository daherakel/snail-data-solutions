# Slack Integration Module
# Crea Lambda function y Function URL para integración con Slack

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
# Lambda: Slack Handler
# =====================================================

# Empaquetar código de Slack handler
data "archive_file" "slack_handler" {
  type        = "zip"
  source_dir  = var.slack_handler_source_dir
  output_path = "${path.module}/.terraform/slack-handler.zip"
  
  excludes = [
    "__pycache__",
    "*.pyc",
    ".git",
    "*.zip"
  ]
}

resource "aws_lambda_function" "slack_handler" {
  filename         = data.archive_file.slack_handler.output_path
  function_name    = "${var.project_name}-${var.environment}-slack-handler"
  role            = var.lambda_slack_handler_role_arn
  handler         = "handler.lambda_handler"
  source_code_hash = data.archive_file.slack_handler.output_base64sha256
  runtime         = "python3.11"

  timeout     = var.slack_handler_timeout
  memory_size = var.slack_handler_memory

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      PROJECT_NAME             = var.project_name
      QUERY_HANDLER_FUNCTION   = var.query_handler_function_name
      SLACK_BOT_TOKEN          = var.slack_bot_token_secret_arn != "" ? null : var.slack_bot_token
      SLACK_SIGNING_SECRET     = var.slack_signing_secret_secret_arn != "" ? null : var.slack_signing_secret
      VERIFY_SLACK_SIGNATURE   = var.verify_slack_signature ? "true" : "false"
      LOG_LEVEL                = var.log_level
      AWS_REGION               = var.aws_region
    }
  }

  # Si se usan Secrets Manager, agregar política para leer secrets
  dynamic "vpc_config" {
    for_each = var.vpc_config != null ? [var.vpc_config] : []
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-slack-handler"
      Environment = var.environment
      Function    = "Slack integration handler"
      Integration = "slack"
    }
  )
}

# CloudWatch Log Group para Slack Handler
resource "aws_cloudwatch_log_group" "slack_handler" {
  name              = "/aws/lambda/${aws_lambda_function.slack_handler.function_name}"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-slack-handler-logs"
      Environment = var.environment
    }
  )
}

# =====================================================
# Lambda Function URL (para recibir eventos de Slack)
# =====================================================

resource "aws_lambda_function_url" "slack_handler" {
  count = var.create_function_url ? 1 : 0

  function_name      = aws_lambda_function.slack_handler.function_name
  authorization_type = "NONE"  # Slack verifica con signing secret

  cors {
    allow_origins      = var.cors_allowed_origins
    allow_methods      = ["POST"]
    allow_headers      = ["content-type", "x-slack-signature", "x-slack-request-timestamp"]
    expose_headers     = []
    max_age            = 300
    allow_credentials  = false
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-slack-handler-url"
      Environment = var.environment
    }
  )
}

# =====================================================
# IAM Policy para leer Secrets Manager (si se usan)
# =====================================================

resource "aws_iam_role_policy" "slack_handler_secrets" {
  count = var.slack_bot_token_secret_arn != "" || var.slack_signing_secret_secret_arn != "" ? 1 : 0

  name = "${var.project_name}-${var.environment}-slack-handler-secrets-policy"
  role = var.lambda_slack_handler_role_arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = compact([
          var.slack_bot_token_secret_arn,
          var.slack_signing_secret_secret_arn
        ])
      }
    ]
  })
}

# =====================================================
# CloudWatch Alarms (opcional)
# =====================================================

resource "aws_cloudwatch_metric_alarm" "slack_handler_errors" {
  count = var.enable_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-slack-handler-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Alert when Slack handler has errors"
  alarm_actions       = var.alarm_sns_topic_arn != "" ? [var.alarm_sns_topic_arn] : []

  dimensions = {
    FunctionName = aws_lambda_function.slack_handler.function_name
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-slack-handler-errors-alarm"
      Environment = var.environment
    }
  )
}

