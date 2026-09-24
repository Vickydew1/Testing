provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "directory_sg" {
  name        = "user-directory-sg"
  description = "Security group for the user directory service"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "directory_exports" {
  bucket = "user-directory-exports"
}

resource "aws_s3_bucket_public_access_block" "directory_exports" {
  bucket                  = aws_s3_bucket.directory_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
