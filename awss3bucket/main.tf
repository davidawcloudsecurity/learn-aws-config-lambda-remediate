# main.tf

# Configure the AWS provider
provider "aws" {
  region = var.region
}

variable "region" {
  default = "us-east-1" # Change to your preferred region
}

variable "conformance_pack_yaml" {
  default = "Operational-Best-Practices-for-Amazon-S3.yaml"
}

resource "aws_s3_bucket" "config_bucket" {
  bucket = "aws-config-delivery-bucket"
  acl    = "private"
}

resource "aws_iam_role" "config_role" {
  name = "aws-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/service-role/AWSConfigRole",
  ]
}

resource "aws_config_configuration_recorder" "main" {
  name     = "main"
  role_arn = aws_iam_role.config_role.arn

  recording_group {
    all_supported = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "main"
  s3_bucket_name = aws_s3_bucket.config_bucket.bucket

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name      = aws_config_configuration_recorder.main.name
  is_enabled = true
}

resource "aws_iam_role" "remediation_role" {
  name = "s3-remediation-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "config.amazonaws.com"
        }
      },
    ]
  })

  managed_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
  ]
}

resource "aws_config_conformance_pack" "my_conformance_pack" {
  name = "my-conformance-pack"

  delivery_s3_bucket = aws_s3_bucket.config_bucket.bucket

  template_body = file("${var.conformance_pack_yaml}")

  input_parameters = {
    BucketName = aws_s3_bucket.config_bucket.bucket
  }
}
