#!/bin/bash
# ==============================================
# DataHub Ingestion Setup Script
# ==============================================

set -e  # Exit on any error

echo "🚀 DataHub Ingestion Setup for Snowflake & dbt"
echo "================================================"

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1-2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version is compatible (requires 3.9+)"
else
    echo "❌ Python $python_version is not compatible. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment (recommended)
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip and install dependencies
echo "📦 Installing DataHub CLI with connectors..."
python3 -m pip install --upgrade pip wheel setuptools

# Install DataHub with Snowflake and dbt connectors
python3 -m pip install --upgrade 'acryl-datahub[snowflake,dbt]'

# Verify installation
echo "🔍 Verifying DataHub CLI installation..."
if datahub version > /dev/null 2>&1; then
    echo "✅ DataHub CLI installed successfully"
    datahub version
else
    echo "❌ DataHub CLI installation failed"
    exit 1
fi

# Check for environment file
echo "🔧 Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f "configs/.env.example" ]; then
        cp configs/.env.example .env
        echo "⚠️  Created .env file from template. Please edit it with your credentials."
    else
        echo "❌ No .env.example file found. Please create .env file manually."
    fi
else
    echo "✅ Environment file exists"
fi

# Test DataHub connectivity (if server is running)
echo "🌐 Testing DataHub server connectivity..."
if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ DataHub server is accessible at localhost:8080"
    
    # Initialize DataHub CLI configuration
    echo "🔑 Initializing DataHub CLI..."
    datahub init || echo "⚠️  DataHub init failed - you may need to run this manually"
else
    echo "⚠️  DataHub server not accessible at localhost:8080"
    echo "    Please ensure DataHub is running before proceeding with ingestion"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Snowflake credentials"
echo "2. Ensure your dbt project has generated artifacts (run 'dbt compile' and 'dbt docs generate')"
echo "3. Run './scripts/validate-setup.sh' to test your configuration"
echo "4. Run './scripts/run-ingestion.sh' to start ingestion"
echo ""
