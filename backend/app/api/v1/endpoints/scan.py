"""
Scan API Endpoints for FraudLens AI.
Handles URL submission, LangGraph execution, persistence, retrieval, and deletion.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database import crud
from app.schemas.scan import ScanCreateRequest, ScanResponse, ScanListResponse
from app.agents.workflow import execute_scan_workflow

logger = logging.getLogger("api_scan")
router = APIRouter()

@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def submit_scan(
    payload: ScanCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a URL for comprehensive risk analysis.
    Executes the multi-agent LangGraph workflow and persists the findings.
    """
    raw_url = payload.url.strip()
    if not raw_url:
        raise HTTPException(status_code=400, detail="Target URL cannot be empty.")

    try:
        # Execute multi-agent orchestration
        workflow_state = await execute_scan_workflow(raw_url)

        if not workflow_state.get("is_valid_url", False):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid URL: {workflow_state.get('url_error', 'Failed validation')}"
            )

        risk_assessment = workflow_state.get("risk_assessment") or {}
        ml_result = workflow_state.get("ml_result") or {}

        # Prepare database record
        scan_dict = {
            "id": workflow_state["scan_id"],
            "url": raw_url,
            "normalized_url": workflow_state.get("normalized_url"),
            "risk_level": risk_assessment.get("risk_level", "INCONCLUSIVE"),
            "risk_score": risk_assessment.get("risk_score", 50),
            "model_score": ml_result.get("phishing_score"),
            "model_version": ml_result.get("model_version", "1.0.0"),
            "model_type": ml_result.get("model_type", "RandomForest"),
            "is_phishing_predicted": ml_result.get("is_phishing_predicted"),
            "status": workflow_state.get("status", "completed"),
            "error_message": workflow_state.get("url_error"),
            "plain_explanation": workflow_state.get("explanation"),
            "features": workflow_state.get("features"),
            "feature_explanations": ml_result.get("feature_explanations"),
            "indicators": risk_assessment.get("indicators"),
            "recommendations": risk_assessment.get("recommendations"),
            "domain_intel": workflow_state.get("domain_intel"),
            "threat_intel": workflow_state.get("threat_intel")
        }

        # Persist scan record so each scan event increments count and updates history
        record = await crud.create_scan_record(db, scan_dict)
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scan execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal scanning error: {str(e)}")

@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan_details(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves full scan evidence and risk assessment by scan ID."""
    record = await crud.get_scan_by_id(db, scan_id)
    if not record:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return record

@router.get("/scans", response_model=ScanListResponse)
async def list_scans_history(
    search: Optional[str] = Query(None, description="Filter by URL keyword"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW, MEDIUM, HIGH, INCONCLUSIVE)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieves paginated scan history with search and risk filters."""
    result = await crud.list_scans(
        db,
        search=search,
        risk_level=risk_level,
        limit=limit,
        offset=offset
    )
    return result

@router.delete("/scans/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
@router.delete("/scan/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan_record(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Deletes a specific scan record and associated conversation history."""
    deleted = await crud.delete_scan(db, scan_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return None
