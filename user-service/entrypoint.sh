#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status, treat unset variables as errors, and fail on pipeline errors.
set -euo pipefail

# Function to display CLI help
cli_help() {
  local cli_name=${0##*/}
  echo "
$cli_name
System entrypoint CLI
Usage: $cli_name [command]
Commands:
  migrate           Apply database migrations
  createsuperuser   Create Django superuser
  test              Run tests with coverage
  dev               Start development server (Django runserver)
  prod              Start production server (gunicorn)
  runserver         Alias for dev (backward compatibility)
  *                 Display this help message
"
  exit 1
}


# Main command handler
case "${1:-}" in
  migrate)
    python manage.py migrate
    ;;
  createsuperuser)
    python manage.py createsuperuser --noinput
    ;;
  test)
    pytest --cov-report term-missing --cov=. --cov-config=.coveragerc tests/ -s
    ;;
  dev|runserver)
    # Development server: Django runserver
    PORT=${PORT:-8001}
    echo "Starting development server (Django runserver) on 0.0.0.0:$PORT"
    exec python manage.py runserver 0.0.0.0:$PORT
    ;;
  prod)
    PORT=${PORT:-8001}
    WORKERS=${WORKERS:-4}
    TIMEOUT=${TIMEOUT:-120}

    exec gunicorn core.wsgi:application \
      --bind 0.0.0.0:$PORT \
      --workers $WORKERS \
      --timeout $TIMEOUT \
      --access-logfile - \
      --error-logfile - \
      --log-level info
    ;;
  *)
    cli_help
    ;;
esac
