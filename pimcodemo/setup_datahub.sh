#!/bin/bash
# PIMCO DataHub Setup Script
# Sets environment variables and runs metadata creation

export DATAHUB_GMS_URL="https://test-environment.acryl.io/gms"
export DATAHUB_PAT="eyJhbGciOiJIUzI1NiJ9.eyJhY3RvclR5cGUiOiJVU0VSIiwiYWN0b3JJZCI6Im1hcnR5LnN0am9obkBhY3J5bC5pbyIsInR5cGUiOiJQRVJTT05BTCIsInZlcnNpb24iOiIyIiwianRpIjoiYWQyMTUwMjctMzE1OS00NTczLWFjNzUtN2MzMGUwZjVmNTQ5Iiwic3ViIjoibWFydHkuc3Rqb2huQGFjcnlsLmlvIiwiaXNzIjoiZGF0YWh1Yi1tZXRhZGF0YS1zZXJ2aWNlIn0.9qUt5egwb8bAMcr1gNvncTAv_kaXZdqTS9gow1qh4kA"

echo "Setting up DataHub metadata..."
echo "================================"
echo ""

python3 scripts/create_metadata.py

echo ""
echo "DataHub setup complete!"
