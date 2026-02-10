############################################
# Locals (naming convention: bos-*) (Brotherhood Of Steel)
############################################
locals {
  name_prefix = var.project_name
}

############################################
# Bonus A - Data + Locals
############################################

# Explanation: bos wants to know “who am I in this galaxy?” so ARNs can be scoped properly.
data "aws_caller_identity" "bos_self01" {}

# Explanation: Region matters—hyperspace lanes change per sector.
data "aws_region" "bos_region01" {}

locals {
  # Explanation: Name prefix is the roar that echoes through every tag.
  bos_prefix = var.project_name

  # TODO: Students should lock this down after apply using the real secret ARN from outputs/state
  bos_secret_arn_guess = "arn:aws:secretsmanager:${data.aws_region.bos_region01.region}:${data.aws_caller_identity.bos_self01.account_id}:secret:${local.bos_prefix}/rds/mysql*"
}

############################################
# Bonus B - ALB (Public) -> Target Group (Private EC2) + TLS + WAF + Monitoring
############################################

locals {
  # Explanation: This is the roar address — where the galaxy finds your app.
  bos_fqdn = "${var.app_subdomain}.${var.domain_name}"
}

############################################
# Bonus B - Route53 (Hosted Zone + DNS records + ACM validation + ALIAS to ALB)
############################################

locals {
  # Explanation: Chewbacca needs a home planet—Route53 hosted zone is your DNS territory.
  bos_zone_name = var.domain_name

  # Explanation: Use either Terraform-managed zone or a pre-existing zone ID (students choose their destiny).
  # bos_zone_id = var.manage_route53_in_terraform ? aws_route53_zone.bos_zone01[0].zone_id : var.route53_hosted_zone_id
  bos_zone_id = var.route53_hosted_zone_id
  # Explanation: This is the app address that will growl at the galaxy (app.chewbacca-growl.com).
  bos_app_fqdn = "${var.app_subdomain}.${var.domain_name}"
}