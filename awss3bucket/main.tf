# Configure the AWS provider
provider "aws" {
  region = var.region
}

variable region {
  default = "us-east-1" # Change to your preferred region
}
