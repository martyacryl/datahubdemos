#!/usr/bin/env python3
"""
Quick Snowflake DMF Demo
A simple, repeatable demo script for customers to test DMF extraction and ingestion.
"""

import os
import json
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from snowflake_assertion_extractor import SnowflakeAssertionExtractor
from datahub_assertion_ingester import DataHubAssertionIngester, ExternalAssertion

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_banner():
    """Print demo banner."""
    print("=" * 70)
    print("🏔️  Snowflake DMF to DataHub - Quick Demo")
    print("=" * 70)
    print("This demo will:")
    print("1. Connect to your Snowflake account")
    print("2. Extract DMFs and other assertions")
    print("3. Ingest them into DataHub as custom assertions")
    print("4. Show you what was created")
    print("=" * 70)

def check_environment():
    """Check if environment is properly configured."""
    logger.info("🔍 Checking environment configuration...")
    
    required_vars = {
        'Snowflake': ['SNOWFLAKE_ACCOUNT', 'SNOWFLAKE_USER', 'SNOWFLAKE_PASSWORD', 'SNOWFLAKE_WAREHOUSE', 'SNOWFLAKE_DATABASE'],
        'DataHub': ['DATAHUB_GMS_URL', 'DATAHUB_GMS_TOKEN']
    }
    
    missing_vars = []
    for category, vars_list in required_vars.items():
        for var in vars_list:
            if not os.getenv(var):
                missing_vars.append(f"{category}: {var}")
    
    if missing_vars:
        logger.error("❌ Missing required environment variables:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        logger.error("\nPlease check your .env file and ensure all required variables are set.")
        return False
    
    logger.info("✅ Environment configuration looks good!")
    return True

def test_connections():
    """Test connections to Snowflake and DataHub."""
    logger.info("🔌 Testing connections...")
    
    # Test Snowflake
    try:
        extractor = SnowflakeAssertionExtractor()
        conn = extractor._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA(), CURRENT_USER()")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Snowflake: Connected to {result[0]}.{result[1]} as {result[2]}")
        snowflake_ok = True
    except Exception as e:
        logger.error(f"❌ Snowflake: Connection failed - {str(e)}")
        snowflake_ok = False
    
    # Test DataHub
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        # Test with a simple assertion
        test_assertion = ExternalAssertion(
            source_id="quick-demo-test",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:test,test.test_table,PROD)",
            assertion_type="Connection Test",
            description="Quick demo connection test",
            platform="demo"
        )
        
        assertion_urn = ingester.create_assertion(test_assertion)
        
        if assertion_urn:
            logger.info(f"✅ DataHub: Connected to {datahub_gms_url}")
            datahub_ok = True
        else:
            logger.error("❌ DataHub: Connection test failed")
            datahub_ok = False
            
    except Exception as e:
        logger.error(f"❌ DataHub: Connection failed - {str(e)}")
        datahub_ok = False
    
    return snowflake_ok and datahub_ok

def extract_and_ingest_assertions(verbose=False):
    """Extract assertions from Snowflake and ingest to DataHub."""
    logger.info("📊 Extracting assertions from Snowflake...")
    
    try:
        # Extract assertions
        extractor = SnowflakeAssertionExtractor()
        assertions = extractor.extract_assertions()
        
        if not assertions:
            logger.warning("⚠️  No assertions found in Snowflake. Make sure you have DMFs or constraints set up.")
            return [], []
        
        logger.info(f"✅ Extracted {len(assertions)} assertions from Snowflake")
        
        # Count by type
        dmf_count = len([a for a in assertions if 'DMF' in a.get('assertion_type', '')])
        constraint_count = len([a for a in assertions if 'Constraint' in a.get('assertion_type', '')])
        validation_count = len([a for a in assertions if 'Validation' in a.get('assertion_type', '')])
        
        logger.info(f"   📈 DMF assertions: {dmf_count}")
        logger.info(f"   🔒 Constraint assertions: {constraint_count}")
        logger.info(f"   ✅ Validation assertions: {validation_count}")
        
        if verbose:
            logger.info("\n📋 Detailed assertion list:")
            for i, assertion in enumerate(assertions, 1):
                logger.info(f"   {i}. {assertion['assertion_type']}: {assertion['description']}")
                logger.info(f"      Source ID: {assertion['source_id']}")
        
        # Ingest to DataHub
        logger.info("\n📤 Ingesting assertions to DataHub...")
        
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
                        'type': assertion['assertion_type'],
                        'description': assertion['description']
                    })
                    logger.info(f"   ✅ Created: {assertion['source_id']}")
                else:
                    failed_assertions.append(assertion['source_id'])
                    logger.warning(f"   ⚠️  Failed: {assertion['source_id']}")
                    
            except Exception as e:
                failed_assertions.append(assertion['source_id'])
                logger.warning(f"   ⚠️  Error with {assertion['source_id']}: {str(e)}")
        
        logger.info(f"\n✅ Successfully created {len(successful_assertions)} assertions in DataHub")
        if failed_assertions:
            logger.warning(f"⚠️  Failed to create {len(failed_assertions)} assertions")
        
        return successful_assertions, failed_assertions
        
    except Exception as e:
        logger.error(f"❌ Error during extraction/ingestion: {str(e)}")
        return [], []

def save_results(assertions, successful_assertions, failed_assertions):
    """Save demo results to file."""
    results = {
        'timestamp': datetime.now().isoformat(),
        'demo_type': 'Quick Snowflake DMF Demo',
        'snowflake_assertions_extracted': len(assertions),
        'datahub_assertions_created': len(successful_assertions),
        'datahub_assertions_failed': len(failed_assertions),
        'successful_assertions': successful_assertions,
        'failed_assertions': failed_assertions,
        'all_snowflake_assertions': assertions
    }
    
    filename = f"quick_dmf_demo_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Results saved to: {filename}")
    return filename

def print_summary(successful_assertions, failed_assertions):
    """Print demo summary."""
    print("\n" + "=" * 70)
    print("🎉 Demo Summary")
    print("=" * 70)
    print(f"✅ Successfully created: {len(successful_assertions)} assertions in DataHub")
    print(f"⚠️  Failed to create: {len(failed_assertions)} assertions")
    
    if successful_assertions:
        print("\n📊 Created Assertions:")
        for assertion in successful_assertions:
            print(f"   • {assertion['type']}: {assertion['source_id']}")
            print(f"     Description: {assertion['description']}")
    
    if failed_assertions:
        print(f"\n⚠️  Failed Assertions ({len(failed_assertions)}):")
        for assertion_id in failed_assertions:
            print(f"   • {assertion_id}")
    
    print("\n🔍 Next Steps:")
    print("1. Check your DataHub UI for the new assertions")
    print("2. View the detailed results in the generated JSON file")
    print("3. Run assertion evaluations to see data quality results")
    print("4. Create more DMFs in Snowflake and run this demo again")
    print("=" * 70)

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description='Quick Snowflake DMF Demo')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--skip-connections', action='store_true', help='Skip connection tests')
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_banner()
    
    # Check environment
    if not check_environment():
        return 1
    
    # Test connections (unless skipped)
    if not args.skip_connections:
        if not test_connections():
            logger.error("❌ Connection tests failed. Please check your credentials.")
            return 1
    
    # Extract and ingest assertions
    successful_assertions, failed_assertions = extract_and_ingest_assertions(args.verbose)
    
    if not successful_assertions and not failed_assertions:
        logger.error("❌ No assertions were processed. Please check your Snowflake setup.")
        return 1
    
    # Save results
    results_file = save_results([], successful_assertions, failed_assertions)
    
    # Print summary
    print_summary(successful_assertions, failed_assertions)
    
    logger.info("🎉 Quick demo completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main())
