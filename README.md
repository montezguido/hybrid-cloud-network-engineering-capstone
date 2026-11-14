# Hybrid Cloud Network Engineering Capstone

[![Verify independent portfolio exercises](https://github.com/montezguido/hybrid-cloud-network-engineering-capstone/actions/workflows/verify-network-design.yml/badge.svg?branch=main)](https://github.com/montezguido/hybrid-cloud-network-engineering-capstone/actions/workflows/verify-network-design.yml)

A sanitized engineering case study of an officially passed B.S. Cloud and Network Engineering capstone that implemented and validated a secure hybrid network connecting a segmented enterprise environment in GNS3 to AWS through an encrypted Site-to-Site IPsec VPN.

> **Portfolio disclosure:** This repository is an employer-facing technical case study. It does not contain academic assessment instructions, evaluator materials, student information, credentials, restricted lab files, proprietary screenshots, or copied course configurations. Architecture diagrams and documentation in this repository are original portfolio artifacts created to explain the engineering work.

---

## Project Summary

The project required designing, implementing, troubleshooting, and validating a hybrid network that combined an on-premises-style enterprise environment with AWS cloud resources.

The local environment used multiple VLANs to separate administrative, operational, and server workloads. Routing, DHCP, NAT, and access-control policies were enforced through the edge router. The AWS side used a dedicated VPC with separate web and application network tiers, Security Groups, and private routing across an encrypted Site-to-Site VPN.

The final environment was tested through eight documented functional scenarios covering local segmentation, IP addressing, routing, source-based security policy, AWS segmentation, external access, hybrid VPN connectivity, encrypted data transfer, and security enforcement across the hybrid boundary.

---

## Independent, executable engineering demonstration

This repository also contains a **newly written synthetic network-design validator**, separate from the university capstone implementation. It uses fictitious VPC/subnet definitions and requires no AWS credentials or cloud deployment.

- [Validator source](portfolio_demo/validate_design.py) — Python standard-library checks for CIDR formatting, duplicate or overlapping VPC/subnet ranges, subnet containment, and simple private-subnet exposure rules.
- [Synthetic design input](portfolio_demo/sample_design.json) — deliberately invented addressing, not the institution's lab network.
- [Network-design unit tests](tests/test_design_validator.py) — positive and negative CIDR/subnet test cases.
- [Offline policy-intent verifier](portfolio_demo/verify_access_policy.py) and [fictional allowlist/scenarios](portfolio_demo/sample_access_policy.json) — models expected ALLOW/DENY behavior without connecting to AWS.
- [Policy regression tests](tests/test_access_policy.py) — check implicit-deny behavior, unexpected access, input validation, and overly broad permissions.
- [GitHub Actions workflow](.github/workflows/verify-network-design.yml) — runs unit tests and both synthetic examples on Linux and Windows.
- [Requirements-to-evidence matrix](docs/requirements-evidence.md) — distinguishes historical capstone validation from current executable portfolio checks.
- [Original TC1–TC8 traceability](docs/tyn1-test-case-traceability.md) — source-aligned historical test summary, Terraform/VPN evidence, and limitations.

Run from the repository root with Python 3.11 or later:

```bash
python -m unittest discover -s tests -v
python portfolio_demo/validate_design.py portfolio_demo/sample_design.json
python portfolio_demo/verify_access_policy.py portfolio_demo/sample_access_policy.json
```

**Scope limitation:** These static design and allowlist-policy checks do not inspect live AWS configurations, prove routing, access-control enforcement, or VPN connectivity, or reproduce the original capstone environment. The original project's eight historical validation areas are documented separately below and mapped to public evidence in the [requirements-to-evidence matrix](docs/requirements-evidence.md).


## Architecture

```mermaid
flowchart LR
    subgraph ONPREM["Enterprise / GNS3 Environment"]
        ADMIN["Administration VLAN"]
        OPS["Operations VLAN"]
        SERVERS["Server VLAN"]
        SW["Layer 2 Switching\n802.1Q Trunks"]
        R1["Edge Router\nDHCP | Inter-VLAN Routing\nNAT | ACLs"]

        ADMIN --> SW
        OPS --> SW
        SERVERS --> SW
        SW --> R1
    end

    R1 -->|"No-NAT private route"| VPN["Encrypted Site-to-Site\nIPsec VPN"]
    VPN --> VGW["AWS Virtual Private Gateway"]

    subgraph AWS["AWS Cloud Environment"]
        VPC["AWS VPC"]
        WEB["Web Tier Subnet\nEC2 + Security Group"]
        APP["Application Tier Subnet\nPrivate EC2 + Security Group"]

        VGW --> VPC
        VPC --> WEB
        VPC --> APP
    end

    INTERNET((Internet)) -->|"Controlled public access"| WEB
```

The public diagram intentionally uses generalized labels and omits environment-specific addresses and implementation secrets.

For a deeper walkthrough, see [Architecture & Design Decisions](docs/architecture.md).

---

## Engineering Objectives

The implementation focused on the following goals:

- Segment enterprise users and servers into separate VLANs.
- Provide dynamic addressing where appropriate while preserving static addressing for infrastructure services.
- Route traffic between approved local segments.
- Enforce different access outcomes based on source network.
- Provide outbound Internet access without exposing internal addressing.
- Separate public-facing and private workloads in AWS.
- Establish encrypted private connectivity between the local environment and AWS.
- Preserve original source addresses across the VPN so security controls could make source-aware decisions.
- Validate both connectivity and denial conditions rather than testing only successful traffic flows.
- Preserve configuration state through version-controlled checkpoints.

---

## Local Network Design

The enterprise side was modeled in GNS3 and separated into three functional zones:

| Segment | Purpose | Design Intent |
|---|---|---|
| Administration VLAN | Authorized management/user traffic | Allowed access to approved internal and cloud resources |
| Operations VLAN | General operational users | More restrictive access to protected resources |
| Server VLAN | Local infrastructure/services | Static or predictable addressing and controlled reachability |

The edge router provided:

- DHCP services for user networks
- Inter-VLAN routing
- Outbound NAT
- Static/private routing toward AWS
- ACL-based source filtering
- A no-NAT path for VPN-bound traffic

Layer 2 switching used VLAN membership and 802.1Q trunks to preserve segmentation between switches.

---

## AWS Network Design

The AWS environment used a dedicated VPC with separate workload tiers:

### Web Tier

- Placed in a distinct subnet
- Hosted an EC2 web workload
- Allowed controlled external reachability
- Protected by a purpose-built Security Group

### Application Tier

- Placed in a separate private-oriented subnet
- Hosted an EC2 application workload
- Not intended for direct public exposure
- Restricted with source-aware Security Group rules

This separation allowed public access to terminate at the web layer while keeping application resources governed by private routing and security policy.

---

## Hybrid Connectivity

The hybrid path combined AWS Site-to-Site VPN components with a StrongSwan IPsec endpoint on the customer side.

```mermaid
sequenceDiagram
    participant Admin as Administration VLAN
    participant Router as Edge Router
    participant StrongSwan as StrongSwan VPN Endpoint
    participant AWSVPN as AWS Site-to-Site VPN
    participant App as Private AWS Application

    Admin->>Router: Private application traffic
    Router->>StrongSwan: Route without source NAT
    StrongSwan->>AWSVPN: Encrypt with IPsec
    AWSVPN->>App: Deliver private traffic
    App-->>AWSVPN: Response
    AWSVPN-->>StrongSwan: Encrypted return traffic
    StrongSwan-->>Router: Decrypt and route
    Router-->>Admin: Return response
```

A key implementation decision was preserving the original private source network across the VPN. This allowed cloud-side security controls to distinguish authorized Administration traffic from restricted Operations traffic instead of treating all VPN traffic as one trusted source.

---

## Security Model

The design used layered controls rather than relying on the VPN alone:

- **VLAN segmentation** separated local trust zones.
- **ACLs** enforced source-based policy at the local router.
- **No-NAT VPN routing** preserved source identity across the hybrid path.
- **AWS Security Groups** limited access to cloud workloads.
- **Public/private subnet separation** reduced unnecessary exposure.
- **IPsec encryption** protected traffic crossing the hybrid boundary.
- **Validation of denied traffic** confirmed that connectivity did not equal unrestricted trust.

The strongest security validation used the same private AWS application destination with two different local source networks. The authorized source succeeded while the restricted source was blocked, demonstrating policy enforcement across the hybrid boundary.

See [Security Controls](docs/security-controls.md) for additional detail.

---

## Functional Validation

The original TYN1 capstone functionality report documents **eight specific historical test cases**, each with a reported PASS result. The summary below follows those original TC numbers; it does **not** mean the network is live today. See the [test-case traceability guide](docs/tyn1-test-case-traceability.md) for the generalized verification steps and evidence limitations.

| Original test case | Historical validation focus | Reported outcome |
|---|---|---|
| TC1 — Local Layer 2 segmentation | VLAN membership, 802.1Q trunks, same-VLAN communication | PASS |
| TC2 — Local addressing and external routing | DHCP, static server addressing, routing, general outbound NAT | PASS |
| TC3 — Local source-based access control | Administration allowed; Operations restricted to the same local server | PASS |
| TC4 — AWS subnet segmentation | VPC subnets, EC2 workload placement, approved web-to-app flow | PASS |
| TC5 — AWS web external access | Web response, internal app proxying, verified Elastic IP | PASS |
| TC6 — AWS cloud access control | App TCP service allowed; unauthorized TCP/22 access blocked | PASS |
| TC7 — Hybrid IPsec VPN | Terraform VPN plan, tunnel status, private reachability, encrypted counters | PASS |
| TC8 — Hybrid source-aware security | Applied security-group policy, Administration allowed; Operations denied | PASS |

The historical VPN validation went beyond checking whether configuration objects existed. The original report documents:

- an established and installed IPsec security association,
- AWS reporting the active VPN tunnel as operational,
- successful reachability to private AWS workloads,
- encrypted packet and byte counters increasing during data-plane tests, and
- preserved configuration state in version control.

**VPN limitation:** One tunnel was UP during the original validation; the second AWS-provided tunnel remained DOWN. Dual-tunnel failover and production availability were **not** verified.

See [Validation Strategy](docs/validation.md) for the public testing methodology.

---

## Troubleshooting & Recovery Mindset

The project required more than initial configuration. The engineering process emphasized recovery and evidence:

1. Validate the intended state before changing configuration.
2. Isolate Layer 2, Layer 3, NAT, ACL, VPN, and cloud security behavior independently.
3. Confirm both control-plane state and data-plane traffic.
4. Verify successful traffic and intentional denial conditions.
5. Re-test after remediation instead of assuming configuration changes succeeded.
6. Preserve known-good milestones in version control.

This approach helped separate routing problems from security-policy problems and VPN negotiation from actual encrypted application traffic.

---

## Technologies & Skills Demonstrated

**AWS**  
VPC • EC2 • Security Groups • Site-to-Site VPN • Virtual Private Gateway • Customer Gateway Concepts • Public/Private Network Design

**Networking**  
VLANs • 802.1Q • DHCP • NAT • ACLs • Inter-VLAN Routing • Static Routing • IPsec • Source-Based Policy • Network Segmentation

**Lab & Operations**  
GNS3 • StrongSwan • Linux Networking • Connectivity Testing • Failure Isolation • Recovery Validation

**Engineering Workflow**  
Git • GitLab • Configuration Checkpoints • Evidence-Based Testing • Technical Documentation • Architecture Design

---

## Key Engineering Lessons

### A VPN Is Connectivity, Not Trust

Establishing an encrypted tunnel should not automatically grant every connected network access to every cloud workload. Source-aware controls were preserved and tested across the hybrid boundary.

### Control Plane and Data Plane Must Both Be Verified

A tunnel reporting `UP` does not prove application traffic is actually crossing it. Validation included private workload reachability and nonzero encrypted traffic counters.

### Denied Traffic Is Evidence Too

A security design is not validated only by successful pings. Intentional failure from a restricted source demonstrated that segmentation and access-control rules were doing useful work.

### Address Translation Can Break Security Intent

Preserving original private source addressing across the VPN was necessary for downstream policy decisions. A blanket NAT design would have obscured source identity.

### Version Control Supports Recovery

Configuration checkpoints provided a repeatable recovery path after topology and security changes and made the implementation easier to reproduce and audit.

---

## Repository Structure

```text
hybrid-cloud-network-engineering-capstone/
├── README.md
├── docs/
│   ├── architecture.md
│   ├── security-controls.md
│   ├── validation.md
│   ├── tyn1-test-case-traceability.md
│   ├── lessons-learned.md
│   └── requirements-evidence.md
├── portfolio_demo/
│   ├── sample_design.json
│   ├── validate_design.py
│   ├── sample_access_policy.json
│   └── verify_access_policy.py
├── tests/
│   ├── test_design_validator.py
│   └── test_access_policy.py
└── .github/workflows/
    └── verify-network-design.yml
```

---

## Academic & Publication Note

This project originated as a university capstone and was officially evaluated as passing. This public repository intentionally documents only the engineering concepts, architecture, sanitized implementation decisions, validation strategy, and lessons learned that are appropriate for a professional portfolio.

It does **not** publish:

- assessment instructions or rubrics,
- evaluator feedback,
- student identifiers,
- lab credentials or secrets,
- institution-provided configuration files,
- restricted source materials,
- original submission screenshots, or
- any content that would allow the academic assessment to be reconstructed as a solution package.

---

## Next Steps

Potential independent extensions to this architecture include:

- Rebuild the cloud infrastructure with Terraform modules.
- Add automated configuration validation through CI/CD.
- Add centralized CloudWatch and VPC Flow Log monitoring.
- Add redundant VPN tunnels and explicit failover testing.
- Replace static routing with a dynamic routing design where appropriate.
- Add Infrastructure as Code security scanning.
- Add automated network reachability and policy tests.
- Extend the architecture with containerized workloads or EKS.

---

## Status

**Capstone: Officially Passed**  
**Degree: Conferral Pending**
