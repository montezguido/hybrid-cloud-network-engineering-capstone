# Requirements-to-Evidence Matrix

This document helps a reviewer distinguish **historical university capstone results** from **current, independently runnable public evidence**. The original capstone was evaluated as passing. Its assessment files, credentials, original configuration exports, and screenshots are **not** hosted in this public repository.

## Historical capstone: documented implementation and validation

The following summarizes the professional engineering outcomes recorded in the sanitized [validation case study](validation.md), not newly executed tests. "Reported PASS" means the original capstone result was documented as passing; it is **not a claim that the lab is currently deployed**.

| Engineering requirement | Historical verification approach (generalized) | Reported result | Public evidence |
|---|---|---|---|
| Segment different enterprise functions | Review VLAN membership, tagged trunks, expected within-segment reachability | PASS | [Network architecture](architecture.md), [validation summary](validation.md) |
| Supply user addressing and stable service addressing | Confirm DHCP-assigned client settings and static service reachability | PASS | [Validation summary](validation.md) |
| Provide intentional local routing | Verify inter-VLAN reachability and expected route selection | PASS | [Architecture](architecture.md), [validation summary](validation.md) |
| Restrict protected local traffic by source | Compare authorized and unauthorized source-network outcomes | PASS | [Security controls](security-controls.md), [validation summary](validation.md) |
| Separate AWS workload tiers | Confirm VPC/subnet placement, appropriate routes and security-group behavior | PASS | [Architecture](architecture.md), [validation summary](validation.md) |
| Publish only the intended web-facing workload | Confirm web-tier access while keeping the application tier private | PASS | [Security controls](security-controls.md), [validation summary](validation.md) |
| Establish functional encrypted hybrid connectivity | Confirm tunnel state and private path traffic, including encrypted counters | PASS | [Architecture](architecture.md), [validation summary](validation.md) |
| Enforce source-aware hybrid authorization | Compare approved and restricted source access to the same private cloud service | PASS | [Security controls](security-controls.md), [validation summary](validation.md) |

**Evidence limitation:** The public links above contain narrative summaries and generalized diagrams, not independent screenshots, packet captures, device configurations, AWS account access, or a replayable copy of the original capstone lab. The original test results should not be conflated with the new Python exercises below.

## Independent public verification: executable portfolio exercises

| Engineering objective | Independent evidence | How to verify | Scope |
|---|---|---|---|
| Catch invalid, overlapping, or out-of-bound CIDRs | [Design validator](../portfolio_demo/validate_design.py), [fictional design](../portfolio_demo/sample_design.json) | Run validator and unit tests | Static JSON design model, not live AWS |
| Check simple private-subnet exposure intent | Design validator and [regression tests](../tests/test_design_validator.py) | Run unit tests | Static design rules only, not route-table inspection |
| Preserve intended source-aware access | [Policy-intent verifier](../portfolio_demo/verify_access_policy.py), [fictional policy](../portfolio_demo/sample_access_policy.json) | Run policy verification | Permit-only offline model with implicit deny; not a firewall or AWS Security Group |
| Detect overly broad permissions and unexpected denials | [Access-policy regression tests](../tests/test_access_policy.py) | Run unit tests | Synthetic input scenarios |
| Repeat checks across platforms | [GitHub Actions workflow](../.github/workflows/verify-network-design.yml) | Review the [Actions tab](https://github.com/montezguido/hybrid-cloud-network-engineering-capstone/actions) | Unit checks and offline samples; no AWS deployment |

Run from the repository root using Python 3.11+:

```bash
python -m unittest discover -s tests -v
python portfolio_demo/validate_design.py portfolio_demo/sample_design.json
python portfolio_demo/verify_access_policy.py portfolio_demo/sample_access_policy.json
```

The policy example uses deliberately fictitious source networks, application labels, and permissions. A policy-model **ALLOW/DENY result does not prove actual data-plane behavior**, access-control-list semantics, VPN connectivity, encryption, or production security.

## Design decisions to discuss in an interview

- **Why preserve source identity?** Source-based policies are easier to enforce when VPN traffic is not indiscriminately source-NATed.
- **Why test denials?** An allowed request proves reachability, while a blocked request can demonstrate intended restriction.
- **Why separate public/private workloads?** Reduce direct exposure of private services and establish explicit traffic paths.
- **Why inspect traffic counters?** A tunnel status indicator does not independently prove that expected application traffic traverses the tunnel.
- **Why not deploy the capstone publicly?** The original educational environment contains restricted materials and would require new cloud resources, security review, and potential AWS charges.

**Future independent work (not implemented):** Terraform-driven AWS deployment, controlled integration tests, live VPN redundancy/failover, cloud-network-policy inspection, and safe teardown verification.
