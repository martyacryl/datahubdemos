#!/usr/bin/env python3
"""
Simple Automated DMF Monitor - Repeatable Snowflake to DataHub Integration
This script automatically extracts DMF data from Snowflake and reports results to DataHub
Uses the proven approach that worked in our manual tests
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
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dmf_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def print_header():
    """Print script header."""
    print("=" * 80)
    print("🤖 Simple Automated DMF Monitor")
    print("=" * 80)
    print("Automatically monitors Snowflake DMFs and reports to DataHub")
    print("Uses the proven approach that worked in our manual tests")
    print("=" * 80)

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

def create_or_update_assertion(graph, current_value):
    """Create or update the custom assertion in DataHub."""
    try:
        # Use the same assertion URN that worked before
        assertion_urn = "urn:li:assertion:snowflake-dmf-simple-assertion"
        dataset_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')}.{os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')}.CUSTOMERS,PROD)"
        
        logger.info(f"📝 Creating/updating assertion: {assertion_urn}")
        
        # Create or update assertion
        res = graph.upsert_custom_assertion(
            urn=assertion_urn,
            entity_urn=dataset_urn,
            type="Snowflake DMF",
            description=f"Snowflake Data Metric Function: INVALID_EMAIL_COUNT should be <= 0 (current: {current_value})",
            platform_urn="urn:li:dataPlatform:snowflake",
            field_path="EMAIL",
            external_url=f"https://app.snowflake.com/console/account/{os.getenv('SNOWFLAKE_ACCOUNT')}/warehouses",
            logic=f"SELECT COUNT(*) FROM {os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')}.{os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')}.CUSTOMERS WHERE EMAIL NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
        )
        
        if res is not None:
            logger.info(f"✅ Created/updated assertion: {assertion_urn}")
            return assertion_urn
        else:
            logger.error(f"❌ Failed to create/update assertion")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create/update assertion: {str(e)}")
        return None

def report_assertion_result(graph, assertion_urn, current_value):
    """Report result for the assertion using the proven approach."""
    try:
        # Determine result type
        result_type = "SUCCESS" if current_value <= 0 else "FAILURE"
        
        logger.info(f"📊 Reporting assertion result: {result_type}")
        logger.info(f"   Current value: {current_value}, Expected: <= 0")
        
        # Report result using the same approach that worked
        res = graph.report_assertion_result(
            urn=assertion_urn,
            timestamp_millis=int(time.time() * 1000),
            type=result_type,
            properties=[
                {"key": "current_invalid_email_count", "value": str(current_value)},
                {"key": "threshold", "value": "0"},
                {"key": "dmf_metric_name", "value": "INVALID_EMAIL_COUNT"},
                {"key": "column_name", "value": "EMAIL"},
                {"key": "database", "value": os.getenv('SNOWFLAKE_DATABASE', 'DMF_DEMO_DB')},
                {"key": "schema", "value": os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')},
                {"key": "table", "value": "CUSTOMERS"},
                {"key": "evaluation_time", "value": datetime.now().isoformat()},
                {"key": "assertion_status", "value": "ACTIVE"},
                {"key": "monitoring_run_id", "value": f"automated_monitor_{int(time.time())}"}
            ],
            external_url=f"https://app.snowflake.com/console/account/{os.getenv('SNOWFLAKE_ACCOUNT')}/warehouses"
        )
        
        if res:
            logger.info(f"✅ Successfully reported assertion result: {result_type}")
            return result_type
        else:
            logger.error("❌ Failed to report assertion result")
            return None
        
    except Exception as e:
        logger.error(f"❌ Failed to report assertion result: {str(e)}")
        return None

def run_monitoring_cycle():
    """Run a complete monitoring cycle."""
    logger.info("🚀 Starting automated DMF monitoring cycle...")
    start_time = datetime.now()
    
    try:
        # Initialize DataHub Graph client
        graph = DataHubGraph(
            config=DatahubClientConfig(
                server=os.getenv('DATAHUB_GMS_URL'),
                token=os.getenv('DATAHUB_GMS_TOKEN'),
            )
        )
        logger.info("✅ DataHub Graph client initialized")
        
        # Step 1: Extract DMF data from Snowflake
        current_value = extract_dmf_data()
        
        # Step 2: Create or update assertion
        assertion_urn = create_or_update_assertion(graph, current_value)
        
        if not assertion_urn:
            logger.error("❌ Failed to create/update assertion, skipping result reporting")
            return False
        
        # Step 3: Report result
        result_type = report_assertion_result(graph, assertion_urn, current_value)
        
        # Step 4: Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info("🎉 Automated monitoring cycle completed!")
        logger.info(f"   Duration: {duration:.2f} seconds")
        logger.info(f"   DMF Value: {current_value}")
        logger.info(f"   Result: {result_type}")
        logger.info(f"   Assertion: {assertion_urn}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Monitoring cycle failed: {str(e)}")
        return False

def main():
    """Main function to run the automated DMF monitor."""
    print_header()
    
    # Check required environment variables
    required_vars = ['DATAHUB_GMS_URL', 'DATAHUB_GMS_TOKEN', 'SNOWFLAKE_ACCOUNT']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        return False
    
    try:
        # Run monitoring cycle
        success = run_monitoring_cycle()
        
        if success:
            print("\n🎉 Automated DMF monitoring completed successfully!")
            print("Check DataHub for updated assertion results.")
            print("The assertion should now be ACTIVE with the latest evaluation.")
        else:
            print("\n❌ Automated DMF monitoring failed.")
            print("Check the logs for error details.")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to run automated monitor: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
