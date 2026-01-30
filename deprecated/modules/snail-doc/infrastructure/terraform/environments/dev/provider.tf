# AWS Provider configuration for DEV environment

provider "aws" {
  region = "us-east-1"

  default_tags {
    tags = {
      Project     = "snail-bedrock"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}
