#!/bin/bash
# Script to set up the directory structure for the DataHub Metadata Testing Demo

# Create main directory
mkdir -p datahub-metadata-test-demo
cd datahub-metadata-test-demo

# Create test_configs directory
mkdir -p test_configs

# Copy files to their respective locations
echo "Copying files to the appropriate directories..."

# The script assumes you've extracted all the artifacts to a single directory
# You'll need to adjust the paths if the files are in different locations

# Copy main files
cp ../README.md .
cp ../requirements.txt .
cp ../run_demo.py .

# Copy test configurations
cp ../schema_completeness_test.json test_configs/
cp ../ownership_test.json test_configs/
cp ../freshness_test.json test_configs/

echo "Directory structure created successfully!"
echo ""
echo "To run the demo:"
echo "1. cd datahub-metadata-test-demo"
echo "2. pip install -r requirements.txt"
echo "3. export DATAHUB_GMS_URL=<your-datahub-url>"
echo "4. export DATAHUB_TOKEN=<your-personal-access-token>"
echo "5. python run_demo.py"