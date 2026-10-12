"""
Deterministic Risk Assessment Engine for FraudLens AI.
Combines Machine Learning prediction, explainable SHAP signals,
domain intelligence, and external threat feeds into an evidence-based
risk evaluation (LOW, MEDIUM, HIGH, INCONCLUSIVE) with documented decision rules.
"""

from typing import Dict, Any, List

class RiskAssessmentEngine:
    @staticmethod
    def calculate_risk(
        ml_result: Dict[str, Any],
        domain_intel: Dict[str, Any],
        threat_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates structured risk score (0-100) and risk level.
        Applies strict, testable decision rules.
        """
        indicators: List[Dict[str, str]] = []
        decision_rules_triggered: List[str] = []

        phishing_score = ml_result.get("phishing_score")
        features = ml_result.get("features", {})
        metadata = ml_result.get("metadata", {})

        has_confirmed_threat = threat_intel.get("has_confirmed_threat", False)
        confirmed_sources = threat_intel.get("confirmed_sources", [])

        dns_status = domain_intel.get("dns_status", "no_records")
        dns_err = domain_intel.get("dns_resolution_error")
        ssl_data = domain_intel.get("ssl_certificate", {})
        is_ip_host = metadata.get("has_ip_hostname", False)
        keywords_found = metadata.get("phishing_keywords_found", [])

        # Base score from ML model (0 to 100)
        base_ml_score = int(round((phishing_score if phishing_score is not None else 0.5) * 100))
        computed_score = base_ml_score

        # Rule 1: Confirmed Threat Intelligence Feed Match
        if has_confirmed_threat:
            computed_score = max(computed_score, 98)
            decision_rules_triggered.append("RULE_THREAT_INTEL_CONFIRMED")
            indicators.append({
                "type": "threat_intel",
                "severity": "CRITICAL",
                "title": "Confirmed Threat Intelligence Match",
                "description": f"URL is flagged in verified threat databases: {', '.join(confirmed_sources)}."
            })

        # Rule 2: IP Address in Hostname
        if is_ip_host:
            computed_score = max(computed_score, 85)
            decision_rules_triggered.append("RULE_IP_HOSTNAME")
            indicators.append({
                "type": "domain_indicator",
                "severity": "HIGH",
                "title": "Raw IP Address Hostname",
                "description": "URL bypasses standard DNS domain names by using a numerical IP literal."
            })

        # Rule 3: SSRF / Internal Resolution Block
        if dns_err and "restricted internal" in dns_err:
            computed_score = 99
            decision_rules_triggered.append("RULE_SSRF_INTERNAL_DESTINATION")
            indicators.append({
                "type": "security_safeguard",
                "severity": "CRITICAL",
                "title": "Restricted Network Destination",
                "description": "Host resolves to an internal RFC 1918 or cloud metadata network address."
            })

        # Rule 4: Phishing Brand / Sensitive Keywords in URL
        if keywords_found:
            computed_score = min(100, computed_score + 10)
            decision_rules_triggered.append("RULE_SUSPICIOUS_KEYWORDS")
            indicators.append({
                "type": "lexical_indicator",
                "severity": "HIGH" if computed_score >= 70 else "MEDIUM",
                "title": "High-Risk Security Keywords in URL",
                "description": f"Contains security-sensitive lure keywords: {', '.join(keywords_found)}."
            })

        # Rule 5: SSL Certificate Status
        if ssl_data.get("is_expired"):
            computed_score = min(100, computed_score + 15)
            decision_rules_triggered.append("RULE_EXPIRED_CERTIFICATE")
            indicators.append({
                "type": "ssl_indicator",
                "severity": "HIGH",
                "title": "Expired SSL Certificate",
                "description": "The TLS certificate presented by the host has expired."
            })
        elif features.get("IsHTTPS") == 0:
            computed_score = min(100, computed_score + 8)
            decision_rules_triggered.append("RULE_NO_HTTPS")
            indicators.append({
                "type": "ssl_indicator",
                "severity": "MEDIUM",
                "title": "Unencrypted HTTP Scheme",
                "description": "Communication with this host is unencrypted and vulnerable to interception."
            })

        # Rule 6: High Obfuscation or Nested Subdomains
        if features.get("HasObfuscation") == 1 or features.get("NoOfObfuscatedChar", 0) > 0:
            computed_score = min(100, computed_score + 8)
            decision_rules_triggered.append("RULE_URL_OBFUSCATION")
            indicators.append({
                "type": "lexical_indicator",
                "severity": "MEDIUM",
                "title": "URL Character Obfuscation",
                "description": "Encoded or percent-escaped characters detected in URL structure."
            })

        if features.get("NoOfSubDomain", 0) >= 3:
            computed_score = min(100, computed_score + 7)
            decision_rules_triggered.append("RULE_HIGH_SUBDOMAINS")
            indicators.append({
                "type": "domain_indicator",
                "severity": "MEDIUM",
                "title": "Excessive Nested Subdomains",
                "description": f"URL utilizes {features.get('NoOfSubDomain')} subdomains, commonly used in impersonation."
            })

        # Determine Final Risk Level
        if dns_status == "no_records" and phishing_score is None:
            risk_level = "INCONCLUSIVE"
            decision_summary = "Host failed DNS resolution and machine learning inference could not complete."
        elif has_confirmed_threat or computed_score >= 75:
            risk_level = "HIGH"
            decision_summary = "High probability of phishing or credential theft based on model features and security signals."
        elif computed_score >= 45:
            risk_level = "MEDIUM"
            decision_summary = "Elevated risk characteristics detected; manual caution and verification recommended."
        else:
            risk_level = "LOW"
            decision_summary = "URL characteristics align with benign website patterns. Automated checks found no active threats."

        # Safety Recommendations based on risk level
        recommendations = RiskAssessmentEngine._generate_recommendations(risk_level, indicators)

        return {
            "risk_level": risk_level,
            "risk_score": min(100, max(0, computed_score)),
            "model_phishing_score": phishing_score,
            "decision_summary": decision_summary,
            "rules_triggered": decision_rules_triggered,
            "indicators": indicators,
            "recommendations": recommendations,
            "limitations_notice": (
                "FraudLens AI risk assessments are based on empirical URL structure analysis, "
                "machine learning classification, and available threat intelligence feeds. "
                "Automated detection does not constitute a guarantee of safety or malicious intent."
            )
        }

    @staticmethod
    def _generate_recommendations(risk_level: str, indicators: List[Dict[str, str]]) -> List[str]:
        if risk_level == "HIGH":
            return [
                "DO NOT enter credentials, passwords, or personal financial information on this website.",
                "If you arrived via an email or SMS, navigate directly to the official organization website instead.",
                "If you already submitted credentials, immediately reset your password on the genuine service and enable MFA.",
                "Report this URL to your organization's security team or Anti-Phishing Working Group (APWG)."
            ]
        elif risk_level == "MEDIUM":
            return [
                "Carefully inspect the full domain name in the browser address bar before interacting.",
                "Verify whether the organization typically uses this specific top-level domain.",
                "Avoid downloading executable attachments or granting browser permissions.",
                "Use an isolated browser sandbox if visiting for investigation purposes."
            ]
        elif risk_level == "INCONCLUSIVE":
            return [
                "The domain did not resolve or security evidence was insufficient to render a confident assessment.",
                "Re-check the URL for typographical errors.",
                "Exercise caution and verify the source before proceeding."
            ]
        else:
            return [
                "URL exhibits standard legitimate structural characteristics.",
                "Always verify the browser lock icon and ensure the domain matches your intended destination.",
                "Stay vigilant against sophisticated zero-day campaigns that clone legitimate layouts."
            ]
