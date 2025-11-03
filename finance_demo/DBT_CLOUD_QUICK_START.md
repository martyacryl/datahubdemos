# dbt Cloud Quick Start Guide

This is a simplified step-by-step guide for getting started with dbt Cloud for the finance analytics demo.

## Step 1: Create Project in dbt Cloud

1. Go to https://cloud.getdbt.com
2. Click **"New Project"**
3. Name: `Finance Analytics Demo`
4. Select **"Snowflake"**
5. Click **"Continue"**

## Step 2: Connect Snowflake

Fill in your Snowflake details:
- **Account**: `YOUR_ACCOUNT` (e.g., `abc12345`)
- **Warehouse**: `YOUR_WAREHOUSE` (e.g., `COMPUTE_WH`)
- **Database**: `FINANCE_ANALYTICS`
- **Schema**: `BRONZE`
- **User**: `YOUR_USERNAME`
- **Password**: `YOUR_PASSWORD`
- Click **"Test Connection"** → **"Continue"**

## Step 3: Connect Repository

### Option A: GitHub (Easier)

1. Click **"GitHub"**
2. Authorize dbt Cloud
3. Select your repository
4. **Repository Directory**: `datahubdemos/finance_demo/dbt_project`
5. Click **"Test"** → **"Continue"**

### Option B: dbt Cloud IDE (No Git)

1. Click **"dbt Cloud IDE"**
2. You'll create files manually in the next step

## Step 4: Add Files (If Using IDE)

If you chose "dbt Cloud IDE", go to **"Develop"** and create these files:

1. `dbt_project.yml` - Copy from `datahubdemos/finance_demo/dbt_project/dbt_project.yml`
2. `packages.yml` - Copy from `datahubdemos/finance_demo/dbt_project/packages.yml`
3. `models/bronze/schema.yml` - Copy from `datahubdemos/finance_demo/dbt_project/models/bronze/schema.yml`
4. `models/silver/silver_revenue.sql` - Copy from `datahubdemos/finance_demo/dbt_project/models/silver/silver_revenue.sql`
5. `models/silver/schema.yml` - Copy from `datahubdemos/finance_demo/dbt_project/models/silver/schema.yml`
6. `models/gold/gold_revenue_summary.sql` - Copy from `datahubdemos/finance_demo/dbt_project/models/gold/gold_revenue_summary.sql`
7. `models/gold/schema.yml` - Copy from `datahubdemos/finance_demo/dbt_project/models/gold/schema.yml`

## Step 5: Run dbt

1. In dbt Cloud IDE, open the terminal (bottom panel)
2. Run:
   ```bash
   dbt build
   ```
3. Wait for it to complete
4. Then run:
   ```bash
   dbt docs generate
   ```

## Step 6: Get dbt Cloud IDs

You'll need these for DataHub ingestion:

1. **Account ID**: Go to **"Settings"** → **"Account Settings"** → Note the Account ID
2. **Project ID**: Go to **"Settings"** → **"Project Settings"** → Note the Project ID
3. **Job ID**: 
   - Go to **"Deploy"** → **"Jobs"**
   - Click **"Create Job"** or use an existing job
   - Name: `Finance Analytics Build`
   - Command: `dbt build`
   - Schedule: Manual (or set a schedule)
   - Note the Job ID from the URL or job details
4. **API Token**: 
   - Go to **"Settings"** → **"Profile"** → **"API Tokens"**
   - Click **"Create Token"**
   - Name: `DataHub Ingestion`
   - Copy the token immediately (you won't see it again!)

## Step 7: Configure DataHub Ingestion

1. Update `dbt_cloud_ingestion_recipe.yml`:
   - Replace `YOUR_DBT_CLOUD_ACCOUNT_ID` with your Account ID
   - Replace `YOUR_DBT_CLOUD_PROJECT_ID` with your Project ID
   - Replace `YOUR_DBT_CLOUD_JOB_ID` with your Job ID

2. Set environment variable:
   ```bash
   export DBT_CLOUD_TOKEN=your_api_token_here
   export DATAHUB_PAT=your_datahub_pat_here
   ```

3. Run ingestion:
   ```bash
   datahub ingest -c datahubdemos/finance_demo/dbt_cloud_ingestion_recipe.yml
   ```

## What Happens Next?

- dbt Cloud ingestion will automatically:
  - Fetch manifest, catalog, and run_results from dbt Cloud API
  - Create dbt models in DataHub
  - Apply tags and terms based on meta mappings
  - Create lineage between dbt models and Snowflake tables

## Troubleshooting

**"Project not found"**: Check Account ID and Project ID are correct
**"Job not found"**: Make sure you've created a job in dbt Cloud
**"Authentication failed"**: Verify your API token is correct
**"No artifacts found"**: Make sure you've run `dbt build` and `dbt docs generate` in dbt Cloud

## Need Help?

See `DBT_CLOUD_SETUP.md` for detailed instructions.

