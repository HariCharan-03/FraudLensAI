"""
Pydantic Schemas for System Health and Dashboard Analytics.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.scan import ScanResponse

class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    database: Dict[str, Any]
    machine_learning: Dict[str, Any]
    threat_intelligence: Dict[str, Any]
    rag_knowledge_base: Dict[str, Any]

class RiskDistributionItem(BaseModel):
    name: str
    value: int
    color: str

class DashboardStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_scans: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    inconclusive_count: int
    distribution: List[RiskDistributionItem]
    recent_scans: List[ScanResponse]
