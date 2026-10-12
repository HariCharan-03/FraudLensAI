"""
API v1 Router aggregating all endpoints.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import scan, assistant, health, stats

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(scan.router, tags=["Scans"])
api_router.include_router(assistant.router, tags=["Assistant"])
api_router.include_router(stats.router, tags=["Analytics & Seed"])
