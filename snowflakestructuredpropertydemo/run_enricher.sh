#!/bin/bash

# DataHub Retention Period Enricher Runner Script

set -e

echo "DataHub Retention Period Enricher"
echo "================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
required_vars=("DATAHUB_GMS_TOKEN" "SNOWFLAKE_USER" "SNOWFLAKE_PASSWORD" "SNOWFLAKE_ACCOUNT" "SNOWFLAKE_WAREHOUSE" "SNOWFLAKE_DATABASE")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "Configuration:"
echo "  DataHub GMS URL: ${DATAHUB_GMS_URL:-https://test-environment.acryl.io/gms}"
echo "  Snowflake Account: ${SNOWFLAKE_ACCOUNT}"
echo "  Snowflake Database: ${SNOWFLAKE_DATABASE}"
echo "  Snowflake Schema: ${SNOWFLAKE_SCHEMA:-INFORMATION_SCHEMA}"
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

# Register structured property first
echo ""
echo "Registering structured property..."
python register_property.py

if [ $? -eq 0 ]; then
    echo "Structured property registered successfully"
else
    echo "Warning: Failed to register structured property (may already exist)"
fi

# Run the enricher
echo ""
echo "Running retention enricher..."
python retention_transformer.py

echo ""
echo "Enricher completed successfully!"
