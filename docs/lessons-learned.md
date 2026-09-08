# Engineering Lessons Learned

## Hybrid Connectivity Is a Systems Problem

The project reinforced that a hybrid network is not solved by creating a VPN object alone. Successful operation depended on Layer 2 segmentation, routing, NAT behavior, source preservation, tunnel state, Security Groups, and workload placement all agreeing with one another.

---

## A Tunnel Being Up Is Not Enough

Control-plane status provided only part of the evidence. The stronger validation came from proving that private application traffic actually crossed the encrypted path and that packet and byte counters increased during testing.

---

## Security Requires Testing Failure

Allowed traffic proved reachability. Blocked traffic proved policy.

Testing the same protected destination from different source networks made it possible to distinguish routing success from security enforcement and demonstrated that access controls remained active across the hybrid boundary.

---

## NAT Can Change Security Meaning

Source-aware controls depend on preserving source identity. If all VPN-bound traffic had been translated to one address, downstream AWS controls would have lost the ability to distinguish the originating enterprise segment.

The no-NAT design for private VPN traffic therefore supported both routing and security objectives.

---

## Troubleshooting Should Move Layer by Layer

A useful troubleshooting sequence was:

1. Confirm endpoint addressing.
2. Confirm VLAN membership and trunks.
3. Confirm local routes.
4. Confirm NAT behavior.
5. Confirm ACLs and Security Groups.
6. Confirm VPN negotiation.
7. Confirm private route selection.
8. Generate traffic and inspect data-plane evidence.

This prevented a single symptom from being misdiagnosed as a VPN issue when the root cause could exist elsewhere in the path.

---

## Version Control Is an Operational Tool

Git/GitLab checkpoints were useful beyond software development. Preserving known-good network configuration milestones improved recoverability, made changes easier to audit, and reduced the risk of losing a working topology during later modifications.

---

## Documentation Improves Engineering Quality

Writing reproducible test procedures forced assumptions to become explicit. Each test needed a defined purpose, expected outcome, evidence, and final result.

That discipline improved troubleshooting because failures could be tied back to a specific layer or policy instead of being described only as “connectivity problems.”

---

## Production-Oriented Improvements

If rebuilding the environment as an independent production-style project, the next improvements would be:

- Terraform modules for VPC, routing, Security Groups, and VPN components
- Automated validation with CI/CD
- CloudWatch and VPC Flow Logs
- Automated policy and reachability tests
- Dynamic routing and redundant VPN failover
- Configuration management for customer-side infrastructure
- Centralized security monitoring
- Infrastructure as Code scanning
- Containerized or EKS-hosted application workloads

These extensions would move the design from a validated hybrid networking capstone toward a repeatable cloud-platform engineering implementation.
