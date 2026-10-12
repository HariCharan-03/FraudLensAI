"""
Pydantic Schemas for URL Scans and Risk Evidence.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class ScanCreateRequest(BaseModel):
    url: str = Field(..., description="Target website URL to scan (e.g., https://example.com)", min_length=3, max_length=2048)

class RiskIndicatorSchema(BaseModel):
    type: str
    severity: str
    title: str
    description: str

class FeatureExplanationSchema(BaseModel):
    feature_name: str
    display_name: str
    description: str
    feature_value: Any
    shap_impact: float
    direction: str
    abs_impact: float
    summary_text: str

class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    normalized_url: Optional[str] = None
    created_at: datetime
    risk_level: str
    risk_score: int
    model_score: Optional[float] = None
    model_version: Optional[str] = None
    model_type: Optional[str] = None
    is_phishing_predicted: Optional[bool] = None
    status: str
    error_message: Optional[str] = None
    plain_explanation: Optional[str] = None

    features: Optional[Dict[str, Any]] = None
    feature_explanations: Optional[List[Dict[str, Any]]] = None
    indicators: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    domain_intel: Optional[Dict[str, Any]] = None
    threat_intel: Optional[Dict[str, Any]] = None

class ScanListResponse(BaseModel):
    items: List[ScanResponse]
    total: int
    limit: int
    offset: int
