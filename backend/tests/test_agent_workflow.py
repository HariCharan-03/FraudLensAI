"""
Unit tests for LangGraph multi-agent workflow execution and routing.
"""

import pytest
from app.agents.workflow import execute_scan_workflow

@pytest.mark.asyncio
async def test_workflow_successful_execution():
    state = await execute_scan_workflow("https://www.wikipedia.org")
    assert state["status"] == "completed"
    assert state["is_valid_url"] is True
    assert state["risk_assessment"] is not None
    assert state["ml_result"] is not None
    assert len(state["execution_trace"]) >= 5
    assert "explanation_node" in state["execution_trace"]

@pytest.mark.asyncio
async def test_workflow_invalid_url_termination():
    state = await execute_scan_workflow("ftp://invalid-scheme.local")
    assert state["is_valid_url"] is False
    assert state["status"] == "failed"
    assert "Unsupported URL scheme" in state["url_error"]
