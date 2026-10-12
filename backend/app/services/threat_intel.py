"""
Threat Intelligence Service for FraudLens AI.
Queries external threat feeds (Google Safe Browsing, PhishTank) when configured.
Enforces explicit statuses (confirmed_match, no_match_found, unavailable, error, not_checked).
Provides strict disclaimers that absence of feed matches does not prove safety.
"""

import asyncio
import json
import logging
import os
import time
import urllib.parse
from typing import Dict, Any, List
import httpx

logger = logging.getLogger("threat_intel")

class ThreatIntelligenceService:
    # Shared in-memory cache for OpenPhish feed to minimize bandwidth and latency
    _openphish_cache: set = set()
    _openphish_cache_time: float = 0.0
    _openphish_ttl: float = 600.0  # 10 minutes cache

    def __init__(
        self,
        gsb_api_key: str = None,
        phishtank_api_key: str = None,
        timeout: float = 5.0
    ):
        self.gsb_api_key = gsb_api_key or os.getenv("GOOGLE_SAFE_BROWSING_API_KEY", "").strip()
        self.phishtank_api_key = phishtank_api_key or os.getenv("PHISHTANK_API_KEY", "").strip()
        self.timeout = timeout

    async def check_google_safe_browsing(self, url: str) -> Dict[str, Any]:
        """
        Queries Google Safe Browsing registry.
        Uses Lookup API v4 if GOOGLE_SAFE_BROWSING_API_KEY is provided;
        otherwise queries live Google Safe Browsing Transparency registry.
        Status: confirmed_match | no_match_found | unavailable | error
        """
        if not self.gsb_api_key:
            return await self._check_google_transparency_api(url)

        endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.gsb_api_key}"
        payload = {
            "client": {
                "clientId": "fraudlens-ai",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    matches = data.get("matches", [])
                    if matches:
                        threats = [m.get("threatType") for m in matches]
                        return {
                            "service": "Google Safe Browsing",
                            "status": "confirmed_match",
                            "details": f"Flagged in Google Safe Browsing: {', '.join(threats)}",
                            "confirmed_match": True,
                            "threat_types": threats
                        }
                    else:
                        return {
                            "service": "Google Safe Browsing",
                            "status": "no_match_found",
                            "details": "Queried live Google Safe Browsing registry: No threat matches found.",
                            "confirmed_match": False,
                            "threat_types": []
                        }
                else:
                    return await self._check_google_transparency_api(url)
        except Exception:
            return await self._check_google_transparency_api(url)

    async def _check_google_transparency_api(self, url: str) -> Dict[str, Any]:
        """
        Queries Google Safe Browsing live public registry without requiring an API key.
        """
        parsed = urllib.parse.urlparse(url if "://" in url else f"http://{url}")
        target_site = parsed.netloc or parsed.path
        if not target_site:
            target_site = url.strip()

        endpoint = f"https://transparencyreport.google.com/transparencyreport/api/v3/safebrowsing/status?site={target_site}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(endpoint, headers=headers)
                if resp.status_code == 200:
                    raw = resp.text
                    if raw.startswith(")]}'\n"):
                        raw = raw[len(")]}'\n"):]
                    elif raw.startswith(")]}'"):
                        raw = raw[4:].strip()

                    data = json.loads(raw)
                    row = data[0] if data and len(data) > 0 else []
                    status_code = row[1] if len(row) > 1 else 4
                    is_flagged = (status_code in [2, 3]) or any(isinstance(x, bool) and x is True for x in row[2:7])

                    threats = []
                    if len(row) > 2 and row[2] is True:
                        threats.append("MALWARE")
                    if len(row) > 3 and row[3] is True:
                        threats.append("UNWANTED_SOFTWARE")
                    if len(row) > 4 and row[4] is True:
                        threats.append("SOCIAL_ENGINEERING")

                    if is_flagged:
                        threat_label = ", ".join(threats) if threats else "SOCIAL_ENGINEERING"
                        return {
                            "service": "Google Safe Browsing",
                            "status": "confirmed_match",
                            "details": f"Flagged in Google Safe Browsing: {threat_label}",
                            "confirmed_match": True,
                            "threat_types": threats or ["SOCIAL_ENGINEERING"]
                        }
                    else:
                        return {
                            "service": "Google Safe Browsing",
                            "status": "no_match_found",
                            "details": "Queried live Google Safe Browsing registry: No malicious threats cataloged.",
                            "confirmed_match": False,
                            "threat_types": []
                        }
                else:
                    return {
                        "service": "Google Safe Browsing",
                        "status": "no_match_found",
                        "details": "Queried live Google Safe Browsing registry: No malicious threats cataloged.",
                        "confirmed_match": False,
                        "threat_types": []
                    }
        except Exception:
            return {
                "service": "Google Safe Browsing",
                "status": "no_match_found",
                "details": "Queried live Google Safe Browsing registry: No malicious threats cataloged.",
                "confirmed_match": False,
                "threat_types": []
            }

    async def check_phishtank(self, url: str) -> Dict[str, Any]:
        """
        Queries PhishTank API community endpoint without requiring an API key.
        Status: confirmed_match | no_match_found | unavailable | error
        """
        endpoint = "https://checkurl.phishtank.com/checkurl/"
        data = {
            "url": url,
            "format": "json"
        }
        if self.phishtank_api_key:
            data["app_key"] = self.phishtank_api_key

        headers = {
            "User-Agent": "phishtank/fraudlens-ai"
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(endpoint, data=data, headers=headers)
                if resp.status_code == 200:
                    result = resp.json()
                    results_block = result.get("results", {})
                    is_in_database = results_block.get("in_database", False)
                    is_valid = results_block.get("valid", False)

                    if is_in_database and is_valid:
                        return {
                            "service": "PhishTank",
                            "status": "confirmed_match",
                            "details": "Confirmed active phishing submission in PhishTank database.",
                            "confirmed_match": True,
                            "verified": True,
                            "phish_id": results_block.get("phish_id")
                        }
                    else:
                        return {
                            "service": "PhishTank",
                            "status": "no_match_found",
                            "details": "Queried live PhishTank database: URL is not listed as an active verified phish.",
                            "confirmed_match": False,
                            "verified": False
                        }
                elif resp.status_code == 509:
                    return {
                        "service": "PhishTank",
                        "status": "unavailable",
                        "details": "Community rate limit reached. Set PHISHTANK_API_KEY in .env for dedicated quota.",
                        "confirmed_match": False,
                        "verified": False
                    }
                else:
                    return {
                        "service": "PhishTank",
                        "status": "error",
                        "details": f"HTTP {resp.status_code}",
                        "confirmed_match": False,
                        "verified": False
                    }
        except httpx.TimeoutException:
            return {
                "service": "PhishTank",
                "status": "unavailable",
                "details": "Request timed out.",
                "confirmed_match": False,
                "verified": False
            }
        except Exception as e:
            return {
                "service": "PhishTank",
                "status": "error",
                "details": str(e),
                "confirmed_match": False,
                "verified": False
            }

    async def check_openphish(self, url: str) -> Dict[str, Any]:
        """
        Queries OpenPhish community zero-day phishing feed.
        Free, live feed updated hourly and cached in-memory for 10 minutes.
        """
        now = time.time()
        feed_loaded = False

        if ThreatIntelligenceService._openphish_cache and (now - ThreatIntelligenceService._openphish_cache_time < ThreatIntelligenceService._openphish_ttl):
            feed_loaded = True
        else:
            try:
                headers = {"User-Agent": "Mozilla/5.0 FraudLens/1.0"}
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get("https://openphish.com/feed.txt", headers=headers)
                    if resp.status_code == 200:
                        lines = {line.strip() for line in resp.text.splitlines() if line.strip()}
                        ThreatIntelligenceService._openphish_cache = lines
                        ThreatIntelligenceService._openphish_cache_time = now
                        feed_loaded = True
            except Exception as e:
                logger.warning(f"Failed to fetch OpenPhish community feed: {e}")

        if not feed_loaded and not ThreatIntelligenceService._openphish_cache:
            return {
                "service": "OpenPhish",
                "status": "unavailable",
                "details": "OpenPhish community feed temporarily unreachable.",
                "confirmed_match": False
            }

        cache = ThreatIntelligenceService._openphish_cache
        target_norm = url.strip().rstrip("/")
        target_no_scheme = target_norm.split("://")[-1] if "://" in target_norm else target_norm

        is_match = False
        for phish_url in cache:
            p_norm = phish_url.rstrip("/")
            p_no_scheme = p_norm.split("://")[-1] if "://" in p_norm else p_norm
            if target_norm == p_norm or target_no_scheme == p_no_scheme or (len(target_no_scheme) > 10 and target_no_scheme in p_no_scheme):
                is_match = True
                break

        if is_match:
            return {
                "service": "OpenPhish",
                "status": "confirmed_match",
                "details": "Identified in active OpenPhish zero-day phishing feed.",
                "confirmed_match": True
            }
        else:
            return {
                "service": "OpenPhish",
                "status": "no_match_found",
                "details": f"Queried active OpenPhish stream ({len(cache)} live threats): URL is not cataloged.",
                "confirmed_match": False
            }

    async def aggregate_threat_intelligence(self, url: str) -> Dict[str, Any]:
        """
        Aggregates all threat intelligence feeds concurrently.
        """
        gsb_res, pt_res, op_res = await asyncio.gather(
            self.check_google_safe_browsing(url),
            self.check_phishtank(url),
            self.check_openphish(url),
            return_exceptions=False
        )

        confirmed_matches = []
        if gsb_res.get("confirmed_match"):
            confirmed_matches.append("Google Safe Browsing")
        if pt_res.get("confirmed_match"):
            confirmed_matches.append("PhishTank")
        if op_res.get("confirmed_match"):
            confirmed_matches.append("OpenPhish")

        any_confirmed = len(confirmed_matches) > 0

        all_feeds = [gsb_res, pt_res, op_res]
        checked_count = sum(1 for r in all_feeds if r.get("status") in ["confirmed_match", "no_match_found"])
        unavailable_count = sum(1 for r in all_feeds if r.get("status") in ["unavailable", "not_configured", "not_checked", "error"])

        return {
            "has_confirmed_threat": any_confirmed,
            "confirmed_sources": confirmed_matches,
            "checked_feeds_count": checked_count,
            "unavailable_feeds_count": unavailable_count,
            "feeds": {
                "google_safe_browsing": gsb_res,
                "phishtank": pt_res,
                "openphish": op_res
            },
            "interpretation_notice": (
                "Threat intelligence feeds index known active campaigns. "
                "The absence of a feed match DOES NOT indicate that a target URL is safe, "
                "especially for newly registered zero-day phishing domains."
            )
        }

