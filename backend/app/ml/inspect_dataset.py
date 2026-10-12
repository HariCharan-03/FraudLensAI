"""
Dataset Inspection Script for PhiUSIIL Phishing URL Dataset.
Calculates summary statistics, missing values, class distributions,
and potential data leakage identifiers.
"""

import json
import logging
import os
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("inspect_dataset")

DATASET_PATH = "data/raw/PhiUSIIL_Phishing_URL_Dataset.csv"
OUTPUT_REPORT = "docs/dataset_inspection_report.json"

def inspect():
    if not os.path.exists(DATASET_PATH):
        logger.error(f"Dataset file not found at {DATASET_PATH}")
        return

    logger.info("Loading dataset...")
    df = pd.read_csv(DATASET_PATH)
    total_rows, total_cols = df.shape
    logger.info(f"Loaded {total_rows:,} rows and {total_cols} columns.")

    # Clean BOM or whitespace from column names if present
    df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]

    missing_series = df.isnull().sum()
    missing_dict = {col: int(cnt) for col, cnt in missing_series.items() if cnt > 0}

    # Duplicates check
    url_duplicates = int(df["URL"].duplicated().sum()) if "URL" in df.columns else 0
    full_duplicates = int(df.duplicated().sum())

    # Target class distribution
    # UCI documentation specifies: label 1 = legitimate, label 0 = phishing
    class_counts_raw = df["label"].value_counts().to_dict()
    class_dist = {
        "label_1_legitimate": int(class_counts_raw.get(1, 0)),
        "label_0_phishing": int(class_counts_raw.get(0, 0)),
        "phishing_percentage": round(float(class_counts_raw.get(0, 0)) / total_rows * 100, 2),
        "legitimate_percentage": round(float(class_counts_raw.get(1, 0)) / total_rows * 100, 2),
    }

    # Column categorization
    identifier_columns = ["FILENAME"]
    url_only_candidate_features = [
        "URLLength", "DomainLength", "IsDomainIP", "URLSimilarityIndex",
        "CharContinuationRate", "TLDLegitimateProb", "URLCharProb", "TLDLength",
        "NoOfSubDomain", "HasObfuscation", "NoOfObfuscatedChar", "ObfuscationRatio",
        "NoOfLettersInURL", "LetterRatioInURL", "NoOfDegitsInURL", "DegitRatioInURL",
        "NoOfEqualsInURL", "NoOfQMarkInURL", "NoOfAmpersandInURL",
        "NoOfOtherSpecialCharsInURL", "SpacialCharRatioInURL", "IsHTTPS"
    ]
    webpage_derived_features = [
        "LineOfCode", "LargestLineLength", "HasTitle", "Title",
        "DomainTitleMatchScore", "URLTitleMatchScore", "HasFavicon", "Robots",
        "IsResponsive", "NoOfURLRedirect", "NoOfSelfRedirect", "HasDescription",
        "NoOfPopup", "NoOfiFrame", "HasExternalFormSubmit", "HasSocialNet",
        "HasSubmitButton", "HasHiddenFields", "HasPasswordField", "Bank", "Pay",
        "Crypto", "HasCopyrightInfo", "NoOfImage", "NoOfCSS", "NoOfJS",
        "NoOfSelfRef", "NoOfEmptyRef", "NoOfExternalRef"
    ]

    leakage_risks = [
        {"column": "FILENAME", "reason": "Artifact filename in collection directory; purely an arbitrary ID with high risk of spurious correlation."},
        {"column": "Title / HasTitle", "reason": "Requires fetching and parsing live HTML, unavailable during zero-day pre-render URL inspection; risk of SSRF during live inference."},
        {"column": "URLTitleMatchScore / DomainTitleMatchScore", "reason": "Derived from live webpage HTML title; offline-only feature."},
        {"column": "Webpage tags (LineOfCode, NoOfCSS, NoOfJS, Bank, Pay, Crypto)", "reason": "Requires active web crawling, exposes scanner to malicious payloads."}
    ]

    report = {
        "dataset_name": "PhiUSIIL Phishing URL (Website) Dataset",
        "official_source": "https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+website+dataset",
        "total_instances": total_rows,
        "total_features": total_cols,
        "actual_column_names": list(df.columns),
        "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": missing_dict,
        "full_duplicate_rows": full_duplicates,
        "url_duplicate_rows": url_duplicates,
        "class_distribution": class_dist,
        "target_mapping": {
            "uci_label_0": "Phishing (mapped to model target 1)",
            "uci_label_1": "Legitimate (mapped to model target 0)"
        },
        "identifier_columns": identifier_columns,
        "url_only_candidate_features": url_only_candidate_features,
        "webpage_derived_features": webpage_derived_features,
        "leakage_risks_identified": leakage_risks
    }

    os.makedirs(os.path.dirname(OUTPUT_REPORT), exist_ok=True)
    with open(OUTPUT_REPORT, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Dataset inspection complete. Saved report to {OUTPUT_REPORT}")
    print("\n--- DATASET INSPECTION SUMMARY ---")
    print(f"Total Rows: {total_rows:,}")
    print(f"Total Columns: {total_cols}")
    print(f"Missing Values: {len(missing_dict)} columns with missing data")
    print(f"URL Duplicates: {url_duplicates:,}")
    print(f"Class Distribution: {class_dist}")
    print(f"URL-only Features: {len(url_only_candidate_features)}")
    print(f"Webpage-derived Features: {len(webpage_derived_features)}")

if __name__ == "__main__":
    inspect()
