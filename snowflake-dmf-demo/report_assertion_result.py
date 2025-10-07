#!/usr/bin/env python3
"""
Report Assertion Result - Make Custom Assertion Active
This script reports results for the custom assertion to make it active
Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions#report-results-for-custom-assertions
"""

import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from snowflake_assertion_extractor import SnowflakeAssertionExtractor
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_demo_header():
    """Print demo header."""
    print("=" * 70)
    print("📊 Report Assertion Result - Make Custom Assertion Active")
    print("=" * 70)
    print("This reports results for the custom assertion to make it active")
    print("Based on: https://docs.datahub.com/docs/api/tutorials/custom-assertions")
    print("=" * 70)

def extract_dmf_data():
    """Extract current DMF data from Snowflake."""
    logger.info("📊 Extracting current DMF data from Snowflake...")
    
    try:
        extractor = SnowflakeAssertionExtractor()
        assertions = extractor.extract_assertions()
        
        # Get the most recent DMF value
        if assertions:
            latest_assertion = assertions[0]  # Most recent
            current_value = latest_assertion.get('properties', {}).get('value', 0)
            current_value = int(current_value) if current_value is not None else 0
            logger.info(f"✅ Current DMF value: {current_value}")
            return current_value
        else:
            logger.warning("⚠️  No DMF assertions found")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Failed to extract DMF data: {str(e)}")
        return 0

def report_assertion_result():
    """Report result for the custom assertion to make it active."""
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    if not all([datahub_gms_url, datahub_token]):
        logger.error("❌ Missing DataHub credentials in .env file")
        return False
    
    # Extract current DMF data
    current_value = extract_dmf_data()
    
    try:
        # Initialize DataHub Graph client
        graph = DataHubGraph(
            config=DatahubClientConfig(
                server=datahub_gms_url,
                token=datahub_token,
            )
        )
        logger.info("✅ DataHub Graph client initialized")
        
        # The assertion URN we created
        assertion_urn = "urn:li:assertion:snowflake-dmf-simple-assertion"
        
        logger.info(f"Assertion URN: {assertion_urn}")
        
        # Determine result type based on current value
        result_type = "SUCCESS" if current_value <= 0 else "FAILURE"
        
        logger.info(f"📊 Reporting assertion result: {result_type}")
        logger.info(f"   Current value: {current_value}, Expected: <= 0")
        
        # Report result for assertion
        res = graph.report_assertion_result(
            urn=assertion_urn,
            timestamp_millis=int(time.time() * 1000),  # Current Unix timestamp in milliseconds
            type=result_type,  # SUCCESS, FAILURE, ERROR, or INIT
            properties=[
                {"key": "current_invalid_email_count", "value": str(current_value)},
                {"key": "threshold", "value": "0"},
                {"key": "dmf_metric_name", "value": "INVALID_EMAIL_COUNT"},
                {"key": "column_name", "value": "EMAIL"},
                {"key": "database", "value": os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')},
                {"key": "schema", "value": os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')},
                {"key": "table", "value": "CUSTOMERS"},
                {"key": "evaluation_time", "value": datetime.now().isoformat()},
                {"key": "assertion_status", "value": "ACTIVE"}
            ],
            external_url=f"https://app.snowflake.com/console/account/{os.getenv('SNOWFLAKE_ACCOUNT')}/warehouses"
        )
        
        if res:
            logger.info(f"✅ Successfully reported assertion result: {result_type}")
            return True, result_type, current_value
        else:
            logger.error("❌ Failed to report assertion result")
            return False, None, None
        
    except Exception as e:
        logger.error(f"❌ Failed to report assertion result: {str(e)}")
        return False, None, None

def main():
    """Run the report assertion result demo."""
    print_demo_header()
    
    # Get configuration
    datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
    datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
    
    if not all([datahub_gms_url, datahub_token]):
        logger.error("❌ Missing DataHub credentials in .env file")
        return False
    
    try:
        # Report assertion result
        success, result_type, current_value = report_assertion_result()
        
        if not success:
            logger.error("❌ Demo failed")
            return False
        
        # Summary
        print("\n" + "=" * 70)
        print("🎉 Report Assertion Result Demo Summary")
        print("=" * 70)
        print(f"✅ DMF Value Extracted: {current_value}")
        print(f"✅ Result Reported: {result_type}")
        print(f"✅ Threshold: 0 invalid emails allowed")
        
        if result_type == "FAILURE":
            print(f"🚨 Data Quality Issue: {current_value} invalid emails exceed threshold of 0")
        else:
            print("✅ Data Quality: All emails are valid")
        
        print("\n🔍 What to check in DataHub:")
        print("1. Go to the Datasets section")
        print("2. Look for 'CUSTOMERS' table")
        print("3. Click on the table and check the Assertions tab")
        print("4. Look for the 'Snowflake DMF' assertion")
        print("5. This assertion should now show as ACTIVE with evaluation results")
        print("6. Check the evaluation history for the reported result")
        
        print(f"\n🎯 Assertion URN: urn:li:assertion:snowflake-dmf-simple-assertion")
        
        print("\n💡 Key Features:")
        print("   - Reports actual evaluation results to DataHub")
        print("   - Makes the custom assertion active")
        print("   - Includes detailed properties and external URL")
        print("   - Should show evaluation history in DataHub UI")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Report assertion result demo completed!")
        print("The custom assertion should now be ACTIVE in DataHub!")
    else:
        print("\n❌ Demo failed. Check the logs above for details.")
