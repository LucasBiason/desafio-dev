# cnab-dashboard — multi-stage: base (deps + app), test (CI), runtime (final)

# Stage: base
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY cnab-shared /tmp/cnab-shared
RUN pip install --no-cache-dir /tmp/cnab-shared

COPY cnab-dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cnab-dashboard/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY cnab-dashboard/app ./app
COPY cnab-dashboard/pyproject.toml .

EXPOSE 8004

# Stage: test
FROM base AS test

COPY cnab-dashboard/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY cnab-dashboard/tests ./tests
COPY cnab-dashboard/.coveragerc .

ENTRYPOINT ["/entrypoint.sh"]
CMD ["test"]

# Stage: runtime
FROM base AS runtime

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

LABEL org.opencontainers.image.title="cnab-dashboard" \
      org.opencontainers.image.description="CNAB analytics dashboard service (FastAPI)" \
      org.opencontainers.image.vendor="CNAB Parser"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["runserver"]
