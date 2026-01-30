provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "poc" {
  bucket = var.bucket_name

  tags = var.tags
}
