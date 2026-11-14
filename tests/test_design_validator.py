"""Regression checks for the independent, synthetic network-design validator."""

import copy
import json
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "portfolio_demo"))
from validate_design import validate_design  # noqa: E402

SAMPLE = Path(__file__).resolve().parents[1] / "portfolio_demo" / "sample_design.json"


class NetworkDesignTests(unittest.TestCase):
    def setUp(self):
        self.design = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def test_valid_example(self):
        self.assertEqual(validate_design(self.design), [])

    def test_missing_vpcs(self):
        self.assertTrue(validate_design({}))

    def test_duplicate_vpc(self):
        duplicate = copy.deepcopy(self.design["vpcs"][0])
        self.design["vpcs"].append(duplicate)
        self.assertTrue(any("duplicate VPC" in x for x in validate_design(self.design)))

    def test_overlapping_vpcs(self):
        duplicate = copy.deepcopy(self.design["vpcs"][0])
        duplicate["name"] = "example-west"
        self.design["vpcs"].append(duplicate)
        self.assertTrue(any("VPC CIDR overlaps" in x for x in validate_design(self.design)))

    def test_overlapping_subnets(self):
        self.design["vpcs"][0]["subnets"][1]["cidr"] = "172.22.1.0/24"
        self.assertTrue(any("subnet overlaps" in x for x in validate_design(self.design)))

    def test_subnet_outside_vpc(self):
        self.design["vpcs"][0]["subnets"][1]["cidr"] = "192.0.2.0/24"
        self.assertTrue(any("outside parent VPC" in x for x in validate_design(self.design)))

    def test_private_igw_route(self):
        self.design["vpcs"][0]["subnets"][1]["route_to_igw"] = True
        self.assertTrue(any("should not route directly" in x for x in validate_design(self.design)))

    def test_private_auto_public_ip(self):
        self.design["vpcs"][0]["subnets"][1]["public_ip_on_launch"] = True
        self.assertTrue(any("should not auto-assign" in x for x in validate_design(self.design)))

    def test_invalid_cidr(self):
        self.design["vpcs"][0]["subnets"][0]["cidr"] = "invalid"
        self.assertTrue(any("invalid IPv4 CIDR" in x for x in validate_design(self.design)))

    def test_invalid_boolean(self):
        self.design["vpcs"][0]["subnets"][0]["route_to_igw"] = "yes"
        self.assertTrue(any("must be a boolean" in x for x in validate_design(self.design)))


if __name__ == "__main__":
    unittest.main()
