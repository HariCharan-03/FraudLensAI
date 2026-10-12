"""
Security Safeguards & SSRF Mitigation for FraudLens AI.
Blocks loopback, private, link-local, multicast, cloud metadata addresses,
and reserved IP blocks to protect internal infrastructure.
"""

import ipaddress
import socket
import logging
from typing import Tuple, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger("security_ssrf")

ALLOWED_SCHEMES = {"http", "https"}

# Blocked IP ranges: RFC 1918, loopback, link-local, cloud metadata, multicast, broadcast
DISALLOWED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (only valid as source address)
    ipaddress.ip_network("10.0.0.0/8"),         # Private-use (RFC 1918)
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback (RFC 1122)
    ipaddress.ip_network("169.254.0.0/16"),     # Link-local / AWS/GCP/Azure Cloud Metadata (RFC 3927)
    ipaddress.ip_network("172.16.0.0/12"),      # Private-use (RFC 1918)
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments (RFC 6890)
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay Anycast (RFC 7526)
    ipaddress.ip_network("192.168.0.0/16"),     # Private-use (RFC 1918)
    ipaddress.ip_network("198.18.0.0/15"),      # Network benchmark tests (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast (RFC 5771)
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for future use (RFC 1112)
    ipaddress.ip_network("255.255.255.255/32"), # Broadcast
    # IPv6 blocks
    ipaddress.ip_network("::1/128"),            # IPv6 Loopback
    ipaddress.ip_network("::/128"),             # IPv6 Unspecified
    ipaddress.ip_network("fe80::/10"),          # IPv6 Link-local
    ipaddress.ip_network("fc00::/7"),           # IPv6 Unique Local Address
    ipaddress.ip_network("ff00::/8")            # IPv6 Multicast
]

class SSRFProtectionError(ValueError):
    """Raised when an address resolves to a restricted/private network destination."""
    pass

def validate_url_scheme(url: str) -> str:
    """Ensures URL scheme is strictly http or https."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() if parsed.scheme else "http"
    if scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Unsupported URL scheme '{scheme}'. Only HTTP and HTTPS are permitted.")
    return scheme

def is_ip_disallowed(ip_str: str) -> bool:
    """Checks whether an IP address belongs to any private, loopback, or cloud-metadata network."""
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
            return True
        for net in DISALLOWED_NETWORKS:
            if ip_obj in net:
                return True
        return False
    except ValueError:
        return True

def safe_resolve_hostname(hostname: str, timeout: float = 3.0) -> Tuple[List[str], Optional[str]]:
    """
    Safely resolves a hostname to IP addresses and checks every resolved IP
    against SSRF blocklists to prevent DNS-rebinding attacks.
    Returns: (safe_ips, error_message)
    """
    clean_host = hostname.strip().lower().split(":")[0].strip("[]")
    if not clean_host:
        return [], "Empty hostname"

    # Direct IP literal check
    try:
        ip_obj = ipaddress.ip_address(clean_host)
        if is_ip_disallowed(str(ip_obj)):
            return [], f"Host '{clean_host}' resolves to restricted internal or private address space."
        return [str(ip_obj)], None
    except ValueError:
        pass  # It is a domain name, proceed with DNS resolution

    try:
        # Resolve via getaddrinfo with socket timeout
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(timeout)
        try:
            addr_info = socket.getaddrinfo(clean_host, None)
        finally:
            socket.setdefaulttimeout(old_timeout)

        resolved_ips = list({item[4][0] for item in addr_info if item and item[4]})
        if not resolved_ips:
            return [], "DNS resolution returned no records."

        safe_ips = []
        for ip_addr in resolved_ips:
            if is_ip_disallowed(ip_addr):
                return [], f"Security Alert: Domain '{clean_host}' resolves to restricted internal IP {ip_addr} (SSRF blocked)."
            safe_ips.append(ip_addr)

        return safe_ips, None

    except socket.gaierror as e:
        return [], f"DNS lookup failed: {e}"
    except Exception as e:
        return [], f"DNS resolution error: {str(e)}"
