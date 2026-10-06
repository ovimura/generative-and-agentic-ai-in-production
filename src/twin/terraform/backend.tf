# "arn:aws:iam::623208129368:role/github-actions-twin-deploy"
terraform {
  backend "s3" {
    # These values will be set by deployment scripts
    # For local development, they can be passed via -backend-config
  }
}