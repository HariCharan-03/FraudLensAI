"""
Main FastAPI Application Entrypoint for FraudLens AI.
Configures CORS, lifespan startup, database initialization, and versioned routes.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from app.api.v1.router import api_router
from app.database.session import init_db
from app.ml.pipeline import ml_pipeline_instance
from app.rag.vector_store import rag_store_instance

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fraudlens_main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Initializing FraudLens AI Backend...")
    await init_db()

    # Verify ML Engine
    if ml_pipeline_instance.is_ready:
        logger.info(f"ML Pipeline is READY with model: {ml_pipeline_instance.feature_meta.get('model_type')}")
    else:
        logger.warning("ML Pipeline is NOT READY. Predictions may return model_not_ready.")

    # Verify RAG store
    if rag_store_instance.is_indexed:
        logger.info(f"RAG Knowledge Store is READY with {len(rag_store_instance.chunks)} chunks.")

    yield
    logger.info("Shutting down FraudLens AI Backend.")

app = FastAPI(
    title="FraudLens AI - Intelligent Phishing Detection & Website Risk Analysis Platform",
    description=(
        "Production-grade cybersecurity platform combining machine learning URL classification, "
        "SHAP explainability, domain intelligence, SSRF defense, LangGraph multi-agent orchestration, "
        "and RAG-powered security assistance."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
origins_env = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]')
try:
    allowed_origins = json.loads(origins_env)
except Exception:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include v1 API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "FraudLens AI",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": "/api/v1"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
