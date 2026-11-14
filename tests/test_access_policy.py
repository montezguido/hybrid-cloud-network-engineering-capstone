"""Unit tests for an independent policy-intent verification exercise."""

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "portfolio_demo"))
from verify_access_policy import verify_policy  # noqa: E402

SAMPLE = Path(__file__).resolve().parents[1] / "portfolio_demo" / "sample_access_policy.json"


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(SAMPLE.read_text(encoding="utf-8"))

    def verify_error(self, needle):
        _, errors = verify_policy(self.document)
        self.assertTrue(any(needle in error for error in errors), errors)

    def test_baseline_scenarios(self):
        results, errors = verify_policy(self.document)
        self.assertEqual(errors, [])
        self.assertEqual(len(results), 5)
        self.assertTrue(all(expected == actual for _, expected, actual in results))

    def test_default_deny_without_rules(self):
        self.document["allow_rules"] = []
        self.document["scenarios"] = [self.document["scenarios"][1]]
        self.assertEqual(verify_policy(self.document)[1], [])

    def test_unexpected_authorization_detected(self):
        self.document["allow_rules"][0]["source_cidr"] = "10.88.0.0/16"
        self.verify_error("operations-app-denied: expected DENY, observed ALLOW")

    def test_missing_allow_is_detected(self):
        self.document["allow_rules"] = []
        self.verify_error("administration-app-allowed: expected ALLOW, observed DENY")

    def test_invalid_rule_cidr(self):
        self.document["allow_rules"][0]["source_cidr"] = "bogus"
        self.verify_error("invalid IPv4 network")

    def test_world_open_source_rejected(self):
        self.document["allow_rules"][0]["source_cidr"] = "0.0.0.0/0"
        self.verify_error("world-open")

    def test_invalid_source_address(self):
        self.document["scenarios"][0]["source_ip"] = "not-an-address"
        self.verify_error("invalid IPv4 address")

    def test_invalid_port_bool(self):
        self.document["allow_rules"][0]["port"] = True
        self.verify_error("integer port")

    def test_invalid_protocol(self):
        self.document["allow_rules"][0]["protocol"] = "icmp"
        self.verify_error("protocol must be")

    def test_duplicate_scenarios(self):
        self.document["scenarios"].append(copy.deepcopy(self.document["scenarios"][0]))
        self.verify_error("duplicate scenario name")

    def test_missing_scenarios(self):
        self.document["scenarios"] = []
        self.verify_error("non-empty list")

    def test_non_dict_rule(self):
        self.document["allow_rules"] = [None]
        self.verify_error("expected an object")

    def test_non_dict_document(self):
        self.assertTrue(verify_policy([])[1])

    def test_wrong_destination_blocks_access(self):
        self.document["scenarios"][0]["destination"] = "other-app"
        self.verify_error("administration-app-allowed: expected ALLOW, observed DENY")


if __name__ == "__main__":
    unittest.main()
