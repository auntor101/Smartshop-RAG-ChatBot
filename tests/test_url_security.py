"""Tests for URL ingestion SSRF guards."""

from __future__ import annotations

import pytest

from src.config import reset_settings
from src.url_security import assert_url_safe_for_fetch


def test_blocks_literal_loopback_ip() -> None:
    with pytest.raises(ValueError, match="not allowed"):
        assert_url_safe_for_fetch("http://127.0.0.1/")


def test_blocks_non_http_scheme() -> None:
    with pytest.raises(ValueError, match="Only http"):
        assert_url_safe_for_fetch("file:///etc/passwd")


def test_allowlist_enforced(monkeypatch) -> None:
    monkeypatch.setenv("URL_ALLOWLIST", "good.example.com")
    reset_settings()
    with pytest.raises(ValueError, match="allowlist"):
        assert_url_safe_for_fetch("https://evil.example.com/")
    # Would still need DNS + fetch for success; allowlist match only checks host string
    # Private IP resolution is tested below.
    reset_settings()


def test_blocks_when_dns_resolves_to_private(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.url_security.socket.getaddrinfo",
        lambda *args, **kwargs: [
            (0, 0, 0, "", ("10.0.0.1", 0)),
        ],
    )
    with pytest.raises(ValueError, match="disallowed"):
        assert_url_safe_for_fetch("https://public-looking.example/")
