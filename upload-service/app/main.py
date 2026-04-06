"""Upload Service — CNAB file upload and processing."""

from app.routers.upload_router import upload_router
from cnab_shared import AuthMiddleware, CNABFastAPI

app = CNABFastAPI().setup(
    title="CNAB Upload Service",
    summary="File upload, parsing and processing for CNAB transactions.",
    description="Receives CNAB files, stores upload history, parses and sends data to cnab-service.",
    routers=[upload_router],
    auth_middleware=AuthMiddleware,
    check_database=False,
)
