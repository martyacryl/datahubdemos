# PIMCO DataHub LLM Context Retrieval Demo

## Overview

This demo showcases how DataHub improves LLM text-to-SQL generation by providing context about opaque schema and table names. The demo uses simulated municipal bond data in Snowflake with cryptic naming, enhanced by DataHub metadata (glossary, tags, domains, documentation).

## Architecture

### Data Layer (Snowflake)
- **Bronze Schema** (`BRZ_001`): Raw bond transaction data
- **Silver Schema** (`SLV_009`): Cleaned/standardized data via dynamic tables
- **Gold Schema** (`GLD_003`): Reporting-ready tables with aggregated bond positions

### Metadata Layer (DataHub)
- **Business Glossary**: Terms mapping opaque names to business concepts
- **Tags**: Classification tags for governance
- **Domains**: Business domain organization
- **Documentation**: Table/column descriptions explaining cryptic names

## Setup Instructions

### Prerequisites
1. Snowflake account with appropriate permissions
2. DataHub Cloud account with Personal Access Token (PAT)
3. Python 3.8+ with pip
4. Claude Desktop configured with DataHub MCP server

### Step 1: Snowflake Setup

1. **Create Database and Schemas**:
   ```sql
   -- Run the schema setup script
   USE ROLE ACCOUNTADMIN;
   CREATE DATABASE IF NOT EXISTS PIMCO_DEMO;
   USE DATABASE PIMCO_DEMO;
   
   -- Execute schema setup
   @snowflake/schema_setup.sql;
   ```

2. **Create Dynamic Tables**:
   ```sql
   -- Execute dynamic tables script
   @snowflake/dynamic_tables.sql;
   ```

3. **Seed Data**:
   ```sql
   -- Load seed data
   @snowflake/seed_data.sql;
   ```

4. **Verify Setup**:
   ```sql
   -- Check tables exist
   SHOW TABLES IN SCHEMA BRZ_001;
   SHOW TABLES IN SCHEMA SLV_009;
   SHOW TABLES IN SCHEMA GLD_003;
   
   -- Check dynamic tables
   SHOW DYNAMIC TABLES IN SCHEMA SLV_009;
   SHOW DYNAMIC TABLES IN SCHEMA GLD_003;
   ```

### Step 2: DataHub Cloud Setup

1. **Get DataHub PAT**:
   - Log into DataHub Cloud
   - Navigate to Settings → Access Tokens
   - Create a new Personal Access Token
   - Save the token securely

2. **Set Environment Variables**:
   ```bash
   export DATAHUB_GMS_URL="https://your-datahub-instance.acryl.io"
   export DATAHUB_PAT="your-personal-access-token"
   ```

3. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 3: Ingest Snowflake Metadata

1. **Configure Ingestion Recipe**:
   - Update `datahub/ingestion_recipe.yaml` with your Snowflake credentials:
     ```yaml
     account_id: your_account_id
     username: your_username
     password: your_password
     role: your_role
     warehouse: your_warehouse
     database: PIMCO_DEMO
     ```

2. **Run Ingestion**:
   ```bash
   datahub ingest -c datahub/ingestion_recipe.yaml
   ```

3. **Verify Ingestion**:
   - Log into DataHub Cloud
   - Search for tables like `POS_9912`, `SEG_4421`, `REG_7733`
   - Verify they appear in DataHub

### Step 4: Create Metadata (Glossary, Tags, Domains)

1. **Run Metadata Creation Script**:
   ```bash
   python scripts/create_metadata.py
   ```

2. **Verify Metadata**:
   - In DataHub Cloud, navigate to Glossary
   - Verify glossary terms are created
   - Navigate to Tags and verify tags exist
   - Navigate to Domains and verify domains exist

### Step 5: Apply Documentation

The `create_metadata.py` script includes documentation mappings. You may need to manually apply documentation to tables/columns in DataHub Cloud UI, or extend the script to use the DataHub API to apply documentation programmatically.

### Step 6: Configure Claude Desktop with DataHub MCP

1. **Install DataHub MCP Server** (if not already installed)
2. **Configure Claude Desktop** to use DataHub MCP server
3. **Test Connection**:
   - Ask Claude: "What tables are available in DataHub?"
   - Verify it can access DataHub metadata

## Demo Workflow

### Without DataHub Context

1. **Show Expected Result**:
   - Business question: "Show me total municipal bond positions by region for tax-exempt bonds"

2. **Query Claude Desktop** (without DataHub MCP):
   ```
   I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
   The database is PIMCO_DEMO. What SQL query should I use?
   ```

3. **Expected Behavior**:
   - Claude sees opaque table names: `GLD_003.POS_9912`, `GLD_003.SEG_4421`, `GLD_003.REG_7733`
   - Claude generates incorrect SQL or fails to understand relationships
   - SQL may not join tables correctly or may use wrong columns

4. **Execute SQL in Snowflake UI**:
   - Run the generated SQL
   - Show incorrect or missing results

### With DataHub Context

1. **Query Claude Desktop** (with DataHub MCP enabled):
   ```
   I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
   The database is PIMCO_DEMO. Use DataHub to understand the schema and generate the correct SQL.
   ```

2. **Expected Behavior**:
   - Claude uses DataHub MCP to retrieve context:
     - `POS_9912` = "Aggregated bond positions table"
     - `SEG_4421` = "Segment aggregations table"
     - `REG_7733` = "Region aggregations table"
     - `SEGMENT_CD` = "Segment code (TAX_EXEMPT or TAXABLE)"
     - `REGION_CD` = "Region code"
   - Claude generates correct SQL joining fact and dimension tables
   - SQL includes proper filters for tax-exempt bonds

3. **Execute SQL in Snowflake UI**:
   - Run the generated SQL
   - Show correct results with proper aggregations

## Example Queries

See `demo/query_examples.md` for detailed examples of:
- Expected results
- SQL generated without DataHub context (incorrect)
- SQL generated with DataHub context (correct)
- Sample prompts for Claude Desktop

## Troubleshooting

### Snowflake Issues
- **Dynamic tables not refreshing**: Check warehouse is running and refresh manually
- **Missing data**: Verify seed data script ran successfully
- **Schema not found**: Ensure you're using the correct database

### DataHub Issues
- **Ingestion fails**: Check Snowflake credentials and network access
- **Metadata not appearing**: Wait a few minutes for ingestion to complete
- **PAT not working**: Verify token has correct permissions

### Claude Desktop Issues
- **MCP server not connecting**: Check DataHub MCP server configuration
- **Context not retrieved**: Verify DataHub MCP server is running and connected

## Next Steps

1. Extend the demo with additional queries
2. Add more complex transformations
3. Create additional glossary terms for specific business concepts
4. Add more tags for enhanced discovery
5. Create additional domains for different business areas

