# PIMCO DataHub LLM Demo - Setup Checklist

Use this checklist to track your progress through the setup.

## Prerequisites

- [ ] Snowflake account with appropriate permissions
- [ ] DataHub Cloud account with access
- [ ] Python 3.8+ installed
- [ ] DataHub MCP server configured (or ready to configure)
- [ ] Claude Desktop installed

## Step 1: Snowflake Setup

- [ ] Got Snowflake credentials (account ID, username, password, role, warehouse)
- [ ] Created database `PIMCO_DEMO` (or chosen different name)
- [ ] Ran `snowflake/schema_setup.sql` successfully
- [ ] Verified schemas created: BRZ_001, SLV_009, GLD_003
- [ ] Ran `snowflake/seed_data.sql` successfully
- [ ] Verified data loaded (check counts)
- [ ] Updated warehouse name in `snowflake/dynamic_tables.sql`
- [ ] Ran `snowflake/dynamic_tables.sql` successfully
- [ ] Verified dynamic tables created
- [ ] Verified data flows through pipeline (bronze → silver → gold)
- [ ] Recorded Snowflake credentials for later use

## Step 2: DataHub Cloud Setup

- [ ] Got DataHub Cloud URL
- [ ] Created Personal Access Token (PAT)
- [ ] Saved PAT securely
- [ ] Tested connection (optional)
- [ ] Recorded DataHub credentials

## Step 3: Configure Ingestion Recipe

- [ ] Updated `datahub/ingestion_recipe.yaml` with Snowflake credentials
- [ ] Chose method: Environment variables OR Direct values
- [ ] Set environment variables OR updated YAML file directly
- [ ] Verified credentials are correct

## Step 4: Install Python Dependencies

- [ ] Created virtual environment (optional but recommended)
- [ ] Activated virtual environment
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Verified installation works

## Step 5: Ingest Snowflake Metadata

- [ ] Set environment variables (if using them)
- [ ] Ran ingestion: `datahub ingest -c datahub/ingestion_recipe.yaml`
- [ ] Verified ingestion completed successfully
- [ ] Checked DataHub UI - tables appear
- [ ] Verified schema information is visible

## Step 6: Create Metadata (Glossary, Tags, Domains)

- [ ] Set environment variables: DATAHUB_GMS_URL, DATAHUB_PAT
- [ ] Ran script: `python scripts/create_metadata.py`
- [ ] Verified glossary terms created in DataHub
- [ ] Verified tags created in DataHub
- [ ] Verified domains created in DataHub
- [ ] Checked documentation applied to tables

## Step 7: Apply Tags and Domains to Tables

- [ ] Applied tags to GLD_003 tables (Gold Schema, Reporting, etc.)
- [ ] Applied tags to SLV_009 tables (Silver Schema, etc.)
- [ ] Applied tags to BRZ_001 tables (Bronze Schema, Transaction Data, etc.)
- [ ] Assigned tables to appropriate domains
- [ ] Linked glossary terms to relevant tables
- [ ] Linked glossary terms to relevant columns

## Step 8: Configure Claude Desktop with DataHub MCP

- [ ] Installed DataHub MCP server (if needed)
- [ ] Configured Claude Desktop MCP settings
- [ ] Added DataHub MCP server configuration
- [ ] Tested connection: Asked Claude to search DataHub
- [ ] Verified Claude can retrieve DataHub metadata

## Step 9: Test the Demo

- [ ] Tested query WITHOUT DataHub context
  - [ ] Generated SQL
  - [ ] Ran SQL in Snowflake
  - [ ] Noted issues/wrong results
- [ ] Tested query WITH DataHub context
  - [ ] Generated SQL
  - [ ] Ran SQL in Snowflake
  - [ ] Verified correct results
- [ ] Tested additional example queries
- [ ] Compared before/after results

## Step 10: Prepare for Demo

- [ ] Created demo script/notes
- [ ] Documented key points to highlight
- [ ] Prepared example queries
- [ ] Tested demo flow end-to-end
- [ ] Ready to present!

## Notes

Use this space to record any customizations, issues, or notes:

```
Example:
- Changed database name to PIMCO_PROD
- Had to refresh dynamic tables manually
- Added custom tag "Demo"
```

