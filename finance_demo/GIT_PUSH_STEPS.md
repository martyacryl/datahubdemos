# Git Push and dbt Cloud Setup Steps

## Step 1: Add and Commit to Git

1. **Add the new folder to git:**
   ```bash
   git add datahubdemos/
   ```

2. **Commit the changes:**
   ```bash
   git commit -m "Add finance analytics demo with dbt Cloud integration"
   ```

3. **Push to your repository:**
   ```bash
   git push origin master
   ```
   (Or use your branch name if you're not on master)

## Step 2: Verify Files Are in GitHub

1. Go to your GitHub repository
2. Navigate to `datahubdemos/finance_demo/`
3. Verify you can see:
   - `dbt_project/` folder
   - All the markdown files
   - Recipe YAML files
   - SQL files

## Step 3: Set Up dbt Cloud

### Option A: Connect GitHub Repository (Recommended)

1. **Go to dbt Cloud**: https://cloud.getdbt.com
2. **Create New Project**:
   - Click "New Project"
   - Name: `Finance Analytics Demo`
   - Select "Snowflake"
   - Click "Continue"

3. **Connect Snowflake**:
   - Enter your Snowflake credentials:
     - Account: Your Snowflake account
     - Warehouse: Your warehouse name
     - Database: `FINANCE_ANALYTICS`
     - Schema: `BRONZE`
     - User: Your Snowflake username
     - Password: Your Snowflake password
   - Click "Test Connection"
   - Click "Continue"

4. **Connect GitHub**:
   - Select "GitHub"
   - Authorize dbt Cloud to access your GitHub
   - Select your repository
   - Set **Repository Directory**: `datahubdemos/finance_demo/dbt_project`
   - Click "Test"
   - Click "Continue"

5. **Verify Project Structure**:
   - Go to "Develop" → "File Tree"
   - You should see:
     - `dbt_project.yml`
     - `models/` folder
     - `packages.yml`

### Option B: Use dbt Cloud IDE (No Git)

1. **Create Project in dbt Cloud**
2. **Select "dbt Cloud IDE"** (no Git)
3. **Manually create files** by copying from your local files:
   - Copy files from `datahubdemos/finance_demo/dbt_project/` into dbt Cloud IDE

## Step 4: Create Snowflake Tables First

**IMPORTANT**: Before running dbt, you must create the Snowflake tables!

1. **Open Snowflake** (Snowsight UI or SQL client)
2. **Run the SQL script**:
   - Open `datahubdemos/finance_demo/snowflake_setup.sql`
   - Copy and paste the entire file into Snowflake
   - Execute it

3. **Verify tables were created**:
   ```sql
   SELECT COUNT(*) FROM FINANCE_ANALYTICS.BRONZE.revenue_transactions;
   -- Should return 10
   
   SELECT COUNT(*) FROM FINANCE_ANALYTICS.BRONZE.customer_info;
   -- Should return 5
   ```

## Step 5: Run dbt in Cloud

1. **In dbt Cloud IDE, open the terminal** (bottom panel)
2. **Run dbt build**:
   ```bash
   dbt build
   ```
   This will:
   - Run all models
   - Create views in Snowflake
   - Run any tests

3. **Generate documentation**:
   ```bash
   dbt docs generate
   ```
   This creates the artifacts needed for DataHub ingestion:
   - `manifest.json`
   - `catalog.json`
   - `sources.json`
   - `run_results.json`

## Step 6: Get dbt Cloud IDs for DataHub Ingestion

You'll need these IDs from dbt Cloud:

1. **Account ID**:
   - Go to "Settings" → "Account Settings"
   - Note the Account ID (number)

2. **Project ID**:
   - Go to "Settings" → "Project Settings"
   - Note the Project ID (number)

3. **Job ID**:
   - Go to "Deploy" → "Jobs"
   - Click "Create Job" or use an existing job
   - Name: `Finance Analytics Build`
   - Command: `dbt build`
   - Schedule: Manual (or set a schedule)
   - Note the Job ID from the URL or job details

4. **API Token**:
   - Go to "Settings" → "Profile" → "API Tokens"
   - Click "Create Token"
   - Name: `DataHub Ingestion`
   - Copy the token immediately (you won't see it again!)

## Step 7: Update DataHub Ingestion Recipe

1. **Edit `dbt_cloud_ingestion_recipe.yml`**:
   - Replace `YOUR_DBT_CLOUD_ACCOUNT_ID` with your Account ID
   - Replace `YOUR_DBT_CLOUD_PROJECT_ID` with your Project ID
   - Replace `YOUR_DBT_CLOUD_JOB_ID` with your Job ID

2. **Set environment variables**:
   ```bash
   export DBT_CLOUD_TOKEN=your_api_token_here
   export DATAHUB_PAT=your_datahub_pat_here
   ```

## Step 8: Run DataHub Ingestion

1. **First, run Snowflake ingestion**:
   ```bash
   datahub ingest -c datahubdemos/finance_demo/snowflake_ingestion_recipe.yml
   ```

2. **Then, run dbt Cloud ingestion**:
   ```bash
   datahub ingest -c datahubdemos/finance_demo/dbt_cloud_ingestion_recipe.yml
   ```

## Step 9: Verify in DataHub

1. Go to DataHub Cloud UI
2. Search for `silver_revenue` or `gold_revenue_summary`
3. Verify:
   - Tags are applied (Financial, Sensitive)
   - Glossary terms are applied (Silver/Gold, Revenue, etc.)
   - Lineage shows: Snowflake tables → silver_revenue → gold_revenue_summary

## Troubleshooting

- **"Repository not found"**: Make sure you've pushed to GitHub and the repository is public or you've granted dbt Cloud access
- **"Tables not found"**: Run `snowflake_setup.sql` first in Snowflake
- **"dbt build fails"**: Check that Snowflake tables exist and you have proper permissions
- **"No artifacts found"**: Make sure you've run `dbt docs generate` in dbt Cloud

