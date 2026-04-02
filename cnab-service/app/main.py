"""
CNAB Service - Import and display of CNAB transactions.
Port 8002. Main service for processing CNAB files.
"""

from cnab_shared import CNABFastAPI

app = CNABFastAPI().setup(
    title="CNAB Parser Service",
    summary="API for importing and displaying CNAB transactions.",
    description=(
        "Service responsible for uploading, parsing, normalizing and "
        "storing financial transactions in CNAB format."
    ),
    routers=[],
    check_database=False,
)
