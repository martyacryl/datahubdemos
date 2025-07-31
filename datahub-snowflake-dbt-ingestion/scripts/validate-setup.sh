#!/bin/bash
# DataHub Setup Validation Script

set -e

echo "🔍 Validating DataHub Ingestion Setup"
echo "====================================="

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check required environment variables
echo "🔧 Checking required environment variables..."
required_vars=("SNOWFLAKE_USERNAME" "SNOWFLAKE_PASSWORD" "SNOWFLAKE_ACCOUNT" "DBT_PROJECT_ROOT")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    else
        echo "✅ $var is set"
    fi
done

# Check DataHub server
echo "🌐 Testing DataHub server connectivity..."
if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ DataHub server is accessible"
    datahub check localhost:8080
else
    echo "❌ DataHub server not accessible at localhost:8080"
    exit 1
fi

# Validate dbt artifacts exist
echo "📁 Checking dbt artifacts..."
dbt_artifacts=("manifest.json" "catalog.json")

for artifact in "${dbt_artifacts[@]}"; do
    if [ -f "${DBT_PROJECT_ROOT}/target/$artifact" ]; then
        echo "✅ Found $artifact"
    else
        echo "❌ Missing dbt artifact: ${DBT_PROJECT_ROOT}/target/$artifact"
        echo "    Run 'dbt compile' and 'dbt docs generate' in your dbt project"
        exit 1
    fi
done

# Test configurations with dry run
echo "🧪 Testing configurations..."
echo "Testing Snowflake configuration..."
if datahub ingest -c configs/snowflake-config.yml --dry-run > /dev/null 2>&1; then
    echo "✅ Snowflake configuration is valid"
else
    echo "❌ Snowflake configuration has issues"
    echo "Run: datahub ingest -c configs/snowflake-config.yml --dry-run"
    exit 1
fi

echo "Testing dbt configuration..."
if datahub ingest -c configs/dbt-config.yml --dry-run > /dev/null 2>&1; then
    echo "✅ dbt configuration is valid"
else
    echo "❌ dbt configuration has issues"
    echo "Run: datahub ingest -c configs/dbt-config.yml --dry-run"
    exit 1
fi

echo ""
echo "🎉 All validations passed! Ready for ingestion."
echo ""
