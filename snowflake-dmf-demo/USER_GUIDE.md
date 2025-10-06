# DataHub External Assertion Ingestion - Complete User Guide

This comprehensive guide walks you through every step to set up and use the DataHub External Assertion Ingestion tool, including verification at each stage.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.8+ installed
- [ ] DataHub GMS access with `Edit Assertions` and `Edit Monitors` privileges
- [ ] Valid DataHub Personal Access Token
- [ ] AWS Glue access (for Glue assertions)
- [ ] Snowflake access (for Snowflake assertions)
- [ ] Basic understanding of DataHub assertions and custom assertions

## 🚀 Step-by-Step Implementation

### Step 1: Environment Setup

#### 1.1 Navigate to the Project Directory
```bash
cd /Users/mstjohn/Documents/GitHub/datahubdemos/assertion-ingestion-demo
```

#### 1.2 Create Environment File
```bash
# Copy the example file
cp env.example .env

# Edit with your actual values
nano .env
```

#### 1.3 Configure Your Credentials
Edit `.env` with your actual values:
```bash
# DataHub Configuration
DATAHUB_GMS_URL=https://test-environment.acryl.io/gms
DATAHUB_GMS_TOKEN=your_actual_datahub_token_here

# AWS Glue Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-west-2
GLUE_DATABASE_NAME=your_glue_database

# Snowflake Configuration
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema
```

#### 1.4 Verify Environment Variables
```bash
# Load and check your environment variables
source .env
echo "DataHub URL: $DATAHUB_GMS_URL"
echo "Glue Database: $GLUE_DATABASE_NAME"
echo "Snowflake Account: $SNOWFLAKE_ACCOUNT"
```

**✅ Verification:** You should see your actual values printed without any empty variables.

### Step 2: Install Dependencies

#### 2.1 Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2.2 Install Required Packages
```bash
pip install -r requirements.txt
```

#### 2.3 Verify Installation
```bash
# Test imports
python3 -c "import datahub, boto3, snowflake.connector; print('✅ All packages installed successfully')"
```

**✅ Verification:** You should see "All packages installed successfully" without any import errors.

### Step 3: Test Individual Extractors

#### 3.1 Test Glue Extractor
```bash
python glue_assertion_extractor.py
```

**✅ Verification:** You should see output like:
```
INFO:__main__:Extracting assertions from Glue database: your_database
INFO:__main__:Found 5 tables in database your_database
INFO:__main__:Extracted 15 assertions from 5 tables
INFO:__main__:Assertions saved to: glue_assertions_your_database.json
```

#### 3.2 Test Snowflake Extractor
```bash
python snowflake_assertion_extractor.py
```

**✅ Verification:** You should see output like:
```
INFO:__main__:Extracting assertions from Snowflake database: your_database, schema: your_schema
INFO:__main__:Found 8 tables in database your_database, schema your_schema
INFO:__main__:Extracted 25 assertions from 8 tables
INFO:__main__:Assertions saved to: snowflake_assertions_your_database_your_schema.json
```

### Step 4: Test DataHub Connection

#### 4.1 Create Test Script
Create a file called `test_datahub_connection.py`:
```python
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from datahub_assertion_ingester import DataHubAssertionIngester

load_dotenv()

def test_datahub_connection():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        if not datahub_token:
            print("❌ DATAHUB_GMS_TOKEN environment variable is required")
            return False
        
        # Test DataHub connection
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        # Test with a simple assertion
        from datahub_assertion_ingester import ExternalAssertion
        
        test_assertion = ExternalAssertion(
            source_id="test-connection-001",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:test,test.test_table,PROD)",
            assertion_type="Connection Test",
            description="Test assertion to verify DataHub connection",
            platform="custom"
        )
        
        # Try to create assertion (this will test the connection)
        assertion_urn = ingester.create_assertion(test_assertion)
        
        if assertion_urn:
            print("✅ DataHub connection successful!")
            print(f"✅ Created test assertion: {assertion_urn}")
            return True
        else:
            print("❌ Failed to create test assertion")
            return False
            
    except Exception as e:
        print(f"❌ DataHub connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_datahub_connection()
```

#### 4.2 Run DataHub Test
```bash
python test_datahub_connection.py
```

**✅ Verification:** You should see:
- "DataHub connection successful!"
- Test assertion URN created

### Step 5: Run Dry Run Ingestion

#### 5.1 Run Dry Run for All Sources
```bash
python ingest_all_assertions.py --dry-run --verbose
```

#### 5.2 Verify Dry Run Output
You should see output like:
```
INFO:__main__:DataHub External Assertion Ingestion
INFO:__main__:Processing sources: ['glue', 'snowflake']
INFO:__main__:Extracting assertions from Glue database: your_database
INFO:__main__:Extracted 15 assertions from Glue
INFO:__main__:Extracting assertions from Snowflake database: your_database, schema: your_schema
INFO:__main__:Extracted 25 assertions from Snowflake
INFO:__main__:Total assertions extracted: 40
INFO:__main__:Converted 40 assertions to ExternalAssertion objects
INFO:__main__:Dry run mode: Would ingest 40 assertions

============================================================
DRY RUN SUMMARY
============================================================
Would extract and ingest 40 assertions
Glue: 15 assertions
Snowflake: 25 assertions
```

**✅ Verification:** Look for:
- No connection errors
- Assertions extracted from both sources
- Dry run summary shows expected counts

### Step 6: Run Actual Ingestion

#### 6.1 Run Full Ingestion
```bash
python ingest_all_assertions.py --verbose
```

#### 6.2 Monitor the Output
You should see output like:
```
INFO:__main__:DataHub External Assertion Ingestion
INFO:__main__:Processing sources: ['glue', 'snowflake']
INFO:__main__:Extracting assertions from Glue database: your_database
INFO:__main__:Extracted 15 assertions from Glue
INFO:__main__:Extracting assertions from Snowflake database: your_database, schema: your_schema
INFO:__main__:Extracted 25 assertions from Snowflake
INFO:__main__:Total assertions extracted: 40
INFO:__main__:Converted 40 assertions to ExternalAssertion objects
INFO:datahub_assertion_ingester:Creating assertion: urn:li:assertion:glue-table-type-your_database-table1
INFO:datahub_assertion_ingester:Successfully created assertion: urn:li:assertion:glue-table-type-your_database-table1
...
INFO:__main__:Ingested 40 assertions successfully

============================================================
ASSERTION INGESTION SUMMARY
============================================================
Glue: 15 assertions extracted
Snowflake: 25 assertions extracted

Total assertions: 40
Successfully ingested: 40
Ingestion completed at: 2024-10-03 15:30:45
```

**✅ Verification:** Look for:
- "Successfully ingested: X assertions"
- No error messages
- Summary shows successful ingestion

### Step 7: Verify Assertions in DataHub UI

#### 7.1 Open DataHub UI
1. Navigate to your DataHub instance in a web browser
2. Log in with your credentials

#### 7.2 Check Assertions on Datasets
1. **Search for a dataset** that you know has assertions
2. **Navigate to the dataset page**
3. **Look for "Assertions" section** in the right sidebar or main content
4. **Find your custom assertions** with types like:
   - "Data Type Validation"
   - "Check Constraint"
   - "Table Type Validation"
   - "Storage Format Validation"

#### 7.3 Verify Assertion Details
For each assertion, verify:
- **Assertion type** matches what was extracted
- **Description** is clear and informative
- **Platform** shows the correct source (aws-glue, snowflake)
- **External URL** links to the source system
- **Field path** is correct (for field-level assertions)

**✅ Verification:** You should see:
- Assertions appear in the DataHub UI
- Assertion details match the extracted data
- Links to external systems work correctly

### Step 8: Test Individual Source Ingestion

#### 8.1 Test Glue-Only Ingestion
```bash
python ingest_all_assertions.py --sources glue --verbose
```

**✅ Verification:** Should only process Glue assertions

#### 8.2 Test Snowflake-Only Ingestion
```bash
python ingest_all_assertions.py --sources snowflake --verbose
```

**✅ Verification:** Should only process Snowflake assertions

### Step 9: Test Custom Database/Schema

#### 9.1 Test with Different Glue Database
```bash
python ingest_all_assertions.py --sources glue --glue-database different_database --dry-run
```

#### 9.2 Test with Different Snowflake Database/Schema
```bash
python ingest_all_assertions.py --sources snowflake --snowflake-database different_db --snowflake-schema different_schema --dry-run
```

**✅ Verification:** Should process the specified database/schema

### Step 10: Advanced Usage and Monitoring

#### 10.1 Save Assertions to File
```bash
python ingest_all_assertions.py --output-file my_assertions.json --dry-run
```

**✅ Verification:** Should create `my_assertions.json` with assertion data

#### 10.2 Monitor Assertion Results
After ingestion, you can report results for assertions:
```python
from datahub_assertion_ingester import DataHubAssertionIngester, AssertionResult
import time

ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)

# Report a successful result
result = AssertionResult(
    assertion_urn="urn:li:assertion:your-assertion-id",
    timestamp_millis=int(time.time() * 1000),
    result_type="SUCCESS",
    properties={"validation_passed": "true", "records_checked": "1000"}
)

ingester.report_assertion_result(result)
```

## 🔧 Troubleshooting Common Issues

### Issue 1: Glue Connection Errors
**Symptoms:** "Failed to initialize Glue client" or AWS access errors
**Solutions:**
1. Verify AWS credentials are correct
2. Check AWS region is correct
3. Ensure IAM permissions include Glue access
4. Test with AWS CLI: `aws glue get-databases`

### Issue 2: Snowflake Connection Errors
**Symptoms:** "Failed to connect to Snowflake" or authentication errors
**Solutions:**
1. Verify Snowflake credentials
2. Check account name format (should include region if needed)
3. Ensure warehouse is running
4. Test with SnowSQL: `snowsql -a account -u user -d database`

### Issue 3: DataHub Ingestion Errors
**Symptoms:** "Failed to create assertion" or permission errors
**Solutions:**
1. Verify DataHub token has correct permissions
2. Check entity URNs are valid
3. Ensure DataHub GMS URL is correct
4. Test with simple assertion first

### Issue 4: No Assertions Found
**Symptoms:** "Extracted 0 assertions" from sources
**Solutions:**
1. Check if tables exist in the specified database/schema
2. Verify table names and permissions
3. Check if tables have constraints or properties
4. Try with different database/schema

### Issue 5: Assertion Mapping Errors
**Symptoms:** "Error converting assertion" or missing fields
**Solutions:**
1. Check source data format
2. Verify required fields are present
3. Review assertion extraction logic
4. Test with sample data

## 📊 Success Criteria

You've successfully set up the assertion ingestion when:
- [ ] All connection tests pass
- [ ] Dry run shows expected assertion counts
- [ ] Full ingestion completes without errors
- [ ] Assertions appear in DataHub UI
- [ ] Assertion details are accurate and complete
- [ ] External URLs work correctly
- [ ] Individual source ingestion works

## 🎯 Best Practices

### Configuration
- Use environment variables for sensitive credentials
- Test with dry run before full ingestion
- Start with small databases/schemas
- Monitor ingestion logs for errors

### Assertion Management
- Use descriptive assertion types
- Include clear descriptions
- Set appropriate external URLs
- Group related assertions by platform

### Monitoring
- Set up regular ingestion schedules
- Monitor assertion creation success rates
- Track assertion usage in DataHub
- Review and update mappings regularly

## 📞 Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs for specific error messages
3. Test individual components (Glue, Snowflake, DataHub)
4. Verify permissions and credentials
5. Check DataHub documentation for assertion requirements

## 🔄 Next Steps

After successful setup:
1. **Schedule Regular Ingestion**: Set up automated ingestion schedules
2. **Monitor Assertion Results**: Implement result reporting workflows
3. **Customize Mappings**: Adjust assertion extraction for your specific needs
4. **Scale Up**: Process larger databases and more sources
5. **Integrate**: Connect with your data quality monitoring workflows

The assertion ingestion tool is now ready to help you bring external data quality assertions into DataHub!
