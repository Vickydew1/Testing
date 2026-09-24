provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "inventory_sg" {
  name        = "inventory-service-sg"
  description = "Security group for the inventory service"

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "inventory_snapshots" {
  bucket = "inventory-service-snapshots"
}

resource "aws_s3_bucket_public_access_block" "inventory_snapshots" {
  bucket                  = aws_s3_bucket.inventory_snapshots.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
