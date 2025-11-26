# DynamoDB table for conversational sessions
resource "aws_dynamodb_table" "conversations" {
  name           = "${var.project_name}-${var.environment}-conversations"
  billing_mode   = "PAY_PER_REQUEST" # On-demand pricing for cost efficiency
  hash_key       = "conversation_id"
  range_key      = "message_id"

  attribute {
    name = "conversation_id"
    type = "S"
  }

  attribute {
    name = "message_id"
    type = "S"
  }

  attribute {
    name = "user_id"
    type = "S"
  }

  attribute {
    name = "updated_at"
    type = "N"
  }

  # GSI for listing user conversations sorted by recent activity
  global_secondary_index {
    name            = "UserConversationsIndex"
    hash_key        = "user_id"
    range_key       = "updated_at"
    projection_type = "ALL"
  }

  # TTL to auto-delete old conversations (90 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-conversations"
      Description = "Conversational sessions storage for AI assistant"
    }
  )
}
