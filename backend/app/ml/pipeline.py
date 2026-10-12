"""
Machine Learning Inference Pipeline for FraudLens AI.
Coordinates URL feature extraction, model inference, score calibration,
and explainability.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
import joblib
import pandas as pd

from app.ml.feature_extractor import URLFeatureExtractor, FEATURE_COLUMNS
from app.ml.explainer import ModelExplainer

logger = logging.getLogger("ml_pipeline")

class MLPipeline:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.model = None
        self.feature_meta = None
        self.feature_extractor = None
        self.explainer = None
        self.is_ready = False
        self.initialize()

    def initialize(self):
        model_path = os.path.join(self.model_dir, "model.joblib")
        meta_path = os.path.join(self.model_dir, "feature_meta.json")
        tld_path = os.path.join(self.model_dir, "tld_probs.json")

        self.feature_extractor = URLFeatureExtractor(tld_probs_path=tld_path)
        self.explainer = ModelExplainer(model_dir=self.model_dir)

        if os.path.exists(model_path) and os.path.exists(meta_path):
            try:
                self.model = joblib.load(model_path)
                with open(meta_path, "r") as f:
                    self.feature_meta = json.load(f)
                self.is_ready = True
                logger.info(f"ML Pipeline initialized successfully with model {self.feature_meta.get('model_type')}.")
            except Exception as e:
                logger.error(f"Failed to load model artifacts: {e}")
                self.is_ready = False
        else:
            logger.warning("Model artifacts not found in models/ directory. Run train.py first.")
            self.is_ready = False

    def predict(self, raw_url: str) -> Dict[str, Any]:
        """
        Runs full ML inference on the provided URL.
        Returns extracted features, model probability, classification, and SHAP explanations.
        """
        # 1. Feature extraction
        extraction = self.feature_extractor.extract_features(raw_url)
        features_dict = extraction["features"]
        metadata = extraction["metadata"]

        if not self.is_ready:
            return {
                "status": "model_not_ready",
                "error": "Trained ML model artifacts are not loaded.",
                "features": features_dict,
                "metadata": metadata,
                "phishing_score": None,
                "is_phishing_predicted": None,
                "confidence_score": None,
                "feature_explanations": []
            }

        feature_names = self.feature_meta.get("feature_names", FEATURE_COLUMNS)
        row_df = pd.DataFrame([[features_dict.get(fn, 0) for fn in feature_names]], columns=feature_names)

        # 2. Model prediction
        try:
            probabilities = self.model.predict_proba(row_df)[0]
            # Class 1 is Phishing
            phishing_prob = float(probabilities[1])
            legit_prob = float(probabilities[0])
            is_phishing = bool(phishing_prob >= 0.50)
            confidence = float(max(phishing_prob, legit_prob))

            # 3. Explainability
            explanations = self.explainer.explain(features_dict)

            return {
                "status": "success",
                "model_version": self.feature_meta.get("version", "1.0.0"),
                "model_type": self.feature_meta.get("model_type", "Unknown"),
                "features": features_dict,
                "metadata": metadata,
                "phishing_score": round(phishing_prob, 4),
                "is_phishing_predicted": is_phishing,
                "confidence_score": round(confidence, 4),
                "feature_explanations": explanations
            }
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                "status": "inference_error",
                "error": str(e),
                "features": features_dict,
                "metadata": metadata,
                "phishing_score": None,
                "is_phishing_predicted": None,
                "confidence_score": None,
                "feature_explanations": []
            }

# Global singleton instance
ml_pipeline_instance = MLPipeline()
