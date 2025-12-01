# Glue jobs
resource "aws_glue_job" "cdc" {
  name     = "CDC"
  role_arn = "arn:aws:iam::471112687668:role/AWSGlueServiceRoleDefault"
  command {
    name            = "glueetl"
    script_location = "s3://aws-glue-assets-471112687668-us-east-1/scripts/CDC.py"
    python_version  = "3"
  }
  default_arguments = {
    "--TempDir"                          = "s3://aws-glue-assets-471112687668-us-east-1/temporary/"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-glue-datacatalog"          = "true"
    "--enable-job-insights"              = "true"
    "--enable-metrics"                   = "true"
    "--enable-observability-metrics"     = "true"
    "--enable-spark-ui"                  = "true"
    "--extra-jars"                       = "s3://glue-snail-bucket/jars/s3-tables-catalog-for-iceberg-runtime-0.1.4.jar"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--job-language"                     = "python"
    "--spark-event-logs-path"            = "s3://aws-glue-assets-471112687668-us-east-1/sparkHistoryLogs/"
  }
  glue_version      = "5.0"
  number_of_workers = 10
  worker_type       = "G.1X"
  timeout           = 480
  max_retries       = 0
  execution_class   = "STANDARD"

  execution_property {
    max_concurrent_runs = 1
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [default_arguments, source_control_details, tags, tags_all]
  }
}

resource "aws_glue_job" "csv_to_tabla" {
  name     = "csv-to-tabla"
  role_arn = "arn:aws:iam::471112687668:role/AWSGlueServiceRoleDefault"
  command {
    name            = "glueetl"
    script_location = "s3://aws-glue-assets-471112687668-us-east-1/scripts/csv-to-tabla.py"
    python_version  = "3"
  }
  default_arguments = {
    "--TempDir"                          = "s3://aws-glue-assets-471112687668-us-east-1/temporary/"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-glue-datacatalog"          = "true"
    "--enable-job-insights"              = "true"
    "--enable-metrics"                   = "true"
    "--enable-observability-metrics"     = "true"
    "--enable-spark-ui"                  = "true"
    "--extra-jars"                       = "s3://glue-snail-bucket/jars/s3-tables-catalog-for-iceberg-runtime-0.1.4.jar"
    "--job-bookmark-option"              = "job-bookmark-disable"
    "--job-language"                     = "python"
    "--spark-event-logs-path"            = "s3://aws-glue-assets-471112687668-us-east-1/sparkHistoryLogs/"
  }
  glue_version      = "5.0"
  number_of_workers = 10
  worker_type       = "G.1X"
  timeout           = 480
  max_retries       = 0
  execution_class   = "STANDARD"

  execution_property {
    max_concurrent_runs = 1
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [default_arguments, source_control_details, tags, tags_all]
  }
}
