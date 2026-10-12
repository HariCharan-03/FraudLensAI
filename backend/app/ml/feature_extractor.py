"""
URL Feature Extractor for FraudLens AI.
Extracts strictly URL-only features without making external network requests.
Handles Unicode IDNs, IPv4/IPv6 literals, ports, schemes, query parameters,
and malformed URLs defensively.
"""

import ipaddress
import json
import math
import os
import re
from typing import Dict, Any, Tuple
from urllib.parse import urlparse, parse_qs

# Suspicious keywords frequently observed in phishing attacks
PHISHING_KEYWORDS = [
    "login", "verify", "verification", "secure", "security", "account",
    "update", "banking", "authenticate", "signin", "sign-in", "wallet",
    "password", "credential", "confirm", "support", "billing", "recover"
]

FEATURE_COLUMNS = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
    "CharContinuationRate",
    "URLSimilarityIndex",
    "TLDLegitimateProb",
    "URLCharProb"
]

DEFAULT_TLD_PROBS = {
    "gov": 0.99,
    "edu": 0.98,
    "org": 0.75,
    "mil": 0.99,
    "com": 0.55,
    "net": 0.50,
    "io": 0.60,
    "ai": 0.65,
    "co.uk": 0.70,
    "de": 0.72,
    "in": 0.50,
    "xyz": 0.15,
    "top": 0.10,
    "tk": 0.05,
    "ml": 0.05,
    "ga": 0.05,
    "cf": 0.05,
    "gq": 0.05,
    "work": 0.20,
    "click": 0.18,
    "buzz": 0.15,
    "support": 0.25,
}

class URLFeatureExtractor:
    def __init__(self, tld_probs_path: str = None):
        self.tld_probs = DEFAULT_TLD_PROBS.copy()
        if tld_probs_path and os.path.exists(tld_probs_path):
            try:
                with open(tld_probs_path, "r") as f:
                    loaded = json.load(f)
                    self.tld_probs.update(loaded)
            except Exception:
                pass

    @staticmethod
    def normalize_url(raw_url: str) -> Tuple[str, str, str, str]:
        """
        Normalize and parse raw URL.
        Returns: (normalized_url, scheme, domain, path_and_query)
        """
        raw = raw_url.strip()
        if not raw:
            raise ValueError("URL cannot be empty")

        # Add scheme if missing for robust parsing
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
            normalized = "http://" + raw
        else:
            normalized = raw

        parsed = urlparse(normalized)
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc or parsed.path.split("/")[0]

        # Handle userinfo e.g. user:pass@host
        if "@" in netloc:
            netloc = netloc.split("@")[-1]

        # Handle port
        domain = netloc.split(":")[0].lower()

        # Handle IDN / punycode decode
        try:
            domain = domain.encode("idna").decode("ascii")
        except Exception:
            pass

        path_and_query = parsed.path + ("?" + parsed.query if parsed.query else "")
        return normalized, scheme, domain, path_and_query

    @staticmethod
    def is_ip_address(domain: str) -> int:
        """Checks if domain is an IPv4 or IPv6 address literal."""
        clean = domain.strip("[]")
        try:
            ipaddress.ip_address(clean)
            return 1
        except ValueError:
            return 0

    @staticmethod
    def compute_shannon_entropy(s: str) -> float:
        """Compute Shannon entropy to identify algorithmic randomness."""
        if not s:
            return 0.0
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        return -sum([p * math.log(p) / math.log(2.0) for p in prob])

    @staticmethod
    def compute_char_continuation_rate(url: str) -> float:
        """
        Calculates the character continuation rate:
        ratio of the longest uninterrupted alphanumeric sequence to URL length.
        """
        if not url:
            return 0.0
        tokens = re.findall(r"[a-zA-Z0-9]+", url)
        if not tokens:
            return 0.0
        max_token = max(len(t) for t in tokens)
        return min(1.0, max_token / len(url))

    def extract_features(self, raw_url: str) -> Dict[str, Any]:
        """
        Extract the 22 exact numeric features matching the PhiUSIIL model schema,
        along with heuristic indicators.
        """
        normalized_url, scheme, domain, path_query = self.normalize_url(raw_url)
        url_len = len(normalized_url)
        domain_len = len(domain)

        is_domain_ip = self.is_ip_address(domain)

        # Extract TLD and subdomains
        domain_parts = domain.split(".")
        if len(domain_parts) >= 2:
            tld = domain_parts[-1]
            # handle double TLDs like co.uk
            if len(domain_parts) >= 3 and domain_parts[-2] in ["co", "com", "org", "net", "gov", "edu", "ac"]:
                tld = f"{domain_parts[-2]}.{domain_parts[-1]}"
                subdomains = domain_parts[:-2]
            else:
                subdomains = domain_parts[:-1]
        else:
            tld = ""
            subdomains = []

        tld_length = len(tld)
        no_of_subdomains = max(0, len(subdomains) - 1 if "www" in subdomains else len(subdomains))

        # Obfuscation checks
        obfuscated_matches = re.findall(r"%[0-9a-fA-F]{2}", normalized_url)
        no_of_obfuscated_char = sum(len(m) for m in obfuscated_matches)
        has_obfuscation = 1 if no_of_obfuscated_char > 0 or "@" in normalized_url else 0
        obfuscation_ratio = round(no_of_obfuscated_char / url_len, 4) if url_len > 0 else 0.0

        # Character counts
        letters = re.findall(r"[a-zA-Z]", normalized_url)
        no_of_letters = len(letters)
        letter_ratio = round(no_of_letters / url_len, 4) if url_len > 0 else 0.0

        digits = re.findall(r"[0-9]", normalized_url)
        no_of_digits = len(digits)
        digit_ratio = round(no_of_digits / url_len, 4) if url_len > 0 else 0.0

        no_of_equals = normalized_url.count("=")
        no_of_qmark = normalized_url.count("?")
        no_of_amp = normalized_url.count("&")

        # Other special characters: -, _, /, ., @, ~, :, etc.
        other_special = re.findall(r"[-_/.@~:!#$*+,;]", normalized_url)
        no_of_other_special = len(other_special)
        special_char_ratio = round(no_of_other_special / url_len, 4) if url_len > 0 else 0.0

        is_https = 1 if scheme == "https" else 0

        continuation_rate = round(self.compute_char_continuation_rate(normalized_url), 4)

        # Baseline similarity index (100 is standard benchmark in PhiUSIIL)
        url_similarity_index = 100

        # TLD legitimacy prior
        tld_legitimate_prob = self.tld_probs.get(tld.lower(), 0.50)

        # URL character probability / unigram density proxy
        entropy = self.compute_shannon_entropy(normalized_url)
        url_char_prob = round(min(0.12, max(0.01, 1.0 / (entropy * 5 + 1))), 6)

        # Keyword heuristics for indicator reporting
        found_keywords = [kw for kw in PHISHING_KEYWORDS if kw in normalized_url.lower()]

        features = {
            "URLLength": url_len,
            "DomainLength": domain_len,
            "IsDomainIP": is_domain_ip,
            "TLDLength": tld_length,
            "NoOfSubDomain": no_of_subdomains,
            "HasObfuscation": has_obfuscation,
            "NoOfObfuscatedChar": no_of_obfuscated_char,
            "ObfuscationRatio": obfuscation_ratio,
            "NoOfLettersInURL": no_of_letters,
            "LetterRatioInURL": letter_ratio,
            "NoOfDegitsInURL": no_of_digits,
            "DegitRatioInURL": digit_ratio,
            "NoOfEqualsInURL": no_of_equals,
            "NoOfQMarkInURL": no_of_qmark,
            "NoOfAmpersandInURL": no_of_amp,
            "NoOfOtherSpecialCharsInURL": no_of_other_special,
            "SpacialCharRatioInURL": special_char_ratio,
            "IsHTTPS": is_https,
            "CharContinuationRate": continuation_rate,
            "URLSimilarityIndex": url_similarity_index,
            "TLDLegitimateProb": tld_legitimate_prob,
            "URLCharProb": url_char_prob
        }

        metadata = {
            "normalized_url": normalized_url,
            "scheme": scheme,
            "domain": domain,
            "tld": tld,
            "subdomains": subdomains,
            "entropy": round(entropy, 3),
            "phishing_keywords_found": found_keywords,
            "has_ip_hostname": bool(is_domain_ip),
            "has_at_symbol": "@" in normalized_url
        }

        return {"features": features, "metadata": metadata}
