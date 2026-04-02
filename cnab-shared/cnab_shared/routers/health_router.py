"""Health check router factory for CNAB microservices."""

import os
from datetime import UTC, datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from ..database.database import get_db


def create_health_router(system_name: str) -> APIRouter:
    """Builds a health router with status, readiness, and liveness endpoints."""
    router = APIRouter(tags=["Health"])

    async def health_check(request: Request):
        return {
            "status": "healthy",
            "system_name": system_name,
            "version": os.getenv("SYSTEM_VERSION", "0.1.0"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def readiness_check(request: Request):
        try:
            db = next(get_db())
            db.execute(text("SELECT 1"))
            db.close()
            return {
                "status": "ready",
                "system_name": system_name,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "system_name": system_name,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            )

    async def liveness_check(request: Request):
        return {
            "status": "alive",
            "system_name": system_name,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    router.add_api_route("/", health_check, methods=["GET"], name="health-root")
    router.add_api_route("/health", health_check, methods=["GET"], name="health")
    router.add_api_route("/health/", health_check, methods=["GET"], name="health-slash")
    router.add_api_route("/health/ready", readiness_check, methods=["GET"], name="health-ready")
    router.add_api_route("/health/live", liveness_check, methods=["GET"], name="health-live")

    return router


# Simple health router for backward compatibility
health_router = APIRouter(tags=["Health"])


@health_router.get("/health")
async def simple_health():
    return {"status": "healthy"}
