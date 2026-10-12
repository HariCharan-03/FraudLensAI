"""
Unit tests for deterministic Risk Assessment Engine rules.
"""

from app.services.risk_engine import RiskAssessmentEngine

def test_threat_feed_match_forces_high_risk():
    # Threat feed confirmed match must result in HIGH risk even with lower ML score
    ml_result = {
        "phishing_score": 0.20,
        "features": {"IsHTTPS": 1},
        "metadata": {"has_ip_hostname": False, "phishing_keywords_found": []}
    }
    threat_intel = {
        "has_confirmed_threat": True,
        "confirmed_sources": ["Google Safe Browsing"]
    }
    domain_intel = {"dns_status": "resolved"}

    res = RiskAssessmentEngine.calculate_risk(ml_result, domain_intel, threat_intel)
    assert res["risk_level"] == "HIGH"
    assert res["risk_score"] >= 95
    assert "RULE_THREAT_INTEL_CONFIRMED" in res["rules_triggered"]

def test_ip_hostname_triggers_high_risk():
    ml_result = {
        "phishing_score": 0.50,
        "features": {"IsHTTPS": 0},
        "metadata": {"has_ip_hostname": True, "phishing_keywords_found": []}
    }
    threat_intel = {"has_confirmed_threat": False, "confirmed_sources": []}
    domain_intel = {"dns_status": "resolved"}

    res = RiskAssessmentEngine.calculate_risk(ml_result, domain_intel, threat_intel)
    assert res["risk_level"] == "HIGH"
    assert "RULE_IP_HOSTNAME" in res["rules_triggered"]

def test_clean_url_produces_low_risk():
    ml_result = {
        "phishing_score": 0.15,
        "features": {"IsHTTPS": 1, "HasObfuscation": 0, "NoOfSubDomain": 1},
        "metadata": {"has_ip_hostname": False, "phishing_keywords_found": []}
    }
    threat_intel = {"has_confirmed_threat": False, "confirmed_sources": []}
    domain_intel = {"dns_status": "resolved", "ssl_certificate": {"is_expired": False}}

    res = RiskAssessmentEngine.calculate_risk(ml_result, domain_intel, threat_intel)
    assert res["risk_level"] == "LOW"
    assert res["risk_score"] < 45

def test_missing_ml_and_dns_produces_inconclusive():
    ml_result = {
        "phishing_score": None,
        "features": {},
        "metadata": {"has_ip_hostname": False, "phishing_keywords_found": []}
    }
    threat_intel = {"has_confirmed_threat": False, "confirmed_sources": []}
    domain_intel = {"dns_status": "no_records"}

    res = RiskAssessmentEngine.calculate_risk(ml_result, domain_intel, threat_intel)
    assert res["risk_level"] == "INCONCLUSIVE"
