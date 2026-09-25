provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "billing_sg" {
  name        = "billing-service-sg"
  description = "Security group for the billing service"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "billing_statements" {
  bucket = "billing-service-statements"
}

resource "aws_s3_bucket_public_access_block" "billing_statements" {
  bucket                  = aws_s3_bucket.billing_statements.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
