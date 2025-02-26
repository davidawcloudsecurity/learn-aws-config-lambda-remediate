provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "us-east-1"  # Updated to your specified region
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py"  # Matches the Python file name
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "s3_secure_transport_enforcer" {
  filename         = "lambda_function.zip"
  function_name    = "s3-secure-transport-enforcer"  # Updated name to reflect purpose
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  timeout          = 300  # 5 minutes, sufficient for moderate bucket counts
  memory_size      = 128  # Default, adjust if needed
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

resource "aws_iam_role" "lambda_role" {
  name = "s3_enforcer_lambda_role"  # Updated name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "s3_enforcer_lambda_policy"  # Updated name
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",  # For listing buckets
          "s3:GetBucketPolicy",   # To read policies
          "s3:PutBucketPolicy",   # To update policies
          "s3:ListBucket"         # Included from your original
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${var.region}:*:*"
      }
    ]
  })
}

resource "aws_cloudwatch_event_rule" "every_day" {
  name                = "every-day-s3-check"
  description         = "Runs S3 secure transport enforcement every day at 2 AM UTC"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "check_s3_buckets" {
  rule      = aws_cloudwatch_event_rule.every_day.name
  target_id = "lambda-enforce-s3-secure-transport"
  arn       = aws_lambda_function.s3_secure_transport_enforcer.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_secure_transport_enforcer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_day.arn
}
