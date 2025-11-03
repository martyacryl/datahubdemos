# Finance Analytics DataHub Cloud Demo

This demo demonstrates how to automatically assign DataHub tags and glossary terms to dbt models using meta mappings when ingesting into DataHub Cloud.

## Overview

The demo includes:
- **Snowflake Database**: Raw transaction and customer data in the `FINANCE_ANALYTICS` database
- **dbt Models**: Silver and Gold layer models with meta properties
- **DataHub Tags & Terms**: Financial-focused tags and glossary terms
- **Automatic Tag/Term Assignment**: Meta mappings that automatically apply tags and terms based on dbt model properties

## Architecture

```
BRONZE (Raw Data)
├── revenue_transactions (Snowflake table)
└── customer_info (Snowflake table)

    ↓ (dbt model: silver_revenue)

SILVER (Cleaned & Enriched)
└── silver_revenue (dbt view)

    ↓ (dbt model: gold_revenue_summary)

GOLD (Aggregated)
└── gold_revenue_summary (dbt view)
```

## Prerequisites

1. **Snowflake Account** with:
   - Database access
   - Warehouse configured
   - User credentials with appropriate permissions

2. **DataHub Cloud Access**:
   - Access to `zscaler.acryl.io/gms`
   - Personal Access Token (PAT)

3. **dbt Cloud Access** (or dbt CLI):
   - **Option A (Recommended)**: dbt Cloud account - see `DBT_CLOUD_QUICK_START.md` for setup
   - **Option B**: dbt CLI installed locally:
     ```bash
     pip install dbt-snowflake
     ```

4. **DataHub CLI Installed**:
   ```bash
   pip install acryl-datahub[datahub-rest]
   ```

## Setup Instructions

### Step 1: Create Snowflake Database and Tables

1. Connect to your Snowflake account
2. Run the SQL script to create the database and tables:

```bash
# From Snowflake worksheet or CLI
snowsql -f datahubdemos/finance_demo/snowflake_setup.sql
```

Or manually execute the SQL in `datahubdemos/finance_demo/snowflake_setup.sql`:
- Creates `FINANCE_ANALYTICS` database
- Creates `BRONZE` schema
- Creates `revenue_transactions` and `customer_info` tables
- Inserts sample data

### Step 2: Create Tags and Terms in DataHub Cloud

1. Log in to DataHub Cloud at `zscaler.acryl.io`
2. Navigate to **Settings** → **Tags**
3. Create the following tags (see `datahub_tags_terms.md` for descriptions):
   - `Financial`
   - `Sensitive`
   - `PII`
   - `Revenue Analytics`
   - `Regulatory`

4. Navigate to **Glossary**
5. Create the following glossary terms (see `datahub_tags_terms.md` for detailed descriptions):
   - `Revenue`
   - `Product Revenue`
   - `Customer Revenue`
   - `Financial Metrics`
   - `Transaction Amount`
   - `Gross Revenue`
   - `Net Revenue`
   - `Silver`
   - `Gold`

**Note**: All tags and terms must be created **before** running the dbt ingestion for automatic assignment to work.

### Step 3: Configure dbt Project

**Choose one of the following options:**

#### Option A: Using dbt Cloud (Recommended)

1. **Follow the dbt Cloud setup guide**: See `DBT_CLOUD_QUICK_START.md` for step-by-step instructions
2. **Quick steps**:
   - Create a new project in dbt Cloud
   - Connect to Snowflake
   - Connect your GitHub repository (or use dbt Cloud IDE)
   - Run `dbt build` and `dbt docs generate` in dbt Cloud
   - Get your dbt Cloud Account ID, Project ID, and Job ID
   - Create an API token in dbt Cloud

3. **Skip to Step 7** - Use `dbt_cloud_ingestion_recipe.yml` instead

#### Option B: Using dbt CLI (Local)

1. Navigate to the dbt project directory:
   ```bash
   cd datahubdemos/finance_demo/dbt_project
   ```

2. Edit `profiles.yml` with your Snowflake credentials:
   ```yaml
   finance_analytics:
     target: dev
     outputs:
       dev:
         type: snowflake
         account: YOUR_SNOWFLAKE_ACCOUNT
         user: YOUR_SNOWFLAKE_USER
         password: YOUR_SNOWFLAKE_PASSWORD
         role: YOUR_SNOWFLAKE_ROLE
         database: FINANCE_ANALYTICS
         warehouse: YOUR_SNOWFLAKE_WAREHOUSE
         schema: BRONZE
   ```

3. Test the connection:
   ```bash
   dbt debug
   ```

### Step 4: Run dbt Models

1. Install dbt dependencies (if any):
   ```bash
   dbt deps
   ```

2. Run dbt source snapshot (for freshness):
   ```bash
   dbt source snapshot-freshness
   ```

3. Build dbt models:
   ```bash
   dbt build
   ```

4. Generate dbt artifacts (important for ingestion):
   ```bash
   # Backup run_results.json before docs generate overwrites it
   cp target/run_results.json target/run_results_backup.json
   
   # Generate manifest and catalog
   dbt docs generate
   
   # Restore run_results.json
   cp target/run_results_backup.json target/run_results.json
   ```

This will create the following artifacts in `target/`:
- `manifest.json` - Model definitions and lineage
- `catalog.json` - Schema information
- `sources.json` - Source freshness data
- `run_results.json` - Test results

### Step 5: Set Environment Variables

Set the following environment variables:

```bash
# dbt project root (absolute path to dbt_project directory)
export DBT_PROJECT_ROOT=/path/to/datahubdemos/finance_demo/dbt_project

# Snowflake credentials (for Snowflake ingestion)
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_WAREHOUSE=your_warehouse
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_ROLE=your_role

# DataHub Cloud PAT
export DATAHUB_PAT=your_datahub_pat_token
```

### Step 6: Run Snowflake Ingestion (First)

Ingest the base Snowflake tables first:

```bash
datahub ingest -c datahubdemos/finance_demo/snowflake_ingestion_recipe.yml
```

This will:
- Ingest `FINANCE_ANALYTICS.BRONZE.revenue_transactions`
- Ingest `FINANCE_ANALYTICS.BRONZE.customer_info`
- Create lineage from Snowflake query history
- Profile the tables

### Step 7: Run dbt Ingestion (Second)

After Snowflake ingestion completes, run the dbt ingestion:

**If using dbt Cloud (Recommended):**
```bash
datahub ingest -c datahubdemos/finance_demo/dbt_cloud_ingestion_recipe.yml
```

**If using dbt CLI (Local):**
```bash
datahub ingest -c datahubdemos/finance_demo/dbt_ingestion_recipe.yml
```

This will:
- Ingest dbt models (`silver_revenue`, `gold_revenue_summary`)
- Create lineage between dbt models and Snowflake tables
- **Automatically apply tags and terms** based on meta mappings:
  - `Silver` and `Gold` glossary terms (from `data_tier` meta)
  - `Financial` tag (from `financial_classification` meta)
  - `Sensitive` tag (from `is_sensitive` meta)
  - `Revenue` glossary term (from `domain` meta)
  - Multiple terms from `terms_list` meta (e.g., "Revenue,Product Revenue,Financial Metrics")

### Step 8: Verify in DataHub UI

1. Navigate to DataHub Cloud UI
2. Search for `silver_revenue` or `gold_revenue_summary`
3. Verify:
   - **Tags**: Should show `Financial`, `Sensitive` (if applicable)
   - **Glossary Terms**: Should show `Silver`/`Gold`, `Revenue`, `Product Revenue`, `Financial Metrics`
   - **Lineage**: Should show lineage from Snowflake tables → silver_revenue → gold_revenue_summary
   - **Schema**: Should show column definitions
   - **Documentation**: Should show dbt model descriptions

4. Check column-level tags:
   - Columns with `has_pii: true` in meta should have `PII` tag
   - Columns with `financial_classification: Financial` should have `Financial` tag
   - Columns with `term` meta should have the corresponding glossary term

## How Meta Mappings Work

The dbt ingestion recipe uses `meta_mapping` and `column_meta_mapping` to automatically assign tags and terms based on dbt model meta properties.

### Model-Level Meta Mapping

Example from `silver_revenue.sql`:
```yaml
meta:
  data_tier: Silver          # → Adds "Silver" glossary term
  domain: Revenue            # → Adds "Revenue" glossary term
  financial_classification: Financial  # → Adds "Financial" tag
  is_sensitive: True        # → Adds "Sensitive" tag
```

### Column-Level Meta Mapping

Example from `schema.yml`:
```yaml
columns:
  - name: amount
    meta:
      financial_classification: Financial  # → Adds "Financial" tag
      term: Transaction Amount             # → Adds "Transaction Amount" term
```

### Meta Mapping Configuration

The `dbt_ingestion_recipe.yml` defines mappings that automatically apply tags/terms:

```yaml
meta_mapping:
  data_tier:
    match: "Silver|Gold"
    operation: "add_term"
    config:
      term: "{{ $match }}"  # Uses the matched value
```

## Troubleshooting

### Tags/Terms Not Appearing

1. **Verify tags/terms exist in DataHub**: Check that all tags and terms are created in DataHub UI before ingestion
2. **Check meta properties**: Verify that dbt models have the correct meta properties in `schema.yml` or model files
3. **Check meta mapping config**: Verify the `meta_mapping` section in `dbt_ingestion_recipe.yml` matches your meta properties
4. **Check ingestion logs**: Look for errors in the ingestion output

### Lineage Not Showing

1. **Run Snowflake ingestion first**: Snowflake tables must exist before dbt models can reference them
2. **Check target_platform**: Verify `target_platform: snowflake` matches your Snowflake account
3. **Verify sibling relationships**: Check that dbt models show as siblings to Snowflake tables

### dbt Artifacts Not Found

1. **Verify DBT_PROJECT_ROOT**: Ensure the environment variable points to the correct directory
2. **Run dbt docs generate**: The catalog.json and manifest.json must be generated
3. **Check file paths**: Verify the paths in `dbt_ingestion_recipe.yml` match your dbt project structure

## File Structure

```
datahubdemos/finance_demo/
├── README.md                          # This file
├── DBT_CLOUD_QUICK_START.md           # Quick start guide for dbt Cloud
├── DBT_CLOUD_SETUP.md                 # Detailed dbt Cloud setup guide
├── SETUP_CHECKLIST.md                 # Quick reference checklist
├── snowflake_setup.sql                # SQL script to create Snowflake database/tables
├── datahub_tags_terms.md              # Tags and terms definitions
├── snowflake_ingestion_recipe.yml     # Snowflake ingestion configuration
├── dbt_ingestion_recipe.yml           # dbt ingestion configuration (for dbt CLI)
├── dbt_cloud_ingestion_recipe.yml     # dbt Cloud ingestion configuration (recommended)
└── dbt_project/
    ├── dbt_project.yml                # dbt project configuration
    ├── profiles.yml                   # Snowflake connection profile
    └── models/
        ├── bronze/
        │   └── schema.yml             # Source definitions
        ├── silver/
        │   ├── silver_revenue.sql     # Silver layer model
        │   └── schema.yml             # Silver model documentation
        └── gold/
            ├── gold_revenue_summary.sql  # Gold layer model
            └── schema.yml                # Gold model documentation
```

## Next Steps

1. **Customize Tags/Terms**: Add more tags and terms specific to your finance domain
2. **Add More Models**: Create additional silver and gold models
3. **Add Tests**: Implement dbt tests for data quality
4. **Add Documentation**: Enhance model and column descriptions
5. **Add Owners**: Use `owner` meta property to assign dataset owners

## References

- [dbt Meta Automated Mappings](https://docs.datahub.com/docs/generated/ingestion/sources/dbt#dbt-meta-automated-mappings)
- [dbt Meta Configuration](https://docs.getdbt.com/reference/resource-configs/meta)
- [DataHub dbt Source Documentation](https://docs.datahub.com/docs/generated/ingestion/sources/dbt)
- [DataHub Snowflake Source Documentation](https://docs.datahub.com/docs/generated/ingestion/sources/snowflake)

