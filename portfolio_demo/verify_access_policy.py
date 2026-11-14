#!/usr/bin/env python3
"""Check an invented allowlist policy against expected traffic outcomes.

This offline educational model does NOT query or enforce AWS security groups,
VPN routing, router ACLs, or live connectivity. It is not coursework source.
"""

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any


def _nonempty(value: Any, label: str, errors: list[str]) -> str | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: expected a non-empty string")
        return None
    return value.strip()


def _port(value: Any, label: str, errors: list[str]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 65535:
        errors.append(f"{label}: expected integer port 1-65535")
        return None
    return value


def _protocol(value: Any, label: str, errors: list[str]) -> str | None:
    if value not in ("tcp", "udp"):
        errors.append(f"{label}: protocol must be 'tcp' or 'udp'")
        return None
    return value


def _ipv4_network(value: Any, label: str, errors: list[str]) -> ipaddress.IPv4Network | None:
    try:
        if not isinstance(value, str):
            raise ValueError("expected an IPv4 CIDR string")
        return ipaddress.IPv4Network(value, strict=True)
    except ValueError as exc:
        errors.append(f"{label}: invalid IPv4 network ({exc})")
        return None


def _ipv4_address(value: Any, label: str, errors: list[str]) -> ipaddress.IPv4Address | None:
    try:
        if not isinstance(value, str):
            raise ValueError("expected an IPv4 address string")
        return ipaddress.IPv4Address(value)
    except ValueError as exc:
        errors.append(f"{label}: invalid IPv4 address ({exc})")
        return None


def verify_policy(data: Any) -> tuple[list[tuple[str, str, str]], list[str]]:
    """Return (scenario results, validation/errors); fail closed on invalid models.

    Rules are permit-only entries; all unmatched traffic is DENY by default.
    Tests assert *model intent*, not observed traffic across a real network.
    """
    errors: list[str] = []
    if not isinstance(data, dict):
        return [], ["document: expected an object"]
    rules = data.get("allow_rules")
    scenarios = data.get("scenarios")
    if not isinstance(rules, list):
        errors.append("document: 'allow_rules' must be a list")
        rules = []
    if not isinstance(scenarios, list) or not scenarios:
        errors.append("document: 'scenarios' must be a non-empty list")
        scenarios = []

    permitted = []
    for i, rule in enumerate(rules):
        label = f"allow_rules[{i}]"
        if not isinstance(rule, dict):
            errors.append(f"{label}: expected an object")
            continue
        subnet = _ipv4_network(rule.get("source_cidr"), f"{label}.source_cidr", errors)
        target = _nonempty(rule.get("destination"), f"{label}.destination", errors)
        protocol = _protocol(rule.get("protocol"), f"{label}.protocol", errors)
        port = _port(rule.get("port"), f"{label}.port", errors)
        if subnet == ipaddress.IPv4Network("0.0.0.0/0"):
            errors.append(f"{label}: world-open source is prohibited by this private-service example")
        if None not in (subnet, target, protocol, port):
            permitted.append((subnet, target, protocol, port))

    requests = []
    seen_names: set[str] = set()
    for i, case in enumerate(scenarios):
        label = f"scenarios[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{label}: expected an object")
            continue
        name = _nonempty(case.get("name"), f"{label}.name", errors)
        if name is not None:
            if name in seen_names:
                errors.append(f"{label}: duplicate scenario name '{name}'")
            seen_names.add(name)
        source = _ipv4_address(case.get("source_ip"), f"{label}.source_ip", errors)
        target = _nonempty(case.get("destination"), f"{label}.destination", errors)
        protocol = _protocol(case.get("protocol"), f"{label}.protocol", errors)
        port = _port(case.get("port"), f"{label}.port", errors)
        expected = case.get("expected")
        if expected not in ("ALLOW", "DENY"):
            errors.append(f"{label}.expected: must be 'ALLOW' or 'DENY'")
        if None not in (name, source, target, protocol, port) and expected in ("ALLOW", "DENY"):
            requests.append((name, source, target, protocol, port, expected))

    if errors:
        return [], errors

    results: list[tuple[str, str, str]] = []
    for name, source, target, protocol, port, expected in requests:
        actual = "ALLOW" if any(
            source in subnet and target == dest and protocol == proto and port == allowed_port
            for subnet, dest, proto, allowed_port in permitted
        ) else "DENY"
        results.append((name, expected, actual))
        if actual != expected:
            errors.append(f"{name}: expected {expected}, observed {actual} in policy model")
    return results, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("policy", type=Path, help="Path to synthetic policy/scenarios JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.policy.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot read policy model: {exc}")
        return 2
    results, errors = verify_policy(data)
    for name, expected, actual in results:
        print(f"{name}: expected={expected}, modeled={actual}")
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print(f"PASS: {len(results)} synthetic access scenarios matched expected policy intent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
