provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "ledger_sg" {
  name = "ledger-sg"
  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "ledger_data" {
  bucket = "ledger-data"
  acl    = "public-read"
}
