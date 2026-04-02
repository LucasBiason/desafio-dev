# user-service — multi-stage: base (deps + app), test (CI), runtime (final)
# Build from repo root: docker build -f user-service/Dockerfile .
# Compose: context: .  dockerfile: user-service/Dockerfile

# -----------------------------------------------------------------------------
# Stage: base — runtime dependencies + application code
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY user-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY user-service/app .
COPY user-service/pyproject.toml .

EXPOSE 8001

# -----------------------------------------------------------------------------
# Stage: test — CI; test dependencies and files (not included in the final image)
# -----------------------------------------------------------------------------
FROM base AS test

COPY user-service/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY user-service/tests ./tests
COPY user-service/.coveragerc .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["test"]

# -----------------------------------------------------------------------------
# Stage: runtime — final image (no tests, no pytest)
# -----------------------------------------------------------------------------
FROM base AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

LABEL org.opencontainers.image.title="user-service" \
      org.opencontainers.image.description="Authentication and user management service (Django + JWT)" \
      org.opencontainers.image.vendor="CNAB Parser"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["runserver"]
