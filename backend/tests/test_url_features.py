"""
Unit tests for URL feature extraction and parsing edge cases.
Uses synthetic, safe test URLs labeled clearly as test inputs.
"""

import pytest
from app.ml.feature_extractor import URLFeatureExtractor, FEATURE_COLUMNS

@pytest.fixture
def extractor():
    return URLFeatureExtractor()

def test_url_normalization_missing_scheme(extractor):
    raw = "example.com/login"
    norm, scheme, domain, path = extractor.normalize_url(raw)
    assert scheme == "http"
    assert domain == "example.com"
    assert path == "/login"

def test_url_normalization_with_port(extractor):
    raw = "https://sub.bank.com:8443/auth?token=123"
    norm, scheme, domain, path = extractor.normalize_url(raw)
    assert scheme == "https"
    assert domain == "sub.bank.com"
    assert "token=123" in path

def test_is_ip_address(extractor):
    assert extractor.is_ip_address("192.168.1.1") == 1
    assert extractor.is_ip_address("10.0.0.1") == 1
    assert extractor.is_ip_address("example.com") == 0
    assert extractor.is_ip_address("login.bank.org") == 0

def test_feature_extraction_keys_match_schema(extractor):
    res = extractor.extract_features("https://www.google.com")
    features = res["features"]
    metadata = res["metadata"]

    assert len(features) == len(FEATURE_COLUMNS)
    for col in FEATURE_COLUMNS:
        assert col in features
        assert isinstance(features[col], (int, float))

    assert metadata["domain"] == "www.google.com"
    assert metadata["has_ip_hostname"] is False

def test_obfuscation_detection(extractor):
    # Synthetic test URL with percent-encoding
    obfuscated_url = "http://example.com/%70%61%73%73%77%6f%72%64"
    res = extractor.extract_features(obfuscated_url)
    assert res["features"]["HasObfuscation"] == 1
    assert res["features"]["NoOfObfuscatedChar"] > 0
