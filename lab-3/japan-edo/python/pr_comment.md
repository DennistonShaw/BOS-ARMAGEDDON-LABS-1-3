### SEIR Lab 2 Gate Result: **RED** (FAIL)

**Domain:** `larrryharrisaws.com`  
**CloudFront:** `E35DOVRWEUTMBX` (domain: `d2pksv826xpftg.cloudfront.net`)  
**WAF required:** `true`  
**Logging required:** `true`  
**Origin SG:** `sg-0aa3623d9362f30d7`  

**SLA**
- target: `24h`
- first_seen: `2026-01-22T20:55:32Z`
- due: `2026-01-23T20:55:32Z`
- breached: `false`

**Failures (fix in order)**
- FAIL: Route53 A alias does not point to CloudFront (expected=d2pksv826xpftg.cloudfront.net, actual=d2pksv826xpftg.cloudfront.net.).
- FAIL: Route53 AAAA alias does not point to CloudFront (expected=d2pksv826xpftg.cloudfront.net, actual=d2pksv826xpftg.cloudfront.net.).
- FAIL: CloudFront logging not enabled (DistributionConfig.Logging.Bucket missing).
- FAIL: Log bucket does not exist or not accessible (/aws/ec2/bos-rds-app).
- FAIL: Origin SG sg-0aa3623d9362f30d7 allows port 80 from the world (0.0.0.0/0 or ::/0).

**Warnings**
- WARN: WAF has no managed rule groups detected (consider AWSManagedRules* baseline).
- WARN: Origin SG sg-0aa3623d9362f30d7 has no visible sources on port 443 (check prefix lists / LB SG chaining).

> Reminder: Hennessy does not fix Route53 alias records. Evidence does.
