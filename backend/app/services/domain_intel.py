"""
Domain Intelligence Service for FraudLens AI.
Collects DNS records, TLS/SSL certificate metadata, and server geolocation
strictly using low-level network handshakes and DNS queries.
Arbitrary HTTP body payloads are NEVER downloaded.
"""

import datetime
import logging
import socket
import ssl
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import dns.resolver
import httpx

from app.security.ssrf import safe_resolve_hostname, is_ip_disallowed

logger = logging.getLogger("domain_intel")

class DomainIntelligenceService:
    def __init__(self, dns_timeout: float = 3.0):
        self.dns_timeout = dns_timeout

    def query_dns_records(self, domain: str) -> Dict[str, Any]:
        """
        Queries common DNS record types (A, AAAA, MX, TXT, NS).
        Handles DNS timeouts and non-existent domains gracefully.
        """
        resolver = dns.resolver.Resolver()
        resolver.lifetime = self.dns_timeout
        resolver.timeout = self.dns_timeout

        records: Dict[str, List[str]] = {
            "A": [],
            "AAAA": [],
            "MX": [],
            "TXT": [],
            "NS": []
        }
        status = "no_records"

        for rtype in ["A", "AAAA", "MX", "TXT", "NS"]:
            try:
                answers = resolver.resolve(domain, rtype)
                for rdata in answers:
                    records[rtype].append(str(rdata))
                if records[rtype]:
                    status = "resolved"
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
                continue
            except dns.exception.Timeout:
                logger.debug(f"DNS timeout querying {rtype} for {domain}")
            except Exception as e:
                logger.debug(f"DNS query error ({rtype}): {e}")

        return {
            "status": status,
            "records": records
        }

    def inspect_ssl_certificate(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Performs TLS handshake to inspect certificate without fetching any HTTP body.
        Extracts subject, issuer, validity period, and SANs.
        """
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # inspect even invalid/expired certs to capture evidence

        # Pre-check domain for SSRF before opening TLS socket
        safe_ips, err = safe_resolve_hostname(domain, timeout=self.dns_timeout)
        if err or not safe_ips:
            return {
                "status": "unavailable",
                "error": err or "Hostname could not be safely resolved for TLS handshake."
            }

        target_ip = safe_ips[0]

        try:
            with socket.create_connection((target_ip, port), timeout=3.0) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    cipher = ssock.cipher()
                    version = ssock.version()

                    if not cert_bin:
                        return {"status": "no_certificate"}

                    # Parse cert
                    cert = ssock.getpeercert()
                    if not cert:
                        return {
                            "status": "valid_handshake",
                            "tls_version": version,
                            "cipher": cipher[0] if cipher else None,
                            "note": "TLS handshake completed with unverified certificate."
                        }

                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    subject = dict(x[0] for x in cert.get("subject", []))
                    san = [x[1] for x in cert.get("subjectAltName", []) if x[0] == "DNS"]

                    not_before = cert.get("notBefore")
                    not_after = cert.get("notAfter")

                    # Check expiration
                    is_expired = False
                    if not_after:
                        try:
                            exp_date = datetime.datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                            if datetime.datetime.now(datetime.timezone.utc) > exp_date.replace(tzinfo=datetime.timezone.utc):
                                is_expired = True
                        except Exception:
                            pass

                    return {
                        "status": "valid_certificate",
                        "issuer": issuer.get("organizationName") or issuer.get("commonName", "Unknown"),
                        "subject": subject.get("commonName", domain),
                        "subject_alt_names": san[:8],
                        "valid_from": not_before,
                        "valid_to": not_after,
                        "is_expired": is_expired,
                        "tls_version": version,
                        "cipher": cipher[0] if cipher else None
                    }
        except (socket.timeout, TimeoutError):
            return {"status": "timeout", "error": "TLS handshake timed out on port 443."}
        except ConnectionRefusedError:
            return {"status": "connection_refused", "error": "Port 443 closed or connection refused."}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_server_location(self, ip_address: str) -> Dict[str, Any]:
        """
        Retrieves server geolocation and ISP info for the resolved IP address.
        Uses timeout and validates IP is non-private.
        """
        if is_ip_disallowed(ip_address):
            return {
                "status": "unavailable",
                "error": "IP is a reserved or internal address."
            }

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as")
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success":
                        return {
                            "status": "success",
                            "ip": ip_address,
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "region": data.get("regionName"),
                            "city": data.get("city"),
                            "latitude": data.get("lat"),
                            "longitude": data.get("lon"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "as_number": data.get("as"),
                            "timezone": data.get("timezone")
                        }
        except Exception as e:
            logger.debug(f"GeoIP lookup failed: {e}")

        # Return fallback heuristic structure
        return {
            "status": "unavailable",
            "ip": ip_address,
            "country": "Unknown",
            "city": "Unknown",
            "isp": "Unknown",
            "note": "GeoIP lookup service unreachable or timed out."
        }

    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """
        Runs comprehensive, safe domain intelligence analysis.
        """
        # 1. SSRF safe DNS resolution
        safe_ips, dns_err = safe_resolve_hostname(domain, timeout=self.dns_timeout)

        # 2. DNS record queries
        dns_data = self.query_dns_records(domain)

        # 3. TLS Certificate inspection
        ssl_data = self.inspect_ssl_certificate(domain)

        # 4. Geolocation of primary IP
        primary_ip = safe_ips[0] if safe_ips else None
        geo_data = await self.get_server_location(primary_ip) if primary_ip else {"status": "no_ip"}

        return {
            "domain": domain,
            "resolved_ips": safe_ips,
            "primary_ip": primary_ip,
            "dns_resolution_error": dns_err,
            "dns_records": dns_data["records"],
            "dns_status": dns_data["status"],
            "ssl_certificate": ssl_data,
            "server_location": geo_data
        }
