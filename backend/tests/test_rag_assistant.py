"""
Unit tests for RAG retrieval and grounded AI Cybersecurity Assistant.
"""

import pytest
from app.rag.vector_store import rag_store_instance
from app.rag.assistant import security_assistant_instance

def test_rag_vector_store_indexed():
    assert rag_store_instance.is_indexed is True
    assert len(rag_store_instance.chunks) > 0

def test_rag_retrieval_returns_relevant_chunks():
    chunks = rag_store_instance.retrieve("What should I do if my password was stolen?", top_k=2)
    assert len(chunks) > 0
    assert "source_url" in chunks[0]
    assert "citation" in chunks[0]

@pytest.mark.asyncio
async def test_assistant_grounded_answer():
    fake_scan = {
        "url": "http://paypal-verification.example.com",
        "risk_level": "HIGH",
        "risk_score": 88,
        "model_phishing_score": 0.88,
        "indicators": [{"title": "Keyword match", "description": "paypal keyword used"}],
        "features": {"URLLength": 42},
        "threat_intel": {"confirmed_sources": []}
    }
    res = await security_assistant_instance.answer_question(
        "Why was this URL flagged?",
        fake_scan
    )
    assert res["grounded"] is True
    assert "HIGH" in res["answer"]
    assert len(res["citations"]) > 0
