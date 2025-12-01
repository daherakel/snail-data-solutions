provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  ignore_tags {
    keys = [
      "environment",
      "managed_by",
      "project",
      "CostCenter",
      "Environment",
      "ManagedBy",
      "Name",
      "Owner",
      "Project",
      "Purpose",
      "for-use-with-amazon-emr-managed-policies",
      "AmazonDataZoneBlueprint",
      "AmazonDataZoneDomain",
      "AmazonDataZoneEnvironment",
      "AmazonDataZoneProject",
      "AmazonDataZoneScopeName",
      "ManagedByAmazonSageMakerResource",
      "user:Application",
      "user:Stack"
    ]
  }

  default_tags {
    tags = {
      project     = "snail-data"
      environment = var.environment
      managed_by  = "terraform"
    }
  }
}

provider "aws" {
  alias   = "use2"
  region  = "us-east-2"
  profile = var.aws_profile

  ignore_tags {
    keys = [
      "environment",
      "managed_by",
      "project",
      "CostCenter",
      "Environment",
      "ManagedBy",
      "Name",
      "Owner",
      "Project",
      "Purpose",
      "for-use-with-amazon-emr-managed-policies",
      "AmazonDataZoneBlueprint",
      "AmazonDataZoneDomain",
      "AmazonDataZoneEnvironment",
      "AmazonDataZoneProject",
      "AmazonDataZoneScopeName",
      "ManagedByAmazonSageMakerResource",
      "user:Application",
      "user:Stack"
    ]
  }

  default_tags {
    tags = {
      project     = "snail-data"
      environment = var.environment
      managed_by  = "terraform"
    }
  }
}
