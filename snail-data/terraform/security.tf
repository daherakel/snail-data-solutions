# Security Groups (us-east-1)

resource "aws_security_group" "sg_default" {
  name        = "default"
  description = "default VPC security group"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_emr_master" {
  name        = "ElasticMapReduce-master"
  description = "Master group for Elastic MapReduce created on 2025-01-17T21:07:41.692Z"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_emr_slave" {
  name        = "ElasticMapReduce-slave"
  description = "Slave group for Elastic MapReduce created on 2025-01-17T21:07:41.692Z"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_sagemaker_outbound_nfs" {
  name        = "security-group-for-outbound-nfs-d-8uq7jfb3ghoe"
  description = "[DO NOT DELETE] Security Group that allows outbound NFS traffic for SageMaker Notebooks Domain [d-8uq7jfb3ghoe]"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_sagemaker_inbound_nfs" {
  name        = "security-group-for-inbound-nfs-d-8uq7jfb3ghoe"
  description = "[DO NOT DELETE] Security Group that allows inbound NFS traffic for SageMaker Notebooks Domain [d-8uq7jfb3ghoe]"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_aurora_bedrock_quick_create" {
  name        = "KnowledgeBaseQuickCreateAurora-d9bf7552-5644-4218-b928-d50f8972f257-AuroraDBSecurityGroup-jXDV3pS76RtV"
  description = "Security Group associated with Aurora Cluster as part of Aurora Bedrock Quick Create"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_sqless_poc" {
  name        = "sqless-sg-poc-test"
  description = "Created by RDS management console"
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}

resource "aws_security_group" "sg_datazone" {
  name        = "datazone-4cvnstfo5i89if-dev"
  description = "Security group for the project."
  vpc_id      = aws_vpc.vpc_main.id

  revoke_rules_on_delete = true

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all, revoke_rules_on_delete]
  }
}
