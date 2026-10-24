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
