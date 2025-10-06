#!/usr/bin/env python3
"""
Test DataHub connection and assertion creation capabilities.
"""

import os
import logging
from dotenv import load_dotenv
from datahub_assertion_ingester import DataHubAssertionIngester, ExternalAssertion

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_datahub_connection():
    """Test DataHub connection and assertion creation."""
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        if not datahub_token:
            logger.error("❌ DATAHUB_GMS_TOKEN environment variable is required")
            return False
        
        logger.info(f"Testing DataHub connection to: {datahub_gms_url}")
        
        # Test DataHub connection
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        # Test with a simple assertion
        test_assertion = ExternalAssertion(
            source_id="test-connection-001",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:test,test.test_table,PROD)",
            assertion_type="Connection Test",
            description="Test assertion to verify DataHub connection and assertion creation",
            platform="custom",
            external_url="https://example.com/test",
            logic="SELECT 1 as test_value"
        )
        
        logger.info("Creating test assertion...")
        assertion_urn = ingester.create_assertion(test_assertion)
        
        if assertion_urn:
            logger.info("✅ DataHub connection successful!")
            logger.info(f"✅ Created test assertion: {assertion_urn}")
            
            # Test reporting a result
            from datahub_assertion_ingester import AssertionResult
            import time
            
            logger.info("Testing assertion result reporting...")
            result = AssertionResult(
                assertion_urn=assertion_urn,
                timestamp_millis=int(time.time() * 1000),
                result_type="SUCCESS",
                properties={"test": "true", "connection": "verified"}
            )
            
            if ingester.report_assertion_result(result):
                logger.info("✅ Successfully reported assertion result!")
                return True
            else:
                logger.error("❌ Failed to report assertion result")
                return False
        else:
            logger.error("❌ Failed to create test assertion")
            return False
            
    except Exception as e:
        logger.error(f"❌ DataHub connection failed: {str(e)}")
        return False

def test_assertion_validation():
    """Test assertion data validation."""
    try:
        logger.info("Testing assertion validation...")
        
        # Test valid assertion
        valid_assertion = ExternalAssertion(
            source_id="test-validation-001",
            entity_urn="urn:li:dataset:(urn:li:dataPlatform:test,test.valid_table,PROD)",
            assertion_type="Validation Test",
            description="Test assertion for validation",
            platform="custom"
        )
        
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        ingester = DataHubAssertionIngester(datahub_gms_url, datahub_token)
        
        errors = ingester.validate_assertion_data(valid_assertion)
        if not errors:
            logger.info("✅ Valid assertion passed validation")
        else:
            logger.error(f"❌ Valid assertion failed validation: {errors}")
            return False
        
        # Test invalid assertion
        invalid_assertion = ExternalAssertion(
            source_id="",  # Missing source_id
            entity_urn="",  # Missing entity_urn
            assertion_type="",  # Missing assertion_type
            description="",  # Missing description
            platform=""  # Missing platform
        )
        
        errors = ingester.validate_assertion_data(invalid_assertion)
        if errors:
            logger.info(f"✅ Invalid assertion correctly failed validation: {len(errors)} errors")
        else:
            logger.error("❌ Invalid assertion should have failed validation")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Assertion validation test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("DataHub Connection and Assertion Tests")
    logger.info("=" * 50)
    
    # Test connection
    connection_ok = test_datahub_connection()
    
    if connection_ok:
        # Test validation
        validation_ok = test_assertion_validation()
        
        if validation_ok:
            logger.info("🎉 All tests passed! The assertion ingestion is ready to use.")
            return 0
        else:
            logger.error("❌ Validation tests failed")
            return 1
    else:
        logger.error("❌ Connection test failed")
        return 1

if __name__ == "__main__":
    exit(main())
