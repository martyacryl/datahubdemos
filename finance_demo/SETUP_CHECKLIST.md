# Finance Analytics Demo - Setup Checklist

Use this checklist to ensure all steps are completed in order.

## Prerequisites
- [ ] Snowflake account with database access
- [ ] DataHub Cloud access to `zscaler.acryl.io/gms`
- [ ] DataHub Cloud PAT token
- [ ] dbt installed (`pip install dbt-snowflake`)
- [ ] DataHub CLI installed (`pip install acryl-datahub[datahub-rest]`)

## Step 1: Snowflake Setup
- [ ] Execute `snowflake_setup.sql` in Snowflake
- [ ] Verify tables created: `revenue_transactions`, `customer_info`
- [ ] Verify sample data inserted

## Step 2: DataHub Tags & Terms
- [ ] Create tag: `Financial`
- [ ] Create tag: `Sensitive`
- [ ] Create tag: `PII`
- [ ] Create tag: `Revenue Analytics`
- [ ] Create tag: `Regulatory`
- [ ] Create term: `Revenue`
- [ ] Create term: `Product Revenue`
- [ ] Create term: `Customer Revenue`
- [ ] Create term: `Financial Metrics`
- [ ] Create term: `Transaction Amount`
- [ ] Create term: `Gross Revenue`
- [ ] Create term: `Net Revenue`
- [ ] Create term: `Silver`
- [ ] Create term: `Gold`

## Step 3: dbt Configuration
- [ ] Update `dbt_project/profiles.yml` with Snowflake credentials
- [ ] Test dbt connection: `dbt debug`
- [ ] Run `dbt build` to create models
- [ ] Backup `run_results.json` before `dbt docs generate`
- [ ] Run `dbt docs generate` to create artifacts
- [ ] Restore `run_results.json` backup

## Step 4: Environment Variables
- [ ] Set `DBT_PROJECT_ROOT` (absolute path to dbt_project directory)
- [ ] Set `SNOWFLAKE_ACCOUNT`
- [ ] Set `SNOWFLAKE_WAREHOUSE`
- [ ] Set `SNOWFLAKE_USER`
- [ ] Set `SNOWFLAKE_PASSWORD`
- [ ] Set `SNOWFLAKE_ROLE` (optional)
- [ ] Set `DATAHUB_PAT`

## Step 5: Ingestion
- [ ] Run Snowflake ingestion: `datahub ingest -c snowflake_ingestion_recipe.yml`
- [ ] Verify Snowflake tables appear in DataHub
- [ ] Run dbt ingestion: `datahub ingest -c dbt_ingestion_recipe.yml`
- [ ] Verify dbt models appear in DataHub

## Step 6: Verification
- [ ] Search for `silver_revenue` in DataHub UI
- [ ] Verify tags: `Financial`, `Sensitive`
- [ ] Verify terms: `Silver`, `Revenue`
- [ ] Verify lineage: Snowflake tables → silver_revenue → gold_revenue_summary
- [ ] Search for `gold_revenue_summary` in DataHub UI
- [ ] Verify tags: `Financial`, `Sensitive`
- [ ] Verify terms: `Gold`, `Revenue`, `Product Revenue`, `Financial Metrics`
- [ ] Check column-level tags on `amount` column (should have `Financial` tag)
- [ ] Verify column-level term on `amount` column (should have `Transaction Amount` term)

## Troubleshooting
If tags/terms don't appear:
1. Verify tags/terms exist in DataHub (check spelling - case sensitive)
2. Check dbt model meta properties match meta_mapping config
3. Verify `enable_meta_mapping: true` in dbt_ingestion_recipe.yml
4. Check ingestion logs for errors

If lineage doesn't show:
1. Ensure Snowflake ingestion ran first
2. Verify `target_platform: snowflake` matches your account
3. Check dbt models reference correct source tables

