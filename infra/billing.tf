provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "billing_sg" {
  name = "billing-sg"
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "billing_data" {
  bucket = "billing-data"
  acl    = "public-read"
}
