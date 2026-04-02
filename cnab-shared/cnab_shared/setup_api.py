"""Centralized FastAPI setup for CNAB Parser microservices."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .middleware.exceptions_middleware import CatchExceptionsMiddleware
from .middleware.logging_middleware import LoggingMiddleware
from .routers.health_router import health_router


class CNABFastAPI:
    """Configures a FastAPI application consistently across all microservices."""

    def __init__(self) -> None:
        self.app: FastAPI | None = None

    def setup(
        self,
        title: str,
        summary: str,
        description: str,
        routers: list,
        auth_middleware=None,
        check_database: bool = True,
    ) -> FastAPI:
        """
        Configures and returns the FastAPI application with middlewares and routers.

        Args:
            title: Application title shown in OpenAPI docs.
            summary: Short application summary.
            description: Detailed application description.
            routers: List of APIRouter instances to include.
            auth_middleware: Optional authentication middleware to add.
            check_database: Whether to verify the database on health check.

        Returns:
            Configured FastAPI application instance.
        """
        self.app = FastAPI(title=title, summary=summary, description=description)

        self._setup_cors()
        self.app.add_middleware(CatchExceptionsMiddleware)
        self.app.add_middleware(LoggingMiddleware)

        if auth_middleware:
            self.app.add_middleware(auth_middleware)

        self.app.include_router(health_router)

        for router in routers:
            self.app.include_router(router)

        return self.app

    def _setup_cors(self) -> None:
        """Configures CORS middleware to allow requests from any origin."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            max_age=86400,
        )
