"""
AI Security Assistant Chat API Endpoints for FraudLens AI.
Enables asking follow-up questions grounded in a scan's evidence with RAG retrieval.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database import crud
from app.schemas.assistant import ChatAskRequest, ChatAskResponse, ChatMessageResponse
from app.rag.assistant import security_assistant_instance

router = APIRouter()

@router.post("/scan/{scan_id}/chat", response_model=ChatAskResponse, status_code=status.HTTP_200_OK)
async def chat_with_assistant(
    scan_id: str,
    payload: ChatAskRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a user question regarding a specific scan.
    Returns an answer grounded in the scan's findings and retrieved cybersecurity guidelines.
    """
    scan = await crud.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found.")

    scan_context = {
        "scan_id": scan.id,
        "url": scan.url,
        "normalized_url": scan.normalized_url,
        "risk_level": scan.risk_level,
        "risk_score": scan.risk_score,
        "model_phishing_score": scan.model_score,
        "model_type": scan.model_type,
        "is_phishing_predicted": scan.is_phishing_predicted,
        "indicators": scan.indicators or [],
        "features": scan.features or {},
        "feature_explanations": scan.feature_explanations or [],
        "recommendations": scan.recommendations or [],
        "plain_explanation": scan.plain_explanation,
        "threat_intel": scan.threat_intel or {},
        "domain_intel": scan.domain_intel or {}
    }

    # 1. Save user message to database
    await crud.add_chat_message(
        db,
        scan_id=scan.id,
        role="user",
        content=payload.question
    )

    # 2. Generate grounded answer
    assistant_result = await security_assistant_instance.answer_question(
        question=payload.question,
        scan_context=scan_context
    )

    # 3. Save assistant message with citations to database
    await crud.add_chat_message(
        db,
        scan_id=scan.id,
        role="assistant",
        content=assistant_result["answer"],
        citations=assistant_result["citations"]
    )

    return assistant_result

@router.get("/scan/{scan_id}/chat", response_model=List[ChatMessageResponse])
async def get_chat_history(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves conversation history for a specific scan."""
    scan = await crud.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan record not found.")

    messages = await crud.get_chat_messages_for_scan(db, scan_id)
    return messages
