# API Gateway deployments and stages (us-east-1)

resource "aws_api_gateway_deployment" "ahh_get_mp3_dev" {
  rest_api_id = aws_api_gateway_rest_api.ahh_get_mp3.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "ahh_get_mp3_dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.ahh_get_mp3.id
  deployment_id = aws_api_gateway_deployment.ahh_get_mp3_dev.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_deployment" "ahh_process_mp3_dev" {
  rest_api_id = aws_api_gateway_rest_api.ahh_process_mp3.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "ahh_process_mp3_dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.ahh_process_mp3.id
  deployment_id = aws_api_gateway_deployment.ahh_process_mp3_dev.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_deployment" "ahh_notes_api_dev" {
  rest_api_id = aws_api_gateway_rest_api.ahh_notes_api.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "ahh_notes_api_dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.ahh_notes_api.id
  deployment_id = aws_api_gateway_deployment.ahh_notes_api_dev.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_deployment" "ipoc_snail_dev" {
  rest_api_id = aws_api_gateway_rest_api.ipoc_snail.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "ipoc_snail_dev" {
  stage_name    = "Dev"
  rest_api_id   = aws_api_gateway_rest_api.ipoc_snail.id
  deployment_id = aws_api_gateway_deployment.ipoc_snail_dev.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_deployment" "ahh_api_dev" {
  rest_api_id = aws_api_gateway_rest_api.ahh_api.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "ahh_api_dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.ahh_api.id
  deployment_id = aws_api_gateway_deployment.ahh_api_dev.id

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_deployment" "iphone_store_dev" {
  rest_api_id = aws_api_gateway_rest_api.iphone_store.id
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_api_gateway_stage" "iphone_store_dev" {
  stage_name    = "dev"
  rest_api_id   = aws_api_gateway_rest_api.iphone_store.id
  deployment_id = aws_api_gateway_deployment.iphone_store_dev.id

  lifecycle {
    prevent_destroy = true
  }
}
