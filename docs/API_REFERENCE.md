# FraudLens AI — REST API Reference (v1)

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI Documentation: `http://localhost:8000/docs`

---

## 1. System Health & Diagnostics

### `GET /health`
Returns the operational status of the database, machine learning pipeline, threat feeds, and RAG knowledge base.

**Response Example (200 OK):**
```json
{
  "status": "healthy",
  "app_name": "FraudLens AI",
  "version": "1.0.0",
  "environment": "development",
  "database": {
    "status": "connected"
  },
  "machine_learning": {
    "status": "ready",
    "model_type": "RandomForest",
    "model_version": "1.0.0",
    "features_loaded": 22,
    "shap_explainer_loaded": true
  },
  "threat_intelligence": {
    "google_safe_browsing": "not_configured (optional)",
    "phishtank": "not_configured (optional)",
    "live_dns_resolution": "active (SSRF-protected)"
  },
  "rag_knowledge_base": {
    "status": "indexed",
    "chunks_indexed": 11,
    "sources": [
      "CISA Alert AA22-216A",
      "OWASP Phishing Defense",
      "NIST SP 800-63B / SP 800-177"
    ]
  }
}
```

---

## 2. Scans

### `POST /scan`
Submits a target URL for risk analysis through the LangGraph multi-agent pipeline.

**Request Body:**
```json
{
  "url": "https://www.paypal-secure-verify.com/login"
}
```

**Response Example (201 Created):**
```json
{
  "id": "8817cbcf-2259-451a-a617-c1e0c6dedd8e",
  "url": "https://www.paypal-secure-verify.com/login",
  "normalized_url": "https://www.paypal-secure-verify.com/login",
  "created_at": "2026-10-10T18:21:44.004128Z",
  "risk_level": "MEDIUM",
  "risk_score": 53,
  "model_score": 0.43,
  "model_version": "1.0.0",
  "model_type": "RandomForest",
  "is_phishing_predicted": false,
  "status": "completed",
  "plain_explanation": "FraudLens AI assessed this URL as MEDIUM Risk (Risk Score: 53/100)...",
  "indicators": [
    {
      "type": "lexical_indicator",
      "severity": "MEDIUM",
      "title": "High-Risk Security Keywords in URL",
      "description": "Contains security-sensitive lure keywords: login, secure, verify."
    }
  ],
  "feature_explanations": [
    {
      "feature_name": "NoOfOtherSpecialCharsInURL",
      "display_name": "Count of OtherSpecialCharsInURL",
      "shap_impact": 0.082,
      "direction": "increases_risk",
      "feature_value": 4.0,
      "summary_text": "Increases phishing likelihood based on special characters count."
    }
  ],
  "recommendations": [
    "Carefully inspect the full domain name in the browser address bar before interacting.",
    "Verify whether the organization typically uses this specific top-level domain."
  ]
}
```

---

### `GET /scan/{scan_id}`
Retrieves full forensic details, DNS records, TLS certificate, and SHAP explanations for an existing scan.

---

### `GET /scans`
Lists historical scans with search, risk level filtering, and pagination.

**Query Parameters:**
- `search` (string, optional): Search keyword matching URL.
- `risk_level` (string, optional): Filter by `LOW`, `MEDIUM`, `HIGH`, `INCONCLUSIVE`.
- `limit` (integer, default: 50): Number of records.
- `offset` (integer, default: 0): Page offset.

---

### `DELETE /scans/{scan_id}`
Permanently deletes a scan record and its conversation history. Returns `204 No Content`.

---

## 3. Grounded AI Assistant Chat

### `POST /scan/{scan_id}/chat`
Asks a question grounded in the scan's findings and retrieved cybersecurity literature.

**Request Body:**
```json
{
  "question": "Why was this URL flagged as medium risk?"
}
```

**Response Example (200 OK):**
```json
{
  "answer": "### Analysis of Flagged Risks for `https://...`\nThis target was assessed with an overall risk score of 53/100...",
  "grounded": true,
  "citations": [
    {
      "title": "CISA Phishing Defense & Incident Response Guidance",
      "organization": "Cybersecurity & Infrastructure Security Agency (CISA)",
      "source_url": "https://www.cisa.gov/topics/cyber-threats-and-advisories/phishing",
      "citation": "CISA Phishing Guidance (Alert AA22-216A)",
      "relevance": 0.421
    }
  ],
  "model_used": "Deterministic Cybersecurity Reasoner (Grounded RAG)"
}
```

---

### `GET /scan/{scan_id}/chat`
Returns the chronological conversation history for the specified scan.

---

## 4. Analytics & Demonstration Data

### `GET /stats`
Returns aggregated dashboard metrics (total scans, risk counts, and risk distribution breakdown).

### `POST /seed`
Development helper to generate demonstration scans in fresh environments.
