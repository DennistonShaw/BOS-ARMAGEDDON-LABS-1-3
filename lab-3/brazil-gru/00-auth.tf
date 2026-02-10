# # Provider & Version
# # https://registry.terraform.io/providers/hashicorp/aws/6.17.0/docs

provider "aws" {
  region = var.aws_region
}

provider "aws" {
  alias  = "apnortheast1"
  region = "ap-northeast-1"
}

provider "aws" {
  alias  = "useast1"
  region = "us-east-1"
}

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

terraform {
  backend "s3" {
    bucket = "sp-armageddon-497589205696"
    key    = "gru/sa-east-1/terraform.tfstate"
    region = "sa-east-1"
  }
}