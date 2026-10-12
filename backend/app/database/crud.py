"""
CRUD Operations & Aggregations for FraudLens AI.
Provides scan persistence, filtering, deletion, grounded chat messages,
and real database statistics for the analytics dashboard.
"""

import datetime
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, desc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import ScanRecord, ChatMessageRecord

logger = logging.getLogger("database_crud")

async def create_scan_record(session: AsyncSession, scan_data: Dict[str, Any]) -> ScanRecord:
    record = ScanRecord(**scan_data)
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record

async def get_scan_by_id(session: AsyncSession, scan_id: str) -> Optional[ScanRecord]:
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_scan_by_url(session: AsyncSession, url: str) -> Optional[ScanRecord]:
    """Retrieves an existing scan matching the raw URL, normalized URL, or www/scheme variation."""
    clean_url = url.strip().rstrip("/")
    variations = {url, clean_url}
    for u in list(variations):
        if "://www." in u:
            variations.add(u.replace("://www.", "://"))
        elif "://" in u:
            variations.add(u.replace("://", "://www."))

    stmt = select(ScanRecord).where(
        (ScanRecord.url.in_(variations)) |
        (ScanRecord.normalized_url.in_(variations))
    ).order_by(desc(ScanRecord.created_at)).limit(1)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def update_scan_record(session: AsyncSession, record: ScanRecord, scan_data: Dict[str, Any]) -> ScanRecord:
    """Updates an existing scan record with fresh findings without duplicating."""
    for key, value in scan_data.items():
        if key != "id":
            setattr(record, key, value)
    record.created_at = datetime.datetime.now(datetime.timezone.utc)
    await session.commit()
    await session.refresh(record)
    return record

async def list_scans(
    session: AsyncSession,
    search: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    stmt = select(ScanRecord)

    if search:
        search_pattern = f"%{search.strip()}%"
        stmt = stmt.where(ScanRecord.url.ilike(search_pattern))

    if risk_level and risk_level.upper() != "ALL":
        stmt = stmt.where(ScanRecord.risk_level == risk_level.upper())

    # Count total matching
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await session.execute(count_stmt)).scalar() or 0

    # Paginate and order by newest first
    stmt = stmt.order_by(desc(ScanRecord.created_at)).limit(limit).offset(offset)
    records = (await session.execute(stmt)).scalars().all()

    return {
        "items": records,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }

async def delete_scan(session: AsyncSession, scan_id: str) -> bool:
    stmt = select(ScanRecord).where(ScanRecord.id == scan_id)
    record = (await session.execute(stmt)).scalar_one_or_none()
    if not record:
        return False
    await session.delete(record)
    await session.commit()
    return True

async def get_dashboard_metrics(session: AsyncSession) -> Dict[str, Any]:
    """Calculates live analytics metrics directly from persisted database records."""
    total_stmt = select(func.count(ScanRecord.id))
    total_scans = (await session.execute(total_stmt)).scalar() or 0

    phishing_stmt = select(func.count(ScanRecord.id)).where(ScanRecord.risk_level == "HIGH")
    high_risk_count = (await session.execute(phishing_stmt)).scalar() or 0

    medium_stmt = select(func.count(ScanRecord.id)).where(ScanRecord.risk_level == "MEDIUM")
    medium_risk_count = (await session.execute(medium_stmt)).scalar() or 0

    low_stmt = select(func.count(ScanRecord.id)).where(ScanRecord.risk_level == "LOW")
    low_risk_count = (await session.execute(low_stmt)).scalar() or 0

    inconclusive_stmt = select(func.count(ScanRecord.id)).where(ScanRecord.risk_level == "INCONCLUSIVE")
    inconclusive_count = (await session.execute(inconclusive_stmt)).scalar() or 0

    # Recent scans
    recent_stmt = select(ScanRecord).order_by(desc(ScanRecord.created_at)).limit(8)
    recent_scans = (await session.execute(recent_stmt)).scalars().all()

    # Risk level distribution
    distribution = [
        {"name": "High Risk", "value": high_risk_count, "color": "#ef4444"},
        {"name": "Medium Risk", "value": medium_risk_count, "color": "#f59e0b"},
        {"name": "Low Risk", "value": low_risk_count, "color": "#10b981"},
        {"name": "Inconclusive", "value": inconclusive_count, "color": "#64748b"}
    ]

    return {
        "total_scans": total_scans,
        "high_risk_count": high_risk_count,
        "medium_risk_count": medium_risk_count,
        "low_risk_count": low_risk_count,
        "inconclusive_count": inconclusive_count,
        "distribution": distribution,
        "recent_scans": recent_scans
    }

async def add_chat_message(
    session: AsyncSession,
    scan_id: str,
    role: str,
    content: str,
    citations: Optional[List[Dict[str, Any]]] = None
) -> ChatMessageRecord:
    msg = ChatMessageRecord(
        scan_id=scan_id,
        role=role,
        content=content,
        citations=citations
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg

async def get_chat_messages_for_scan(session: AsyncSession, scan_id: str) -> List[ChatMessageRecord]:
    stmt = select(ChatMessageRecord).where(ChatMessageRecord.scan_id == scan_id).order_by(ChatMessageRecord.created_at)
    return (await session.execute(stmt)).scalars().all()
