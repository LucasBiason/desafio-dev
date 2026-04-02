#!/bin/bash
set -e

# Create additional databases for microservices.
# The default database (POSTGRES_DB = cnab_users) is created automatically.
# This script creates the remaining databases.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE cnab_data;
    CREATE DATABASE cnab_uploads;
    GRANT ALL PRIVILEGES ON DATABASE cnab_data TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE cnab_uploads TO $POSTGRES_USER;
EOSQL

echo "Databases cnab_data and cnab_uploads created successfully."
