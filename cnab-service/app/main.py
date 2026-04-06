"""
CNAB Service - Storage and query service for CNAB transactions.
Port 8002. Stores stores, transactions, and serves balance queries.
"""

from app.routers.dashboard_router import dashboard_router
from app.routers.internal_router import internal_router
from app.routers.store_router import store_router
from app.routers.transaction_type_router import transaction_type_router
from cnab_shared import CNABFastAPI

app = CNABFastAPI().setup(
    title="CNAB Parser Service",
    summary="Storage and query service for CNAB transactions.",
    description=(
        "Stores stores, transactions, and serves balance queries. "
        "Public endpoints require JWT auth; internal endpoints use Fernet token auth."
    ),
    routers=[store_router, transaction_type_router, internal_router, dashboard_router],
    check_database=False,
)
