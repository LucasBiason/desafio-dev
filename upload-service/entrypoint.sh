#!/usr/bin/env bash
set -euo pipefail

# Function to display CLI help
cli_help() {
  local cli_name=${0##*/}
  echo "
$cli_name
System entrypoint CLI
Usage: $cli_name [command]
Commands:
  migrate       Apply Alembic migrations
  test          Run tests with coverage
  dev           Start development server (uvicorn with reload)
  prod          Start production server (uvicorn)
  runserver     Alias for dev (backward compatibility)
  *             Display this help message
"
  exit 1
}


# Main command handler
case "${1:-}" in
  migrate)
    alembic upgrade head
    ;;
  test)
    pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-config=.coveragerc
    ;;
  dev|runserver)
    PORT=${PORT:-8003}
    echo "Starting development server (uvicorn) on 0.0.0.0:$PORT"
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
    ;;
  prod)
    PORT=${PORT:-8003}
    WORKERS=${WORKERS:-4}
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers $WORKERS --log-level info
    ;;
  *)
    cli_help
    ;;
esac
