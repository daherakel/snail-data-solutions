# DynamoDB Module
# Creates DynamoDB tables for query caching and rate limiting

# =====================================================
# Query Cache Table
# =====================================================

resource "aws_dynamodb_table" "query_cache" {
  name           = "${var.project_name}-${var.environment}-query-cache"
  billing_mode   = var.billing_mode

  # On-Demand billing (recommended for variable workloads)
  # PAY_PER_REQUEST = No provisioned capacity, auto-scaling

  # If using PROVISIONED billing mode
  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  hash_key = "query_hash"

  attribute {
    name = "query_hash"
    type = "S"  # String - SHA256 hash of normalized query
  }

  # TTL for automatic expiration of cache entries
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  # Server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-query-cache"
      Description = "Query cache for AI agent responses"
    }
  )
}

# =====================================================
# Rate Limiting Table (Optional)
# =====================================================

resource "aws_dynamodb_table" "rate_limit" {
  count = var.enable_rate_limiting ? 1 : 0

  name           = "${var.project_name}-${var.environment}-rate-limit"
  billing_mode   = var.billing_mode

  read_capacity  = var.billing_mode == "PROVISIONED" ? var.read_capacity : null
  write_capacity = var.billing_mode == "PROVISIONED" ? var.write_capacity : null

  hash_key = "user_id"
  range_key = "window_timestamp"

  attribute {
    name = "user_id"
    type = "S"  # User identifier (IP, session ID, etc.)
  }

  attribute {
    name = "window_timestamp"
    type = "N"  # Timestamp of the rate limit window
  }

  # TTL for automatic cleanup of old rate limit entries
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = var.enable_point_in_time_recovery
  }

  # Server-side encryption
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn
  }

  tags = merge(
    var.tags,
    {
      Name        = "${var.project_name}-${var.environment}-rate-limit"
      Description = "Rate limiting tracking for API requests"
    }
  )
}

# =====================================================
# CloudWatch Alarms (Optional)
# =====================================================

resource "aws_cloudwatch_metric_alarm" "query_cache_read_throttle" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-query-cache-read-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ReadThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300  # 5 minutes
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors DynamoDB read throttle events"
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = aws_dynamodb_table.query_cache.name
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "query_cache_write_throttle" {
  count = var.create_alarms ? 1 : 0

  alarm_name          = "${var.project_name}-${var.environment}-query-cache-write-throttle"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = 300  # 5 minutes
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors DynamoDB write throttle events"
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = aws_dynamodb_table.query_cache.name
  }

  tags = var.tags
}
