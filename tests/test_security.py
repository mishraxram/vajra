import socket
import unittest
from unittest.mock import patch

from vajra.security import UnsafeURLError, validate_public_http_url


class URLValidationTests(unittest.TestCase):
    @patch("vajra.security.socket.getaddrinfo")
    def test_rejects_private_dns_answer(self, resolver):
        resolver.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.8", 443))]
        with self.assertRaises(UnsafeURLError):
            validate_public_http_url("https://research.example/path")

    @patch("vajra.security.socket.getaddrinfo")
    def test_accepts_public_dns_answer(self, resolver):
        resolver.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]
        self.assertEqual(validate_public_http_url("https://research.example/path"), "https://research.example/path")

    def test_rejects_local_ip_schemes_and_url_credentials(self):
        for url in ("http://127.0.0.1/", "file:///etc/passwd", "https://user:pass@example.org/"):
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                validate_public_http_url(url)


if __name__ == "__main__":
    unittest.main()

