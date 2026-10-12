"""
Integration tests for FastAPI endpoints using ASGITransport.
"""

import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] in ["healthy", "degraded"]
            assert data["app_name"] == "FraudLens AI"

@pytest.mark.asyncio
async def test_scan_and_get_scan():
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Create scan
            post_resp = await client.post("/api/v1/scan", json={"url": "https://test-ephemeral-endpoint-check.org"})
            assert post_resp.status_code in [200, 201]
            scan_data = post_resp.json()
            scan_id = scan_data["id"]

            # Get scan
            get_resp = await client.get(f"/api/v1/scan/{scan_id}")
            assert get_resp.status_code == 200
            fetched = get_resp.json()
            assert fetched["id"] == scan_id
            assert fetched["risk_level"] in ["LOW", "MEDIUM", "HIGH", "INCONCLUSIVE"]

            # Clean up test scan so tests never pollute persistence
            del_resp = await client.delete(f"/api/v1/scan/{scan_id}")
            assert del_resp.status_code in [200, 204]

@pytest.mark.asyncio
async def test_list_scans_and_stats():
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            stats_resp = await client.get("/api/v1/stats")
            assert stats_resp.status_code == 200
            assert "total_scans" in stats_resp.json()

            list_resp = await client.get("/api/v1/scans?limit=10")
            assert list_resp.status_code == 200
            assert "items" in list_resp.json()
