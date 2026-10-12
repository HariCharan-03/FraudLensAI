"""
Unit tests for SSRF mitigation and secure URL handling.
"""

import pytest
from app.security.ssrf import is_ip_disallowed, validate_url_scheme, safe_resolve_hostname

def test_scheme_validation_accepts_http_https():
    assert validate_url_scheme("https://example.com") == "https"
    assert validate_url_scheme("http://example.com") == "http"

def test_scheme_validation_rejects_unsupported():
    with pytest.raises(ValueError):
        validate_url_scheme("file:///etc/passwd")

    with pytest.raises(ValueError):
        validate_url_scheme("ftp://internal.repo")

    with pytest.raises(ValueError):
        validate_url_scheme("javascript:alert(1)")

def test_is_ip_disallowed_blocks_private_and_metadata():
    # Loopback
    assert is_ip_disallowed("127.0.0.1") is True
    assert is_ip_disallowed("127.0.0.2") is True
    assert is_ip_disallowed("::1") is True

    # Cloud Metadata (AWS, GCP, Azure)
    assert is_ip_disallowed("169.254.169.254") is True

    # RFC 1918 Private
    assert is_ip_disallowed("10.0.0.1") is True
    assert is_ip_disallowed("172.16.0.1") is True
    assert is_ip_disallowed("192.168.1.1") is True

    # Public IP
    assert is_ip_disallowed("8.8.8.8") is False
    assert is_ip_disallowed("1.1.1.1") is False

def test_safe_resolve_blocks_ip_literal():
    ips, err = safe_resolve_hostname("127.0.0.1")
    assert not ips
    assert "restricted" in err
