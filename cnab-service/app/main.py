"""
CNAB Service - Storage and query service for CNAB transactions.
Port 8002. Stores stores, transactions, and serves balance queries.
"""

from app.routers.store_router import store_router
from app.routers.transaction_router import transaction_router
from app.routers.transaction_type_router import transaction_type_router
from app.routers.upload_router import upload_router
from cnab_shared import CNABFastAPI

app = CNABFastAPI().setup(
    title="CNAB Parser Service",
    summary="Storage and query service for CNAB transactions.",
    description=(
        "Stores stores, transactions, and serves balance queries. "
        "Public endpoints require JWT auth; upload endpoint uses Fernet token auth."
    ),
    routers=[store_router, transaction_router, transaction_type_router, upload_router],
    check_database=False,
)
