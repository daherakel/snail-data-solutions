terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Terraform Cloud (configurar cuando quieras moverlo a remoto)
  # cloud {
  #   organization = "TU_ORG"
  #   workspaces {
  #     name = "snail-tf-cloud-poc"
  #   }
  # }
}
