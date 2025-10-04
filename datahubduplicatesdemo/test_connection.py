#!/usr/bin/env python3
"""
Test DataHub connection and basic functionality
"""

import os
import sys
import logging
from dotenv import load_dotenv
from duplicate_detector import DataHubDuplicateDetector

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_datahub_connection():
    """Test DataHub connection and basic search functionality."""
    try:
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        if not datahub_token:
            logger.error("❌ DATAHUB_GMS_TOKEN environment variable is required")
            return False
        
        logger.info(f"Testing connection to DataHub at: {datahub_gms_url}")
        
        # Create detector instance
        detector = DataHubDuplicateDetector(datahub_gms_url, datahub_token)
        
        # Test basic search
        logger.info("Testing basic asset search...")
        assets = detector.search_assets(query="*", count=5)
        
        if not assets:
            logger.error("❌ No assets found in DataHub")
            return False
        
        logger.info(f"✅ Found {len(assets)} assets (showing first 5)")
        
        # Show sample assets
        for i, asset in enumerate(assets[:3], 1):
            info = detector.extract_asset_info(asset)
            logger.info(f"  {i}. {info['name']} ({info['type']}) - {info['platform']}")
        
        # Test entity type filtering
        logger.info("Testing entity type filtering...")
        datasets = detector.search_assets(entity_types=["dataset"], count=3)
        logger.info(f"✅ Found {len(datasets)} datasets")
        
        charts = detector.search_assets(entity_types=["chart"], count=3)
        logger.info(f"✅ Found {len(charts)} charts")
        
        dashboards = detector.search_assets(entity_types=["dashboard"], count=3)
        logger.info(f"✅ Found {len(dashboards)} dashboards")
        
        logger.info("✅ DataHub connection test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ DataHub connection test failed: {str(e)}")
        return False

def test_detection_algorithms():
    """Test the detection algorithms with sample data."""
    try:
        logger.info("Testing detection algorithms...")
        
        # Create detector instance
        datahub_gms_url = os.getenv('DATAHUB_GMS_URL', 'https://test-environment.acryl.io/gms')
        datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        detector = DataHubDuplicateDetector(datahub_gms_url, datahub_token)
        
        # Test name similarity
        logger.info("Testing name similarity calculation...")
        test_names = [
            ("customer_data", "customer_data_v2"),
            ("user_table", "users_table"),
            ("sales_report", "sales_reports"),
            ("product_info", "product_information"),
            ("orders", "order_data")
        ]
        
        for name1, name2 in test_names:
            similarity = detector.calculate_name_similarity(name1, name2)
            logger.info(f"  '{name1}' vs '{name2}': {similarity:.2%}")
        
        # Test schema similarity
        logger.info("Testing schema similarity calculation...")
        schema1 = [
            {"fieldPath": "id", "type": "INTEGER"},
            {"fieldPath": "name", "type": "VARCHAR"},
            {"fieldPath": "email", "type": "VARCHAR"}
        ]
        schema2 = [
            {"fieldPath": "id", "type": "INTEGER"},
            {"fieldPath": "name", "type": "VARCHAR"},
            {"fieldPath": "email", "type": "VARCHAR"},
            {"fieldPath": "phone", "type": "VARCHAR"}
        ]
        
        similarity = detector.calculate_schema_similarity(schema1, schema2)
        logger.info(f"  Schema similarity: {similarity:.2%}")
        
        logger.info("✅ Detection algorithms test successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Detection algorithms test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    logger.info("Starting DataHub Duplicate Detector tests...")
    
    # Test connection
    connection_ok = test_datahub_connection()
    
    if connection_ok:
        # Test algorithms
        algorithms_ok = test_detection_algorithms()
        
        if algorithms_ok:
            logger.info("🎉 All tests passed! The duplicate detector is ready to use.")
            return 0
        else:
            logger.error("❌ Algorithm tests failed")
            return 1
    else:
        logger.error("❌ Connection test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
