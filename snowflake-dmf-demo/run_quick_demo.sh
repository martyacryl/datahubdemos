#!/bin/bash

# Quick Snowflake DMF Demo Runner
# One-command demo for customers

set -e

echo "🏔️  Quick Snowflake DMF Demo"
echo "============================="

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

# Run the quick demo
echo "🚀 Running quick Snowflake DMF demo..."
python quick_dmf_demo.py "$@"

echo ""
echo "✅ Quick demo completed! Check the generated results file for details."
