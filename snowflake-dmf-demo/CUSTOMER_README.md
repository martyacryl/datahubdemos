# Snowflake DMF to DataHub - Customer Demo

**Transform your Snowflake Data Metric Functions (DMFs) into DataHub custom assertions in minutes!**

## 🎯 What This Does

This demo extracts **Data Metric Functions (DMFs)**, **constraints**, and **validations** from your Snowflake tables and ingests them into DataHub as **custom assertions** for centralized data quality monitoring.

## ⚡ Quick Start (5 minutes)

### 1. Setup
```bash
# Clone and setup
git clone https://github.com/martyacryl/datahubdemos.git
cd datahubdemos/snowflake-dmf-demo
./setup_demo.sh
```

### 2. Configure
Edit `.env` with your credentials:
```bash
# Snowflake
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# DataHub
DATAHUB_GMS_URL=https://your-account.acryl.io/gms
DATAHUB_GMS_TOKEN=your_pat_token
```

### 3. Run Demo
```bash
# Quick demo (recommended)
./run_quick_demo.sh

# Or verbose mode
./run_quick_demo.sh --verbose
```

## 🔍 What Gets Extracted

### Data Metric Functions (DMFs)
- `SNOWFLAKE.CORE.NULL_COUNT` - Monitors null values
- `SNOWFLAKE.CORE.FRESHNESS` - Monitors data freshness  
- `SNOWFLAKE.CORE.VOLUME` - Monitors data volume
- `SNOWFLAKE.CORE.UNIQUE_COUNT` - Monitors unique values
- `SNOWFLAKE.CORE.DUPLICATE_COUNT` - Monitors duplicates
- And more...

### Column Validations
- Data type validations
- Nullability constraints
- Length constraints
- Precision constraints

### Table Constraints
- Check constraints
- Primary key constraints
- Unique constraints

## 📊 Demo Output

You'll see output like this:
```
🏔️  Snowflake DMF to DataHub - Quick Demo
======================================================================
🔍 Checking environment configuration...
✅ Environment configuration looks good!
🔌 Testing connections...
✅ Snowflake: Connected to DEMO_DB.DEMO_SCHEMA as USER
✅ DataHub: Connected to https://your-account.acryl.io/gms
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

🎉 Demo Summary
======================================================================
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
4. Create more DMFs in Snowflake and run this demo again
======================================================================
```

## 🎓 Creating DMFs in Snowflake

If you don't have DMFs yet, here's how to create them:

```sql
-- Example: Create a DMF to monitor null values
ALTER TABLE your_table
    MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email_column)
    ADD EXPECTATION email_null_check CHECK (VALUE <= 10);

-- Example: Create a DMF to monitor data freshness
ALTER TABLE your_table
    MODIFY DATA METRIC FUNCTION SNOWFLAKE.CORE.FRESHNESS ON (created_date)
    ADD EXPECTATION data_freshness_check CHECK (VALUE <= 7);
```

## 🔄 Running Multiple Times

The demo is **idempotent** - safe to run multiple times:
- ✅ Existing assertions won't be duplicated
- ✅ New DMFs will be detected and added
- ✅ Results are timestamped for tracking

## 🛠️ Troubleshooting

### Common Issues:

**Connection Failed**
```
❌ Snowflake: Connection failed - 250001: Invalid credentials
```
**Fix:** Check your Snowflake credentials in `.env`

**No DMFs Found**
```
⚠️ No DMF assertions found for table CUSTOMERS
```
**Fix:** Create DMFs in Snowflake first (see examples above)

**DataHub Permission Error**
```
❌ DataHub: Connection failed - 401 Unauthorized
```
**Fix:** Check your DataHub PAT token has assertion creation permissions

### Debug Mode:
```bash
# Run with detailed logging
./run_quick_demo.sh --verbose
```

## 📁 Files Created

After running the demo, you'll get:
- `quick_dmf_demo_results_YYYYMMDD_HHMMSS.json` - Detailed results
- Console output showing what was created
- New assertions visible in DataHub UI

## 🚀 Next Steps

1. **Check DataHub UI** - Look for new assertions on your tables
2. **Create More DMFs** - Add DMFs to other tables in Snowflake
3. **Run Regularly** - Set up automation to keep DataHub in sync
4. **Monitor Results** - Use DataHub's assertion evaluation features
5. **Scale Up** - Apply to your entire Snowflake environment

## 📞 Support

- **Detailed Guide**: See `DMF_DEMO_GUIDE.md` for step-by-step instructions
- **Full Documentation**: See `README.md` for complete documentation
- **Quick Reference**: See `QUICK_REFERENCE.md` for commands and troubleshooting

## 🎉 Success!

You've successfully bridged Snowflake and DataHub for centralized data quality monitoring! Your Snowflake DMFs are now visible and manageable in DataHub.
