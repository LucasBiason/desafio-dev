# upload-service — multi-stage: base (deps + app), test (CI), runtime (final)
# Build from repo root: docker build -f upload-service/Dockerfile .
# Compose: context: .  dockerfile: upload-service/Dockerfile

# -----------------------------------------------------------------------------
# Stage: base — runtime dependencies + application code
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Shared library (build context = repo root)
COPY cnab-shared /tmp/cnab-shared
RUN pip install --no-cache-dir /tmp/cnab-shared

COPY upload-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY upload-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY upload-service/app ./app
COPY upload-service/alembic ./alembic
COPY upload-service/alembic.ini .
COPY upload-service/pyproject.toml .

# Upload directory
RUN mkdir -p /app/uploads

EXPOSE 8003

# -----------------------------------------------------------------------------
# Stage: test — CI; test dependencies and files (not included in the final image)
# -----------------------------------------------------------------------------
FROM base AS test

COPY upload-service/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY upload-service/tests ./tests
COPY upload-service/.coveragerc .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["test"]

# -----------------------------------------------------------------------------
# Stage: runtime — final image (no tests, no pytest)
# -----------------------------------------------------------------------------
FROM base AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

LABEL org.opencontainers.image.title="upload-service" \
      org.opencontainers.image.description="CNAB file upload and processing service (FastAPI)" \
      org.opencontainers.image.vendor="CNAB Parser"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["runserver"]
