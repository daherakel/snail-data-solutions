# Step Functions Module
# Crea la state machine para orquestar el procesamiento de documentos

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
# Step Functions State Machine
# =====================================================

resource "aws_sfn_state_machine" "document_processing" {
  name     = "${var.project_name}-${var.environment}-document-processing"
  role_arn = var.step_functions_role_arn

  definition = jsonencode({
    Comment = "Workflow para procesar documentos y generar embeddings"
    StartAt = "ProcessDocument"
    States = {
      ProcessDocument = {
        Type     = "Task"
        Resource = var.pdf_processor_lambda_arn
        Comment  = "Procesa el PDF y genera embeddings con ChromaDB"

        Parameters = {
          "bucket.$" = "$.bucket"
          "key.$"    = "$.key"
        }

        Retry = [
          {
            ErrorEquals = [
              "Lambda.ServiceException",
              "Lambda.AWSLambdaException",
              "Lambda.SdkClientException",
              "Lambda.TooManyRequestsException"
            ]
            IntervalSeconds = 2
            MaxAttempts     = 3
            BackoffRate     = 2
          }
        ]

        Catch = [
          {
            ErrorEquals = ["States.ALL"]
            Next        = "ProcessingFailed"
            ResultPath  = "$.error"
          }
        ]

        Next = "ProcessingSucceeded"
      }

      ProcessingSucceeded = {
        Type = "Succeed"
        Comment = "Documento procesado exitosamente"
      }

      ProcessingFailed = {
        Type = "Fail"
        Comment = "Fallo en el procesamiento del documento"
        Error = "ProcessingError"
        Cause = "Error al procesar el documento con Lambda"
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.step_functions.arn}:*"
    include_execution_data = true
    level                  = var.log_level
  }

  tracing_configuration {
    enabled = var.enable_xray
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-document-processing"
      Environment = var.environment
      Purpose     = "Document processing workflow"
    }
  )
}

# =====================================================
# CloudWatch Log Group
# =====================================================

resource "aws_cloudwatch_log_group" "step_functions" {
  name              = "/aws/states/${var.project_name}-${var.environment}-document-processing"
  retention_in_days = var.log_retention_days

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-step-functions-logs"
      Environment = var.environment
    }
  )
}

# =====================================================
# CloudWatch Alarms (opcional)
# =====================================================

resource "aws_cloudwatch_metric_alarm" "execution_failed" {
  count               = var.create_alarms ? 1 : 0
  alarm_name          = "${var.project_name}-${var.environment}-step-functions-failed"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ExecutionsFailed"
  namespace           = "AWS/States"
  period              = "300"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "Alerta cuando falla una ejecución de Step Functions"
  treat_missing_data  = "notBreaching"

  dimensions = {
    StateMachineArn = aws_sfn_state_machine.document_processing.arn
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-step-functions-alarm"
      Environment = var.environment
    }
  )
}
