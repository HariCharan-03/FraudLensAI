"""
Explainable AI (XAI) Service for FraudLens AI.
Uses SHAP (SHapley Additive exPlanations) to explain individual predictions.
Translates mathematical feature contributions into plain-English security insights.
"""

import json
import logging
import os
from typing import Dict, List, Any
import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger("ml_explainer")

FEATURE_DESCRIPTIONS = {
    "URLLength": "Total length of the URL",
    "DomainLength": "Character length of the primary domain",
    "IsDomainIP": "Presence of a raw numerical IP address instead of a domain name",
    "TLDLength": "Length of the Top-Level Domain extension",
    "NoOfSubDomain": "Number of nested subdomains",
    "HasObfuscation": "Presence of URL character obfuscation (hex encoding, percent escapes)",
    "NoOfObfuscatedChar": "Count of obfuscated characters",
    "ObfuscationRatio": "Ratio of obfuscated characters relative to total length",
    "NoOfLettersInURL": "Total alphabetic character count in URL",
    "LetterRatioInURL": "Proportion of alphabetic letters in the URL",
    "NoOfDegitsInURL": "Total count of digits (numbers) in the URL",
    "DegitRatioInURL": "Proportion of numerical digits in the URL",
    "NoOfEqualsInURL": "Count of '=' symbols (often indicating query parameters)",
    "NoOfQMarkInURL": "Count of '?' query delimiter symbols",
    "NoOfAmpersandInURL": "Count of '&' query parameter separators",
    "NoOfOtherSpecialCharsInURL": "Count of special characters (-, _, /, @, etc.)",
    "SpacialCharRatioInURL": "Proportion of special symbols in the URL",
    "IsHTTPS": "Usage of HTTPS encryption protocol",
    "CharContinuationRate": "Continuity of alphanumeric tokens",
    "URLSimilarityIndex": "Lexical similarity index to known legitimate profiles",
    "TLDLegitimateProb": "Prior empirical legitimacy rate for this top-level domain",
    "URLCharProb": "Character unigram density and distribution score"
}

class ModelExplainer:
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.explainer = None
        self.feature_meta = None
        self.load_artifacts()

    def load_artifacts(self):
        explainer_path = os.path.join(self.model_dir, "explainer.joblib")
        meta_path = os.path.join(self.model_dir, "feature_meta.json")

        if os.path.exists(explainer_path):
            try:
                self.explainer = joblib.load(explainer_path)
                logger.info("Loaded SHAP explainer successfully.")
            except Exception as e:
                logger.warning(f"Could not load SHAP explainer: {e}")

        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    self.feature_meta = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load feature metadata: {e}")

    def explain(self, features_dict: Dict[str, Any], top_n: int = 8) -> List[Dict[str, Any]]:
        """
        Calculates SHAP feature attributions for a given feature dictionary.
        Returns sorted list of features with positive/negative risk impacts.
        """
        if self.explainer is None or self.feature_meta is None:
            # Fallback to heuristic attribution if explainer is unavailable
            return self._heuristic_fallback(features_dict)

        feature_names = self.feature_meta["feature_names"]
        row_df = pd.DataFrame([[features_dict.get(fn, 0) for fn in feature_names]], columns=feature_names)

        try:
            shap_values = self.explainer.shap_values(row_df)

            # For binary classifiers in SHAP, shap_values is either a 2D array or list of 2 arrays [class_0, class_1]
            if isinstance(shap_values, list) and len(shap_values) == 2:
                # Use class 1 (Phishing) attribution
                raw_attributions = shap_values[1][0]
            elif isinstance(shap_values, np.ndarray):
                if shap_values.ndim == 3:  # (samples, features, classes)
                    raw_attributions = shap_values[0, :, 1]
                elif shap_values.ndim == 2:
                    raw_attributions = shap_values[0]
                else:
                    raw_attributions = shap_values
            else:
                raw_attributions = np.zeros(len(feature_names))

            explanations = []
            for name, val, impact in zip(feature_names, row_df.iloc[0], raw_attributions):
                impact_float = float(impact)
                direction = "increases_risk" if impact_float > 0 else "lowers_risk" if impact_float < 0 else "neutral"

                explanations.append({
                    "feature_name": name,
                    "display_name": name.replace("NoOf", "Count of ").replace("URL", "URL "),
                    "description": FEATURE_DESCRIPTIONS.get(name, name),
                    "feature_value": float(val) if isinstance(val, (int, float, np.number)) else str(val),
                    "shap_impact": round(impact_float, 4),
                    "direction": direction,
                    "abs_impact": abs(impact_float),
                    "summary_text": self._create_feature_summary(name, val, direction)
                })

            # Sort by absolute impact descending
            explanations.sort(key=lambda x: x["abs_impact"], reverse=True)
            return explanations[:top_n]

        except Exception as e:
            logger.error(f"Error computing SHAP values: {e}")
            return self._heuristic_fallback(features_dict)

    def _create_feature_summary(self, name: str, value: Any, direction: str) -> str:
        prefix = "Increases phishing likelihood" if direction == "increases_risk" else "Indicates benign profile"
        if name == "IsDomainIP" and value == 1:
            return "Using a raw IP address instead of a domain name strongly increases phishing risk."
        if name == "TLDLegitimateProb":
            return f"{prefix} based on TLD historical legitimacy score ({value:.2f})."
        if name == "HasObfuscation" and value == 1:
            return "Obfuscated or percent-encoded characters detected in the URL structure."
        if name == "NoOfSubDomain" and value > 2:
            return f"High count of subdomains ({value}) often used to mask malicious origins."
        if name == "IsHTTPS" and value == 0:
            return "Absence of HTTPS (unencrypted connection) raises risk."
        if name == "URLLength" and value > 75:
            return f"Abnormally long URL ({value} chars) frequently used to hide destination."
        return f"{prefix} for {name} with observed value {value}."

    def _heuristic_fallback(self, features_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Graceful fallback if SHAP artifact is temporarily unavailable
        explanations = []
        for fn in list(features_dict.keys())[:8]:
            val = features_dict.get(fn, 0)
            explanations.append({
                "feature_name": fn,
                "display_name": fn,
                "description": FEATURE_DESCRIPTIONS.get(fn, fn),
                "feature_value": val,
                "shap_impact": 0.0,
                "direction": "neutral",
                "abs_impact": 0.0,
                "summary_text": f"Observed {fn} with value {val}."
            })
        return explanations
