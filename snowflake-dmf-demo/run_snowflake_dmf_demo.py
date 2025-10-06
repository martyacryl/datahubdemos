#!/usr/bin/env python3
"""
Snowflake DMF to DataHub Demo
Complete demo showing how to create DMFs in Snowflake and ingest them into DataHub.
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from snowflake_assertion_extractor import SnowflakeAssertionExtractor
from datahub_assertion_ingester import DataHubAssertionIngester, ExternalAssertion

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_demo_header():
    """Print demo header."""
    print("=" * 60)
    print("🏔️  Snowflake DMF to DataHub Demo")
    print("=" * 60)
    print("This demo shows how to:")
    print("1. Extract DMFs (Data Metric Functions) from Snowflake")
    print("2. Ingest them into DataHub as custom assertions")
    print("3. Verify the assertions in DataHub")
    print("=" * 60)

def check_prerequisites():
    """Check if all prerequisites are met."""
    logger.info("🔍 Checking prerequisites...")
    
    # Check Snowflake credentials
    snowflake_vars = ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE']
    missing_snowflake = [var for var in snowflake_vars if not os.getenv(var)]
    
    if missing_snowflake:
        logger.error(f"❌ Missing Snowflake credentials: {', '.join(missing_snowflake)}")
        return False
    
    # Check DataHub credentials
    if not os.getenv('DATAHUB_GMS_TOKEN'):
        logger.error("❌ Missing DATAHUB_GMS_TOKEN")
        return False
    
    if not os.getenv('DATAHUB_GMS_URL'):
        logger.error("❌ Missing DATAHUB_GMS_URL")
        return False
    
    logger.info("✅ All prerequisites met!")
    return True

def test_snowflake_connection():
    """Test Snowflake connection."""
    logger.info("🔌 Testing Snowflake connection...")
    
    try:
        extractor = SnowflakeAssertionExtractor()
        # Try to get tables to test connection
        conn = extractor._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Connected to Snowflake: {result[0]}.{result[1]}")
        return True
    except Exception as e:
        logger.error(f"❌ Snowflake connection failed: {str(e)}")
        return False

def test_datahub_connection():
    """Test DataHub connection."""
    logger.info("🔌 Testing DataHub connection...")
    
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        # Test with a simple assertion
        test_assertion = ExternalAssertion(
            source_id="demo-test-connection",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:test,test.test_table,PROD)",
            assertion_type="Connection Test",
            description="Test assertion to verify DataHub connection",
            platform="demo"
        )
        
        assertion_urn = ingester.create_assertion(test_assertion)
        
        if assertion_urn:
            logger.info(f"✅ Connected to DataHub: {datahub_gms_url}")
            return True
        else:
            logger.error("❌ DataHub connection test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ DataHub connection failed: {str(e)}")
        return False

def extract_snowflake_assertions():
    """Extract assertions from Snowflake."""
    logger.info("📊 Extracting assertions from Snowflake...")
    
    try:
        extractor = SnowflakeAssertionExtractor()
        assertions = extractor.extract_assertions()
        
        logger.info(f"✅ Extracted {len(assertions)} assertions from Snowflake")
        
        # Count by type
        dmf_count = len([a for a in assertions if 'DMF' in a.get('assertion_type', '')])
        constraint_count = len([a for a in assertions if 'Constraint' in a.get('assertion_type', '')])
        validation_count = len([a for a in assertions if 'Validation' in a.get('assertion_type', '')])
        
        logger.info(f"   📈 DMF assertions: {dmf_count}")
        logger.info(f"   🔒 Constraint assertions: {constraint_count}")
        logger.info(f"   ✅ Validation assertions: {validation_count}")
        
        return assertions
        
    except Exception as e:
        logger.error(f"❌ Failed to extract Snowflake assertions: {str(e)}")
        return []

def ingest_to_datahub(assertions):
    """Ingest assertions to DataHub."""
    logger.info("📤 Ingesting assertions to DataHub...")
    
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        successful_assertions = []
        failed_assertions = []
        
        for assertion in assertions:
            try:
                # Convert to ExternalAssertion
                external_assertion = ExternalAssertion(
                    source_id=assertion['source_id'],
                    entity_urn=assertion['entity_urn'],
                    assertion_type=assertion['assertion_type'],
                    description=assertion['description'],
                    platform=assertion['platform'],
                    field_path=assertion.get('field_path'),
                    external_url=assertion.get('external_url'),
                    logic=assertion.get('logic'),
                    properties=assertion.get('properties', {})
                )
                
                assertion_urn = ingester.create_assertion(external_assertion)
                
                if assertion_urn:
                    successful_assertions.append({
                        'source_id': assertion['source_id'],
                        'assertion_urn': assertion_urn,
                        'type': assertion['assertion_type']
                    })
                    logger.info(f"   ✅ Created: {assertion['source_id']}")
                else:
                    failed_assertions.append(assertion['source_id'])
                    logger.warning(f"   ⚠️  Failed: {assertion['source_id']}")
                    
            except Exception as e:
                failed_assertions.append(assertion['source_id'])
                logger.warning(f"   ⚠️  Error with {assertion['source_id']}: {str(e)}")
        
        logger.info(f"✅ Successfully created {len(successful_assertions)} assertions in DataHub")
        if failed_assertions:
            logger.warning(f"⚠️  Failed to create {len(failed_assertions)} assertions")
        
        return successful_assertions, failed_assertions
        
    except Exception as e:
        logger.error(f"❌ Failed to ingest assertions to DataHub: {str(e)}")
        return [], []

def save_results(assertions, successful_assertions, failed_assertions):
    """Save demo results."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'snowflake_assertions_extracted': len(assertions),
        'datahub_assertions_created': len(successful_assertions),
        'datahub_assertions_failed': len(failed_assertions),
        'successful_assertions': successful_assertions,
        'failed_assertions': failed_assertions,
        'all_snowflake_assertions': assertions
    }
    
    filename = f"snowflake_dmf_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Results saved to: {filename}")
    return filename

def print_demo_summary(successful_assertions, failed_assertions):
    """Print demo summary."""
    print("\n" + "=" * 60)
    print("🎉 Demo Summary")
    print("=" * 60)
    print(f"✅ Successfully created: {len(successful_assertions)} assertions in DataHub")
    print(f"⚠️  Failed to create: {len(failed_assertions)} assertions")
    
    if successful_assertions:
        print("\n📊 Created Assertions:")
        for assertion in successful_assertions:
            print(f"   • {assertion['type']}: {assertion['source_id']}")
    
    print("\n🔍 Next Steps:")
    print("1. Check your DataHub UI for the new assertions")
    print("2. View the detailed results in the generated JSON file")
    print("3. Run assertion evaluations to see data quality results")
    print("=" * 60)

def main():
    """Run the complete demo."""
    print_demo_header()
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("❌ Prerequisites not met. Please check your environment variables.")
        return 1
    
    # Test connections
    if not test_snowflake_connection():
        logger.error("❌ Snowflake connection failed. Please check your credentials.")
        return 1
    
    if not test_datahub_connection():
        logger.error("❌ DataHub connection failed. Please check your credentials.")
        return 1
    
    # Extract assertions from Snowflake
    assertions = extract_snowflake_assertions()
    if not assertions:
        logger.warning("⚠️  No assertions found in Snowflake. Make sure you have DMFs or constraints set up.")
        return 1
    
    # Ingest to DataHub
    successful_assertions, failed_assertions = ingest_to_datahub(assertions)
    
    # Save results
    results_file = save_results(assertions, successful_assertions, failed_assertions)
    
    # Print summary
    print_demo_summary(successful_assertions, failed_assertions)
    
    logger.info("🎉 Demo completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
