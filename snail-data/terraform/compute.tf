# Lambda functions (us-east-1)
resource "aws_lambda_function" "ahh_authorizer" {
  function_name    = "AHH_Authorizer"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_Authorizer-role-bjvxzkht"
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]
  environment {
    variables = {
      "SECRET_NAME" = "ahh-api-token"
    }
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "ahh_generate_clinical_notes" {
  function_name    = "AHH_GENERATE_CLINICAL_NOTES"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "ahh_get_mp3" {
  function_name    = "AHH_GET_MP3"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_helloworld-role-rrabedl8"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}

resource "aws_lambda_function" "ahh_gettranscription" {
  function_name    = "AHH_GetTranscription"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_GetTranscription-role-8tiisd9a"
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "ahh_init_process" {
  function_name    = "AHH_INIT_PROCESS"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_helloworld-role-rrabedl8"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "ahh_process_mp3" {
  function_name    = "AHH_PROCESS_MP3"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_helloworld-role-rrabedl8"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 300
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}

resource "aws_lambda_function" "ahh_save_mp3" {
  function_name    = "AHH_SAVE_MP3"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "ahh_helloworld" {
  function_name    = "AHH_helloworld"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_helloworld-role-rrabedl8"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 30
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "contactvendedortest" {
  function_name    = "ContactVendedorTest"
  role             = "arn:aws:iam::471112687668:role/service-role/ContactVendedorTest-role-t1s90cht"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}

resource "aws_lambda_function" "get_agent_response" {
  function_name    = "GET_AGENT_RESPONSE"
  role             = "arn:aws:iam::471112687668:role/service-role/NLQ-Lambda-role-aw2u47g0"
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "iphone_store_poc" {
  function_name    = "Iphone-store-poc"
  role             = "arn:aws:iam::471112687668:role/service-role/AHH_GENERATE_CLINICAL_NOTES-role-2w9ey1r1"
  runtime          = "python3.12"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "nlq_lambda" {
  function_name    = "NLQ-Lambda"
  role             = "arn:aws:iam::471112687668:role/service-role/NLQ-Lambda-role-aw2u47g0"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}

resource "aws_lambda_function" "nql_lambda_10" {
  function_name    = "NQL-lambda-10"
  role             = "arn:aws:iam::471112687668:role/service-role/NLQ-Lambda-role-aw2u47g0"
  runtime          = "python3.10"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 120
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:phonenumbers_layer:2"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "nql_lambda_aws_api_calls" {
  function_name    = "NQL-lambda-AWS-API-calls"
  role             = "arn:aws:iam::471112687668:role/service-role/NLQ-Lambda-role-aw2u47g0"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 120
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python313:1", "arn:aws:lambda:us-east-1:471112687668:layer:boto3_upgrade:1"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "triggergluejobfroms3" {
  function_name    = "TriggerGlueJobFromS3"
  role             = "arn:aws:iam::471112687668:role/service-role/TriggerGlueJobFromS3-role-np6o3g9d"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}

resource "aws_lambda_function" "ahh_generate_notes_function" {
  function_name    = "ahh_generate_notes_function"
  role             = "arn:aws:iam::471112687668:role/service-role/ahh_generate_notes_function-role-pgg4o24k"
  runtime          = "python3.13"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 3
  memory_size      = 128
  architectures    = ["x86_64"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size
    ]
  }
}

resource "aws_lambda_function" "contact_vendedor_qgvaw" {
  function_name    = "contact_vendedor-qgvaw"
  role             = "arn:aws:iam::471112687668:role/service-role/contact_vendedor-qgvaw-role-DZ1QYRY2XBQ"
  runtime          = "python3.12"
  handler          = "dummy_lambda.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:gspread-layer:1"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size
    ]
  }
}

resource "aws_lambda_function" "ibold_price_detector" {
  function_name    = "ibold-price-detector"
  role             = "arn:aws:iam::471112687668:role/service-role/contact_vendedor-qgvaw-role-DZ1QYRY2XBQ"
  runtime          = "python3.11"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:gspread-layer:1"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size
    ]
  }
}

resource "aws_lambda_function" "ibold_pricing_analyze_v1" {
  function_name    = "ibold-pricing-analyze-v1"
  role             = "arn:aws:iam::471112687668:role/service-role/contact_vendedor-qgvaw-role-DZ1QYRY2XBQ"
  runtime          = "python3.11"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:gspread-layer:1"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size
    ]
  }
}

resource "aws_lambda_function" "ibold_sales_assistant" {
  function_name    = "ibold-sales-assistant"
  role             = "arn:aws:iam::471112687668:role/service-role/contact_vendedor-qgvaw-role-DZ1QYRY2XBQ"
  runtime          = "python3.11"
  handler          = "lambda_function.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 128
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:gspread-layer:1"]

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size
    ]
  }
}

resource "aws_lambda_function" "snail_bedrock_dev_pdf_processor" {
  function_name    = "snail-bedrock-dev-pdf-processor"
  role             = "arn:aws:iam::471112687668:role/snail-bedrock-dev-lambda-pdf-processor"
  runtime          = "python3.11"
  handler          = "handler.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 300
  memory_size      = 1024
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1"]
  environment {
    variables = {
      "BEDROCK_EMBEDDING_MODEL_ID" = "amazon.titan-embed-text-v1"
      "ENVIRONMENT"                = "dev"
      "FAISS_BACKUP_BUCKET"        = "snail-bedrock-dev-chromadb-backup"
      "FAISS_INDEX_KEY"            = "faiss_index.bin"
      "FAISS_METADATA_KEY"         = "faiss_metadata.pkl"
      "LOG_LEVEL"                  = "DEBUG"
      "PROCESSED_BUCKET"           = "snail-bedrock-dev-processed-documents"
      "RAW_BUCKET"                 = "snail-bedrock-dev-raw-documents"
    }
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "snail_bedrock_dev_query_handler" {
  function_name    = "snail-bedrock-dev-query-handler"
  role             = "arn:aws:iam::471112687668:role/snail-bedrock-dev-lambda-query-handler"
  runtime          = "python3.11"
  handler          = "handler.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 512
  architectures    = ["x86_64"]
  layers           = ["arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1"]
  environment {
    variables = {
      "BEDROCK_EMBEDDING_MODEL_ID" = "amazon.titan-embed-text-v1"
      "BEDROCK_LLM_MODEL_ID"       = "anthropic.claude-3-haiku-20240307-v1:0"
      "CACHE_TABLE_NAME"           = "snail-bedrock-dev-query-cache"
      "CACHE_TTL_SECONDS"          = "604800"
      "CONVERSATIONS_TABLE_NAME"   = "snail-bedrock-dev-conversations"
      "ENABLE_CACHE"               = "true"
      "ENVIRONMENT"                = "dev"
      "FAISS_BACKUP_BUCKET"        = "snail-bedrock-dev-chromadb-backup"
      "FAISS_INDEX_KEY"            = "faiss_index.bin"
      "FAISS_METADATA_KEY"         = "faiss_metadata.pkl"
      "LOG_LEVEL"                  = "DEBUG"
      "MAX_CONTEXT_CHUNKS"         = "5"
      "MAX_HISTORY_MESSAGES"       = "10"
    }
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all
    ]
  }
}

resource "aws_lambda_function" "snail_bedrock_dev_slack_handler" {
  function_name    = "snail-bedrock-dev-slack-handler"
  role             = "arn:aws:iam::471112687668:role/snail-bedrock-dev-lambda-query-handler"
  runtime          = "python3.11"
  handler          = "handler.lambda_handler"
  filename         = "${path.module}/artifacts/lambda/blank.zip"
  source_code_hash = filebase64sha256("${path.module}/artifacts/lambda/blank.zip")
  timeout          = 60
  memory_size      = 256
  architectures    = ["x86_64"]
  environment {
    variables = {
      "QUERY_HANDLER_FUNCTION" = "snail-bedrock-dev-query-handler"
      "SLACK_BOT_TOKEN"        = "xoxb-9970550004167-9970666002759-FNY5urldEIOEJDMrjVb8xdMZ"
      "SLACK_SIGNING_SECRET"   = "f851feeb3c59f94be784c00f4c9af97f"
    }
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes = [
      filename,
      source_code_hash,
      environment,
      layers,
      vpc_config,
      image_config,
      dead_letter_config,
      file_system_config,
      kms_key_arn,
      timeout,
      memory_size,
      publish,
      tags,
      tags_all,
      description
    ]
  }
}
