#!/bin/bash
# DataHub Ingestion Execution Script

set -e

echo "🚀 DataHub Metadata Ingestion"
echo "============================="

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Validate setup first
echo "🔍 Running validation checks..."
if ./scripts/validate-setup.sh > /dev/null 2>&1; then
    echo "✅ Validation passed"
else
    echo "❌ Validation failed. Please fix issues before proceeding."
    ./scripts/validate-setup.sh
    exit 1
fi

# Function to run ingestion with error handling
run_ingestion() {
    local config_file=$1
    local source_type=$2
    
    echo ""
    echo "📊 Starting $source_type ingestion..."
    echo "Configuration: $config_file"
    echo "Timestamp: $(date)"
    
    # Run with detailed logging
    if datahub ingest -c "$config_file" --report-to console; then
        echo "✅ $source_type ingestion completed successfully"
        return 0
    else
        echo "❌ $source_type ingestion failed"
        return 1
    fi
}

# Create logs directory
mkdir -p logs

# Run Snowflake ingestion first
echo "🏔️  PHASE 1: Snowflake Metadata Ingestion"
echo "==========================================="
if run_ingestion "configs/snowflake-config.yml" "Snowflake" 2>&1 | tee "logs/snowflake-$(date +%Y%m%d-%H%M%S).log"; then
    echo "✅ Snowflake ingestion successful"
    snowflake_success=true
else
    echo "❌ Snowflake ingestion failed"
    snowflake_success=false
fi

# Wait a moment between ingestions
sleep 5

# Run dbt ingestion second
echo ""
echo "🔄 PHASE 2: dbt Metadata Ingestion"
echo "=================================="
if run_ingestion "configs/dbt-config.yml" "dbt" 2>&1 | tee "logs/dbt-$(date +%Y%m%d-%H%M%S).log"; then
    echo "✅ dbt ingestion successful"
    dbt_success=true
else
    echo "❌ dbt ingestion failed"
    dbt_success=false
fi

# Summary
echo ""
echo "📋 INGESTION SUMMARY"
echo "===================="
echo "Timestamp: $(date)"

if [ "$snowflake_success" = true ]; then
    echo "✅ Snowflake: SUCCESS"
else
    echo "❌ Snowflake: FAILED"
fi

if [ "$dbt_success" = true ]; then
    echo "✅ dbt: SUCCESS"
else
    echo "❌ dbt: FAILED"
fi

if [ "$snowflake_success" = true ] && [ "$dbt_success" = true ]; then
    echo ""
    echo "🎉 All ingestions completed successfully!"
    echo "📊 Check your DataHub instance at: http://localhost:8080"
    echo "🔍 Browse your ingested metadata in the DataHub UI"
    exit 0
else
    echo ""
    echo "⚠️  Some ingestions failed. Check the logs in the 'logs/' directory"
    echo "🛠️  Review the troubleshooting guide: docs/troubleshooting.md"
    exit 1
fi
