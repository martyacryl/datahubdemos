#!/bin/bash

# Customer Workflow Script
# Complete end-to-end demo for Snowflake DMF to DataHub

set -e

echo "🏔️  Snowflake DMF to DataHub - Customer Workflow"
echo "================================================"
echo "This script will guide you through the complete demo process."
echo ""

# Function to check if .env exists
check_env() {
    if [ ! -f .env ]; then
        echo "❌ .env file not found. Please run ./setup_demo.sh first."
        exit 1
    fi
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        echo "❌ Virtual environment not found. Please run ./setup_demo.sh first."
        exit 1
    fi
}

# Function to load environment variables
load_env() {
    export $(cat .env | grep -v '^#' | xargs)
}

# Function to check if user wants to create sample DMFs
ask_create_sample_dmfs() {
    echo "🤔 Do you have existing DMFs in Snowflake? (y/n)"
    read -r response
    
    if [[ "$response" =~ ^[Nn]$ ]]; then
        echo "📊 Creating sample DMFs in Snowflake..."
        source venv/bin/activate
        python create_sample_dmfs.py
        
        if [ $? -eq 0 ]; then
            echo "✅ Sample DMFs created successfully!"
        else
            echo "❌ Failed to create sample DMFs. Please check your Snowflake credentials."
            exit 1
        fi
    else
        echo "✅ Using your existing DMFs."
    fi
}

# Function to run the demo
run_demo() {
    echo ""
    echo "🚀 Running the Snowflake DMF to DataHub demo..."
    echo "This will extract DMFs from Snowflake and ingest them into DataHub."
    echo ""
    
    source venv/bin/activate
    python quick_dmf_demo.py --verbose
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Demo completed successfully!"
        echo ""
        echo "📊 What happened:"
        echo "   • Connected to your Snowflake account"
        echo "   • Extracted DMFs and other assertions"
        echo "   • Ingested them into DataHub as custom assertions"
        echo "   • Generated detailed results file"
        echo ""
        echo "🔍 Next steps:"
        echo "   1. Check your DataHub UI for the new assertions"
        echo "   2. View the generated results JSON file"
        echo "   3. Run assertion evaluations in DataHub"
        echo "   4. Create more DMFs in Snowflake and run this demo again"
    else
        echo "❌ Demo failed. Please check the error messages above."
        exit 1
    fi
}

# Main workflow
main() {
    echo "Step 1: Checking prerequisites..."
    check_env
    check_venv
    load_env
    echo "✅ Prerequisites check passed"
    
    echo ""
    echo "Step 2: Checking for existing DMFs..."
    ask_create_sample_dmfs
    
    echo ""
    echo "Step 3: Running the demo..."
    run_demo
    
    echo ""
    echo "🎉 Customer workflow completed successfully!"
    echo "Your Snowflake DMFs are now visible in DataHub!"
}

# Run the main workflow
main
