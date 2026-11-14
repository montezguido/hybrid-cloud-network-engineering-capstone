#!/usr/bin/env python3
"""Validate a synthetic AWS-style network design; no AWS API calls are made.

This independent portfolio example is not original university assessment code.
"""

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any


def _network(value: Any, label: str, errors: list[str]) -> ipaddress.IPv4Network | None:
    try:
        if not isinstance(value, str):
            raise ValueError("CIDR must be a string")
        return ipaddress.IPv4Network(value, strict=True)
    except (ValueError, ipaddress.AddressValueError) as exc:
        errors.append(f"{label}: invalid IPv4 CIDR ({exc})")
        return None


def validate_design(data: Any) -> list[str]:
    """Return all detected issues in a declarative, synthetic VPC/subnet model."""
    errors: list[str] = []
    if not isinstance(data, dict) or not isinstance(data.get("vpcs"), list) or not data["vpcs"]:
        return ["document: 'vpcs' must be a non-empty list"]

    seen_vpcs: set[str] = set()
    vpc_ranges: list[tuple[str, ipaddress.IPv4Network]] = []
    for index, vpc in enumerate(data["vpcs"]):
        label = f"vpcs[{index}]"
        if not isinstance(vpc, dict):
            errors.append(f"{label}: expected object")
            continue
        name = vpc.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}: missing non-empty name")
            name = label
        if name in seen_vpcs:
            errors.append(f"{label}: duplicate VPC name '{name}'")
        seen_vpcs.add(name)
        vpc_cidr = _network(vpc.get("cidr"), f"{label}.cidr", errors)
        if vpc_cidr is not None:
            for other_name, other_range in vpc_ranges:
                if vpc_cidr.overlaps(other_range):
                    errors.append(f"{label}: VPC CIDR overlaps '{other_name}'")
            vpc_ranges.append((name, vpc_cidr))

        subnets = vpc.get("subnets")
        if not isinstance(subnets, list) or not subnets:
            errors.append(f"{label}: 'subnets' must be a non-empty list")
            continue
        seen_subnets: set[str] = set()
        ranges: list[tuple[str, ipaddress.IPv4Network]] = []
        for j, subnet in enumerate(subnets):
            slabel = f"{label}.subnets[{j}]"
            if not isinstance(subnet, dict):
                errors.append(f"{slabel}: expected object")
                continue
            subnet_name = subnet.get("name")
            if not isinstance(subnet_name, str) or not subnet_name.strip():
                errors.append(f"{slabel}: missing non-empty name")
                subnet_name = slabel
            if subnet_name in seen_subnets:
                errors.append(f"{slabel}: duplicate subnet name '{subnet_name}'")
            seen_subnets.add(subnet_name)
            subnet_cidr = _network(subnet.get("cidr"), f"{slabel}.cidr", errors)
            if subnet_cidr is not None:
                if vpc_cidr is not None and not subnet_cidr.subnet_of(vpc_cidr):
                    errors.append(f"{slabel}: subnet outside parent VPC")
                for other_name, other_range in ranges:
                    if subnet_cidr.overlaps(other_range):
                        errors.append(f"{slabel}: subnet overlaps '{other_name}'")
                ranges.append((subnet_name, subnet_cidr))
            if not isinstance(subnet.get("az"), str) or not subnet["az"].strip():
                errors.append(f"{slabel}: missing non-empty availability-zone label")
            exposure = subnet.get("exposure")
            if exposure not in ("public", "private"):
                errors.append(f"{slabel}: exposure must be 'public' or 'private'")
            for key in ("route_to_igw", "public_ip_on_launch"):
                if not isinstance(subnet.get(key), bool):
                    errors.append(f"{slabel}: {key} must be a boolean")
            if exposure == "private" and subnet.get("route_to_igw") is True:
                errors.append(f"{slabel}: private subnet should not route directly to an IGW")
            if exposure == "private" and subnet.get("public_ip_on_launch") is True:
                errors.append(f"{slabel}: private subnet should not auto-assign public IPs")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path, help="Path to synthetic design JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.design.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Cannot read design: {exc}")
        return 2
    errors = validate_design(data)
    for error in errors:
        print(f"FAIL: {error}")
    if errors:
        return 1
    print("PASS: synthetic network design checks completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
