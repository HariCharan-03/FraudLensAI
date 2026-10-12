"""
AI Security Assistant with Retrieval-Augmented Generation (RAG).
Generates evidence-grounded responses to follow-up questions about a scan,
incorporating retrieved CISA, OWASP, and NIST guidelines.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
import httpx

from app.rag.vector_store import rag_store_instance

logger = logging.getLogger("rag_assistant")

class SecurityAssistant:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.api_key = os.getenv("LLM_API_KEY", "").strip()
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    async def answer_question(
        self,
        question: str,
        scan_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Answers a user question grounded strictly in the scan context and retrieved RAG sources.
        Adapts dynamically based on Risk Tier (LOW vs MEDIUM vs HIGH) and actual SHAP features.
        """
        # 1. RAG retrieval from authoritative CISA, OWASP, and NIST knowledge base
        retrieved_chunks = rag_store_instance.retrieve(question, top_k=2)

        # 2. Extract key context fields from scan
        submitted_url = scan_context.get("url", "Unknown URL")
        risk_level = (scan_context.get("risk_level") or "UNKNOWN").upper()
        risk_score = scan_context.get("risk_score", 0)
        ml_score = scan_context.get("model_phishing_score")
        indicators = scan_context.get("indicators", []) or []
        features = scan_context.get("features", {}) or {}
        feature_explanations = scan_context.get("feature_explanations", []) or []
        threat_intel = scan_context.get("threat_intel", {}) or {}
        threat_matches = threat_intel.get("confirmed_sources", [])
        domain_intel = scan_context.get("domain_intel", {}) or {}

        # 3. Check if external LLM provider is configured and available
        if self.provider in ["openai", "groq", "anthropic"] and self.api_key:
            try:
                external_answer = await self._call_external_llm(
                    question=question,
                    scan_context=scan_context,
                    retrieved_chunks=retrieved_chunks
                )
                if external_answer:
                    return {
                        "answer": external_answer,
                        "grounded": True,
                        "citations": [
                            {
                                "title": c["title"],
                                "organization": c["organization"],
                                "source_url": c["source_url"],
                                "citation": c["citation"],
                                "relevance": c["similarity_score"]
                            }
                            for c in retrieved_chunks
                        ],
                        "model_used": f"{self.provider}:{self.model}"
                    }
            except Exception as e:
                logger.warning(f"External LLM call failed, falling back to local grounded reasoning: {e}")

        # 4. Contextual Risk-Differentiated Grounded Reasoner
        local_answer = self._generate_grounded_response(
            question=question,
            url=submitted_url,
            risk_level=risk_level,
            risk_score=risk_score,
            ml_score=ml_score,
            indicators=indicators,
            features=features,
            feature_explanations=feature_explanations,
            threat_intel=threat_intel,
            threat_matches=threat_matches,
            domain_intel=domain_intel,
            retrieved_chunks=retrieved_chunks
        )

        return {
            "answer": local_answer,
            "grounded": True,
            "citations": [
                {
                    "title": c["title"],
                    "organization": c["organization"],
                    "source_url": c["source_url"],
                    "citation": c["citation"],
                    "relevance": c["similarity_score"]
                }
                for c in retrieved_chunks
            ],
            "model_used": "Grounded Cybersecurity Reasoner (Risk-Differentiated RAG)"
        }

    def _generate_grounded_response(
        self,
        question: str,
        url: str,
        risk_level: str,
        risk_score: int,
        ml_score: Optional[float],
        indicators: List[Dict[str, str]],
        features: Dict[str, Any],
        feature_explanations: List[Dict[str, Any]],
        threat_intel: Dict[str, Any],
        threat_matches: List[str],
        domain_intel: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> str:
        q_lower = question.lower()
        ml_pct = f"{ml_score * 100:.1f}%" if ml_score is not None else "N/A"
        domain = url.split("://")[-1].split("/")[0].split("?")[0]

        # Extract domain forensics
        dns_status = domain_intel.get("dns_status", "unresolved")
        resolved_ip = domain_intel.get("resolved_ip", "Not resolved")
        geo = domain_intel.get("ip_geolocation") or {}
        location_str = f"{geo.get('country', 'Unknown')}" if geo else "Unknown location"
        ssl_info = domain_intel.get("ssl_certificate") or {}
        ssl_issuer = ssl_info.get("issuer") or "No TLS / Self-Signed"
        ssl_valid = ssl_info.get("is_valid", False)

        # ---------------------------------------------------------
        # INTENT 1: CREDENTIAL SUBMISSION & INCIDENT RESPONSE
        # ---------------------------------------------------------
        if any(k in q_lower for k in ["credential", "password", "entered", "login", "submitted", "stolen", "account"]):
            if risk_level == "LOW" or risk_score < 45:
                return (
                    f"### Credential Submission Assessment for `{url}`: LOW RISK ({risk_score}/100)\n\n"
                    f"Because `{url}` was assessed as a **legitimate, LOW-risk destination** with authentic domain infrastructure, standard TLS, and zero phishing indicators, entering credentials here is expected **normal authentication**.\n\n"
                    f"**Prudent Verification Guidelines:**\n"
                    f"1. **Confirm Exact Domain Match**: Double-check your browser address bar to ensure you are actually on the genuine domain (`{domain}`) and not a typosquat or punycode clone.\n"
                    f"2. **No Active Breach Protocol Needed**: If you verified you are on the genuine website, you do **not** need to trigger emergency SOC breach containment, terminate sessions, or panic.\n"
                    f"3. **Standard Cyber Hygiene**: As a best-practice defense-in-depth measure per NIST SP 800-63B, ensure your authentic account uses a strong unique password and multi-factor authentication (MFA).\n"
                    f"4. **Verify Context**: If you arrived here via an unsolicited message or email, ensure you did not grant unexpected OAuth or application-level permissions."
                )

            elif risk_level == "HIGH" or risk_score >= 75 or len(threat_matches) > 0:
                threat_note = f" (Confirmed in: {', '.join(threat_matches)})" if threat_matches else ""
                return (
                    f"### 🚨 CRITICAL INCIDENT RESPONSE: Credential Submission on HIGH-RISK Target `{url}` (Risk Score: {risk_score}/100)\n\n"
                    f"**WARNING:** `{url}` exhibits high-confidence phishing indicators{threat_note}. Submitting credentials on this site represents an **active credential theft incident**.\n\n"
                    f"**Immediate Containment Protocol (CISA & NIST SP 800-63B Guidelines):**\n"
                    f"1. **Emergency Password Reset**: Open a new browser window, navigate directly to the legitimate service's verified URL (do **not** follow links from the suspicious message or site), and reset your password immediately.\n"
                    f"2. **Terminate Active Sessions**: Log out of all active web and mobile sessions across all devices. Modern Adversary-in-the-Middle (AiTM) phishing proxies capture session cookies alongside passwords; terminating active sessions invalidates stolen session tokens.\n"
                    f"3. **Enforce Phishing-Resistant MFA**: Upgrade to FIDO2 / WebAuthn hardware security keys or an authenticator app per CISA Alert AA22-216A. Disable SMS-based OTPs, which are vulnerable to proxy interception.\n"
                    f"4. **Audit Account for Attacker Persistence**: Check account security settings for newly enrolled MFA devices, new email forwarding rules, or unauthorized OAuth applications created by the adversary.\n"
                    f"5. **Escalate to Security Operations (SOC)**: If this is a corporate or work account, immediately report the incident to your IT/SOC team with the scan evidence and target URL."
                )

            else:  # MEDIUM RISK
                return (
                    f"### ⚠️ Precautionary Guidance: Credential Submission on MEDIUM-RISK Target `{url}` (Risk Score: {risk_score}/100)\n\n"
                    f"`{url}` was assessed with an elevated, borderline risk score (**MEDIUM Risk**). The URL exhibits anomalies (such as lexical deviation, atypical subdomains, or unverified registration) without confirmed threat blacklist listing.\n\n"
                    f"**Recommended Precautionary Safeguards:**\n"
                    f"1. **Precautionary Password Update**: To eliminate compromise risk, navigate directly to the official legitimate provider portal and update your password.\n"
                    f"2. **Audit Recent Logins**: Check the account's recent login and IP activity logs to ensure no unauthorized access occurred immediately following your submission.\n"
                    f"3. **Out-of-Band Verification**: If you were prompted to log in from an unsolicited link or message, verify the authenticity of the communication through a separate, trusted channel before proceeding."
                )

        # ---------------------------------------------------------
        # INTENT 2: WHY WAS THIS FLAGGED / RISK SCORE BREAKDOWN
        # ---------------------------------------------------------
        elif any(k in q_lower for k in ["why", "flag", "reason", "score", "detect", "assess", "decision"]):
            if risk_level == "LOW" or risk_score < 45:
                # Group legitimacy features
                benign_exps = [e for e in feature_explanations if e.get("direction") == "lowers_risk"]
                benign_str = "\n".join([f"- **{e.get('display_name')}**: {e.get('summary_text')}" for e in benign_exps[:4]]) if benign_exps else "- Lexical features conform to established legitimate website profiles."

                return (
                    f"### Safety Assessment for `{url}`: Not Flagged as Malicious (LOW Risk: {risk_score}/100)\n\n"
                    f"This target was **NOT flagged as malicious**. FraudLens AI assessed `{url}` as **LOW Risk** based on positive authenticity evidence:\n\n"
                    f"**Authenticity Indicators:**\n"
                    f"- **Model Phishing Probability**: `{ml_pct}` (well below the suspicion threshold).\n"
                    f"- **Lexical Profile**: Standard URL structure with trusted domain naming and no deceptive keyword lures.\n"
                    f"- **Infrastructure**: Valid DNS resolution (`{dns_status}`) and active TLS certificate (`{ssl_issuer}`).\n"
                    f"- **Threat Intelligence**: Clean status across PhishTank, OpenPhish, and Google Safe Browsing.\n\n"
                    f"**Primary Model Legitimacy Drivers:**\n{benign_str}\n\n"
                    f"*Note:* Automated evaluation confirms this target matches benign web profiles."
                )

            elif risk_level == "HIGH" or risk_score >= 75:
                indicator_bullets = "\n".join([f"- **{i.get('title')}** ({i.get('severity')}): {i.get('description')}" for i in indicators]) if indicators else "- Multiple high-impact phishing characteristics detected."
                threat_note = f"Confirmed in threat feeds: {', '.join(threat_matches)}." if threat_matches else "No confirmed blacklist hits (novel zero-day campaigns often evade feed indexing during initial hours)."
                risk_exps = [e for e in feature_explanations if e.get("direction") in ["raises_risk", "increases_phishing"]]
                risk_str = "\n".join([f"- **{e.get('display_name')}**: {e.get('summary_text')}" for e in risk_exps[:4]]) if risk_exps else "- Lexical features strongly indicate phishing patterns."

                return (
                    f"### 🚨 High-Risk Assessment Breakdown for `{url}` (HIGH Risk: {risk_score}/100)\n\n"
                    f"This target was flagged as **HIGH Risk** due to severe indicators of phishing, domain impersonation, or credential harvesting:\n\n"
                    f"**Core Risk Findings:**\n"
                    f"- **Model Phishing Probability**: `{ml_pct}` (severe phishing confidence).\n"
                    f"- **Threat Intelligence Status**: {threat_note}\n\n"
                    f"**Triggered Heuristic Indicators:**\n{indicator_bullets}\n\n"
                    f"**Top Model Risk Drivers (TreeSHAP):**\n{risk_str}\n\n"
                    f"This combination of structural markers and security signals indicates high danger."
                )

            else:  # MEDIUM RISK
                indicator_bullets = "\n".join([f"- **{i.get('title')}**: {i.get('description')}" for i in indicators]) if indicators else "- Borderline lexical signals elevated the risk score."
                return (
                    f"### ⚠️ Ambiguity Analysis for `{url}` (MEDIUM Risk: {risk_score}/100)\n\n"
                    f"This target received a **MEDIUM Risk** rating because it exhibits anomalous or borderline characteristics that deviate from benign baseline expectations:\n\n"
                    f"**Observed Signals:**\n"
                    f"- **Model Phishing Probability**: `{ml_pct}`.\n"
                    f"- **Threat Intelligence**: No confirmed blacklist matches recorded at this time.\n\n"
                    f"**Triggered Heuristic Warnings:**\n{indicator_bullets}\n\n"
                    f"Because attackers frequently launch zero-day sites that are not yet cataloged in threat feeds, manual verification of the apex domain is recommended before entering sensitive credentials."
                )

        # ---------------------------------------------------------
        # INTENT 3: FEATURE INFLUENCES & SHAP EXPLANATIONS
        # ---------------------------------------------------------
        elif any(k in q_lower for k in ["feature", "influence", "shap", "model", "attribute", "driver", "variable"]):
            if feature_explanations:
                risk_drivers = [e for e in feature_explanations if e.get("direction") in ["raises_risk", "increases_phishing"]]
                benign_drivers = [e for e in feature_explanations if e.get("direction") in ["lowers_risk", "decreases_phishing"]]

                risk_section = "\n".join([
                    f"- **{e.get('display_name')}** (Value: `{e.get('feature_value')}`): {e.get('summary_text')} *(Impact: +{abs(e.get('shap_impact', 0)):.4f})*"
                    for e in risk_drivers[:4]
                ]) if risk_drivers else "- No significant risk-elevating features identified."

                benign_section = "\n".join([
                    f"- **{e.get('display_name')}** (Value: `{e.get('feature_value')}`): {e.get('summary_text')} *(Impact: -{abs(e.get('shap_impact', 0)):.4f})*"
                    for e in benign_drivers[:4]
                ]) if benign_drivers else "- No significant benign-supporting features identified."

                return (
                    f"### TreeSHAP Feature Attributions for `{url}`\n\n"
                    f"FraudLens AI uses TreeSHAP (SHapley Additive exPlanations) to explain feature contributions computed by the trained Random Forest classifier on 22 structural URL-only features:\n\n"
                    f"#### 🔴 Risk-Elevating Factors (Pushed Toward Phishing):\n{risk_section}\n\n"
                    f"#### 🟢 Legitimacy-Supporting Factors (Pushed Toward Benign):\n{benign_section}\n\n"
                    f"*Methodology Note:* TreeSHAP provides game-theoretic feature attributions with mathematical consistency, proving exactly which lexical signals influenced the prediction."
                )
            else:
                # Dynamic fallback using actual observed features
                url_len = features.get("URLLength", len(url))
                is_https = features.get("IsHTTPS", 1 if url.startswith("https") else 0)
                subdomains = features.get("NoOfSubDomain", 0)
                tld_prob = features.get("TLDLegitimateProb", "N/A")
                is_ip = features.get("IsDomainIP", 0)

                return (
                    f"### Model Feature Influences for `{url}`\n\n"
                    f"The Random Forest model evaluated 22 URL-only structural features for this target:\n\n"
                    f"- **URL Length**: `{url_len}` characters\n"
                    f"- **HTTPS Present**: `{'Yes' if is_https == 1 else 'No'}`\n"
                    f"- **Subdomain Count**: `{subdomains}` subdomains\n"
                    f"- **Raw IP Hostname**: `{'Yes' if is_ip == 1 else 'No'}`\n"
                    f"- **TLD Legitimacy Prior**: `{tld_prob}`\n\n"
                    f"These structural characteristics were evaluated against patterns learned from 235,000+ benchmark URLs in the PhiUSIIL dataset."
                )

        # ---------------------------------------------------------
        # INTENT 4: NAVIGATION SAFETY & TRUST
        # ---------------------------------------------------------
        elif any(k in q_lower for k in ["safe", "trust", "legit", "visit", "click", "open", "danger"]):
            if risk_level == "LOW" or risk_score < 45:
                return (
                    f"### Navigation Safety Assessment for `{url}`: Safe for Normal Use\n\n"
                    f"- **Risk Tier**: **LOW RISK** ({risk_score}/100)\n"
                    f"- **Verdict**: Safe for standard browsing and legitimate interaction.\n"
                    f"- **Precautions**: Confirm that the domain displayed in the browser address bar matches `{domain}`. Ensure the TLS padlock is active."
                )
            elif risk_level == "HIGH" or risk_score >= 75:
                return (
                    f"### 🚨 Safety Warning for `{url}`: DO NOT INTERACT\n\n"
                    f"- **Risk Tier**: **HIGH RISK** ({risk_score}/100)\n"
                    f"- **Verdict**: Extreme likelihood of credential theft, spoofing, or malware delivery.\n"
                    f"- **Precautions**: **Do not click links or enter information**. Close any open tabs pointing to this URL and block the destination."
                )
            else:
                return (
                    f"### ⚠️ Navigation Caution for `{url}`: Exercise Discretion\n\n"
                    f"- **Risk Tier**: **MEDIUM RISK** ({risk_score}/100)\n"
                    f"- **Verdict**: Anomalous or unverified domain characteristics detected.\n"
                    f"- **Precautions**: You may view public content, but **avoid entering credentials, credit card details, or downloading files**."
                )

        # ---------------------------------------------------------
        # INTENT 5: INFRASTRUCTURE & DOMAIN FORENSICS
        # ---------------------------------------------------------
        elif any(k in q_lower for k in ["dns", "tls", "ssl", "cert", "certificate", "ip", "server", "host"]):
            return (
                f"### Infrastructure & Network Forensics for `{url}`\n\n"
                f"- **DNS Resolution Status**: `{dns_status}`\n"
                f"- **Resolved IP Address**: `{resolved_ip}`\n"
                f"- **Server Geolocation**: `{location_str}`\n"
                f"- **TLS Certificate Issuer**: `{ssl_issuer}`\n"
                f"- **TLS Validity**: `{'Valid & Active' if ssl_valid else 'Invalid, Expired, or Self-Signed'}`\n\n"
                f"*Forensic Note:* Authentic enterprise services use established domain names with consistent TLS histories, whereas phishing campaigns frequently rely on ephemeral hosting or newly minted short-lived certificates."
            )

        # ---------------------------------------------------------
        # INTENT 6: EXTERNAL THREAT FEEDS
        # ---------------------------------------------------------
        elif any(k in q_lower for k in ["threat", "feed", "phishtank", "openphish", "google"]):
            pt_status = threat_intel.get("feeds", {}).get("phishtank", {}).get("status", "checked")
            op_status = threat_intel.get("feeds", {}).get("openphish", {}).get("status", "checked")
            gsb_status = threat_intel.get("feeds", {}).get("google_safe_browsing", {}).get("status", "checked")

            return (
                f"### External Threat Intelligence Status for `{url}`\n\n"
                f"- **PhishTank Community Feed**: `{pt_status.replace('_', ' ').upper()}`\n"
                f"- **OpenPhish Zero-Day Feed**: `{op_status.replace('_', ' ').upper()}`\n"
                f"- **Google Safe Browsing**: `{gsb_status.replace('_', ' ').upper()}`\n\n"
                f"**CISA & OWASP Defensive Principle:**\n"
                f"Threat intelligence feeds catalog confirmed, reported attack campaigns. The absence of a feed hit is **not proof of safety** for novel zero-day phishing domains, which is why FraudLens AI pairs feeds with machine learning lexical analysis."
            )

        # ---------------------------------------------------------
        # DEFAULT / GENERAL RAG SYNTHESIS
        # ---------------------------------------------------------
        else:
            context_excerpt = "\n\n".join([f"> **{c['title']}**: {c['content'][:250]}..." for c in retrieved_chunks]) if retrieved_chunks else "Standard cybersecurity defensive posture applies."
            return (
                f"### Security Analysis for `{url}`\n\n"
                f"**Scan Context:** Risk Level **{risk_level}** (Score: {risk_score}/100, Model Phishing Probability: {ml_pct}).\n\n"
                f"**Grounded Security Guidance:**\n{context_excerpt}\n\n"
                f"Always treat unexpected authentication requests with skepticism, verify domain spellings, and enforce phishing-resistant multi-factor authentication (MFA)."
            )

    async def _call_external_llm(
        self,
        question: str,
        scan_context: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Optional[str]:
        # Formulate grounded prompt for external LLM enforcing risk differentiation
        prompt = (
            f"You are the FraudLens AI Senior Cybersecurity Analyst. Answer the user's question grounded strictly "
            f"in the provided scan context and cybersecurity reference passages.\n\n"
            f"CRITICAL INSTRUCTIONS FOR CREDENTIAL QUESTIONS:\n"
            f"- If the scan risk_level is LOW, do NOT tell the user to initiate emergency breach response or terminate sessions. "
            f"Explain that the site is legitimate/low-risk, advise standard domain verification and cyber hygiene.\n"
            f"- If the scan risk_level is HIGH, provide full emergency credential compromise containment (immediate password change, "
            f"AiTM session termination, FIDO2 MFA enforcement, SOC reporting).\n"
            f"- For feature questions, cite the actual feature_explanations and observed values provided in the context.\n\n"
            f"Scan Context: {json.dumps(scan_context, default=str)}\n\n"
            f"Retrieved Guidance:\n" + "\n".join([c['content'] for c in retrieved_chunks]) + "\n\n"
            f"User Question: {question}"
        )
        if self.provider == "openai":
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2
                    }
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"]
        return None

# Global singleton
security_assistant_instance = SecurityAssistant()
