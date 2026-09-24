provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "demo" {
  name     = "demo-cluster"
  role_arn = "arn:aws:iam::123456789012:role/demo-role"

  vpc_config {
    subnet_ids = ["subnet-abc123", "subnet-def456"]
  }
}

# Intentionally misconfigured for the PR Decorator demo
resource "aws_s3_bucket" "demo_logs" {
  bucket = "demo-pr-decorator-logs"
}

resource "aws_s3_bucket_public_access_block" "demo_logs" {
  bucket                  = aws_s3_bucket.demo_logs.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
