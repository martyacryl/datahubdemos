#!/bin/bash

# DataHub Duplicate Detector Runner Script

set -e

echo "DataHub Duplicate Asset Detector"
echo "================================="

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
echo "  DataHub GMS URL: ${DATAHUB_GMS_URL:-https://test-environment.acryl.io/gms}"
echo "  Entity Types: ${ENTITY_TYPES:-dataset,chart,dashboard}"
echo "  Detection Types: ${DETECTION_TYPES:-name,schema,description}"
echo "  Name Threshold: ${NAME_SIMILARITY_THRESHOLD:-0.8}"
echo "  Schema Threshold: ${SCHEMA_SIMILARITY_THRESHOLD:-0.7}"
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

# Test connection first
echo ""
echo "Testing DataHub connection..."
python test_connection.py

if [ $? -eq 0 ]; then
    echo "Connection test successful!"
else
    echo "Connection test failed. Please check your configuration."
    exit 1
fi

# Run the detector
echo ""
echo "Running duplicate detection..."
python run_detector.py "$@"

echo ""
echo "Detection completed successfully!"
