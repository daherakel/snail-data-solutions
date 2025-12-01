# API Gateway REST (us-east-1)

resource "aws_api_gateway_rest_api" "ahh_get_mp3" {
  name                         = "AHH_GET_MP3"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_208hokbs1g.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}

resource "aws_api_gateway_rest_api" "ahh_process_mp3" {
  name                         = "AHH_PROCESS_MP3"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_2wvwse9yvb.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}

resource "aws_api_gateway_rest_api" "ahh_notes_api" {
  name                         = "AHH_NOTES_API"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_45popfs293.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}

resource "aws_api_gateway_rest_api" "ipoc_snail" {
  name                         = "IPOC-SNAIL"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_hwb5xmz2a1.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}

resource "aws_api_gateway_rest_api" "ahh_api" {
  name                         = "AHH_API"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_pi7aucalk6.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}

resource "aws_api_gateway_rest_api" "iphone_store" {
  name                         = "iphone-store"
  api_key_source               = "HEADER"
  disable_execute_api_endpoint = false
  body                         = file("${path.module}/reference/apigw/exports/apigw_exports_ppaxiqr0n7.json")

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [body, tags, tags_all]
  }
}
