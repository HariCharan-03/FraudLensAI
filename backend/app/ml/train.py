"""
Model Training and Comparison Pipeline for FraudLens AI.
Trains and compares Logistic Regression, Random Forest, and XGBoost
on the official PhiUSIIL Phishing URL Dataset (URL-only features).
Computes exact held-out test metrics, SHAP explainer, and serializes artifacts.
"""

import json
import logging
import os
import time
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_pipeline")

DATASET_PATH = "data/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
MODEL_DIR = "models"
RANDOM_STATE = 42

URL_FEATURE_COLS = [
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

def run_pipeline():
    os.makedirs(MODEL_DIR, exist_ok=True)
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    logger.info("Loading PhiUSIIL dataset...")
    start_t = time.time()
    df = pd.read_csv(DATASET_PATH)
    logger.info(f"Loaded {len(df):,} records in {time.time() - start_t:.2f}s")

    # Clean BOM or whitespace
    df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

    # Deduplicate on URL to prevent train/test contamination
    initial_count = len(df)
    df = df.drop_duplicates(subset=["URL"]).reset_index(drop=True)
    logger.info(f"Dropped {initial_count - len(df)} duplicate URLs. Working with {len(df):,} unique records.")

    # In PhiUSIIL: 1 = Legitimate, 0 = Phishing
    # We map target: 1 = Phishing (positive risk class), 0 = Legitimate
    y = (df["label"] == 0).astype(int).values
    X = df[URL_FEATURE_COLS].copy()

    # Fill any missing values defensively
    X = X.fillna(0.0)

    # Compute empirical TLD probability table from training data only
    logger.info("Splitting dataset into train (70%), validation (15%), test (15%)...")
    X_temp, X_test, y_temp, y_test, df_temp, df_test = train_test_split(
        X, y, df, test_size=0.15, random_state=RANDOM_STATE, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.17647, random_state=RANDOM_STATE, stratify=y_temp
    )
    # Note: 0.85 * 0.17647 ~ 0.15, achieving 70% / 15% / 15% splits

    logger.info(f"Split sizes: Train={len(X_train):,}, Validation={len(X_val):,}, Test={len(X_test):,}")

    # Calculate empirical TLD legitimacy probabilities on train split to prevent leakage
    tld_series = df.loc[X_train.index, "TLD"].astype(str).str.lower()
    legit_series = pd.Series((y_train == 0).astype(int), index=X_train.index)
    tld_stats = pd.DataFrame({"TLD": tld_series, "is_legit": legit_series}).groupby("TLD").agg(["count", "mean"])
    # filter TLDs with at least 5 occurrences
    tld_probs = {}
    for tld_val, row in tld_stats.iterrows():
        cnt = row[("is_legit", "count")]
        prob = row[("is_legit", "mean")]
        if cnt >= 5:
            tld_probs[str(tld_val)] = round(float(prob), 4)

    with open(os.path.join(MODEL_DIR, "tld_probs.json"), "w") as f:
        json.dump(tld_probs, f, indent=2)
    logger.info(f"Saved {len(tld_probs)} empirical TLD probabilities to models/tld_probs.json")

    # Scaler fitted ONLY on train set
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Candidate Models definition
    candidate_models = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            C=1.0,
            random_state=RANDOM_STATE,
            class_weight="balanced"
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=14,
            random_state=RANDOM_STATE,
            class_weight="balanced",
            n_jobs=-1
        ),
        "XGBoost": XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            eval_metric="logloss",
            n_jobs=-1
        )
    }

    comparison_results = {}
    val_predictions = {}

    for name, model in candidate_models.items():
        logger.info(f"Training {name}...")
        t0 = time.time()
        # For tree models, unscaled features preserve exact integer splits, but scaled also works.
        # Tree models fit on unscaled, LR on scaled:
        if name == "LogisticRegression":
            model.fit(X_train_scaled, y_train)
            val_preds = model.predict(X_val_scaled)
            val_probs = model.predict_proba(X_val_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            val_preds = model.predict(X_val)
            val_probs = model.predict_proba(X_val)[:, 1]

        fit_time = time.time() - t0
        prec = float(precision_score(y_val, val_preds))
        rec = float(recall_score(y_val, val_preds))
        f1 = float(f1_score(y_val, val_preds))
        roc_auc = float(roc_auc_score(y_val, val_probs))
        pr_auc = float(average_precision_score(y_val, val_probs))
        acc = float(accuracy_score(y_val, val_preds))
        cm = confusion_matrix(y_val, val_preds).tolist()

        comparison_results[name] = {
            "validation_accuracy": round(acc, 4),
            "validation_precision": round(prec, 4),
            "validation_recall": round(rec, 4),
            "validation_f1": round(f1, 4),
            "validation_roc_auc": round(roc_auc, 4),
            "validation_pr_auc": round(pr_auc, 4),
            "confusion_matrix": cm,
            "train_time_seconds": round(fit_time, 2)
        }
        val_predictions[name] = (val_preds, val_probs)
        logger.info(f"-> {name} Validation F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f} (trained in {fit_time:.2f}s)")

    # Select best model based on Validation F1 & ROC-AUC
    best_model_name = max(comparison_results.keys(), key=lambda k: comparison_results[k]["validation_f1"])
    best_model = candidate_models[best_model_name]
    logger.info(f"\nWinning Model Selected: {best_model_name}")

    # Evaluate winning model on the unviolated HELD-OUT TEST SET
    logger.info("Evaluating selected model on held-out test set...")
    if best_model_name == "LogisticRegression":
        test_preds = best_model.predict(X_test_scaled)
        test_probs = best_model.predict_proba(X_test_scaled)[:, 1]
    else:
        test_preds = best_model.predict(X_test)
        test_probs = best_model.predict_proba(X_test)[:, 1]

    test_acc = float(accuracy_score(y_test, test_preds))
    test_prec = float(precision_score(y_test, test_preds))
    test_rec = float(recall_score(y_test, test_preds))
    test_f1 = float(f1_score(y_test, test_preds))
    test_roc_auc = float(roc_auc_score(y_test, test_probs))
    test_pr_auc = float(average_precision_score(y_test, test_probs))
    cm_test = confusion_matrix(y_test, test_preds)
    tn, fp, fn, tp = cm_test.ravel()

    test_metrics = {
        "selected_model": best_model_name,
        "test_instances": len(y_test),
        "test_phishing_count": int(np.sum(y_test == 1)),
        "test_legitimate_count": int(np.sum(y_test == 0)),
        "test_accuracy": round(test_acc, 4),
        "test_precision": round(test_prec, 4),
        "test_recall": round(test_rec, 4),
        "test_f1": round(test_f1, 4),
        "test_roc_auc": round(test_roc_auc, 4),
        "test_pr_auc": round(test_pr_auc, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp)
        },
        "model_comparison": comparison_results
    }

    # Save artifacts
    logger.info("Serializing model, scaler, and metadata...")
    joblib.dump(best_model, os.path.join(MODEL_DIR, "model.joblib"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.joblib"))

    # Train and serialize SHAP Explainer
    logger.info("Building SHAP Explainer...")
    if best_model_name in ["XGBoost", "RandomForest"]:
        # Use TreeExplainer for fast and exact SHAP values
        explainer = shap.TreeExplainer(best_model)
    else:
        background = shap.kmeans(X_train_scaled, 50)
        explainer = shap.LinearExplainer(best_model, background)
    joblib.dump(explainer, os.path.join(MODEL_DIR, "explainer.joblib"))

    # Feature metadata
    feature_meta = {
        "version": "1.0.0",
        "model_type": best_model_name,
        "feature_names": URL_FEATURE_COLS,
        "num_features": len(URL_FEATURE_COLS),
        "target_mapping": {
            "0": "Legitimate",
            "1": "Phishing"
        },
        "trained_date": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(os.path.join(MODEL_DIR, "feature_meta.json"), "w") as f:
        json.dump(feature_meta, f, indent=2)

    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(test_metrics, f, indent=2)

    logger.info("\n--- TRAINING & EVALUATION REPORT ---")
    logger.info(f"Selected Model: {best_model_name}")
    logger.info(f"Test Accuracy:  {test_acc:.4f}")
    logger.info(f"Test Precision: {test_prec:.4f}")
    logger.info(f"Test Recall:    {test_rec:.4f}")
    logger.info(f"Test F1-Score:  {test_f1:.4f}")
    logger.info(f"Test ROC-AUC:   {test_roc_auc:.4f}")
    logger.info(f"Test PR-AUC:    {test_pr_auc:.4f}")
    logger.info(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn}")
    logger.info(f"All artifacts saved to {MODEL_DIR}/")

if __name__ == "__main__":
    run_pipeline()
