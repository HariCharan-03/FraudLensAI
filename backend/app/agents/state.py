"""
State Schema for FraudLens AI LangGraph Multi-Agent Workflow.
Explicitly typed state tracking scan progression, evidence artifacts,
errors, and structured assessment outputs.
"""

from typing import TypedDict, Dict, Any, List, Optional

class ScanState(TypedDict):
    scan_id: str
    raw_url: str
    normalized_url: Optional[str]
    is_valid_url: bool
    url_error: Optional[str]

    # Component 1: URL Analysis & Features
    features: Optional[Dict[str, Any]]
    url_metadata: Optional[Dict[str, Any]]

    # Component 2: Domain Intelligence
    domain_intel: Optional[Dict[str, Any]]

    # Component 3: ML Detection
    ml_result: Optional[Dict[str, Any]]

    # Component 4: Threat Intelligence
    threat_intel: Optional[Dict[str, Any]]

    # Component 5: Risk Assessment
    risk_assessment: Optional[Dict[str, Any]]

    # Component 6: Plain-English Explanation
    explanation: Optional[str]

    # Workflow metadata
    status: str
    execution_trace: List[str]
