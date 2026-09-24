provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "demo" {
enabled_cluster_log_types = ["api", "audit"]
  role_arn = "arn:aws:iam::123456789012:role/demo-role"

  vpc_config {
    subnet_ids = ["subnet-abc123", "subnet-def456"]
  }
}
