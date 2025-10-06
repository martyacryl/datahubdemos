#!/bin/bash

# Snowflake DMF to DataHub Demo Runner

set -e

echo "🏔️  Snowflake DMF to DataHub Demo"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please run ./setup_demo.sh first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup_demo.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Run the demo
echo "🚀 Running Snowflake DMF to DataHub demo..."
python run_snowflake_dmf_demo.py

echo ""
echo "✅ Demo completed! Check the generated results file for details."
