# Quick Start Guide

This is a condensed version of the setup. For detailed instructions, see `SETUP_GUIDE.md`.

## 1. Snowflake Setup (5-10 minutes)

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS PIMCO_DEMO;
USE DATABASE PIMCO_DEMO;

-- Run scripts in order:
-- 1. snowflake/schema_setup.sql
-- 2. snowflake/seed_data.sql  
-- 3. snowflake/dynamic_tables.sql (update warehouse name first!)
```

**Fill in:**
- [ ] Snowflake account ID
- [ ] Username, password, role
- [ ] Warehouse name (update in dynamic_tables.sql)

## 2. DataHub Cloud Setup (2-3 minutes)

1. Log into DataHub Cloud
2. Go to Settings → Access Tokens
3. Create new token
4. Copy token (save it!)

**Fill in:**
- [ ] DataHub Cloud URL
- [ ] Personal Access Token (PAT)

## 3. Configure & Run (5 minutes)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATAHUB_GMS_URL="https://your-instance.acryl.io"
export DATAHUB_PAT="your_token"
export SNOWFLAKE_ACCOUNT_ID="your_account"
export SNOWFLAKE_USERNAME="your_username"
export SNOWFLAKE_PASSWORD="your_password"
export SNOWFLAKE_ROLE="ACCOUNTADMIN"
export SNOWFLAKE_WAREHOUSE="COMPUTE_WH"
export SNOWFLAKE_DATABASE="PIMCO_DEMO"

# Or create .env file (recommended)
cp .env.template .env
# Edit .env with your values
source .env
```

```bash
# Ingest Snowflake metadata
datahub ingest -c datahub/ingestion_recipe.yaml

# Create metadata (glossary, tags, domains)
python scripts/create_metadata.py
```

## 4. Apply Tags & Domains (via DataHub UI)

For each table:
- Add tags (Gold Schema, Municipal Bonds, Reporting, etc.)
- Assign to domains
- Link glossary terms

## 5. Configure Claude Desktop

Add DataHub MCP server configuration with your DataHub URL and PAT.

## 6. Test Demo

**Without DataHub:**
```
Query Claude: "Show me total municipal bond positions by region for tax-exempt bonds in PIMCO_DEMO database"
→ Get wrong SQL
```

**With DataHub:**
```
Query Claude: "Show me total municipal bond positions by region for tax-exempt bonds in PIMCO_DEMO database. Use DataHub to understand the schema."
→ Get correct SQL
```

## Common Issues

**Dynamic tables not refreshing:**
```sql
ALTER DYNAMIC TABLE SLV_009.DT_TXN_7821 REFRESH;
```

**Ingestion fails:**
- Check credentials in ingestion_recipe.yaml
- Verify Snowflake connection works

**Metadata not appearing:**
- Wait a few minutes after ingestion
- Check DataHub UI for errors

## Need Help?

See `SETUP_GUIDE.md` for detailed troubleshooting and step-by-step instructions.

