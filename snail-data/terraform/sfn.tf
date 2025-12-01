# Step Functions

resource "aws_sfn_state_machine" "snail_bedrock_dev_document_processing" {
  name     = "snail-bedrock-dev-document-processing"
  role_arn = "arn:aws:iam::471112687668:role/snail-bedrock-dev-step-functions"

  definition = file("${path.module}/reference/sfn/definitions/snail-bedrock-dev-document-processing.asl.json")

  logging_configuration {
    include_execution_data = true
    level                  = "ALL"
    log_destination        = "arn:aws:logs:us-east-1:471112687668:log-group:/aws/states/snail-bedrock-dev-document-processing:*"
  }

  tracing_configuration {
    enabled = false
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [definition, tags, tags_all, logging_configuration]
  }
}
