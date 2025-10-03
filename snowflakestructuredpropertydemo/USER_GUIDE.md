# DataHub Retention Period Enricher - Complete User Guide

This guide walks you through every step to set up and run the retention period enricher, including verification at each stage.

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] Python 3.9+ installed
- [ ] Access to Snowflake with `INFORMATION_SCHEMA` permissions
- [ ] DataHub GMS access with `MANAGE_STRUCTURED_PROPERTIES` permission
- [ ] Valid DataHub Personal Access Token
- [ ] Snowflake credentials (username, password, account, warehouse, database)

## 🚀 Step-by-Step Implementation

### Step 1: Environment Setup

#### 1.1 Navigate to the Project Directory
```bash
cd /Users/mstjohn/Documents/GitHub/datahubdemos/snowflakestructuredpropertydemo
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

# Snowflake Configuration
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=INFORMATION_SCHEMA
```

#### 1.4 Verify Environment Variables
```bash
# Load and check your environment variables
source .env
echo "DataHub URL: $DATAHUB_GMS_URL"
echo "Snowflake Account: $SNOWFLAKE_ACCOUNT"
echo "Snowflake Database: $SNOWFLAKE_DATABASE"
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
python3 -c "import snowflake.connector, requests, json; print('✅ All packages installed successfully')"
```

**✅ Verification:** You should see "All packages installed successfully" without any import errors.

### Step 3: Test Snowflake Connection

#### 3.1 Create Test Script
Create a file called `test_snowflake.py`:
```python
#!/usr/bin/env python3
import os
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_snowflake_connection():
    try:
        # Connect to Snowflake
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'INFORMATION_SCHEMA')
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        result = cursor.fetchone()
        
        print(f"✅ Snowflake connection successful!")
        print(f"✅ Found {result[0]} base tables in INFORMATION_SCHEMA")
        
        # Test retention data query
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' 
            AND RETENTION_TIME IS NOT NULL
        """)
        retention_count = cursor.fetchone()
        print(f"✅ Found {retention_count[0]} tables with retention data")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Snowflake connection failed: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    test_snowflake_connection()
```

#### 3.2 Run Snowflake Test
```bash
python test_snowflake.py
```

**✅ Verification:** You should see:
- "Snowflake connection successful!"
- Number of base tables found
- Number of tables with retention data

### Step 4: Test DataHub Connection

#### 4.1 Create Test Script
Create a file called `test_datahub.py`:
```python
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_datahub_connection():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        # Test DataHub connection
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Simple search query
        search_query = {
            "query": "*",
            "entityTypes": ["dataset"],
            "start": 0,
            "count": 1
        }
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": """
                query search($input: SearchInput!) {
                    search(input: $input) {
                        searchResults {
                            entity {
                                urn
                                type
                            }
                        }
                    }
                }
                """,
                "variables": {"input": search_query}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ DataHub GraphQL errors: {data['errors']}")
                return False
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            print(f"✅ DataHub connection successful!")
            print(f"✅ Found {len(search_results)} datasets (showing first 1)")
            
            if search_results:
                print(f"✅ Sample dataset URN: {search_results[0]['entity']['urn']}")
            
            return True
        else:
            print(f"❌ DataHub connection failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ DataHub connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_datahub_connection()
```

#### 4.2 Run DataHub Test
```bash
python test_datahub.py
```

**✅ Verification:** You should see:
- "DataHub connection successful!"
- Number of datasets found
- Sample dataset URN

### Step 5: Register Structured Property

#### 5.1 Register the Property
```bash
python register_property.py
```

#### 5.2 Verify Property Registration
Create a file called `verify_property.py`:
```python
#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def verify_structured_property():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Query to check if structured property exists
        query = """
        query getStructuredProperty($urn: String!) {
            structuredProperty(urn: $urn) {
                name
                displayName
                description
                type
                definition {
                    entityTypes
                    valueType
                }
            }
        }
        """
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": query,
                "variables": {"urn": "urn:li:structuredProperty:retention_period"}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            property_data = data.get('data', {}).get('structuredProperty')
            if property_data:
                print("✅ Structured property 'retention_period' found!")
                print(f"   Name: {property_data['name']}")
                print(f"   Display Name: {property_data['displayName']}")
                print(f"   Type: {property_data['type']}")
                return True
            else:
                print("❌ Structured property 'retention_period' not found")
                return False
        else:
            print(f"❌ Failed to query structured property: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying structured property: {str(e)}")
        return False

if __name__ == "__main__":
    verify_structured_property()
```

```bash
python verify_property.py
```

**✅ Verification:** You should see the structured property details printed.

### Step 6: Run the Enricher

#### 6.1 Run the Main Script
```bash
python retention_transformer.py
```

#### 6.2 Monitor the Output
You should see output like:
```
INFO:__main__:Retrieved retention data for 25 tables
INFO:__main__:Processing 15 tables in PROD_DB.PUBLIC
INFO:__main__:Updated 12 assets in PROD_DB.PUBLIC
INFO:__main__:Processing 10 tables in PROD_DB.ANALYTICS
INFO:__main__:Updated 8 assets in PROD_DB.ANALYTICS
INFO:__main__:Retention data processing completed successfully
```

**✅ Verification:** Look for:
- Number of tables found in Snowflake
- Number of assets updated in each database/schema
- "Retention data processing completed successfully"

### Step 7: Verify Results in DataHub

#### 7.1 Check via GraphQL Query
Create a file called `verify_results.py`:
```python
#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def verify_retention_properties():
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        headers = {
            'Authorization': f'Bearer {datahub_token}',
            'Content-Type': 'application/json'
        }
        
        # Query to find assets with retention properties
        query = """
        query search($input: SearchInput!) {
            search(input: $input) {
                searchResults {
                    entity {
                        urn
                        type
                        ... on Dataset {
                            structuredProperties {
                                structuredProperty {
                                    name
                                }
                                values {
                                    value
                                }
                            }
                        }
                    }
                }
            }
        }
        """
        
        # Search for datasets with retention_period property
        search_input = {
            "query": "structuredProperties:retention_period",
            "entityTypes": ["dataset"],
            "start": 0,
            "count": 10
        }
        
        response = requests.post(
            f"{datahub_gms_url}/graphql",
            json={
                "query": query,
                "variables": {"input": search_input}
            },
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            search_results = data.get('data', {}).get('search', {}).get('searchResults', [])
            print(f"✅ Found {len(search_results)} datasets with retention properties")
            
            for result in search_results[:3]:  # Show first 3
                entity = result['entity']
                urn = entity['urn']
                properties = entity.get('structuredProperties', [])
                
                print(f"\n📊 Dataset: {urn}")
                for prop in properties:
                    if prop['structuredProperty']['name'] == 'retention_period':
                        value = json.loads(prop['values'][0]['value'])
                        print(f"   Retention Time: {value.get('retention_time')} days")
                        print(f"   Retention Unit: {value.get('retention_unit')}")
                        print(f"   Enabled: {value.get('is_retention_enabled')}")
                        print(f"   Last Updated: {value.get('last_updated')}")
            
            return True
        else:
            print(f"❌ Failed to query results: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying results: {str(e)}")
        return False

if __name__ == "__main__":
    verify_retention_properties()
```

```bash
python verify_results.py
```

**✅ Verification:** You should see:
- Number of datasets with retention properties
- Sample retention data for a few datasets

#### 7.2 Check via DataHub UI

1. **Open DataHub UI** in your browser
2. **Search for a table** that you know has retention data
3. **Navigate to the dataset page**
4. **Look for "Properties" section** in the right sidebar
5. **Find "Retention Period"** structured property
6. **Click to expand** and see the retention details

**✅ Verification:** You should see:
- Retention Period property in the Properties section
- Retention time, unit, enabled status, and last updated timestamp

### Step 8: Troubleshooting Common Issues

#### 8.1 Snowflake Connection Issues
```bash
# Test with verbose logging
python -c "
import snowflake.connector
import os
from dotenv import load_dotenv
load_dotenv()

try:
    conn = snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE')
    )
    print('✅ Connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
"
```

#### 8.2 DataHub Permission Issues
```bash
# Test DataHub token permissions
python -c "
import requests
import os
from dotenv import load_dotenv
load_dotenv()

headers = {'Authorization': f'Bearer {os.getenv(\"DATAHUB_GMS_TOKEN\")}'}
response = requests.get(f'{os.getenv(\"DATAHUB_GMS_URL\")}/config', headers=headers)
print(f'Status: {response.status_code}')
print(f'Response: {response.text[:200]}...')
"
```

#### 8.3 No Assets Found
If you see "No DataHub assets found for {db_schema}":
1. Verify your Snowflake database/schema names match DataHub exactly
2. Check that tables are properly ingested into DataHub
3. Verify the URN format matches: `urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)`

## 🎯 Success Criteria

You've successfully completed the setup when:
- [ ] Snowflake connection test passes
- [ ] DataHub connection test passes  
- [ ] Structured property is registered
- [ ] Enricher runs without errors
- [ ] Retention properties appear in DataHub UI
- [ ] GraphQL verification shows retention data

## 📞 Getting Help

If you encounter issues:
1. Check the logs for specific error messages
2. Verify all environment variables are set correctly
3. Test each component individually (Snowflake, DataHub, property registration)
4. Check DataHub permissions for structured properties
5. Verify Snowflake user has INFORMATION_SCHEMA access

## 🔄 Running Again

To run the enricher again (e.g., for new tables or updated retention data):
```bash
# Just run the main script
python retention_transformer.py
```

The enricher will:
- Skip tables that already have retention properties (unless you modify the code)
- Add retention properties to new tables
- Update existing properties if retention data has changed
