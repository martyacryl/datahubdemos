#!/usr/bin/env python3
"""
Extract DMFs from Snowflake and ingest them into DataHub as custom assertions.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import snowflake.connector
from datahub_assertion_ingester import DataHubAssertionIngester, ExternalAssertion

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SnowflakeDMFExtractor:
    """Extract DMFs from Snowflake and convert to DataHub assertions."""
    
    def __init__(self):
        self.snowflake_config = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE', 'DEMO_DB'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA', 'DEMO_SCHEMA')
        }
        
        self.datahub_gms_url = os.getenv('DATAHUB_GMS_URL')
        self.datahub_token = os.getenv('DATAHUB_GMS_TOKEN')
        
        if not self.datahub_token:
            raise ValueError("DATAHUB_GMS_TOKEN environment variable is required")
    
    def connect_to_snowflake(self):
        """Connect to Snowflake."""
        try:
            conn = snowflake.connector.connect(**self.snowflake_config)
            logger.info("✅ Connected to Snowflake successfully")
            return conn
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {str(e)}")
            raise
    
    def extract_dmfs(self, conn) -> List[Dict[str, Any]]:
        """Extract DMF information from Snowflake."""
        try:
            cursor = conn.cursor()
            
            # Query to get DMF information
            query = """
            SELECT 
                TABLE_NAME,
                COLUMN_NAME,
                METRIC_FUNCTION_NAME,
                EXPECTATION_NAME,
                EXPECTATION_EXPRESSION,
                CREATED_ON
            FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS_RAW
            WHERE TABLE_NAME = 'CUSTOMERS'
            AND EXPECTATION_NAME IS NOT NULL
            ORDER BY CREATED_ON DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            dmfs = []
            for row in results:
                dmf = {
                    'table_name': row[0],
                    'column_name': row[1],
                    'metric_function': row[2],
                    'expectation_name': row[3],
                    'expectation_expression': row[4],
                    'created_on': row[5].isoformat() if row[5] else None
                }
                dmfs.append(dmf)
            
            logger.info(f"✅ Extracted {len(dmfs)} DMFs from Snowflake")
            return dmfs
            
        except Exception as e:
            logger.error(f"❌ Failed to extract DMFs: {str(e)}")
            raise
        finally:
            cursor.close()
    
    def convert_to_datahub_assertion(self, dmf: Dict[str, Any]) -> ExternalAssertion:
        """Convert Snowflake DMF to DataHub assertion."""
        
        # Construct DataHub URN for the table
        table_urn = f"urn:li:dataset:(urn:li:dataPlatform:snowflake,{self.snowflake_config['database']}.{self.snowflake_config['schema']}.{dmf['table_name']},PROD)"
        
        # Create description
        description = f"Snowflake DMF: {dmf['metric_function']} on column '{dmf['column_name']}' with expectation '{dmf['expectation_name']}'"
        
        # Create external URL (Snowflake console URL)
        external_url = f"https://{self.snowflake_config['account']}.snowflakecomputing.com/console#/data/databases/{self.snowflake_config['database']}/schemas/{self.snowflake_config['schema']}/tables/{dmf['table_name']}"
        
        # Create logic description
        logic = f"{dmf['metric_function']} ON ({dmf['column_name']}) {dmf['expectation_expression']}"
        
        return ExternalAssertion(
            source_id=f"snowflake_dmf_{dmf['expectation_name']}",
            entity_urn=table_urn,
            assertion_type="Data Quality Expectation",
            description=description,
            platform="snowflake",
            external_url=external_url,
            logic=logic,
            properties={
                "snowflake_table": dmf['table_name'],
                "snowflake_column": dmf['column_name'],
                "metric_function": dmf['metric_function'],
                "expectation_name": dmf['expectation_name'],
                "expectation_expression": dmf['expectation_expression'],
                "created_on": dmf['created_on']
            }
        )
    
    def ingest_to_datahub(self, assertions: List[ExternalAssertion]) -> List[str]:
        """Ingest assertions into DataHub."""
        try:
            ingester = DataHubAssertionIngester(self.datahub_gms_url, self.datahub_token)
            assertion_urns = []
            
            for assertion in assertions:
                logger.info(f"Creating assertion: {assertion.source_id}")
                assertion_urn = ingester.create_assertion(assertion)
                
                if assertion_urn:
                    assertion_urns.append(assertion_urn)
                    logger.info(f"✅ Created assertion: {assertion_urn}")
                else:
                    logger.error(f"❌ Failed to create assertion: {assertion.source_id}")
            
            return assertion_urns
            
        except Exception as e:
            logger.error(f"❌ Failed to ingest assertions to DataHub: {str(e)}")
            raise
    
    def run_extraction(self):
        """Run the complete extraction and ingestion process."""
        logger.info("🚀 Starting Snowflake DMF extraction and DataHub ingestion")
        
        # Connect to Snowflake
        conn = self.connect_to_snowflake()
        
        try:
            # Extract DMFs
            dmfs = self.extract_dmfs(conn)
            
            if not dmfs:
                logger.warning("⚠️ No DMFs found in Snowflake. Make sure you've run the setup_snowflake_demo.sql script first.")
                return
            
            # Convert to DataHub assertions
            assertions = [self.convert_to_datahub_assertion(dmf) for dmf in dmfs]
            
            # Ingest to DataHub
            assertion_urns = self.ingest_to_datahub(assertions)
            
            # Save results
            results = {
                "timestamp": datetime.now().isoformat(),
                "snowflake_dmfs_extracted": len(dmfs),
                "datahub_assertions_created": len(assertion_urns),
                "assertion_urns": assertion_urns,
                "dmfs": dmfs
            }
            
            with open("dmf_extraction_results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info("🎉 DMF extraction and ingestion completed successfully!")
            logger.info(f"📊 Extracted {len(dmfs)} DMFs from Snowflake")
            logger.info(f"📊 Created {len(assertion_urns)} assertions in DataHub")
            logger.info(f"📄 Results saved to: dmf_extraction_results.json")
            
        finally:
            conn.close()

def main():
    """Main function."""
    try:
        extractor = SnowflakeDMFExtractor()
        extractor.run_extraction()
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
