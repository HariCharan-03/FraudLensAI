"""
Hybrid Multi-Agent Workflow for FraudLens AI using LangGraph.
Orchestrates URL feature extraction, safe domain resolution, ML prediction,
threat intelligence aggregation, deterministic risk assessment, and plain-English explanation.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from app.agents.state import ScanState
from app.ml.pipeline import ml_pipeline_instance
from app.security.ssrf import validate_url_scheme
from app.services.domain_intel import DomainIntelligenceService
from app.services.threat_intel import ThreatIntelligenceService
from app.services.risk_engine import RiskAssessmentEngine

logger = logging.getLogger("agent_workflow")

domain_service = DomainIntelligenceService(dns_timeout=3.0)
threat_service = ThreatIntelligenceService(timeout=4.0)

async def validate_and_extract_url_node(state: ScanState) -> Dict[str, Any]:
    """Component 1: Validates URL and extracts numerical URL-only features."""
    trace = list(state.get("execution_trace", []))
    trace.append("validate_and_extract_url_node")
    raw_url = state["raw_url"].strip()

    try:
        validate_url_scheme(raw_url)
        extraction = ml_pipeline_instance.feature_extractor.extract_features(raw_url)
        return {
            "is_valid_url": True,
            "url_error": None,
            "normalized_url": extraction["metadata"]["normalized_url"],
            "features": extraction["features"],
            "url_metadata": extraction["metadata"],
            "execution_trace": trace
        }
    except Exception as e:
        logger.warning(f"URL validation failed for '{raw_url}': {e}")
        return {
            "is_valid_url": False,
            "url_error": str(e),
            "features": None,
            "url_metadata": None,
            "status": "failed",
            "execution_trace": trace
        }

async def domain_intelligence_node(state: ScanState) -> Dict[str, Any]:
    """Component 2: Gathers DNS records, SSL certificate, and server location safely."""
    trace = list(state.get("execution_trace", []))
    trace.append("domain_intelligence_node")
    domain = state["url_metadata"]["domain"]

    domain_data = await domain_service.analyze_domain(domain)
    return {
        "domain_intel": domain_data,
        "execution_trace": trace
    }

async def threat_intelligence_node(state: ScanState) -> Dict[str, Any]:
    """Component 3: Queries optional external threat feeds (Safe Browsing, PhishTank)."""
    trace = list(state.get("execution_trace", []))
    trace.append("threat_intelligence_node")
    norm_url = state["normalized_url"]

    threat_data = await threat_service.aggregate_threat_intelligence(norm_url)
    return {
        "threat_intel": threat_data,
        "execution_trace": trace
    }

async def ml_detection_node(state: ScanState) -> Dict[str, Any]:
    """Component 4: Runs trained ML model inference and SHAP explainability."""
    trace = list(state.get("execution_trace", []))
    trace.append("ml_detection_node")
    raw_url = state["raw_url"]

    ml_res = ml_pipeline_instance.predict(raw_url)
    return {
        "ml_result": ml_res,
        "execution_trace": trace
    }

async def risk_assessment_node(state: ScanState) -> Dict[str, Any]:
    """Component 5: Deterministic risk assessment combining all findings."""
    trace = list(state.get("execution_trace", []))
    trace.append("risk_assessment_node")

    ml_res = state.get("ml_result") or {}
    domain_intel = state.get("domain_intel") or {}
    threat_intel = state.get("threat_intel") or {}

    risk_eval = RiskAssessmentEngine.calculate_risk(
        ml_result=ml_res,
        domain_intel=domain_intel,
        threat_intel=threat_intel
    )

    return {
        "risk_assessment": risk_eval,
        "execution_trace": trace
    }

async def explanation_node(state: ScanState) -> Dict[str, Any]:
    """Component 6: Synthesizes structured results into an understandable explanation."""
    trace = list(state.get("execution_trace", []))
    trace.append("explanation_node")

    risk_eval = state.get("risk_assessment", {})
    risk_level = risk_eval.get("risk_level", "Unknown")
    risk_score = risk_eval.get("risk_score", 0)
    ml_res = state.get("ml_result", {})
    explanations = ml_res.get("feature_explanations", [])
    threat_intel = state.get("threat_intel", {})

    top_drivers = [e for e in explanations if e.get("direction") == "increases_risk"][:3]
    driver_text = ", ".join([f"{d['display_name']} ({d['summary_text']})" for d in top_drivers]) if top_drivers else "no individual features exhibited strong anomalous patterns."

    confirmed_sources = threat_intel.get("confirmed_sources", [])
    feed_text = f"Confirmed in threat repositories: {', '.join(confirmed_sources)}." if confirmed_sources else "No active campaign matches recorded in external feeds."

    plain_explanation = (
        f"FraudLens AI assessed this URL as {risk_level} Risk (Risk Score: {risk_score}/100). "
        f"The trained machine learning classifier produced a phishing probability score of {ml_res.get('phishing_score', 'N/A')}. "
        f"Primary model risk drivers included {driver_text} "
        f"Threat intelligence status: {feed_text}"
    )

    return {
        "explanation": plain_explanation,
        "status": "completed",
        "execution_trace": trace
    }

def route_after_validation(state: ScanState) -> Literal["proceed", "end"]:
    if not state.get("is_valid_url", False):
        return "end"
    return "proceed"

# Build LangGraph StateGraph
def build_scan_graph():
    builder = StateGraph(ScanState)

    builder.add_node("validate_url", validate_and_extract_url_node)
    builder.add_node("domain_intel", domain_intelligence_node)
    builder.add_node("threat_intel", threat_intelligence_node)
    builder.add_node("ml_detection", ml_detection_node)
    builder.add_node("risk_assessment", risk_assessment_node)
    builder.add_node("explanation", explanation_node)

    builder.set_entry_point("validate_url")

    builder.add_conditional_edges(
        "validate_url",
        route_after_validation,
        {
            "proceed": "domain_intel",
            "end": END
        }
    )

    builder.add_edge("domain_intel", "threat_intel")
    builder.add_edge("threat_intel", "ml_detection")
    builder.add_edge("ml_detection", "risk_assessment")
    builder.add_edge("risk_assessment", "explanation")
    builder.add_edge("explanation", END)

    return builder.compile()

# Global compiled graph
scan_workflow_graph = build_scan_graph()

async def execute_scan_workflow(raw_url: str, scan_id: str = None) -> ScanState:
    """Entry point to run full LangGraph scan pipeline."""
    initial_state: ScanState = {
        "scan_id": scan_id or str(uuid.uuid4()),
        "raw_url": raw_url,
        "normalized_url": None,
        "is_valid_url": False,
        "url_error": None,
        "features": None,
        "url_metadata": None,
        "domain_intel": None,
        "ml_result": None,
        "threat_intel": None,
        "risk_assessment": None,
        "explanation": None,
        "status": "pending",
        "execution_trace": []
    }

    final_state = await scan_workflow_graph.ainvoke(initial_state)
    return final_state
