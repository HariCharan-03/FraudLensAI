"""
Pydantic Schemas for AI Security Assistant Chat and RAG Sources.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class ChatAskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=1000, description="User question regarding the scan")

class CitationSchema(BaseModel):
    title: str
    organization: str
    source_url: str
    citation: str
    relevance: Optional[float] = None

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scan_id: str
    role: str
    content: str
    citations: Optional[List[CitationSchema]] = None
    created_at: datetime

class ChatAskResponse(BaseModel):
    answer: str
    grounded: bool
    citations: List[CitationSchema]
    model_used: str
