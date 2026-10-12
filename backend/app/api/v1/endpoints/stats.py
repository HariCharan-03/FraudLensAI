"""
Dashboard Analytics & Seed Endpoints for FraudLens AI.
Aggregates real statistics from PostgreSQL / SQLite persistence.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database import crud
from app.schemas.health import DashboardStatsResponse
from app.agents.workflow import execute_scan_workflow

router = APIRouter()

@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_statistics(db: AsyncSession = Depends(get_db)):
    """Retrieves live dashboard statistics calculated from actual persisted scans."""
    metrics = await crud.get_dashboard_metrics(db)
    return metrics

@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_sample_scans(db: AsyncSession = Depends(get_db)):
    """
    Development-only helper: Seeds a few diverse, realistic scans
    (labeled as sample data) if the database is fresh.
    """
    sample_urls = [
        "https://www.github.com",
        "https://www.wikipedia.org",
        "http://secure-login-update-paypal-verification.com/account/login?token=abc",
        "http://192.168.1.1/admin/login.php",
        "https://verify-appleid-support-icloud.tk/manage/account",
        "https://www.microsoft.com"
    ]

    # Check existing scan count
    existing_list = await crud.list_scans(db, limit=1)
    if existing_list["total"] >= 20:
        return {
            "status": "already_seeded",
            "message": "Database already contains 20 curated scans. No duplicate scans added.",
            "scan_ids": []
        }

    seeded_records = []
    for u in sample_urls:
        existing_rec = await crud.get_scan_by_url(db, u)
        if existing_rec:
            continue

        state = await execute_scan_workflow(u)
        risk_assessment = state.get("risk_assessment") or {}
        ml_result = state.get("ml_result") or {}

        scan_dict = {
            "id": state["scan_id"],
            "url": u,
            "normalized_url": state.get("normalized_url"),
            "risk_level": risk_assessment.get("risk_level", "INCONCLUSIVE"),
            "risk_score": risk_assessment.get("risk_score", 50),
            "model_score": ml_result.get("phishing_score"),
            "model_version": ml_result.get("model_version", "1.0.0"),
            "model_type": ml_result.get("model_type", "RandomForest"),
            "is_phishing_predicted": ml_result.get("is_phishing_predicted"),
            "status": state.get("status", "completed"),
            "error_message": state.get("url_error"),
            "plain_explanation": state.get("explanation"),
            "features": state.get("features"),
            "feature_explanations": ml_result.get("feature_explanations"),
            "indicators": risk_assessment.get("indicators"),
            "recommendations": risk_assessment.get("recommendations"),
            "domain_intel": state.get("domain_intel"),
            "threat_intel": state.get("threat_intel"),
            "is_sample_seed": True
        }
        rec = await crud.create_scan_record(db, scan_dict)
        seeded_records.append(rec.id)

    return {
        "status": "success",
        "message": f"Seeded {len(seeded_records)} realistic demonstration scans.",
        "scan_ids": seeded_records
    }
