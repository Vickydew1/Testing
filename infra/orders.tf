provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "orders_sg" {
  name = "orders-sg"
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "orders_data" {
  bucket = "orders-data"
  acl    = "public-read"
}
