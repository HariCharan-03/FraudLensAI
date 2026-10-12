# FraudLens AI — Intelligent Phishing Detection and Website Risk Analysis Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![Machine Learning](https://img.shields.io/badge/ML-RandomForest%20%7C%20TreeSHAP-orange.svg)](https://scikit-learn.org)

FraudLens AI is an end-to-end, evidence-based cybersecurity platform that analyzes submitted URLs and available security telemetry to identify deceptive phishing websites. It combines machine learning trained on 235,000+ benchmark URLs, mathematical explainable AI (SHAP), SSRF-safe domain handshakes, a hybrid multi-agent LangGraph workflow, and an LLM-powered cybersecurity assistant using Retrieval-Augmented Generation (RAG).

---

## 1. Core Workflow & Architecture

FraudLens AI inspects target URLs through an evidence-based pipeline that separates structural lexical signals, live infrastructure checks, and calibrated model inferences:

```
[Target URL] ---> [SSRF Scheme Validator]
                        |
                        v
          +-----------------------------+
          | LangGraph Agent Workflow    |
          +-----------------------------+
           |           |           |
           v           v           v
       [Lexical]    [Domain]     [Model]
       22 Features  DNS & TLS   Random Forest
           |           |           |
           +-----------+-----------+
                       |
                       v
         [TreeSHAP Feature Attributions]
                       |
                       v
       [Deterministic Risk Rules Engine]
                       |
                       v
         +-----------------------------+
         | Cyber Forensic Dashboard    |
         | & Grounded RAG Assistant    |
         +-----------------------------+
```

### Key Technical Pillars:
1. **Pre-Render Safety**: Live arbitrary webpage rendering is disabled by default to eliminate browser exploit kit exposure and Server-Side Request Forgery (SSRF).
2. **Leakage-Free ML**: Trained exclusively on 22 URL-only structural features extracted from the official UCI PhiUSIIL dataset with strict partition isolation.
3. **Transparent Explainability**: Individual predictions feature exact TreeSHAP attributions indicating which factors raise or lower phishing probability.
4. **LangGraph Orchestration**: Deterministic tools and specialized reasoners coordinate through a typed state machine with conditional routing and execution tracing.
5. **Grounded RAG Assistant**: Follow-up questions are answered using scan findings synthesized with official cybersecurity standards from CISA, OWASP, and NIST.

---

## 2. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, React Router, Recharts, Lucide React.
- **Backend API**: Python 3.11+, FastAPI, Pydantic v2, Uvicorn, httpx, dnspython.
- **Machine Learning & XAI**: scikit-learn, XGBoost, TreeSHAP, joblib, pandas, NumPy.
- **Agentic AI & RAG**: LangGraph, TF-IDF / Cosine Similarity Vector Store, configurable LLM providers (Mock, OpenAI, Anthropic, Groq).
- **Database & Persistence**: SQLAlchemy 2.0 (Async), SQLite / PostgreSQL 16, Alembic.
- **Testing & Tooling**: pytest, pytest-asyncio, Docker, Docker Compose.

---

## 3. Machine Learning Methodology & Evaluation

### Official Dataset Inspection
- **Source**: [UCI Machine Learning Repository #967 (PhiUSIIL Phishing URL Dataset)](https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+website+dataset)
- **Total Instances**: 235,795 rows (56 raw columns)
- **Class Balance**: 134,850 Legitimate (57.19%) vs. 100,945 Phishing (42.81%)
- **Data Leakage Controls**:
  - `FILENAME` identifier dropped to eliminate spurious artifact correlations.
  - Webpage-derived HTML features excluded from the inference pipeline.
  - 425 duplicate URLs purged prior to splitting.
  - Scaler fitted exclusively on the 70% training split.

### Model Benchmarks (Validation Set: $N=35,306$)
| Model | Validation F1 | Validation ROC-AUC | Validation Precision | Validation Recall |
|---|---|---|---|---|
| Logistic Regression (Balanced) | 99.98% | 1.0000 | 1.0000 | 0.9995 |
| **Random Forest (100 Trees, Depth 14)** | **100.00%** | **1.0000** | **1.0000** | **0.9999** |
| XGBoost (150 Trees, Depth 6) | 100.00% | 1.0000 | 1.0000 | 0.9999 |

### Held-Out Test Set Results ($N=35,306$)
- **Accuracy**: `99.99%`
- **Precision**: `1.0000` (100%)
- **Recall**: `0.9997` (99.97%)
- **F1-Score**: `0.9999`
- **ROC-AUC**: `1.0000`
- **Confusion Matrix**: True Positives: `15,074` | True Negatives: `20,228` | False Positives: `0` | False Negatives: `4`

---

## 4. Repository Structure

```
FRAUDLENS-AI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Scan, Assistant, Health, Stats routes
│   │   ├── agents/              # LangGraph StateGraph & nodes
│   │   ├── database/            # SQLAlchemy models, async session, CRUD
│   │   ├── ml/                  # Feature extractor, train pipeline, explainer
│   │   ├── rag/                 # Vector store & CISA/OWASP/NIST knowledge base
│   │   ├── security/            # SSRF guard & IP blocklists
│   │   ├── services/            # Domain intel, threat feeds, risk engine
│   │   └── main.py              # FastAPI app & lifespan handler
│   ├── tests/                   # 24 automated unit & integration tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # RiskGauge, SHAP Chart, ServerLocation, etc.
│   │   ├── pages/               # Landing, Dashboard, Scanner, Result, History, Assistant, Settings
│   │   ├── services/            # API client
│   │   ├── types/               # TypeScript interfaces
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── data/raw/                    # Official UCI PhiUSIIL CSV dataset
├── models/                      # Serialized model, SHAP explainer, metrics
├── docs/                        # Architecture, ML Methodology, API docs
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 5. Quickstart & Local Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### Option A: Native Local Development (Recommended)

1. **Clone repository and configure environment**:
   ```bash
   cp .env.example .env
   ```

2. **Set up Python Virtual Environment**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Train Model & Build Artifacts (Pre-trained artifacts already in `models/`)**:
   ```bash
   python app/ml/train.py
   ```

4. **Run Backend Test Suite**:
   ```bash
   PYTHONPATH=. pytest tests -v
   ```

5. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Start React Frontend** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

### Option B: Docker Compose

```bash
docker-compose up --build
```
- Frontend Dashboard: [http://localhost:3000](http://localhost:3000)
- Backend REST API: [http://localhost:8000](http://localhost:8000)
- OpenAPI Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 6. Security Controls & SSRF Safeguards

FraudLens AI enforces defensive security measures:
- **SSRF Defense**: Automatically blocks connections to private networks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`, `::1`), link-local (`169.254.0.0/16`), multicast, and cloud metadata APIs (`169.254.169.254`).
- **DNS-Rebinding Protection**: Target hostnames are resolved and checked prior to opening any socket connection.
- **Zero Webpage Execution**: Does not load arbitrary JavaScript or download malicious drive-by binaries.
- **Secret Isolation**: Threat intelligence API keys remain exclusively on the server and are never exposed in frontend bundles.

---

## 7. Responsible-Use & Operational Limitations

- **Evidence-Based Risk**: Risk levels (`LOW`, `MEDIUM`, `HIGH`, `INCONCLUSIVE`) indicate structural anomalies and threat feed matches; they do not constitute a guarantee that a site is safe or malicious.
- **Zero-Day Feeds**: Absence of a match in Google Safe Browsing or PhishTank is never interpreted as proof of legitimacy, as novel phishing domains often evade indexing during initial hours.
- **Defense in Depth**: Always verify genuine domains in the browser address bar and enforce phishing-resistant FIDO2/WebAuthn credentials.
