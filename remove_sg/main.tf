provider "aws" {
  region = var.region # Change to your preferred region
}

variable region {
  type = string
default = "us-west-2"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "lambda_function.py" # Matches your file name
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "sg_inbound_outbound_checker" {
  filename         = "lambda_function.zip"
  function_name    = "sg-inbound-outbound-checker"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.8"
  timeout          = 60
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}

resource "aws_iam_role" "lambda_role" {
  name = "sg_checker_lambda_role"

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
  name = "sg_checker_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:DescribeSecurityGroups",
          "ec2:RevokeSecurityGroupEgress",
          "ec2:RevokeSecurityGroupIngress",
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}
resource "aws_cloudwatch_event_rule" "every_day" {
  name                = "every-day-trigger"
  description         = "Fires every day at 2 AM UTC"
  schedule_expression = "cron(0 2 * * ? *)"
}

resource "aws_cloudwatch_event_target" "check_sg_rule" {
  rule      = aws_cloudwatch_event_rule.every_day.name
  target_id = "lambda-check-sg-rule"
  arn       = aws_lambda_function.sg_inbound_outbound_checker.arn
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sg_inbound_outbound_checker.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_day.arn
}
