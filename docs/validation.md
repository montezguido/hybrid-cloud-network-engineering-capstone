# Validation Strategy

## Purpose

The capstone used structured functional testing to prove that the hybrid network behaved as designed. Validation covered successful communication, expected denial conditions, VPN state, encrypted traffic movement, and preserved configuration state.

The public version below summarizes the methodology without reproducing restricted academic test instructions or original submission evidence.

---

## Test Areas

### 1. Layer 2 Segmentation

Validated:

- required VLANs existed,
- trunks carried the intended VLANs,
- same-segment communication behaved correctly.

### 2. Addressing

Validated:

- dynamic addressing for user networks,
- predictable static addressing for infrastructure workloads,
- correct default-gateway behavior.

### 3. Local Routing

Validated:

- inter-VLAN routing,
- expected route selection,
- successful reachability where policy permitted it.

### 4. Local Security Policy

Validated different outcomes for the same protected local resource based on source network.

An authorized source succeeded while a restricted source failed, confirming that router policy—not simple topology—determined access.

### 5. AWS Networking

Validated:

- VPC and subnet segmentation,
- cloud workload placement,
- Security Group behavior,
- private and public reachability according to design.

### 6. External Access

Validated controlled external access to the intended public-facing web workload without requiring public exposure of the private application workload.

### 7. Hybrid VPN

Validation included both control-plane and data-plane evidence:

- StrongSwan showed an established and installed IPsec security association.
- AWS independently reported the active tunnel as operational.
- Private AWS workloads were reachable through private addressing.
- Encrypted packet and byte counters increased after generated traffic.
- Version-control checkpoints preserved the working state.

### 8. Hybrid Security

The same private AWS application destination was tested from different on-premises source networks.

- Authorized Administration traffic reached the application.
- Restricted Operations traffic was blocked.

This proved that security policy remained meaningful across the hybrid boundary.

---

## Validation Philosophy

The project followed several practical testing principles:

1. **Verify state before testing traffic.** Confirm VLANs, routes, tunnel state, and policy configuration first.
2. **Test one layer at a time.** Separate switching, routing, NAT, VPN, and workload-security problems.
3. **Test positive and negative outcomes.** A security control is not proven merely because allowed traffic works.
4. **Check control plane and data plane.** A tunnel can report operational while application traffic still fails.
5. **Re-test after every remediation.** A successful command does not guarantee the intended end state.
6. **Preserve known-good milestones.** Version control provides reproducibility and recovery evidence.

---

## Result Summary

| Validation Area | Outcome |
|---|---|
| Layer 2 segmentation | PASS |
| Addressing | PASS |
| Local routing | PASS |
| Local source-based security | PASS |
| AWS networking and segmentation | PASS |
| Controlled external access | PASS |
| Hybrid IPsec VPN | PASS |
| Hybrid source-based security | PASS |

The completed capstone was officially evaluated as passing.
