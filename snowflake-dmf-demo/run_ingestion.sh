#!/bin/bash

# DataHub External Assertion Ingestion Runner Script

set -e

echo "DataHub External Assertion Ingestion"
echo "===================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
required_vars=("DATAHUB_GMS_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "Configuration:"
echo "  DataHub GMS URL: ${DATAHUB_GMS_URL}"
echo "  Glue Database: ${GLUE_DATABASE_NAME:-Not set}"
echo "  Snowflake Account: ${SNOWFLAKE_ACCOUNT:-Not set}"
echo "  Snowflake Database: ${SNOWFLAKE_DATABASE:-Not set}"
echo ""

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

# Test DataHub connection first
echo ""
echo "Testing DataHub connection..."
python test_datahub_connection.py

if [ $? -eq 0 ]; then
    echo "DataHub connection test successful!"
else
    echo "DataHub connection test failed. Please check your configuration."
    exit 1
fi

# Run the ingestion
echo ""
echo "Running assertion ingestion..."
python ingest_all_assertions.py "$@"

echo ""
echo "Ingestion completed successfully!"
