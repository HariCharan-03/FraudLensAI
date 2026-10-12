# FraudLens AI — Machine Learning & Explainability Methodology

## 1. Dataset Provenance & Inspection

FraudLens AI utilizes the official **PhiUSIIL Phishing URL (Website) Dataset** published by Arvind Prasad and Shalini Chandra (Computers & Security, 2024), hosted by the UC Irvine Machine Learning Repository.

- **Official Source**: [UCI ML Repository #967](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+website+dataset)
- **Total Records**: 235,795 instances
- **Total Columns**: 56 features
- **Missing Values**: 0 (complete dataset)
- **Raw Class Distribution**:
  - `label = 1` (Legitimate): 134,850 URLs (57.19%)
  - `label = 0` (Phishing): 100,945 URLs (42.81%)
- **Model Target Mapping**: In our pipeline, positive class $y = 1$ corresponds to Phishing ($\text{label} == 0$), and $y = 0$ corresponds to Legitimate ($\text{label} == 1$).

---

## 2. Data Leakage Prevention

Rigorous leakage mitigation was implemented during dataset engineering:
1. **Identifier Exclusion**: The `FILENAME` column (arbitrary file IDs like `521848.txt`) was excluded to eliminate spurious correlation.
2. **Offline vs. Online Feature Separation**:
   - Webpage-derived features (`LineOfCode`, `LargestLineLength`, `Title`, `NoOfCSS`, `NoOfJS`, `NoOfiFrame`, `Bank`, `Pay`, `Crypto`) were excluded from the live inference pipeline because live page fetching exposes the scanning infrastructure to malware/SSRF and fails when zero-day phishing sites go offline.
   - The scanner operates strictly on **22 URL-only structural features**.
3. **Train-Set Only Scaler Fitting**: StandardScaler and empirical Top-Level Domain prior probabilities were fitted strictly on the training partition ($N=164,758$).
4. **Duplicate Deduplication**: 425 duplicate URL records were purged prior to splitting to prevent cross-partition contamination.

---

## 3. Extracted URL-Only Feature Schema

| Feature Name | Description | Type |
|---|---|---|
| `URLLength` | Total character count of normalized URL | Integer |
| `DomainLength` | Character count of primary domain name | Integer |
| `IsDomainIP` | Indicator if hostname is an IPv4 or IPv6 address literal | Binary (0/1) |
| `TLDLength` | Length of Top-Level Domain extension | Integer |
| `NoOfSubDomain` | Number of nested subdomains | Integer |
| `HasObfuscation` | Presence of percent-encoded or hex characters | Binary (0/1) |
| `NoOfObfuscatedChar` | Total count of obfuscated characters | Integer |
| `ObfuscationRatio` | Ratio of obfuscated characters to total URL length | Float |
| `NoOfLettersInURL` | Count of alphabetic characters `[a-zA-Z]` | Integer |
| `LetterRatioInURL` | Proportion of alphabetic characters | Float |
| `NoOfDegitsInURL` | Count of numeric digits `[0-9]` | Integer |
| `DegitRatioInURL` | Proportion of numeric digits | Float |
| `NoOfEqualsInURL` | Count of `=` parameter assignment characters | Integer |
| `NoOfQMarkInURL` | Count of `?` query delimiter characters | Integer |
| `NoOfAmpersandInURL` | Count of `&` parameter separators | Integer |
| `NoOfOtherSpecialCharsInURL` | Count of symbols (`-`, `_`, `/`, `.`, `@`, `~`, etc.) | Integer |
| `SpacialCharRatioInURL` | Proportion of special symbols | Float |
| `IsHTTPS` | Presence of `https://` secure transport scheme | Binary (0/1) |
| `CharContinuationRate` | Ratio of longest uninterrupted alphanumeric token | Float |
| `URLSimilarityIndex` | Lexical similarity score to verified legitimate benchmarks | Float |
| `TLDLegitimateProb` | Empirical prior legitimacy frequency for the TLD | Float |
| `URLCharProb` | Character distribution and Shannon unigram density score | Float |

---

## 4. Model Selection & Comparison

Three candidate models were evaluated on the Stratified Validation set ($N=35,306$):

| Candidate Model | Validation Accuracy | Validation Precision | Validation Recall | Validation F1-Score | Validation ROC-AUC | Train Time |
|---|---|---|---|---|---|---|
| **Logistic Regression** (Balanced, Scaled) | 99.98% | 1.0000 | 0.9995 | 0.9998 | 1.0000 | 0.17s |
| **Random Forest** (100 Trees, Depth 14) | **100.00%** | **1.0000** | **0.9999** | **1.0000** | **1.0000** | 1.47s |
| **XGBoost** (150 Trees, Depth 6) | 100.00% | 1.0000 | 0.9999 | 1.0000 | 1.0000 | 0.50s |

**Selection Decision**: Random Forest was chosen as the primary deployment model due to its optimal balance between non-linear boundary capture, zero external library dependency during inference, and seamless integration with exact TreeSHAP algorithms.

---

## 5. Held-Out Test Set Evaluation

The winning Random Forest model was evaluated once on the virgin held-out test split ($N=35,306$):

- **Test Accuracy**: `99.99%`
- **Test Precision**: `1.0000`
- **Test Recall**: `0.9997`
- **Test F1-Score**: `0.9999`
- **Test ROC-AUC**: `1.0000`
- **Test PR-AUC**: `1.0000`

### Confusion Matrix on Test Set
- **True Positives (Phishing correctly caught)**: `15,074`
- **True Negatives (Legitimate correctly cleared)**: `20,228`
- **False Positives (Benign misclassified as phishing)**: `0`
- **False Negatives (Phishing missed)**: `4`

---

## 6. Explainable AI with TreeSHAP

Rather than treating the classifier as a black box, FraudLens AI integrates **TreeSHAP** (SHapley Additive exPlanations):

$$\phi_i(x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} [f_x(S \cup \{i\}) - f_x(S)]$$

- For every individual URL submitted by a user, SHAP calculates the exact marginal contribution of each of the 22 features.
- Positive SHAP contributions ($\phi_i > 0$) raise phishing probability (highlighted in red in the UI).
- Negative SHAP contributions ($\phi_i < 0$) lower phishing probability (highlighted in green in the UI).
- The system translates these attributions into plain English security findings.
