# Snowflake DMF to DataHub - Complete Demo Guide

This guide provides step-by-step instructions for creating DMFs in Snowflake and ingesting them into DataHub.

## 🎯 Demo Overview

**What you'll accomplish:**
1. Create sample data and DMFs in Snowflake
2. Extract DMFs from Snowflake metadata
3. Ingest them as custom assertions in DataHub
4. Verify the assertions in DataHub UI

**Time required:** 15-20 minutes

## 📋 Prerequisites

- Snowflake account with appropriate permissions
- DataHub Cloud account with PAT token
- Python 3.8+ installed

## 🚀 Step-by-Step Demo

### Step 1: Setup the Demo Environment

```bash
# 1. Clone the repository
git clone https://github.com/martyacryl/datahubdemos.git
cd datahubdemos/snowflake-dmf-demo

# 2. Run the setup script
./setup_demo.sh
```

### Step 2: Configure Your Credentials

Edit the `.env` file with your actual credentials:

```bash
# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=your_schema_name

# DataHub Configuration
DATAHUB_GMS_URL=https://your-account.acryl.io/gms
DATAHUB_GMS_TOKEN=your_pat_token_here
```

### Step 3: Create Sample DMFs in Snowflake (Optional)

If you don't have existing DMFs, run this SQL in Snowflake to create sample ones:

```sql
-- Run this in Snowflake to create sample DMFs
-- Copy and paste the contents of setup_snowflake_demo.sql
```

Or run it directly:
```bash
# Connect to Snowflake and run the setup script
snowsql -f setup_snowflake_demo.sql
```

### Step 4: Run the Demo

```bash
# Run the complete demo
./run_demo.sh
```

### Step 5: Verify Results

1. **Check the console output** - You'll see what was extracted and created
2. **Check DataHub UI** - Look for new custom assertions
3. **Check the results file** - Look for `snowflake_dmf_demo_results_*.json`

## 🔍 What You'll See

### Console Output Example:
```
🏔️  Snowflake DMF to DataHub Demo
==================================
🔍 Checking prerequisites...
✅ All prerequisites met!
🔌 Testing Snowflake connection...
✅ Connected to Snowflake: DEMO_DB.DEMO_SCHEMA
🔌 Testing DataHub connection...
✅ Connected to DataHub: https://your-account.acryl.io/gms
📊 Extracting assertions from Snowflake...
✅ Extracted 5 assertions from Snowflake
   📈 DMF assertions: 2
   🔒 Constraint assertions: 1
   ✅ Validation assertions: 2
📤 Ingesting assertions to DataHub...
   ✅ Created: snowflake-dmf-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-email_null_check
   ✅ Created: snowflake-dmf-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-data_freshness_check
   ✅ Created: snowflake-column-type-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-EMAIL
   ✅ Created: snowflake-column-nullable-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-CUSTOMER_ID
   ✅ Created: snowflake-pk-constraint-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-PK_CUSTOMER_ID
✅ Successfully created 5 assertions in DataHub
📄 Results saved to: snowflake_dmf_demo_results_20241220_143022.json

🎉 Demo Summary
============================================================
✅ Successfully created: 5 assertions in DataHub
⚠️  Failed to create: 0 assertions

📊 Created Assertions:
   • Data Quality Expectation (DMF): snowflake-dmf-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-email_null_check
   • Data Quality Expectation (DMF): snowflake-dmf-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-data_freshness_check
   • Data Type Validation: snowflake-column-type-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-EMAIL
   • Nullability Validation: snowflake-column-nullable-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-CUSTOMER_ID
   • Primary Key Constraint: snowflake-pk-constraint-DEMO_DB-DEMO_SCHEMA-CUSTOMERS-PK_CUSTOMER_ID

🔍 Next Steps:
1. Check your DataHub UI for the new assertions
2. View the detailed results in the generated JSON file
3. Run assertion evaluations to see data quality results
============================================================
```

### DataHub UI Verification:
1. Go to your DataHub instance
2. Search for "CUSTOMERS" table
3. Click on the table
4. Go to the "Assertions" tab
5. You should see the new custom assertions

## 🛠️ Troubleshooting

### Common Issues:

**1. Snowflake Connection Failed**
```
❌ Snowflake connection failed: 250001: Invalid credentials
```
**Solution:** Check your Snowflake credentials in `.env` file

**2. DataHub Connection Failed**
```
❌ DataHub connection failed: 401 Unauthorized
```
**Solution:** Check your DataHub PAT token and GMS URL

**3. No DMFs Found**
```
⚠️ No DMF assertions found for table CUSTOMERS
```
**Solution:** Make sure you've created DMFs in Snowflake first

**4. Permission Errors**
```
❌ Failed to create assertion: Access denied
```
**Solution:** Ensure your DataHub PAT token has assertion creation permissions

### Debug Mode:
```bash
# Run with verbose logging
python run_snowflake_dmf_demo.py --verbose
```

## 📊 Understanding the Results

### DMF Assertions Created:
- **email_null_check**: Monitors null values in EMAIL column
- **data_freshness_check**: Monitors data freshness based on CREATED_DATE

### Column Validations Created:
- **Data Type Validation**: Ensures columns match expected data types
- **Nullability Validation**: Ensures NOT NULL constraints are respected

### Constraint Assertions Created:
- **Primary Key Constraint**: Ensures primary key uniqueness
- **Check Constraints**: Validates custom business rules

## 🔄 Running Multiple Times

The demo is idempotent - you can run it multiple times safely:
- Existing assertions won't be duplicated
- New DMFs will be detected and added
- Results are timestamped for tracking

## 📈 Next Steps

1. **Create more DMFs** in Snowflake for other tables
2. **Run the demo regularly** to keep DataHub in sync
3. **Set up automation** using cron jobs or CI/CD
4. **Monitor assertion results** in DataHub UI
5. **Create custom DMFs** for your specific data quality needs

## 🎓 Learning Outcomes

After completing this demo, you'll understand:
- How Snowflake DMFs work and how to create them
- How to extract Snowflake metadata programmatically
- How to create custom assertions in DataHub
- How to bridge Snowflake and DataHub for centralized data quality monitoring
- How to automate the process for ongoing data quality management
