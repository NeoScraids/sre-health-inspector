"""
Unit tests for SRE Health Inspector.
"""

import unittest
from src.inspector import check_http_endpoint, check_ssl_certificate


class TestInspector(unittest.TestCase):
    def test_http_endpoint_structure(self):
        result = check_http_endpoint("https://httpbin.org/status/200", timeout=5.0)
        self.assertIn("check", result)
        self.assertIn("status", result)
        self.assertIn("latency_ms", result)

    def test_ssl_certificate_structure(self):
        result = check_ssl_certificate("github.com", port=443, timeout=5.0)
        self.assertIn("check", result)
        self.assertIn("status", result)
        self.assertIn("days_remaining", result)


if __name__ == "__main__":
    unittest.main()
