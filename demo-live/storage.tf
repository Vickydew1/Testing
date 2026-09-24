# Live demo — intentionally misconfigured storage for the checkout service
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "checkout_exports" {
  bucket = "checkout-service-exports"
}

resource "aws_s3_bucket_public_access_block" "checkout_exports" {
  bucket                  = aws_s3_bucket.checkout_exports.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_db_instance" "orders" {
  identifier        = "orders-db"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  username          = "admin"
  password          = "ChangeMe123!"
  publicly_accessible = true
  skip_final_snapshot = true
}
