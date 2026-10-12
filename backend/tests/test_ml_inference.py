"""
Unit tests for Machine Learning inference and SHAP explainability.
"""

from app.ml.pipeline import ml_pipeline_instance

def test_pipeline_readiness():
    assert ml_pipeline_instance.is_ready is True
    assert ml_pipeline_instance.model is not None
    assert ml_pipeline_instance.feature_meta is not None
    assert len(ml_pipeline_instance.feature_meta["feature_names"]) == 22

def test_inference_probability_bounds():
    test_url = "https://www.example.org"
    res = ml_pipeline_instance.predict(test_url)
    assert res["status"] == "success"
    assert 0.0 <= res["phishing_score"] <= 1.0
    assert 0.0 <= res["confidence_score"] <= 1.0
    assert isinstance(res["is_phishing_predicted"], bool)

def test_shap_explanations_structure():
    test_url = "http://192.168.1.1/login.php"
    res = ml_pipeline_instance.predict(test_url)
    explanations = res["feature_explanations"]
    assert len(explanations) > 0

    first = explanations[0]
    assert "feature_name" in first
    assert "shap_impact" in first
    assert first["direction"] in ["increases_risk", "lowers_risk", "neutral"]
    assert "summary_text" in first
