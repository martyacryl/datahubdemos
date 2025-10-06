# Snowflake DMF to DataHub Demo

This demo shows how to extract Data Metric Functions (DMFs) and other assertions from Snowflake and ingest them into DataHub as custom assertions.

## 🎯 What This Demo Does

1. **Connects to Snowflake** and extracts existing DMFs, constraints, and validations
2. **Converts them to DataHub format** as custom assertions
3. **Ingests them into DataHub** for centralized monitoring
4. **Provides detailed reporting** on what was created

## 🚀 Quick Start

### Prerequisites
- Snowflake account with appropriate permissions
- DataHub Cloud account with PAT token
- Python 3.8+

### 1. Setup
```bash
# Clone this repository
git clone <your-repo-url>
cd snowflake-dmf-demo

# Run setup script
./setup_demo.sh
```

### 2. Configure
Edit the `.env` file with your credentials:
```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# DataHub Configuration
DATAHUB_GMS_URL=https://your-account.acryl.io/gms
DATAHUB_GMS_TOKEN=your_pat_token
```

### 3. Run Demo

**Option A: Quick Demo (Recommended)**
```bash
# Quick demo - extracts existing DMFs
./run_quick_demo.sh
```

**Option B: Complete Workflow**
```bash
# Complete workflow with sample DMF creation
./customer_workflow.sh
```

**Option C: Manual Steps**
```bash
# Run the full demo pipeline
./run_demo.sh
```

## 📁 Files Overview

- **`run_snowflake_dmf_demo.py`** - Main demo script
- **`snowflake_assertion_extractor.py`** - Extracts DMFs and constraints from Snowflake
- **`datahub_assertion_ingester.py`** - Ingests assertions into DataHub
- **`setup_snowflake_demo.sql`** - Optional: Creates sample DMFs for testing
- **`setup_demo.sh`** - Setup script for dependencies
- **`run_demo.sh`** - Easy demo runner
- **`env.example`** - Environment configuration template

## 🔧 What Gets Extracted

The demo extracts three types of assertions from Snowflake:

### 1. Data Metric Functions (DMFs)
- `SNOWFLAKE.CORE.NULL_COUNT` - Monitors null values
- `SNOWFLAKE.CORE.FRESHNESS` - Monitors data freshness
- `SNOWFLAKE.CORE.VOLUME` - Monitors data volume
- And more...

### 2. Column Validations
- Data type validations
- Nullability constraints
- Length constraints
- Precision constraints

### 3. Table Constraints
- Check constraints
- Primary key constraints
- Unique constraints

## 📊 Demo Output

The demo will:
- ✅ Test connections to Snowflake and DataHub
- 📊 Extract all assertions from your Snowflake tables
- 📤 Ingest them as custom assertions in DataHub
- 📄 Generate a detailed results JSON file
- 🎉 Show you what was created

## 🎓 Learning Outcomes

- How DMFs work in Snowflake
- How to extract Snowflake metadata programmatically
- How to create custom assertions in DataHub
- How to bridge Snowflake and DataHub for centralized data quality monitoring

## 🔍 Verification

After running the demo:
1. Check your DataHub UI for new assertions
2. Look for the generated results JSON file
3. Run assertion evaluations to see data quality results
