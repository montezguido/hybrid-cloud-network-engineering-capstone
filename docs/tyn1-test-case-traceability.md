# Original Capstone: Test-Case Traceability

This guide summarizes the **eight individual test cases in the privately retained ClearPath TYN1 Capstone Functionality Report**. The source is the completed academic report, not an always-running AWS environment. It includes test descriptions, captured outputs, and an individually reported **PASS** outcome for each case. The original assessment report and screenshots are intentionally **not republished**.

The separately developed portfolio validators in this repository do **not** recreate the school lab or run AWS VPN tests.

## Historical implementation and test results

| Original test case | Tested requirement | Generalized validation evidence recorded in the private report | Reported outcome |
|---|---|---|---|
| **TC1 — Local Layer 2 segmentation** | Separate local users and services while preserving needed switch-to-switch connectivity | Three functional VLANs, tagged 802.1Q trunk checks on two switches, same-VLAN ICMP reachability | PASS |
| **TC2 — Local addressing and external routing** | Provide DHCP to user segments, static service addressing, routed access, and outbound connectivity | DHCP scope/lease checks, static server address and gateway, routed client-to-server reachability, default route and outbound source NAT | PASS |
| **TC3 — Local reachability security** | Permit a selected local source and restrict another to the *same* server | Router forward-filter inspection; Administration ICMP succeeded while Operations ICMP was denied | PASS |
| **TC4 — AWS subnet segmentation** | Separate AWS web and application workloads into appropriate network tiers while retaining their required connectivity | VPC/subnet inspection, actual EC2 subnet placement, successful cross-subnet web-to-app flow | PASS |
| **TC5 — AWS external access and tier routing** | Expose the intended web tier and reach the application tier privately | Public web response, private web-to-application reverse-proxy response, assigned and verified static Elastic IP | PASS |
| **TC6 — AWS cloud access-control behavior** | Permit required web-to-app traffic while preventing unauthorized application access | A temporary test source reached the private app on the approved TCP application port; SSH-port connection failed; AWS application security group authorized only the necessary source/service; test resource later removed | PASS |
| **TC7 — Encrypted hybrid Site-to-Site VPN** | Establish a private on-premises-to-AWS path with evidence of traffic traversal | Terraform VPN/routing plan, StrongSwan ESTABLISHED and INSTALLED SA, AWS tunnel UP, private workload pings succeeding, and nonzero encrypted byte/packet counters; Git checkpoint | PASS |
| **TC8 — Source-aware hybrid security** | Allow Administration and restrict Operations across the *same* VPN to the *same* private app | Terraform in-place security-group change plan, applied AWS group inspection, Administration ICMP succeeded and Operations ICMP failed, VPN counters confirmed encrypted path activity | PASS |

**Result classification:** These are documented PASS outcomes in a historical academic report. They are **not rerun in this repository**, and the original evaluator document is not hosted publicly. A failed ICMP test is most convincing when examined alongside the policy, common destination, known-good allowed source, and tunnel state, as this report did.

## Technical decisions a hiring manager can probe

### 1. Routing and source preservation
The enterprise environment used separate Layer 2 VLANs, routed user/service access, and outbound NAT for general external traffic. For private VPN destinations, the design preserved the original internal source addressing so AWS policy could distinguish approved and restricted network segments. Outbound NAT and VPN no-NAT were **different paths**; the original report documents both.

### 2. AWS application tiers
The application workload had private addressing and was reached through the web tier for approved application traffic. The cloud security test was **not** merely a different-subnet check: it used the same application destination with a permitted TCP application port and an unpermitted SSH port, then inspected the supporting security-group policy.

### 3. VPN control plane *and* data plane
The historical test combined the customer-side StrongSwan SA, AWS tunnel state, private-IP reachability, and IPsec traffic counters. The original report also documented Terraform planning of VPN components and an in-place Security Group update.

### 4. Real limitation: no tested VPN redundancy
The report states that **one AWS-provided tunnel was UP and the other remained DOWN** during the validation. The capstone demonstrated a working single active IPsec path, **not dual-tunnel failover or production high availability**. Dynamic routing, redundant tunnel recovery, and automated deployment validation are opportunities for future independent work.

## Evidence separation and safety

- **Historical evidence (private):** original TYN1 report, screenshots, AWS account-specific values, school lab devices, original GitLab history, and assessment details.
- **Public historical summary:** [architecture](architecture.md), [security decisions](security-controls.md), and [validation](validation.md).
- **Independent executable demonstration:** [synthetic network design validator](../portfolio_demo/validate_design.py), [offline allowlist policy verifier](../portfolio_demo/verify_access_policy.py), and [unit tests](../tests/).
- **Automated verification:** [GitHub Actions](../.github/workflows/verify-network-design.yml) checks the **independent code only**. It does not validate the prior GNS3/AWS network or restore its VPN.

This page intentionally omits the original public tunnel endpoints, private host addresses, school-provided screenshots, raw policies, and institutional assessment instructions.

## Interview-ready explanation

> In my WGU capstone I built and tested a segmented GNS3-to-AWS hybrid network. I verified DHCP, local routing, AWS two-tier access, and controlled source-to-destination reachability. For the VPN, I checked both StrongSwan and AWS status, confirmed private workload reachability, and inspected encrypted traffic counters. I also used Terraform to plan infrastructure changes and validated that authorized Administration traffic could reach a private application while restricted Operations traffic could not. The project verified one active VPN tunnel; it did not demonstrate production failover. My public repository contains separate, original Python validation exercises rather than the restricted lab files.

**Source note:** Prepared by reviewing the private ClearPath TYN1 capstone functionality report, including its test descriptions and embedded verification figures. The public materials do not independently certify the original school assessment grade.
