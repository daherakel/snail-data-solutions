# Network (us-east-1)

resource "aws_vpc" "vpc_main" {
  cidr_block           = "172.31.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "default"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_a" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.80.0/20"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1a"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_b" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.16.0/20"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1b"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_c" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.32.0/20"
  availability_zone       = "us-east-1c"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1c"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_d" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.0.0/20"
  availability_zone       = "us-east-1d"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1d"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_e" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.48.0/20"
  availability_zone       = "us-east-1e"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1e"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_subnet" "subnet_public_f" {
  vpc_id                  = aws_vpc.vpc_main.id
  cidr_block              = "172.31.64.0/20"
  availability_zone       = "us-east-1f"
  map_public_ip_on_launch = true

  tags = {
    Name = "default-us-east-1f"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}

resource "aws_route_table" "rtb_main" {
  vpc_id = aws_vpc.vpc_main.id

  tags = {
    Name = "default"
  }

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags, tags_all]
  }
}
