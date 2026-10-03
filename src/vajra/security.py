from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit


class UnsafeURLError(ValueError):
    pass


def validate_public_http_url(url: str) -> str:
    """Validate a URL before a network fetch; reject local and non-public targets."""
    if not isinstance(url, str) or not url or len(url) > 4096:
        raise UnsafeURLError("URL is missing or too long")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise UnsafeURLError("Malformed URL") from exc
    if parts.scheme.lower() not in {"http", "https"}:
        raise UnsafeURLError("Only http and https URLs are allowed")
    if not parts.hostname or parts.username is not None or parts.password is not None:
        raise UnsafeURLError("URL must have a host and must not contain credentials")
    host = parts.hostname.rstrip(".").lower()
    if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal")):
        raise UnsafeURLError("Local hostnames are not allowed")
    try:
        literal = ipaddress.ip_address(host)
        addresses = [literal]
    except ValueError:
        try:
            answers = socket.getaddrinfo(host, port or (443 if parts.scheme == "https" else 80), type=socket.SOCK_STREAM)
        except OSError as exc:
            raise UnsafeURLError("Host could not be resolved") from exc
        addresses = []
        for answer in answers:
            try:
                addresses.append(ipaddress.ip_address(answer[4][0].split("%", 1)[0]))
            except ValueError as exc:
                raise UnsafeURLError("Host returned an invalid address") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise UnsafeURLError("Host must resolve only to public IP addresses")
    return url

