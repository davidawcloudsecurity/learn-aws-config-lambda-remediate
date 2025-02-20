provider "aws" {
  region = var.region
}

variable "region" {
  type    = string
  default = "us-west-2"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py" # Make sure this matches your Python file name
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "s3_public_access_checker" {
  filename         = "lambda_function.zip"
  function_name    = "s3-public-access-checker"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"  # Updated to a more recent Python version
  timeout          = 300         # Increased timeout to 5 minutes for processing multiple buckets
  memory_size      = 128         # Default memory size
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

resource "aws_iam_role" "lambda_role" {
  name = "s3_checker_lambda_role"

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
  name = "s3_checker_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:GetBucketPublicAccessBlock",
				  "s3:PutBucketPublicAccessBlock",
          "s3:ListBucket"
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
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_cloudwatch_event_rule" "every_day" {
  name                = "every-day-s3-check"
  description         = "Runs S3 public access check every day at 2 AM UTC"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "check_s3_buckets" {
  rule      = aws_cloudwatch_event_rule.every_day.name
  target_id = "lambda-check-s3-buckets"
  arn       = aws_lambda_function.s3_public_access_checker.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_public_access_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_day.arn
}
