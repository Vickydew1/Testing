provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "inventory_sg" {
  name = "inventory-sg"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "inventory_data" {
  bucket = "inventory-data"
  acl    = "public-read"
}
