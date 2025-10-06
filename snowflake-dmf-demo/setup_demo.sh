#!/bin/bash

# Snowflake DMF to DataHub Demo Setup Script

set -e

echo "🏔️  Snowflake DMF to DataHub Demo Setup"
echo "========================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ Created .env file. Please edit it with your credentials."
    echo ""
    echo "Required configuration:"
    echo "  - SNOWFLAKE_ACCOUNT: Your Snowflake account identifier"
    echo "  - SNOWFLAKE_USER: Your Snowflake username"
    echo "  - SNOWFLAKE_PASSWORD: Your Snowflake password"
    echo "  - SNOWFLAKE_WAREHOUSE: Your Snowflake warehouse"
    echo "  - SNOWFLAKE_DATABASE: Your Snowflake database"
    echo "  - SNOWFLAKE_SCHEMA: Your Snowflake schema"
    echo "  - DATAHUB_GMS_URL: Your DataHub GMS URL (e.g., https://account.acryl.io/gms)"
    echo "  - DATAHUB_GMS_TOKEN: Your DataHub PAT token"
    echo ""
    echo "Please edit .env file and run this script again."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check required environment variables
required_vars=("SNOWFLAKE_ACCOUNT" "SNOWFLAKE_USER" "SNOWFLAKE_PASSWORD" "SNOWFLAKE_WAREHOUSE" "SNOWFLAKE_DATABASE" "DATAHUB_GMS_TOKEN")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Required environment variable $var is not set in .env file"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up DMFs in Snowflake (optional - see setup_snowflake_demo.sql)"
echo "2. Run the demo: python run_snowflake_dmf_demo.py"
echo "3. Or run with the shell script: ./run_demo.sh"
echo ""
echo "For detailed instructions, see README.md"
