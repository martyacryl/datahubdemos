#!/bin/bash
# File: datahub/ingestion/run_ingestion.sh
# Purpose: Run the DataHub ingestion pipeline for Snowflake metadata

# Check if environment variables are set
if [ -z "$DATAHUB_PAT" ]; then
  if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    source .env
  else
    echo "Error: DATAHUB_PAT environment variable not set."
    echo "Please run './create_pat.sh' first or set it manually."
    exit 1
  fi
fi

if [ -z "$SNOWFLAKE_PASSWORD" ]; then
  read -s -p "Enter your Snowflake password for DATAHUB_USER: " SNOWFLAKE_PASSWORD
  echo
  export SNOWFLAKE_PASSWORD
fi

# Run the ingestion pipeline
echo "Starting Snowflake metadata ingestion to DataHub..."
datahub ingest -c snowflake_config.yaml

# Check if ingestion was successful
if [ $? -eq 0 ]; then
  echo "Ingestion completed successfully!"
else
  echo "Ingestion failed. Please check the logs."
  exit 1
fi

# Apply additional metadata (domains, glossary terms, tags)
echo "Applying additional metadata..."
cd ../metadata
./apply_metadata.sh

echo "Metadata ingestion and enrichment complete."
