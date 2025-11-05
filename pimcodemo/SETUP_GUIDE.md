# PIMCO DataHub LLM Demo - Complete Setup Guide

This guide walks you through setting up the entire demo step-by-step.

## Prerequisites Checklist

Before starting, ensure you have:
- [ ] Snowflake account with appropriate permissions (CREATE SCHEMA, CREATE TABLE, CREATE DYNAMIC TABLE)
- [ ] DataHub Cloud account with access
- [ ] Python 3.8+ installed
- [ ] DataHub MCP server configured (or ready to configure)
- [ ] Claude Desktop installed and configured

---

## Step 1: Snowflake Setup

### 1.1 Get Snowflake Credentials

You'll need:
- **Account ID**: (e.g., `xy12345.us-east-1`)
- **Username**: Your Snowflake username
- **Password**: Your Snowflake password
- **Role**: (e.g., `ACCOUNTADMIN` or `SYSADMIN`)
- **Warehouse**: (e.g., `COMPUTE_WH`)
- **Database**: We'll create `PIMCO_DEMO` (or use existing)

### 1.2 Connect to Snowflake

Open Snowflake UI or use SnowSQL:
```bash
# If using SnowSQL
snowsql -a <account_id> -u <username> -w <warehouse> -d <database>
```

### 1.3 Create Database (if needed)

```sql
USE ROLE ACCOUNTADMIN;
CREATE DATABASE IF NOT EXISTS PIMCO_DEMO;
USE DATABASE PIMCO_DEMO;
```

**Note**: Replace `PIMCO_DEMO` with your preferred database name if different.

### 1.4 Run Complete Setup Script (Recommended - One File)

**Option A: Complete Setup (Recommended)**

1. Open `snowflake/setup_complete.sql` in Snowflake UI
2. **IMPORTANT**: Verify warehouse name is correct:
   - The script uses `WAREHOUSE = 'MSJDEMO'`
   - If your warehouse has a different name, replace `MSJDEMO` with your actual warehouse name
3. Execute the entire script (copy and paste all of it)
4. The script will:
   - Drop all schemas (clean slate)
   - Create schemas
   - Create bronze tables
   - Create silver static tables
   - Insert seed data
   - Create dynamic tables
   - Create views
5. Wait for dynamic tables to refresh (1-5 minutes)
6. Verify setup:
   ```sql
   -- Check schemas
   SHOW SCHEMAS IN DATABASE PIMCO_DEMO;
   -- Should see: BRZ_001, SLV_009, GLD_003
   
   -- Check bronze data
   SELECT COUNT(*) FROM BRZ_001.TX_0421;
   -- Should see: 30
   
   -- Check dynamic tables
   SHOW DYNAMIC TABLES IN SCHEMA SLV_009;
   SHOW DYNAMIC TABLES IN SCHEMA GLD_003;
   
   -- Check views
   SHOW VIEWS IN SCHEMA SLV_009;
   SHOW VIEWS IN SCHEMA GLD_003;
   ```

**Option B: Step-by-Step Setup (Alternative)**

1. Open `snowflake/schema_setup.sql` in Snowflake UI
2. Ensure you're using the correct database: `USE DATABASE PIMCO_DEMO;`
3. Execute the script
4. Verify schemas were created:
   ```sql
   SHOW SCHEMAS IN DATABASE PIMCO_DEMO;
   -- Should see: BRZ_001, SLV_009, GLD_003
   ```

5. Run Seed Data Script:
   - Open `snowflake/seed_data.sql` in Snowflake UI
   - Execute the script
   - Verify data was loaded:
     ```sql
     SELECT COUNT(*) FROM BRZ_001.TX_0421;
     SELECT COUNT(*) FROM BRZ_001.REF_7832;
     SELECT COUNT(*) FROM BRZ_001.ISS_5510;
     ```

6. Run Dynamic Tables Script:
   - Open `snowflake/dynamic_tables.sql` in Snowflake UI
   - **IMPORTANT**: Update the `WAREHOUSE` references:
     - Search for `WAREHOUSE = 'MSJDEMO'` 
     - Replace `MSJDEMO` with your actual warehouse name if different
   - Execute the script
   - Wait for dynamic tables to refresh (may take a few minutes)
   - Verify dynamic tables were created:
     ```sql
     SHOW DYNAMIC TABLES IN SCHEMA SLV_009;
     SHOW DYNAMIC TABLES IN SCHEMA GLD_003;
     ```

7. Run Views Script:
   - Open `snowflake/views.sql` in Snowflake UI
   - Execute the script
   - Verify views were created:
     ```sql
     SHOW VIEWS IN SCHEMA SLV_009;
     SHOW VIEWS IN SCHEMA GLD_003;
     ```

### 1.5 Verify Data Pipeline

Check that data flows through the pipeline:
```sql
-- Check bronze data
SELECT COUNT(*) FROM BRZ_001.TX_0421;
-- Should see: 30

-- Check silver data (from dynamic table or view)
SELECT COUNT(*) FROM SLV_009.DT_TXN_7821;
SELECT COUNT(*) FROM SLV_009.TXN_7821;  -- View

-- Check gold data (from dynamic table or view)
SELECT COUNT(*) FROM GLD_003.DT_POS_9912;
SELECT COUNT(*) FROM GLD_003.POS_9912;  -- View
```

**Note**: Dynamic tables may take a few minutes to refresh. You can manually refresh:
```sql
ALTER DYNAMIC TABLE SLV_009.DT_TXN_7821 REFRESH;
ALTER DYNAMIC TABLE GLD_003.DT_POS_9912 REFRESH;
```

**Architecture Summary**:
- **Bronze Tables** (static): Source data (`BRZ_001.*`)
- **Dynamic Tables** (auto-refresh): Transformations (`SLV_009.DT_*`, `GLD_003.DT_*`)
- **Views** (clean querying): Query interface (`SLV_009.*`, `GLD_003.*`)

### 1.8 Record Your Snowflake Details

Fill in these values for later use:
```
SNOWFLAKE_ACCOUNT_ID = <your_account_id>
SNOWFLAKE_USERNAME = <your_username>
SNOWFLAKE_PASSWORD = <your_password>
SNOWFLAKE_ROLE = <your_role>
SNOWFLAKE_WAREHOUSE = <your_warehouse>
SNOWFLAKE_DATABASE = PIMCO_DEMO
```

---

## Step 2: DataHub Cloud Setup

### 2.1 Get DataHub Cloud URL

1. Log into your DataHub Cloud instance
2. Copy the URL (e.g., `https://your-instance.acryl.io` or `https://datahub.pimco.com`)
3. This is your `DATAHUB_GMS_URL`

### 2.2 Create Personal Access Token (PAT)

1. In DataHub Cloud, go to **Settings** → **Access Tokens** (or **Personal Access Tokens**)
2. Click **Create Token** or **Generate Token**
3. Give it a name (e.g., "PIMCO Demo Token")
4. Set appropriate permissions (at minimum: **Edit Metadata**, **View Metadata**)
5. Copy the token immediately (you won't be able to see it again)
6. Save it securely - this is your `DATAHUB_PAT`

### 2.3 Test Connection (Optional)

You can test the connection with a simple Python script:
```python
from datahub.ingestion.graph.client import DataHubGraph

graph = DataHubGraph(
    config={
        "server": "https://your-instance.acryl.io",  # Your DataHub URL
        "token": "your-token-here",  # Your PAT
    }
)

# Test connection
print("Connected to DataHub!")
```

### 2.4 Record Your DataHub Details

Fill in these values:
```
DATAHUB_GMS_URL = <your_datahub_url>
DATAHUB_PAT = <your_personal_access_token>
```

---

## Step 3: Configure Ingestion Recipe

### 3.1 Update Ingestion Recipe

1. Open `datahub/ingestion_recipe.yaml`
2. Replace the placeholder values with your actual Snowflake credentials:

```yaml
source:
  type: snowflake
  config:
    account_id: <YOUR_ACCOUNT_ID>  # e.g., xy12345.us-east-1
    username: <YOUR_USERNAME>
    password: <YOUR_PASSWORD>
    role: <YOUR_ROLE>  # e.g., ACCOUNTADMIN
    warehouse: <YOUR_WAREHOUSE>  # e.g., COMPUTE_WH
    database: PIMCO_DEMO  # or your database name
    
    # Update these if needed
    include_schemas:
      - BRZ_001
      - SLV_009
      - GLD_003
```

3. **Option A: Use Environment Variables (Recommended)**
   - Keep the `${SNOWFLAKE_ACCOUNT_ID}` format
   - Set environment variables before running ingestion

4. **Option B: Replace with Actual Values**
   - Replace `${SNOWFLAKE_ACCOUNT_ID}` with actual values
   - **⚠️ WARNING**: Don't commit credentials to git!

### 3.2 Set Environment Variables (if using Option A)

Create a `.env` file or export variables:
```bash
export SNOWFLAKE_ACCOUNT_ID="xy12345.us-east-1"
export SNOWFLAKE_USERNAME="your_username"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_DATABASE="PIMCO_DEMO"
export DATAHUB_GMS_URL="https://your-instance.acryl.io"
export DATAHUB_PAT="your_token_here"
```

Or create a `.env` file:
```bash
# .env file (DO NOT COMMIT THIS!)
SNOWFLAKE_ACCOUNT_ID=xy12345.us-east-1
SNOWFLAKE_USERNAME=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=ACCOUNTADMIN
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=PIMCO_DEMO
DATAHUB_GMS_URL=https://your-instance.acryl.io
DATAHUB_PAT=your_token_here
```

Then load it:
```bash
# If using .env file
source .env

# Or if using python-dotenv in a script
# from dotenv import load_dotenv
# load_dotenv()
```

---

## Step 4: Install Python Dependencies

### 4.1 Create Virtual Environment (Recommended)

```bash
cd /Users/mstjohn/Documents/GitHub/pimcodemo
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4.2 Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.3 Verify Installation

```bash
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('DataHub SDK installed successfully!')"
```

---

## Step 5: Ingest Snowflake Metadata into DataHub

### 5.1 Run Ingestion

Make sure your environment variables are set (or update the YAML file directly):

```bash
# If using environment variables
datahub ingest -c datahub/ingestion_recipe.yaml

# Or if you updated the YAML file directly
datahub ingest -c datahub/ingestion_recipe.yaml
```

### 5.2 Verify Ingestion

1. Log into DataHub Cloud
2. Search for tables like:
   - `POS_9912`
   - `SEG_4421`
   - `REG_7733`
   - `TX_0421`
3. Verify they appear in DataHub
4. Check that schema information is visible

### 5.3 Troubleshooting Ingestion

If ingestion fails:
- Check Snowflake credentials are correct
- Verify network connectivity to Snowflake
- Check that warehouse is running
- Verify database/schema names match exactly
- Check DataHub logs for specific errors

---

## Step 6: Create Metadata (Glossary, Tags, Domains)

### 6.1 Set Environment Variables

Make sure these are set:
```bash
export DATAHUB_GMS_URL="https://your-instance.acryl.io"
export DATAHUB_PAT="your_token_here"
export SNOWFLAKE_DATABASE="PIMCO_DEMO"  # Optional, defaults to PIMCO_DEMO
```

### 6.2 Run Metadata Creation Script

```bash
python scripts/create_metadata.py
```

### 6.3 Verify Metadata Creation

1. **Check Glossary Terms**:
   - In DataHub, go to **Glossary**
   - Verify terms like "Municipal Bond Position", "Tax-Exempt Municipal Bond" appear
   
2. **Check Tags**:
   - In DataHub, go to **Tags**
   - Verify tags like "Municipal Bonds", "Fixed Income", "Gold Schema" appear
   
3. **Check Domains**:
   - In DataHub, go to **Domains**
   - Verify domains like "Municipal Bonds", "Trading Operations" appear

### 6.4 Verify Documentation Applied

1. In DataHub, search for a table like `GLD_003.POS_9912`
2. Check that the table has a description
3. Verify the description explains what the cryptic name means

**Note**: If documentation wasn't applied, it may be because:
- Tables weren't ingested yet (run ingestion first)
- URN format doesn't match (check the error messages in script output)
- You may need to manually add documentation via DataHub UI

---

## Step 7: Apply Tags and Domains to Tables

### 7.1 Manual Application (via DataHub UI)

For each table, you should:
1. Search for the table in DataHub
2. Click on the table
3. Add tags:
   - `Municipal Bonds`
   - `Gold Schema` (for GLD_003 tables)
   - `Silver Schema` (for SLV_009 tables)
   - `Bronze Schema` (for BRZ_001 tables)
   - `Reporting` (for GLD_003 tables)
   - `Financial Metrics` (for tables with PAR_VALUE, MARKET_VALUE)
   - `Position Data` (for POS_9912)
   - `Transaction Data` (for TX_0421, TXN_7821)
   - `Dimension Data` (for DIM_* tables)
   - `Aggregated` (for SEG_4421, REG_7733, ISS_8844, GRO_5566)

4. Assign to domains:
   - GLD_003 tables → `Reporting & Analytics` domain
   - SLV_009 tables → `Municipal Bonds` domain
   - BRZ_001 tables → `Trading Operations` domain

### 7.2 Link Glossary Terms to Tables/Columns

1. For each table, add glossary terms:
   - `POS_9912` → Link to "Municipal Bond Position", "Par Value", "Market Value"
   - `SEG_4421` → Link to "Bond Segment", "Tax-Exempt Municipal Bond", "Taxable Municipal Bond"
   - `REG_7733` → Link to "Geographic Region"
   - `TX_0421`, `TXN_7821` → Link to "Bond Transaction"
   - `GRO_5566` → Link to "Position Growth"

2. For columns, add glossary terms:
   - `PAR_VALUE` → Link to "Par Value"
   - `MARKET_VALUE` → Link to "Market Value"
   - `SEGMENT_CD` → Link to "Bond Segment"
   - `REGION_CD` → Link to "Geographic Region"
   - `MATURITY_DATE` → Link to "Maturity Date"
   - `COUPON_RATE` → Link to "Coupon Rate"
   - `CREDIT_RATING` → Link to "Credit Rating"

**Note**: This can be done programmatically, but the current script focuses on creating the metadata entities. Manual linking via UI is often easier for a demo.

---

## Step 8: Configure Claude Desktop with DataHub MCP

### 8.1 Install DataHub MCP Server (if not already installed)

Follow DataHub MCP server installation instructions.

### 8.2 Configure Claude Desktop

1. Open Claude Desktop settings
2. Find MCP server configuration
3. Add DataHub MCP server configuration:
   ```json
   {
     "mcpServers": {
       "datahub": {
         "command": "path/to/datahub-mcp-server",
         "args": [
           "--server-url", "https://your-instance.acryl.io",
           "--token", "your_pat_here"
         ]
       }
     }
   }
   ```

### 8.3 Test DataHub MCP Connection

In Claude Desktop, ask:
```
Can you search DataHub for tables related to municipal bonds?
```

If it works, you should see Claude retrieve information from DataHub.

---

## Step 9: Test the Demo

### 9.1 Test Without DataHub Context

1. **Disable DataHub MCP** in Claude Desktop (or just don't mention it)
2. Ask Claude:
   ```
   I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
   The database is PIMCO_DEMO. What SQL query should I use?
   ```
3. Copy the generated SQL
4. Run it in Snowflake UI
5. Note the issues (wrong tables, missing joins, incorrect filters)

### 9.2 Test With DataHub Context

1. **Enable DataHub MCP** in Claude Desktop
2. Ask Claude:
   ```
   I need to query Snowflake for total municipal bond positions by region for tax-exempt bonds. 
   The database is PIMCO_DEMO. Use DataHub to understand the schema and generate the correct SQL.
   ```
3. Copy the generated SQL
4. Run it in Snowflake UI
5. Compare results - should be correct!

### 9.3 Run Example Queries

See `demo/query_examples.md` for more examples:
- Position growth over time
- Top issuers by value
- Maturity analysis

---

## Step 10: Prepare for Demo

### 10.1 Create Demo Script

Prepare a simple script showing:
1. Expected business question
2. SQL generated without DataHub (wrong)
3. SQL generated with DataHub (correct)
4. Results comparison

### 10.2 Document Key Points

- Highlight the opaque table names
- Show how DataHub provides context
- Demonstrate correct SQL generation
- Show business-friendly results

---

## Troubleshooting

### Snowflake Issues

**Dynamic tables not refreshing**:
```sql
ALTER DYNAMIC TABLE SLV_009.DT_TXN_7821 REFRESH;
ALTER DYNAMIC TABLE GLD_003.DT_POS_9912 REFRESH;
```

**Missing data**:
- Verify seed data script ran successfully
- Check warehouse is running
- Verify dynamic tables are enabled

**Schema not found**:
- Ensure you're using the correct database
- Check schema names match exactly (case-sensitive)

### DataHub Issues

**Ingestion fails**:
- Check Snowflake credentials
- Verify network connectivity
- Check warehouse is running
- Verify database/schema names match exactly

**Metadata not appearing**:
- Wait a few minutes for ingestion to complete
- Check ingestion logs for errors
- Verify PAT has correct permissions

**PAT not working**:
- Verify token hasn't expired
- Check token has correct permissions
- Regenerate token if needed

### Claude Desktop Issues

**MCP server not connecting**:
- Check DataHub MCP server is running
- Verify configuration is correct
- Check server URL and token

**Context not retrieved**:
- Verify DataHub MCP server is configured correctly
- Test connection with a simple query
- Check DataHub MCP server logs

---

## Quick Reference

### Environment Variables Checklist

```bash
# Snowflake
SNOWFLAKE_ACCOUNT_ID=<your_account_id>
SNOWFLAKE_USERNAME=<your_username>
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_ROLE=<your_role>
SNOWFLAKE_WAREHOUSE=<your_warehouse>
SNOWFLAKE_DATABASE=PIMCO_DEMO

# DataHub
DATAHUB_GMS_URL=<your_datahub_url>
DATAHUB_PAT=<your_token>
```

### Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Ingest Snowflake metadata
datahub ingest -c datahub/ingestion_recipe.yaml

# Create metadata (glossary, tags, domains)
python scripts/create_metadata.py

# Test Python connection
python -c "from datahub.ingestion.graph.client import DataHubGraph; print('OK')"
```

### Key Tables to Check

- `BRZ_001.TX_0421` - Raw transactions
- `SLV_009.DT_TXN_7821` - Cleaned transactions (dynamic table)
- `GLD_003.POS_9912` - Aggregated positions (dynamic table)
- `GLD_003.SEG_4421` - Segment aggregations (dynamic table)
- `GLD_003.REG_7733` - Region aggregations (dynamic table)

---

## Next Steps After Setup

1. ✅ All steps completed
2. ✅ Test queries work correctly
3. ✅ Demo is ready to present
4. ✅ Document any customizations made

Good luck with your demo! 🚀

