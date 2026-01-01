#!/bin/bash
# Script to run HRIS Complete Migration SQL files in order.
# This script executes 00-02 on SSO database and 03-13 on HRIS database.

# Exit on error
set -e

echo "=== HRIS Complete Migration Execution ==="

# Load environment variables from .env if it exists
if [ -f .env ]; then
    # Use allexport to export all variables from sourced file
    set -a
    source <(sed 's/\r$//' .env | grep -v '^[[:space:]]*#' | grep -v '^[[:space:]]*$')
    set +a
fi

# Configuration
SSO_DB="sso_stg"
HRIS_DB=${POSTGRES_DB:-"hris_stg"}
DB_USER=${POSTGRES_USER:-"postgres"}
DB_HOST=${POSTGRES_SERVER:-"localhost"}
DB_PORT=${POSTGRES_PORT:-"5432"}

# Function to run SQL file
run_sql() {
    local db=$1
    local file=$2
    echo "Running $file on database $db..."
    PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$db" -f "$file"
}

MIGRATION_DIR="sql/migration_output"

if [ ! -d "$MIGRATION_DIR" ]; then
    echo "Error: Migration directory $MIGRATION_DIR not found. Run scripts/migrate_workforce.py first."
    exit 1
fi

echo "Step 1: Executing SSO migrations (00-02)..."
for i in 00 01 02; do
    FILE=$(ls $MIGRATION_DIR/${i}_*.sql 2>/dev/null || echo "")
    if [ -n "$FILE" ]; then
        run_sql "$SSO_DB" "$FILE"
    else
        echo "Warning: File for step $i not found, skipping."
    fi
done

echo "Step 2: Executing HRIS migrations (03-13)..."
for i in {03..13}; do
    FILE=$(ls $MIGRATION_DIR/${i}_*.sql 2>/dev/null || echo "")
    if [ -n "$FILE" ]; then
        run_sql "$HRIS_DB" "$FILE"
    else
        echo "Warning: File for step $i not found, skipping."
    fi
done

echo "=== Migration Complete! ==="
