# Requirements-to-Evidence Matrix

This document helps a reviewer distinguish **historical university capstone results** from **current, independently runnable public evidence**. The private TYN1 capstone functionality report records a PASS outcome for each of eight test cases. Its assessment files, credentials, original configuration exports, and screenshots are **not** hosted in this public repository.

## Historical capstone: documented implementation and validation

The following matches the original report’s individual TC1–TC8 structure. Every PASS is a **historical report outcome**, not an independent retest or proof that the original lab is still running. The school report and its screenshots are retained privately.

| Original capstone case | Generalized reported evidence | Historical result | Review source |
|---|---|---|---|
| TC1 — Local VLAN segmentation | VLAN membership, switch trunk tagging, intra-VLAN testing | PASS | [Original test-case traceability](tyn1-test-case-traceability.md) |
| TC2 — Addressing and external routing | DHCP, static service addresses, routed reachability, outbound NAT | PASS | [Original test-case traceability](tyn1-test-case-traceability.md) |
| TC3 — Local policy enforcement | Same local server: Administration succeeds, Operations denied | PASS | [Security controls](security-controls.md) |
| TC4 — AWS subnet segmentation | Distinct web/app subnets, EC2 placement, permitted cross-subnet service | PASS | [Architecture](architecture.md) |
| TC5 — AWS external access | Public web response, internal application proxy, Elastic IP association | PASS | [Validation](validation.md) |
| TC6 — Cloud application policy | Approved TCP app service reachable; unauthorized SSH port blocked | PASS | [Original test-case traceability](tyn1-test-case-traceability.md) |
| TC7 — Hybrid VPN | Terraform VPN plan, StrongSwan and AWS tunnel checks, private traffic and encrypted counters | PASS | [Original test-case traceability](tyn1-test-case-traceability.md) |
| TC8 — Source-aware hybrid security | Security-group policy change and actual allowed/denied source-path tests | PASS | [Security controls](security-controls.md) |

**Evidence limitation:** The public links above contain narrative summaries and generalized diagrams, not original screenshots, packet captures, device configurations, AWS account access, or a replayable copy of the capstone lab. TC7 validated only one active VPN tunnel; failover was not tested. The original results should not be conflated with the new Python exercises below.

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
