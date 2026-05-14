"""Safe HTTP fetch helpers to reduce SSRF risk for URL ingestion."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests

from .config import get_settings

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "metadata.google.internal",
    }
)


def _is_blocked_hostname(hostname: str) -> bool:
    h = hostname.lower().strip(".")
    if h in _BLOCKED_HOSTNAMES:
        return True
    if h.endswith(".localhost") or h.endswith(".local"):
        return True
    return False


def _resolve_host_ips(hostname: str) -> list[str]:
    """Resolve hostname to IP strings (IPv4/IPv6)."""
    ips: list[str] = []
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve host: {hostname}") from exc
    for _fam, _typ, _proto, _canon, sockaddr in infos:
        ip_str = sockaddr[0]
        if ip_str not in ips:
            ips.append(ip_str)
    if not ips:
        raise ValueError(f"No addresses for host: {hostname}")
    return ips


def _ip_is_forbidden(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if addr.is_loopback or addr.is_link_local or addr.is_private or addr.is_reserved:
        return True
    if addr.is_multicast or addr.is_unspecified:
        return True
    return False


def assert_url_safe_for_fetch(url: str) -> None:
    """Raise ValueError if URL scheme/host is not allowed or resolves to forbidden IPs."""
    settings = get_settings()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https URLs are allowed.")
    if not parsed.hostname:
        raise ValueError("URL must include a hostname.")
    host = parsed.hostname
    if _is_blocked_hostname(host):
        raise ValueError("This hostname is not allowed.")

    allow = settings.url_allowlist_hosts
    if allow:
        host_l = host.lower()
        if not any(
            host_l == d.lower() or host_l.endswith("." + d.lower()) for d in allow
        ):
            raise ValueError("URL host is not in the configured allowlist.")

    for ip_str in _resolve_host_ips(host):
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if _ip_is_forbidden(addr):
            raise ValueError("URL resolves to a disallowed network address.")


def fetch_url_bytes(url: str) -> tuple[bytes, str]:
    """GET URL with redirect cap, response size cap, and SSRF checks on each hop.

    Returns (body_bytes, final_url).
    """
    settings = get_settings()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; RAGBot/1.0; +https://example.com/bot)"
        )
    }
    current = url
    max_redir = settings.max_url_redirects
    timeout = settings.url_fetch_timeout_seconds

    for _ in range(max_redir + 1):
        assert_url_safe_for_fetch(current)
        resp = requests.get(
            current,
            headers=headers,
            timeout=timeout,
            allow_redirects=False,
            stream=True,
        )
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("location") or resp.headers.get("Location")
            if not loc:
                raise ValueError("Redirect without Location header.")
            current = urljoin(current, loc)
            resp.close()
            continue
        resp.raise_for_status()
        chunks: list[bytes] = []
        total = 0
        for chunk in resp.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > settings.max_url_fetch_bytes:
                resp.close()
                raise ValueError("Response exceeds maximum allowed size.")
            chunks.append(chunk)
        resp.close()
        return b"".join(chunks), current

    raise ValueError("Too many redirects.")
