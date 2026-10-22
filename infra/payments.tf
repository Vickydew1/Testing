provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "payments_sg" {
  name = "payments-sg"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "payments_data" {
  bucket = "payments-data"
  acl    = "public-read"
}
