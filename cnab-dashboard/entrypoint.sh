#!/usr/bin/env bash

set -euo pipefail

cli_help() {
  local cli_name=${0##*/}
  echo "
$cli_name
System entrypoint CLI
Usage: $cli_name [command]
Commands:
  test          Run tests with coverage
  dev           Start development server (uvicorn with reload)
  prod          Start production server (uvicorn)
  runserver     Alias for dev (backward compatibility)
  *             Display this help message
"
  exit 1
}

case "${1:-}" in
  test)
    pytest tests/ -v --tb=short --cov=app --cov-report=term-missing --cov-config=.coveragerc
    ;;
  dev|runserver)
    PORT=${PORT:-8004}
    echo "Starting development server (uvicorn) on 0.0.0.0:$PORT"
    exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --reload
    ;;
  prod)
    PORT=${PORT:-8004}
    WORKERS=${WORKERS:-4}
    exec uvicorn app.main:app \
      --host 0.0.0.0 \
      --port "$PORT" \
      --workers $WORKERS \
      --log-level info
    ;;
  *)
    cli_help
    ;;
esac
