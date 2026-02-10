# Class 7 — Armageddon (Winter 2026)
**Group:** Brotherhood Of Steel

This repository contains a series of progressive AWS architecture labs completed as part of the **Armageddon** curriculum. Each lab builds on the previous one, introducing increasingly advanced cloud design patterns focused on **security, scalability, compliance, and real-world enterprise practices**.

---

## Repository Structure

This repository is organized into three labs, each representing a deliberate step in architectural maturity.

### **Lab 1 — Baseline AWS Infrastructure**
Introduces foundational AWS components including VPCs, public and private subnets, EC2, RDS, IAM roles, and basic monitoring. This lab establishes a functional baseline architecture with minimal complexity.

### **Lab 2 — Secure Private Architecture**
Builds on Lab 1 by introducing private compute, controlled ingress, NAT gateways, VPC endpoints, and improved security boundaries. The focus shifts toward production-style isolation and least-privilege access.

### **Lab 3 — Global & Compliant Architecture**
Extends the architecture across multiple regions with global ingress, regional segmentation, and strict data residency controls. This lab demonstrates how to design architectures that meet compliance and regulatory requirements at scale.

---

## How to Navigate This Repository

- Each lab has its own directory with a dedicated `README.md`
- Architecture diagrams are provided in both view-only and editable formats
- Screenshots are included as supporting evidence for lab requirements

---

## Technologies Used

### **Cloud & Infrastructure**
- Amazon Web Services (AWS)
- Virtual Private Cloud (VPC)
- EC2
- RDS (MySQL)
- IAM
- Route 53
- CloudFront
- AWS WAF
- Application Load Balancer (ALB)
- Transit Gateway
- NAT Gateway
- VPC Interface Endpoints (PrivateLink)
- Security Groups
- Network ACLs

### **Monitoring & Management**
- CloudWatch
- SNS
- Secrets Manager
- Systems Manager Parameter Store

### **Tooling & Platforms**
- Terraform
- Amazon Linux 2023
- Python (Flask / Werkzeug)
- MySQL
- HTTP / HTTPS (TLS)
- `curl`
- GitHub
- Draw.io
