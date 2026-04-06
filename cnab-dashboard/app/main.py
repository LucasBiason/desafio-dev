"""
CNAB Dashboard Service - Analytics and visualization for CNAB data.
Port 8004. Read-only service that queries cnab_data for dashboard statistics.
"""

from app.routers.dashboard_router import dashboard_router
from cnab_shared import CNABFastAPI

app = CNABFastAPI().setup(
    title="CNAB Dashboard Service",
    summary="Analytics and visualization service for CNAB data.",
    description=(
        "Read-only service providing aggregated statistics, charts data, "
        "and transaction detail for the analytics dashboard. Queries the shared cnab_data database."
    ),
    routers=[dashboard_router],
    check_database=False,
)
