# Architecture Intent

This architecture is designed to provide global application access while enforcing strict regional data residency through technical controls. Global services are deliberately separated from regional compute and data layers to ensure that compliance is enforced by design rather than policy.

Tokyo (ap-northeast-1) serves as the system of record and compliance boundary. All persistent data, including personally identifiable and health-related information, is stored and processed exclusively within this region. The primary Amazon RDS database and read replicas reside in private subnets and are not publicly accessible. Database access is limited to encrypted, application-level connections from authorized application components.

São Paulo (sa-east-1) is intentionally limited to stateless application compute. No persistent storage services are deployed in this region, ensuring that regulated data cannot be stored, cached, or reconstructed outside Japan. Compute resources may process requests but do not retain sensitive data locally.

Cross-region connectivity is provided through a tightly scoped AWS Transit Gateway peering connection. This peering permits only required, encrypted database traffic and is not configured as a general-purpose network mesh, enforcing controlled cross-border access at the network layer.

Amazon Route 53 and Amazon CloudFront operate solely as global routing and delivery layers. These services do not store or process sensitive application data and are excluded from the regulated data path.

As a result, regulated data remains within Japan, cross-border data flows are transient and encrypted, and overseas regions are technically prevented from persisting sensitive information. This architecture aligns with APPI data residency and cross-border transfer requirements through enforceable architectural controls.
