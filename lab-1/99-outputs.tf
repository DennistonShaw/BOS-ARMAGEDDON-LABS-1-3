# Explanation: Outputs are your mission report—what got built and where to find it.
output "bos_vpc_id" {
  value = aws_vpc.bos_vpc01.id
}

output "bos_public_subnet_ids" {
  value = aws_subnet.bos_public_subnets[*].id
}

output "bos_private_subnet_ids" {
  value = aws_subnet.bos_private_subnets[*].id
}

output "bos_ec2_instance_id" {
  value = aws_instance.bos_ec201_private_bonus.id
}

output "bos_rds_endpoint" {
  value = aws_db_instance.bos_rds01.address
}

output "bos_sns_topic_arn" {
  value = aws_sns_topic.bos_sns_topic01.arn
}

output "bos_log_group_name" {
  value = aws_cloudwatch_log_group.bos_log_group01.name
}

#Bonus-A outputs (append to outputs.tf)

# Explanation: These outputs prove bos built private hyperspace lanes (endpoints) instead of public chaos.
output "bos_vpce_ssm_id" {
  value = aws_vpc_endpoint.bos_vpce_ssm01.id
}

output "bos_vpce_logs_id" {
  value = aws_vpc_endpoint.bos_vpce_logs01.id
}

output "bos_vpce_secrets_id" {
  value = aws_vpc_endpoint.bos_vpce_secrets01.id
}

output "bos_vpce_s3_id" {
  value = aws_vpc_endpoint.bos_vpce_s3_gw01.id
}

output "bos_private_ec2_instance_id_bonus" {
  value = aws_instance.bos_ec201_private_bonus.id
}

# Explanation: Outputs are the mission coordinates — where to point your browser and your blasters.
output "bos_alb_dns_name" {
  value = aws_lb.bos_alb01.dns_name
}

output "bos_app_fqdn" {
  value = "${var.app_subdomain}.${var.domain_name}"
}

output "bos_target_group_arn" {
  value = aws_lb_target_group.bos_tg01.arn
}

output "bos_acm_cert_arn" {
  value = aws_acm_certificate.bos_acm_cert01.arn
}

output "bos_waf_arn" {
  value = var.enable_waf ? aws_wafv2_web_acl.bos_waf01[0].arn : null
}

output "bos_dashboard_name" {
  value = aws_cloudwatch_dashboard.bos_dashboard01.dashboard_name
}

output "bos_route53_zone_id" {
  value = local.bos_zone_id
}

output "bos_app_url_https" {
  value = "https://${var.app_subdomain}.${var.domain_name}"
}

output "bos_waf_log_destination" {
  value = var.waf_log_destination
}

output "bos_waf_cw_log_group_name" {
  value = var.waf_log_destination == "cloudwatch" ? aws_cloudwatch_log_group.bos_waf_log_group01[0].name : null
}

# output "chewbacca_waf_logs_s3_bucket" {
#   value = var.waf_log_destination == "s3" ? aws_s3_bucket.chewbacca_waf_logs_bucket01[0].bucket : null 
# }

# output "chewbacca_waf_firehose_name" {
#   value = var.waf_log_destination == "firehose" ? aws_kinesis_firehose_delivery_stream.chewbacca_waf_firehose01[0].name : null 
# }