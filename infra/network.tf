provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "payments_sg" {
  name        = "payments-service-sg"
  description = "Security group for the payments service"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "payments_archive" {
  bucket = "payments-service-archive"
}

resource "aws_db_instance" "payments_db" {
  identifier          = "payments-db"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = "postgres"
  password            = "Payments2026!"
  publicly_accessible = true
  skip_final_snapshot = true
}
