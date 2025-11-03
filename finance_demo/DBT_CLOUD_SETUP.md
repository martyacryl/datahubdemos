# dbt Cloud Setup Guide for Finance Analytics Demo

This guide walks you through setting up the finance analytics demo project in dbt Cloud.

## Prerequisites

- Access to dbt Cloud account
- Snowflake account with the `FINANCE_ANALYTICS` database created (from `snowflake_setup.sql`)
- Snowflake credentials (account, warehouse, user, password, role)

## Step 1: Create a New dbt Cloud Project

1. **Log in to dbt Cloud**
   - Go to https://cloud.getdbt.com (or your dbt Cloud URL)
   - Sign in with your account

2. **Create a New Project**
   - Click **"New Project"** or **"Add Project"** button
   - Name it: `Finance Analytics Demo`
   - Select **"Snowflake"** as your warehouse type
   - Click **"Continue"**

## Step 2: Connect to Snowflake

1. **Configure Snowflake Connection**
   - Enter your Snowflake connection details:
     - **Account**: Your Snowflake account identifier (e.g., `abc12345` or `abc12345.us-east-1`)
     - **Warehouse**: Your Snowflake warehouse name (e.g., `COMPUTE_WH`)
     - **Database**: `FINANCE_ANALYTICS`
     - **Schema**: `BRONZE` (this will be the default schema)
     - **Role**: Your Snowflake role (optional, can leave blank)
     - **User**: Your Snowflake username
     - **Password**: Your Snowflake password
     - **Authentication Method**: Password (unless you use key pair auth)

2. **Test Connection**
   - Click **"Test Connection"** to verify it works
   - If successful, click **"Continue"**

## Step 3: Set Up Repository Connection

You have two options:

### Option A: Use GitHub (Recommended)

1. **Connect GitHub Repository**
   - Select **"GitHub"** as your repository provider
   - Authorize dbt Cloud to access your GitHub
   - Select the repository where you've stored the `datahubdemos/finance_demo` folder
   - Choose the branch (usually `main` or `master`)
   - Set **Repository Directory**: `datahubdemos/finance_demo/dbt_project` (this is important!)
   - Click **"Test"** and then **"Continue"**

### Option B: Use dbt Cloud IDE (No Git Required)

1. **Use dbt Cloud IDE**
   - Select **"dbt Cloud IDE"** (no Git required)
   - This will create a project directly in dbt Cloud
   - You'll need to copy/paste files manually (see Step 4)

## Step 4: Upload Project Files

### If Using GitHub (Option A)

1. **Verify Repository Structure**
   - Ensure your GitHub repo has the `datahubdemos/finance_demo/dbt_project` folder structure
   - dbt Cloud will automatically detect the files

2. **Check Project Structure**
   - In dbt Cloud, go to **"Develop"** → **"File Tree"**
   - You should see:
     - `dbt_project.yml`
     - `models/` folder
       - `bronze/`
       - `silver/`
       - `gold/`
     - `packages.yml`

### If Using dbt Cloud IDE (Option B)

1. **Create Files in dbt Cloud IDE**
   - Go to **"Develop"** → **"File Tree"**
   - Click **"New File"** to create each file
   - Copy and paste the contents from the local files:

   **Files to create:**
   - `dbt_project.yml` (copy from `datahubdemos/finance_demo/dbt_project/dbt_project.yml`)
   - `packages.yml` (copy from `datahubdemos/finance_demo/dbt_project/packages.yml`)
   - `models/bronze/schema.yml` (copy from `datahubdemos/finance_demo/dbt_project/models/bronze/schema.yml`)
   - `models/silver/silver_revenue.sql` (copy from `datahubdemos/finance_demo/dbt_project/models/silver/silver_revenue.sql`)
   - `models/silver/schema.yml` (copy from `datahubdemos/finance_demo/dbt_project/models/silver/schema.yml`)
   - `models/gold/gold_revenue_summary.sql` (copy from `datahubdemos/finance_demo/dbt_project/models/gold/gold_revenue_summary.sql`)
   - `models/gold/schema.yml` (copy from `datahubdemos/finance_demo/dbt_project/models/gold/schema.yml`)

## Step 5: Configure dbt Project Settings

1. **Update dbt Project Settings**
   - Go to **"Settings"** → **"Project Settings"**
   - Verify:
     - **Project Name**: `Finance Analytics Demo`
     - **Repository**: Your connected repo
     - **Repository Directory**: `datahubdemos/finance_demo/dbt_project` (if using GitHub)
     - **dbt Version**: Latest stable version (e.g., 1.5.x or 1.6.x)

2. **Update Connection Settings**
   - Go to **"Settings"** → **"Connection"**
   - Verify Snowflake connection details match your setup
   - **Default Schema**: `BRONZE`
   - **Target**: `dev`

## Step 6: Install Dependencies

1. **Install dbt Packages**
   - In the dbt Cloud IDE, open the terminal
   - Run:
     ```bash
     dbt deps
     ```
   - This installs any packages defined in `packages.yml`
   - In our case, we don't have any packages, so this will complete quickly

## Step 7: Test Connection and Parse Project

1. **Parse Project**
   - In dbt Cloud IDE, click **"Parse"** button (or press `Ctrl/Cmd + Enter`)
   - This validates your dbt project structure
   - Check for any errors in the output panel

2. **Test Connection**
   - Click **"Test Connection"** button
   - Verify it connects to Snowflake successfully

## Step 8: Run dbt Models

### Step 8a: Run Source Snapshot (for Freshness)

1. **Run Source Snapshot**
   - In dbt Cloud IDE, open the command line
   - Run:
     ```bash
     dbt source snapshot-freshness
     ```
   - This creates the `sources.json` file (optional for freshness checks)

### Step 8b: Build All Models

1. **Build All Models**
   - In dbt Cloud IDE command line, run:
     ```bash
     dbt build
     ```
   - This will:
     - Run all models (silver_revenue, gold_revenue_summary)
     - Run any tests
     - Create the `run_results.json` file

2. **Watch the Output**
   - You'll see progress in the command output
   - Models should materialize as views in Snowflake
   - Check for any errors

### Step 8c: Generate Documentation Artifacts

1. **Generate dbt Artifacts**
   - **IMPORTANT**: First, backup `run_results.json`:
     ```bash
     # In dbt Cloud IDE terminal, you can't directly copy files
     # But dbt Cloud will keep the run_results.json from the previous step
     ```
   - Now run:
     ```bash
     dbt docs generate
     ```
   - This creates:
     - `manifest.json` (model definitions and lineage)
     - `catalog.json` (schema information)
     - `sources.json` (source freshness - if you ran snapshot-freshness)

2. **Verify Artifacts Created**
   - In dbt Cloud, go to **"Develop"** → **"File Tree"**
   - Navigate to `target/` folder
   - You should see:
     - `manifest.json`
     - `catalog.json`
     - `sources.json`
     - `run_results.json`

## Step 9: Download Artifacts for DataHub Ingestion

Since dbt Cloud stores artifacts in the cloud, you have a few options:

### Option A: Use dbt Cloud API (Recommended)

1. **Get Your dbt Cloud Account ID and Project ID**
   - Go to **"Settings"** → **"Account Settings"**
   - Note your **Account ID**
   - Go to **"Settings"** → **"Project Settings"**
   - Note your **Project ID**

2. **Get Your dbt Cloud API Token**
   - Go to **"Settings"** → **"Profile"** → **"API Tokens"**
   - Click **"Create Token"**
   - Name it: `DataHub Ingestion`
   - Copy the token (you'll only see it once!)

3. **Download Artifacts via API**
   - You can use the dbt Cloud API to download artifacts
   - Or use the dbt Cloud ingestion source (see below)

### Option B: Use dbt Cloud Ingestion Source (Easier)

Instead of downloading artifacts, you can use the **dbt-cloud** ingestion source directly:

1. **Update DataHub Ingestion Recipe**
   - Use `dbt-cloud` source instead of `dbt` source
   - This connects directly to dbt Cloud API
   - No need to download artifacts manually!

   See `dbt_cloud_ingestion_recipe.yml` for the configuration.

### Option C: Download from dbt Cloud UI

1. **Download Artifacts**
   - In dbt Cloud, artifacts are stored in the `target/` directory
   - If you have access to the file system, you can download them
   - Or use the dbt Cloud API to retrieve them

## Step 10: Verify Models in Snowflake

1. **Check Snowflake**
   - Go to your Snowflake account
   - Navigate to `FINANCE_ANALYTICS` database
   - You should see:
     - `SILVER` schema with `silver_revenue` view
     - `GOLD` schema with `gold_revenue_summary` view

2. **Query the Views**
   - Test the silver view:
     ```sql
     SELECT * FROM FINANCE_ANALYTICS.SILVER.silver_revenue LIMIT 10;
     ```
   - Test the gold view:
     ```sql
     SELECT * FROM FINANCE_ANALYTICS.GOLD.gold_revenue_summary LIMIT 10;
     ```

## Troubleshooting

### Connection Issues

- **"Connection failed"**: Verify Snowflake credentials in **"Settings"** → **"Connection"**
- **"Cannot find database"**: Ensure `FINANCE_ANALYTICS` database exists in Snowflake
- **"Permission denied"**: Check Snowflake user has access to database and warehouse

### Model Errors

- **"Relation does not exist"**: Run `snowflake_setup.sql` first to create tables
- **"Schema does not exist"**: dbt will create schemas automatically, but check Snowflake permissions
- **"Compilation error"**: Check dbt Cloud IDE output for specific error messages

### Artifact Issues

- **"manifest.json not found"**: Run `dbt docs generate` after `dbt build`
- **"catalog.json not found"**: Run `dbt docs generate` - it creates both files
- **"run_results.json missing"**: Run `dbt build` first, then `dbt docs generate`

## Next Steps

After completing dbt Cloud setup:

1. **Create Tags and Terms in DataHub Cloud** (see `datahub_tags_terms.md`)
2. **Set up DataHub Ingestion**:
   - Option A: Use `dbt-cloud` ingestion source (recommended - connects directly to dbt Cloud)
   - Option B: Use `dbt` ingestion source (requires downloading artifacts)
3. **Run Snowflake Ingestion** (see `snowflake_ingestion_recipe.yml`)
4. **Run dbt Ingestion** (see `dbt_cloud_ingestion_recipe.yml` or `dbt_ingestion_recipe.yml`)
5. **Verify in DataHub UI** - tags, terms, and lineage should appear automatically!

## Additional Resources

- [dbt Cloud Documentation](https://docs.getdbt.com/docs/cloud/about-cloud/overview)
- [dbt Cloud IDE Guide](https://docs.getdbt.com/docs/cloud/develop-in-the-cloud)
- [dbt Cloud API Documentation](https://docs.getdbt.com/docs/dbt-cloud-apis)

